from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm


ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = ROOT / "data" / "datasets" / "audio" / "xabarnavis_audio_0_4_deepfake_audio_dataset"
METADATA_DIR = DATASET_DIR / "metadata"
DEFAULT_MODEL_ID = "facebook/wav2vec2-base"
SAMPLE_RATE = 16000


@dataclass
class AudioItem:
    path: Path
    label: int


class AudioCsvDataset(Dataset):
    def __init__(self, csv_path: Path, max_seconds: float) -> None:
        self.items: list[AudioItem] = []
        with csv_path.open(newline="", encoding="utf-8") as file:
            for row in csv.DictReader(file):
                path = Path(row["path"])
                if path.is_file():
                    self.items.append(AudioItem(path=path, label=int(row["label"])))
        if not self.items:
            raise ValueError(f"No audio files found from manifest: {csv_path}")
        self.max_seconds = max_seconds

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> dict:
        import librosa
        import numpy as np

        item = self.items[index]
        audio, _ = librosa.load(str(item.path), sr=SAMPLE_RATE, mono=True)
        max_samples = int(SAMPLE_RATE * self.max_seconds)
        if len(audio) > max_samples:
            audio = audio[:max_samples]
        if len(audio) == 0:
            audio = np.zeros(SAMPLE_RATE, dtype=np.float32)
        return {"audio": audio.astype("float32"), "label": item.label}


def main() -> None:
    parser = argparse.ArgumentParser(description="Train Xabarnavis Audio 0.4 fake-vs-real speech classifier.")
    parser.add_argument("--train-csv", type=Path, default=METADATA_DIR / "train.csv")
    parser.add_argument("--val-csv", type=Path, default=METADATA_DIR / "val.csv")
    parser.add_argument("--test-csv", type=Path, default=METADATA_DIR / "test.csv")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts" / "runs" / "legacy" / "audio_04_wav2vec2")
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--max-seconds", type=float, default=10.0)
    parser.add_argument("--freeze-feature-extractor", action="store_true")
    args = parser.parse_args()

    from transformers import AutoFeatureExtractor, AutoModelForAudioClassification

    args.output_dir.mkdir(parents=True, exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    extractor = AutoFeatureExtractor.from_pretrained(args.model_id)
    model = AutoModelForAudioClassification.from_pretrained(
        args.model_id,
        num_labels=2,
        label2id={"real": 0, "fake": 1},
        id2label={0: "real", 1: "fake"},
        ignore_mismatched_sizes=True,
    ).to(device)
    if args.freeze_feature_extractor and hasattr(model, "freeze_feature_encoder"):
        model.freeze_feature_encoder()

    train_loader = make_loader(args.train_csv, extractor, args.batch_size, args.max_seconds, shuffle=True)
    val_loader = make_loader(args.val_csv, extractor, args.batch_size, args.max_seconds, shuffle=False)
    test_loader = make_loader(args.test_csv, extractor, args.batch_size, args.max_seconds, shuffle=False)

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)
    criterion = nn.CrossEntropyLoss()
    best_val_acc = -1.0

    for epoch in range(1, args.epochs + 1):
        train_loss = train_one_epoch(model, train_loader, optimizer, criterion, device, epoch)
        val_metrics = evaluate(model, val_loader, criterion, device, "val")
        row = {"epoch": epoch, "train_loss": train_loss, **val_metrics}
        append_metrics(args.output_dir / "metrics.jsonl", row)
        print(json.dumps(row, indent=2))
        if val_metrics["val_accuracy"] > best_val_acc:
            best_val_acc = val_metrics["val_accuracy"]
            save_model(model, extractor, args.output_dir / "best_model")
            torch.save({"epoch": epoch, "val_accuracy": best_val_acc}, args.output_dir / "best.pt")

    test_metrics = evaluate(model, test_loader, criterion, device, "test")
    (args.output_dir / "test_metrics.json").write_text(json.dumps(test_metrics, indent=2), encoding="utf-8")
    print(json.dumps(test_metrics, indent=2))
    save_model(model, extractor, args.output_dir / "last_model")


def make_loader(csv_path: Path, extractor, batch_size: int, max_seconds: float, shuffle: bool) -> DataLoader:
    dataset = AudioCsvDataset(csv_path, max_seconds=max_seconds)

    def collate(batch: list[dict]) -> dict:
        audios = [item["audio"] for item in batch]
        labels = torch.tensor([item["label"] for item in batch], dtype=torch.long)
        inputs = extractor(audios, sampling_rate=SAMPLE_RATE, return_tensors="pt", padding=True)
        inputs["labels"] = labels
        return inputs

    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, num_workers=0, collate_fn=collate)


def train_one_epoch(model, loader: DataLoader, optimizer, criterion, device: str, epoch: int) -> float:
    model.train()
    losses: list[float] = []
    for batch in tqdm(loader, desc=f"audio train epoch {epoch}", leave=False):
        labels = batch.pop("labels").to(device)
        batch = {key: value.to(device) for key, value in batch.items()}
        optimizer.zero_grad(set_to_none=True)
        logits = model(**batch).logits
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()
        losses.append(float(loss.detach().cpu()))
    return sum(losses) / max(len(losses), 1)


@torch.no_grad()
def evaluate(model, loader: DataLoader, criterion, device: str, prefix: str) -> dict[str, float]:
    model.eval()
    total = 0
    correct = 0
    losses: list[float] = []
    for batch in tqdm(loader, desc=f"audio eval {prefix}", leave=False):
        labels = batch.pop("labels").to(device)
        batch = {key: value.to(device) for key, value in batch.items()}
        logits = model(**batch).logits
        loss = criterion(logits, labels)
        pred = torch.argmax(logits, dim=1)
        total += labels.numel()
        correct += int((pred == labels).sum().item())
        losses.append(float(loss.detach().cpu()))
    return {
        f"{prefix}_loss": round(sum(losses) / max(len(losses), 1), 6),
        f"{prefix}_accuracy": round(correct / max(total, 1), 6),
    }


def save_model(model, extractor, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(output_dir)
    extractor.save_pretrained(output_dir)


def append_metrics(path: Path, row: dict) -> None:
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(row) + "\n")


if __name__ == "__main__":
    main()





