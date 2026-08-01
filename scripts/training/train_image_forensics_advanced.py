from __future__ import annotations

import argparse
import copy
import csv
import io
import json
import math
import random
from contextlib import nullcontext
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from PIL import Image, ImageFilter, ImageFile
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms
from torchvision.transforms import functional as TF
from tqdm import tqdm


ImageFile.LOAD_TRUNCATED_IMAGES = True
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA = ROOT / "data" / "raw" / "xabarnavis_datasets"
BINARY_LABELS = {"real": 0, "ai_generated": 1}
THREE_CLASS_LABELS = {"real": 0, "ai_generated": 1, "manipulated": 2}


@dataclass(frozen=True)
class Config:
    dataset_root: str
    train_csv: str
    val_csv: str
    test_csv: str
    output_dir: str
    image_size: int
    batch_size: int
    epochs: int
    learning_rate: float
    backbone_learning_rate: float
    weight_decay: float
    label_smoothing: float
    warmup_epochs: int
    accumulation_steps: int
    patience: int
    num_workers: int
    seed: int
    device: str
    pretrained: bool


class RobustTrainTransform:
    def __init__(self, size: int) -> None:
        self.size = size
        self.crop = transforms.RandomResizedCrop(size, scale=(0.55, 1.0), ratio=(0.75, 1.333))
        self.jitter = transforms.ColorJitter(0.12, 0.12, 0.08, 0.02)
        self.normalize = transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])

    def __call__(self, image: Image.Image) -> torch.Tensor:
        image = image.convert("RGB")
        if random.random() < 0.50:
            image = TF.hflip(image)
        image = self.crop(image)
        if random.random() < 0.35:
            image = self.jitter(image)
        if random.random() < 0.25:
            image = image.filter(ImageFilter.GaussianBlur(random.uniform(0.1, 1.2)))
        if random.random() < 0.55:
            image = jpeg_roundtrip(image, random.choice([50, 60, 70, 80, 90, 95]))
        if random.random() < 0.20:
            small = random.choice([128, 160, 192, 224])
            image = image.resize((small, small), Image.Resampling.BILINEAR).resize(
                (self.size, self.size), Image.Resampling.BICUBIC
            )
        return self.normalize(TF.to_tensor(image))


def jpeg_roundtrip(image: Image.Image, quality: int) -> Image.Image:
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=quality, subsampling=random.choice([0, 1, 2]))
    buffer.seek(0)
    with Image.open(buffer) as decoded:
        return decoded.convert("RGB")


class ManifestDataset(Dataset):
    def __init__(self, root: Path, manifest: Path, transform: object, label_map: dict[str, int]) -> None:
        self.root = root
        self.label_map = label_map
        self.rows = pd.read_csv(manifest)
        self.rows = self.rows[self.rows.label.isin(label_map)].reset_index(drop=True)
        if self.rows.empty:
            raise ValueError(f"No real/ai_generated samples in {manifest}")
        self.transform = transform

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor, int]:
        row = self.rows.iloc[index]
        with Image.open(self.root / str(row.image_path)) as image:
            tensor = self.transform(image.convert("RGB"))
        return tensor, torch.tensor(self.label_map[str(row.label)]), index


class SpectralBranch(nn.Module):
    def __init__(self, output_dim: int = 256) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Conv2d(1, 32, 5, stride=2, padding=2), nn.BatchNorm2d(32), nn.GELU(),
            nn.Conv2d(32, 64, 3, stride=2, padding=1), nn.BatchNorm2d(64), nn.GELU(),
            nn.Conv2d(64, 128, 3, stride=2, padding=1), nn.BatchNorm2d(128), nn.GELU(),
            nn.Conv2d(128, 256, 3, stride=2, padding=1), nn.BatchNorm2d(256), nn.GELU(),
            nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(256, output_dim), nn.GELU(),
        )

    def forward(self, image: torch.Tensor) -> torch.Tensor:
        # FFT remains float32 under AMP; half-precision CUDA FFT supports only
        # restricted power-of-two dimensions and is less stable for this branch.
        with torch.autocast(device_type=image.device.type, enabled=False):
            image32 = image.float()
            gray = 0.299 * image32[:, 0:1] + 0.587 * image32[:, 1:2] + 0.114 * image32[:, 2:3]
            spectrum = torch.fft.fftshift(torch.fft.fft2(gray, norm="ortho"), dim=(-2, -1)).abs()
            spectrum = torch.log1p(spectrum)
            mean = spectrum.mean(dim=(-2, -1), keepdim=True)
            std = spectrum.std(dim=(-2, -1), keepdim=True).clamp_min(1e-6)
        return self.network((spectrum - mean) / std)


