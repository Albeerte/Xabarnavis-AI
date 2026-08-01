from __future__ import annotations

import argparse
import csv
import random
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET = ROOT / "data" / "datasets" / "audio" / "xabarnavis_audio_0_4_deepfake_audio_dataset"
DEFAULT_METADATA = DEFAULT_DATASET / "metadata"
AUDIO_EXTS = {".wav", ".mp3", ".flac", ".m4a", ".ogg"}
FAKE_TOKENS = {"fake", "spoof", "deepfake", "synthetic", "ai", "generated", "clone"}
REAL_TOKENS = {"real", "bonafide", "bona-fide", "genuine", "human", "original", "authentic"}


@dataclass(frozen=True)
class AudioRecord:
    path: Path
    label: int
    label_name: str


def main() -> None:
    parser = argparse.ArgumentParser(description="Build train/val/test manifests for Xabarnavis Audio 0.4 dataset.")
    parser.add_argument("--dataset-dir", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--val-ratio", type=float, default=0.10)
    parser.add_argument("--test-ratio", type=float, default=0.10)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    records = find_audio_records(args.dataset_dir)
    if not records:
        raise SystemExit(
            f"No labelled audio files found under {args.dataset_dir}.\n"
            "Expected folder/file names containing labels such as real, bonafide, genuine, fake, spoof, deepfake, or synthetic."
        )

    fake_count = sum(1 for item in records if item.label == 1)
    real_count = sum(1 for item in records if item.label == 0)
    if fake_count == 0 or real_count == 0:
        raise SystemExit(f"Need both classes. Found real={real_count}, fake={fake_count}.")

    random.Random(args.seed).shuffle(records)
    splits = stratified_split(records, args.val_ratio, args.test_ratio, args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for split, rows in splits.items():
        write_csv(args.output_dir / f"{split}.csv", rows)

    print(f"Dataset: {args.dataset_dir}")
    print(f"Output: {args.output_dir}")
    print(f"Total: {len(records)} | real={real_count} | fake={fake_count}")
    for split, rows in splits.items():
        print(f"{split}: {len(rows)}")


def find_audio_records(dataset_dir: Path) -> list[AudioRecord]:
    records: list[AudioRecord] = []
    for path in dataset_dir.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in AUDIO_EXTS:
            continue
        label = infer_label(path)
        if label is None:
            continue
        records.append(AudioRecord(path=path, label=label, label_name="fake" if label == 1 else "real"))
    return records


def infer_label(path: Path) -> int | None:
    parts = [part.lower() for part in path.parts]
    name = path.stem.lower()
    haystack = [*parts, name]
    if any(any(token in item for token in FAKE_TOKENS) for item in haystack):
        return 1
    if any(any(token in item for token in REAL_TOKENS) for item in haystack):
        return 0
    return None


def stratified_split(records: list[AudioRecord], val_ratio: float, test_ratio: float, seed: int) -> dict[str, list[AudioRecord]]:
    rng = random.Random(seed)
    grouped = {0: [], 1: []}
    for item in records:
        grouped[item.label].append(item)
    output = {"train": [], "val": [], "test": []}
    for label_records in grouped.values():
        rng.shuffle(label_records)
        total = len(label_records)
        test_count = max(1, int(total * test_ratio))
        val_count = max(1, int(total * val_ratio))
        output["test"].extend(label_records[:test_count])
        output["val"].extend(label_records[test_count : test_count + val_count])
        output["train"].extend(label_records[test_count + val_count :])
    for rows in output.values():
        rng.shuffle(rows)
    return output


def write_csv(path: Path, records: list[AudioRecord]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["path", "label", "label_name"])
        writer.writeheader()
        for item in records:
            writer.writerow({"path": str(item.path), "label": item.label, "label_name": item.label_name})


if __name__ == "__main__":
    main()





