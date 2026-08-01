from __future__ import annotations

import argparse
import csv
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
from PIL import Image, ImageFile
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support, roc_auc_score
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms
from tqdm import tqdm


ImageFile.LOAD_TRUNCATED_IMAGES = True

ROOT = Path(__file__).resolve().parents[2]
DATASET_ROOT = ROOT / "data" / "raw" / "xabarnavis_datasets"
RUNS_DIR = ROOT / "artifacts" / "runs" / "legacy"
LABEL_TO_ID = {"real": 0, "ai_generated": 1}
ID_TO_LABEL = {0: "real", 1: "ai_generated"}


@dataclass(frozen=True)
class TrainConfig:
    dataset_root: str
    train_csv: str
    val_csv: str
    test_csv: str | None
    output_dir: str
    backbone: str
    image_size: int
    batch_size: int
    epochs: int
    lr: float
    weight_decay: float
    num_workers: int
    seed: int
    pretrained: bool
    freeze_backbone: bool
    class_weights: str
    device: str
    media_type: str
    dataset_origin: str
    model_name: str
    model_version: str


class ManifestImageDataset(Dataset):
    def __init__(self, dataset_root: Path, csv_path: Path, transform: transforms.Compose) -> None:
        self.dataset_root = dataset_root
        self.csv_path = csv_path
        self.transform = transform
        self.rows = pd.read_csv(csv_path)
        self.rows = self.rows[self.rows["label"].isin(LABEL_TO_ID.keys())].reset_index(drop=True)
        if self.rows.empty:
            raise ValueError(f"No AI-vs-real rows found in {csv_path}")

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        row = self.rows.iloc[index]
        image_path = self.dataset_root / str(row["image_path"])
        with Image.open(image_path) as image:
            image_tensor = self.transform(image.convert("RGB"))
        label = torch.tensor(LABEL_TO_ID[str(row["label"])], dtype=torch.long)
        return image_tensor, label


def main() -> None:
    args = parse_args()
    set_seed(args.seed)

    dataset_root = args.dataset_root.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    device = resolve_device(args.device)
    config = TrainConfig(
        dataset_root=str(dataset_root),
        train_csv=str(args.train_csv),
        val_csv=str(args.val_csv),
        test_csv=str(args.test_csv) if args.test_csv else None,
        output_dir=str(output_dir),
        backbone=args.backbone,
        image_size=args.image_size,
        batch_size=args.batch_size,
        epochs=args.epochs,
        lr=args.lr,
        weight_decay=args.weight_decay,
        num_workers=args.num_workers,
        seed=args.seed,
        pretrained=args.pretrained,
        freeze_backbone=args.freeze_backbone,
        class_weights=args.class_weights,
        device=device,
        media_type=args.media_type,
        dataset_origin=args.dataset_origin,
        model_name=args.model_name,
        model_version=args.model_version,
    )
    (output_dir / "config.json").write_text(json.dumps(asdict(config), indent=2), encoding="utf-8")

    train_transform, eval_transform = build_transforms(args.image_size)
    train_loader = make_loader(dataset_root, args.train_csv, train_transform, args.batch_size, args.num_workers, True)
    val_loader = make_loader(dataset_root, args.val_csv, eval_transform, args.batch_size, args.num_workers, False)
    test_loader = (
        make_loader(dataset_root, args.test_csv, eval_transform, args.batch_size, args.num_workers, False)
        if args.test_csv
        else None
    )

    model = build_model(args.backbone, args.pretrained, args.freeze_backbone).to(device)
    class_weight_tensor = build_class_weights(train_loader.dataset, args.class_weights, device)
    criterion = nn.CrossEntropyLoss(weight=class_weight_tensor)
    optimizer = torch.optim.AdamW(
        [param for param in model.parameters() if param.requires_grad],
        lr=args.lr,
        weight_decay=args.weight_decay,
    )
    scaler = torch.amp.GradScaler("cuda", enabled=device.startswith("cuda"))

    start_epoch = 1
    best_auc = -1.0
    if args.resume:
        checkpoint = torch.load(args.resume, map_location=device)
        model.load_state_dict(checkpoint["model"])
        optimizer.load_state_dict(checkpoint["optimizer"])
        start_epoch = int(checkpoint["epoch"]) + 1
        best_auc = float(checkpoint.get("best_auc", -1.0))
        print(f"Resumed from {args.resume} at epoch {start_epoch}")

    metrics_csv = output_dir / "metrics.csv"
    init_metrics_csv(metrics_csv)

    for epoch in range(start_epoch, args.epochs + 1):
        train_loss = train_one_epoch(model, train_loader, criterion, optimizer, scaler, device, epoch)
        val_metrics = evaluate(model, val_loader, criterion, device, split_name="val")
        row = {"epoch": epoch, "train_loss": train_loss, **val_metrics}
        append_metrics(metrics_csv, row)
        print(json.dumps(row, indent=2))

        is_best = val_metrics["val_auc"] > best_auc
        if is_best:
            best_auc = val_metrics["val_auc"]
        save_checkpoint(output_dir, model, optimizer, epoch, best_auc, is_best)

    best_path = output_dir / "best.pt"
    if best_path.exists():
        checkpoint = torch.load(best_path, map_location=device)
        model.load_state_dict(checkpoint["model"])

    if test_loader is not None:
        test_metrics = evaluate(model, test_loader, criterion, device, split_name="test")
        (output_dir / "test_metrics.json").write_text(json.dumps(test_metrics, indent=2), encoding="utf-8")
        print(json.dumps(test_metrics, indent=2))

    if args.export_onnx:
        export_onnx(model, output_dir / "ai_detector_effnet_b0.onnx", args.image_size, device)

    metadata = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "media_type": args.media_type,
        "dataset_origin": args.dataset_origin,
        "model_name": args.model_name,
        "model_version": args.model_version,
        "labels": ID_TO_LABEL,
        "best_auc": best_auc,
        "note": "Binary AI-vs-real model. Validate on unseen generators before forensic use.",
    }
    (output_dir / "model_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train Xabarnavis AI-vs-real image classifier.")
    parser.add_argument("--dataset-root", type=Path, default=DATASET_ROOT)
    parser.add_argument("--train-csv", type=Path, default=DATASET_ROOT / "metadata" / "train.csv")
    parser.add_argument("--val-csv", type=Path, default=DATASET_ROOT / "metadata" / "val.csv")
    parser.add_argument("--test-csv", type=Path, default=DATASET_ROOT / "metadata" / "test.csv")
    parser.add_argument("--output-dir", type=Path, default=RUNS_DIR / "ai_real_effnet_b0")
    parser.add_argument("--backbone", choices=["efficientnet_b0", "resnet18"], default="efficientnet_b0")
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--num-workers", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    parser.add_argument("--media-type", default="photo", choices=["photo", "video", "audio", "text"])
    parser.add_argument("--dataset-origin", default="milliy", choices=["external", "milliy"])
    parser.add_argument("--model-name", default="xabarnavis_image_0.1")
    parser.add_argument("--model-version", default="0.1")
    parser.add_argument("--pretrained", action="store_true", help="Use ImageNet pretrained weights.")
    parser.add_argument("--freeze-backbone", action="store_true", help="Train only the classifier head.")
    parser.add_argument(
        "--class-weights",
        choices=["balanced", "none"],
        default="balanced",
        help="Use inverse-frequency class weights by default.",
    )
    parser.add_argument("--resume", type=Path, default=None)
    parser.add_argument("--export-onnx", action="store_true")
    return parser.parse_args()


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def resolve_device(device: str) -> str:
    if device == "auto":
        return "cuda" if torch_cuda_is_usable() else "cpu"
    if device == "cuda" and not torch_cuda_is_usable():
        raise SystemExit("CUDA requested, but this PyTorch build cannot execute on the installed GPU.")
    return device