class RGBSpectralForensics(nn.Module):
    def __init__(self, pretrained: bool = True, num_classes: int = 2) -> None:
        super().__init__()
        weights = models.ConvNeXt_Tiny_Weights.DEFAULT if pretrained else None
        self.rgb = models.convnext_tiny(weights=weights)
        rgb_dim = self.rgb.classifier[-1].in_features
        self.rgb.classifier = nn.Identity()
        self.spectral = SpectralBranch(256)
        self.classifier = nn.Sequential(
            nn.LayerNorm(rgb_dim + 256),
            nn.Dropout(0.30),
            nn.Linear(rgb_dim + 256, 256),
            nn.GELU(),
            nn.Dropout(0.20),
            nn.Linear(256, num_classes),
        )

    def forward(self, image: torch.Tensor) -> torch.Tensor:
        rgb_features = self.rgb(image).flatten(1)
        spectral_features = self.spectral(image)
        return self.classifier(torch.cat([rgb_features, spectral_features], dim=1))


class ModelEMA:
    def __init__(self, model: nn.Module, decay: float = 0.9995) -> None:
        self.model = copy.deepcopy(model).eval()
        self.decay = decay
        for parameter in self.model.parameters():
            parameter.requires_grad_(False)

    @torch.no_grad()
    def update(self, model: nn.Module) -> None:
        source = model.state_dict()
        for name, value in self.model.state_dict().items():
            if value.is_floating_point():
                value.mul_(self.decay).add_(source[name].detach(), alpha=1.0 - self.decay)
            else:
                value.copy_(source[name])


def main() -> None:
    args = parse_args()
    set_seed(args.seed)
    label_map = THREE_CLASS_LABELS if args.task == "three_class" else BINARY_LABELS
    if args.task == "three_class" and args.train_csv == DEFAULT_DATA / "metadata/train.csv":
        args.train_csv = DEFAULT_DATA / "metadata_3class/train.csv"
        args.val_csv = DEFAULT_DATA / "metadata_3class/val.csv"
        args.test_csv = DEFAULT_DATA / "metadata_3class/test.csv"
    device = resolve_device(args.device)
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    config = Config(
        str(args.dataset_root.resolve()), str(args.train_csv), str(args.val_csv), str(args.test_csv),
        str(output), args.image_size, args.batch_size, args.epochs, args.learning_rate,
        args.backbone_learning_rate, args.weight_decay, args.label_smoothing, args.warmup_epochs,
        args.accumulation_steps, args.patience, args.num_workers, args.seed, device, args.pretrained,
    )
    (output / "config.json").write_text(json.dumps(asdict(config), indent=2), encoding="utf-8")

    train_transform = RobustTrainTransform(args.image_size)
    eval_transform = transforms.Compose([
        transforms.Resize(int(args.image_size * 1.10)), transforms.CenterCrop(args.image_size),
        transforms.ToTensor(), transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    train_ds = ManifestDataset(args.dataset_root, args.train_csv, train_transform, label_map)
    val_ds = ManifestDataset(args.dataset_root, args.val_csv, eval_transform, label_map)
    test_ds = ManifestDataset(args.dataset_root, args.test_csv, eval_transform, label_map)
    train_loader = loader(train_ds, args, True)
    val_loader = loader(val_ds, args, False)
    test_loader = loader(test_ds, args, False)

    model = RGBSpectralForensics(args.pretrained, len(label_map)).to(device)
    ema = ModelEMA(model, args.ema_decay)
    weights = class_weights(train_ds, device)
    criterion = nn.CrossEntropyLoss(weight=weights, label_smoothing=args.label_smoothing)
    optimizer = torch.optim.AdamW([
        {"params": model.rgb.parameters(), "lr": args.backbone_learning_rate},
        {"params": model.spectral.parameters(), "lr": args.learning_rate},
        {"params": model.classifier.parameters(), "lr": args.learning_rate},
    ], weight_decay=args.weight_decay)
    total_steps = math.ceil(len(train_loader) / args.accumulation_steps) * args.epochs
    warmup_steps = math.ceil(len(train_loader) / args.accumulation_steps) * args.warmup_epochs
    scheduler = torch.optim.lr_scheduler.LambdaLR(
        optimizer, lambda step: lr_multiplier(step, warmup_steps, total_steps)
    )
    scaler = torch.amp.GradScaler("cuda", enabled=device.startswith("cuda"))
    start_epoch, best_auc = 1, -1.0
    if args.resume:
        checkpoint = torch.load(args.resume, map_location=device)
        model.load_state_dict(checkpoint["model"])
        ema.model.load_state_dict(checkpoint["ema"])
        optimizer.load_state_dict(checkpoint["optimizer"])
        scheduler.load_state_dict(checkpoint["scheduler"])
        start_epoch, best_auc = checkpoint["epoch"] + 1, checkpoint["best_auc"]

    metrics_path = output / "metrics.csv"
    if not metrics_path.exists():
        metrics_path.write_text("epoch,train_loss,val_auc,val_f1,val_accuracy,learning_rate\n", encoding="utf-8")
    stale = 0
    for epoch in range(start_epoch, args.epochs + 1):
        loss = train_epoch(model, ema, train_loader, criterion, optimizer, scheduler, scaler, device, args)
        metrics, _ = evaluate(ema.model, val_loader, device, len(label_map))
        current_auc = metrics["auc"]
        with metrics_path.open("a", newline="", encoding="utf-8") as file:
            csv.writer(file).writerow([epoch, loss, current_auc, metrics["f1"], metrics["accuracy"], optimizer.param_groups[-1]["lr"]])
        improved = current_auc > best_auc
        best_auc = max(best_auc, current_auc)
        stale = 0 if improved else stale + 1
        checkpoint = {
            "epoch": epoch, "best_auc": best_auc, "model": model.state_dict(), "ema": ema.model.state_dict(),
            "optimizer": optimizer.state_dict(), "scheduler": scheduler.state_dict(), "config": asdict(config),
        }
        torch.save(checkpoint, output / "last.pt")
        if improved:
            torch.save(checkpoint, output / "best.pt")
        print(json.dumps({"epoch": epoch, "train_loss": loss, "validation": metrics, "best_auc": best_auc}, indent=2))
        if stale >= args.patience:
            print(f"Early stopping after {stale} epochs without AUC improvement.")
            break

    best = torch.load(output / "best.pt", map_location=device)
    ema.model.load_state_dict(best["ema"])
    test_metrics, predictions = evaluate(ema.model, test_loader, device, len(label_map))
    group_metrics = evaluate_groups(test_ds.rows, predictions, len(label_map))
    result = {"test": test_metrics, "groups": group_metrics, "best_validation_auc": best["best_auc"]}
    (output / "test_metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (output / "model_metadata.json").write_text(json.dumps({
        "created_at": datetime.now(timezone.utc).isoformat(), "architecture": "ConvNeXt-Tiny RGB + FFT spectral CNN",
        "labels": label_map, "task": args.task, "checkpoint": "best EMA", "forensic_limit": "Probability screening, not proof of authenticity",
    }, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train Xabarnavis advanced RGB + spectral AI-image detector.")
    parser.add_argument("--dataset-root", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--train-csv", type=Path, default=DEFAULT_DATA / "metadata/train.csv")
    parser.add_argument("--val-csv", type=Path, default=DEFAULT_DATA / "metadata/val.csv")
    parser.add_argument("--test-csv", type=Path, default=DEFAULT_DATA / "metadata/test.csv")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts/runs/image/rgb-spectral-v1")
    parser.add_argument("--task", choices=["binary", "three_class"], default="binary")
    parser.add_argument("--image-size", type=int, default=384)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--backbone-learning-rate", type=float, default=3e-5)
    parser.add_argument("--weight-decay", type=float, default=0.05)
    parser.add_argument("--label-smoothing", type=float, default=0.05)
    parser.add_argument("--warmup-epochs", type=int, default=2)
    parser.add_argument("--accumulation-steps", type=int, default=4)
    parser.add_argument("--patience", type=int, default=6)
    parser.add_argument("--ema-decay", type=float, default=0.9995)
    parser.add_argument("--num-workers", type=int, default=4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--pretrained", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--resume", type=Path)
    return parser.parse_args()


def loader(dataset: Dataset, args: argparse.Namespace, shuffle: bool) -> DataLoader:
    return DataLoader(dataset, batch_size=args.batch_size, shuffle=shuffle, num_workers=args.num_workers,
                      pin_memory=args.device != "cpu", persistent_workers=args.num_workers > 0,
                      drop_last=shuffle)


def train_epoch(model: nn.Module, ema: ModelEMA, data: DataLoader, criterion: nn.Module,
                optimizer: torch.optim.Optimizer, scheduler: object, scaler: object,
                device: str, args: argparse.Namespace) -> float:
    model.train()
    optimizer.zero_grad(set_to_none=True)
    total_loss, total = 0.0, 0
    for step, (images, labels, _) in enumerate(tqdm(data, desc="training"), 1):
        images, labels = images.to(device, non_blocking=True), labels.to(device, non_blocking=True)
        context = torch.amp.autocast("cuda") if device.startswith("cuda") else nullcontext()
        with context:
            loss = criterion(model(images), labels) / args.accumulation_steps
        scaler.scale(loss).backward()
        if step % args.accumulation_steps == 0 or step == len(data):
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(optimizer)
            scaler.update()
            optimizer.zero_grad(set_to_none=True)
            scheduler.step()
            ema.update(model)
        total_loss += float(loss.detach()) * args.accumulation_steps * labels.size(0)
        total += labels.size(0)
    return total_loss / max(total, 1)


@torch.no_grad()
def evaluate(model: nn.Module, data: DataLoader, device: str, num_classes: int) -> tuple[dict[str, float], pd.DataFrame]:
    model.eval()
    labels_all, probabilities, indices = [], [], []
    for images, labels, batch_indices in tqdm(data, desc="evaluating", leave=False):
        logits = model(images.to(device, non_blocking=True))
        probabilities.extend(torch.softmax(logits, 1).cpu().tolist())
        labels_all.extend(labels.tolist())
        indices.extend(batch_indices.tolist())
    probability_array = np.asarray(probabilities)
    predictions = probability_array.argmax(axis=1).tolist()
    average = "binary" if num_classes == 2 else "macro"
    precision, recall, f1, _ = precision_recall_fscore_support(labels_all, predictions, average=average, zero_division=0)
    try:
        auc = (
            roc_auc_score(labels_all, probability_array[:, 1])
            if num_classes == 2
            else roc_auc_score(labels_all, probability_array, multi_class="ovr", average="macro")
        )
    except ValueError:
        auc = 0.0
    metrics = {"auc": float(auc), "accuracy": float(accuracy_score(labels_all, predictions)),
               "precision": float(precision), "recall": float(recall), "f1": float(f1)}
    frame_data: dict[str, object] = {"row_index": indices, "label_id": labels_all, "prediction": predictions}
    for class_id in range(num_classes):
        frame_data[f"prob_{class_id}"] = probability_array[:, class_id]
    return metrics, pd.DataFrame(frame_data)


def evaluate_groups(rows: pd.DataFrame, predictions: pd.DataFrame, num_classes: int) -> dict[str, dict[str, dict[str, float]]]:
    joined = predictions.merge(rows.reset_index().rename(columns={"index": "row_index"}), on="row_index")
    output: dict[str, dict[str, dict[str, float]]] = {}
    for column in ("source", "generator"):
        if column not in joined:
            continue
        output[column] = {}
        for name, group in joined.groupby(column):
            labels = group.label_id.tolist()
            predicted = group.prediction.tolist()
            metrics = {"count": int(len(group)), "accuracy": float(accuracy_score(labels, predicted))}
            if len(set(labels)) == num_classes:
                probs = group[[f"prob_{item}" for item in range(num_classes)]].to_numpy()
                metrics["auc"] = float(
                    roc_auc_score(labels, probs[:, 1]) if num_classes == 2
                    else roc_auc_score(labels, probs, multi_class="ovr", average="macro")
                )
            output[column][str(name)] = metrics
    return output


def class_weights(dataset: ManifestDataset, device: str) -> torch.Tensor:
    counts = dataset.rows.label.map(dataset.label_map).value_counts()
    total = len(dataset)
    class_count = len(dataset.label_map)
    return torch.tensor([total / (class_count * max(int(counts.get(i, 0)), 1)) for i in range(class_count)], device=device)


def lr_multiplier(step: int, warmup: int, total: int) -> float:
    if step < warmup:
        return max(step, 1) / max(warmup, 1)
    progress = (step - warmup) / max(total - warmup, 1)
    return 0.05 + 0.95 * 0.5 * (1.0 + math.cos(math.pi * min(progress, 1.0)))


def resolve_device(requested: str) -> str:
    if requested == "cuda" and not torch.cuda.is_available():
        raise SystemExit("CUDA requested but CUDA PyTorch is unavailable.")
    return "cuda" if requested == "auto" and torch.cuda.is_available() else ("cpu" if requested == "auto" else requested)


def set_seed(seed: int) -> None:
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = True


if __name__ == "__main__":
    main()