def torch_cuda_is_usable() -> bool:
    try:
        if not torch.cuda.is_available():
            return False
        major, minor = torch.cuda.get_device_capability(0)
        arch = f"sm_{major}{minor}"
        arch_list = set(torch.cuda.get_arch_list()) if hasattr(torch.cuda, "get_arch_list") else set()
        if arch_list and arch not in arch_list:
            return False
        torch.zeros(1, device="cuda").cpu()
        return True
    except Exception:
        return False


def build_transforms(image_size: int) -> tuple[transforms.Compose, transforms.Compose]:
    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    train_transform = transforms.Compose(
        [
            transforms.RandomResizedCrop(image_size, scale=(0.75, 1.0)),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(brightness=0.08, contrast=0.08, saturation=0.05),
            transforms.ToTensor(),
            normalize,
        ]
    )
    eval_transform = transforms.Compose(
        [
            transforms.Resize(int(image_size * 1.15)),
            transforms.CenterCrop(image_size),
            transforms.ToTensor(),
            normalize,
        ]
    )
    return train_transform, eval_transform


def make_loader(
    dataset_root: Path,
    csv_path: Path,
    transform: transforms.Compose,
    batch_size: int,
    num_workers: int,
    shuffle: bool,
) -> DataLoader:
    dataset = ManifestImageDataset(dataset_root, csv_path, transform)
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=torch_cuda_is_usable(),
    )


def build_class_weights(dataset: ManifestImageDataset, mode: str, device: str) -> torch.Tensor | None:
    if mode == "none":
        return None
    counts = dataset.rows["label"].map(LABEL_TO_ID).value_counts().to_dict()
    total = sum(counts.values())
    weights = []
    for class_id in range(len(LABEL_TO_ID)):
        class_count = max(int(counts.get(class_id, 0)), 1)
        weights.append(total / (len(LABEL_TO_ID) * class_count))
    tensor = torch.tensor(weights, dtype=torch.float32, device=device)
    print(f"Using class weights: real={tensor[0].item():.4f}, ai_generated={tensor[1].item():.4f}")
    return tensor


def build_model(backbone: str, pretrained: bool, freeze_backbone: bool) -> nn.Module:
    if backbone == "efficientnet_b0":
        weights = models.EfficientNet_B0_Weights.DEFAULT if pretrained else None
        model = models.efficientnet_b0(weights=weights)
        if freeze_backbone:
            for param in model.features.parameters():
                param.requires_grad = False
        in_features = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(in_features, 2)
        return model

    weights = models.ResNet18_Weights.DEFAULT if pretrained else None
    model = models.resnet18(weights=weights)
    if freeze_backbone:
        for name, param in model.named_parameters():
            if not name.startswith("fc."):
                param.requires_grad = False
    model.fc = nn.Linear(model.fc.in_features, 2)
    return model


def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    scaler: torch.cuda.amp.GradScaler,
    device: str,
    epoch: int,
) -> float:
    model.train()
    total_loss = 0.0
    total_items = 0
    progress = tqdm(loader, desc=f"train epoch {epoch}", leave=False)
    for images, labels in progress:
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)
        optimizer.zero_grad(set_to_none=True)

        amp_context = torch.amp.autocast("cuda") if device.startswith("cuda") else nullcontext()
        with amp_context:
            logits = model(images)
            loss = criterion(logits, labels)

        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()

        batch_size = labels.size(0)
        total_loss += float(loss.detach().cpu()) * batch_size
        total_items += batch_size
        progress.set_postfix(loss=total_loss / max(total_items, 1))

    return total_loss / max(total_items, 1)


@torch.no_grad()
def evaluate(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: str,
    split_name: str,
) -> dict[str, float | list[list[int]]]:
    model.eval()
    total_loss = 0.0
    total_items = 0
    all_labels: list[int] = []
    all_predictions: list[int] = []
    all_ai_probs: list[float] = []

    for images, labels in tqdm(loader, desc=f"eval {split_name}", leave=False):
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)
        logits = model(images)
        loss = criterion(logits, labels)
        probs = torch.softmax(logits, dim=1)
        predictions = torch.argmax(probs, dim=1)

        batch_size = labels.size(0)
        total_loss += float(loss.detach().cpu()) * batch_size
        total_items += batch_size
        all_labels.extend(labels.cpu().tolist())
        all_predictions.extend(predictions.cpu().tolist())
        all_ai_probs.extend(probs[:, 1].cpu().tolist())

    precision, recall, f1, _ = precision_recall_fscore_support(
        all_labels,
        all_predictions,
        average="binary",
        zero_division=0,
    )
    try:
        auc = roc_auc_score(all_labels, all_ai_probs)
    except ValueError:
        auc = 0.0
    if not math.isfinite(float(auc)):
        auc = 0.0

    matrix = confusion_matrix(all_labels, all_predictions, labels=[0, 1]).tolist()
    return {
        f"{split_name}_loss": total_loss / max(total_items, 1),
        f"{split_name}_accuracy": accuracy_score(all_labels, all_predictions),
        f"{split_name}_precision_ai": float(precision),
        f"{split_name}_recall_ai": float(recall),
        f"{split_name}_f1_ai": float(f1),
        f"{split_name}_auc": float(auc),
        f"{split_name}_confusion_matrix": matrix,
    }


def init_metrics_csv(path: Path) -> None:
    if path.exists():
        return
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "epoch",
                "train_loss",
                "val_loss",
                "val_accuracy",
                "val_precision_ai",
                "val_recall_ai",
                "val_f1_ai",
                "val_auc",
                "val_confusion_matrix",
            ]
        )


def append_metrics(path: Path, row: dict[str, object]) -> None:
    with path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                row["epoch"],
                row["train_loss"],
                row["val_loss"],
                row["val_accuracy"],
                row["val_precision_ai"],
                row["val_recall_ai"],
                row["val_f1_ai"],
                row["val_auc"],
                json.dumps(row["val_confusion_matrix"]),
            ]
        )


def save_checkpoint(
    output_dir: Path,
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    epoch: int,
    best_auc: float,
    is_best: bool,
) -> None:
    payload = {
        "epoch": epoch,
        "best_auc": best_auc,
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict(),
    }
    torch.save(payload, output_dir / "last.pt")
    if is_best:
        torch.save(payload, output_dir / "best.pt")


def export_onnx(model: nn.Module, path: Path, image_size: int, device: str) -> None:
    model.eval()
    dummy = torch.randn(1, 3, image_size, image_size, device=device)
    torch.onnx.export(
        model,
        dummy,
        path,
        input_names=["image"],
        output_names=["logits"],
        dynamic_axes={"image": {0: "batch"}, "logits": {0: "batch"}},
        opset_version=18,
    )
    print(f"Exported ONNX model: {path}")


if __name__ == "__main__":
    main()





