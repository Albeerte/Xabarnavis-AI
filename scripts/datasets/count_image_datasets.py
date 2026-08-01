from __future__ import annotations

import argparse
import csv
import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DATASET_ROOT = ROOT / "data" / "raw" / "xabarnavis_datasets"
READY_ROOT = ROOT / "data" / "ready" / "image"
OUTPUT_PATH = ROOT / "storage" / "dataset_inventory.json"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Count all local Xabarnavis image datasets.")
    parser.add_argument("--dataset-root", type=Path, default=DATASET_ROOT)
    parser.add_argument("--ready-root", type=Path, default=READY_ROOT)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()

    inventory = {
        "status": "ready",
        "language": "uz",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "note_uz": "Bu hisob lokal papkalardagi mavjud image fayllar asosida tuzilgan.",
        "dataset_root": str(args.dataset_root.resolve()),
        "ready_dataset_root": str(args.ready_root.resolve()),
        "image_extensions": sorted(IMAGE_EXTENSIONS),
        "xabarnavis_datasets": count_dataset_root(args.dataset_root),
        "raw_manifests": count_raw_manifests(args.dataset_root),
        "data/ready/image": count_ready_dataset(args.ready_root),
    }
    inventory["grand_total_images"] = (
        inventory["xabarnavis_datasets"]["total_images"]
        + inventory["data/ready/image"]["total_images"]
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(_summary(inventory), ensure_ascii=False, indent=2))


def count_dataset_root(root: Path) -> dict[str, Any]:
    labels = ["real", "ai_generated", "manipulated", "test_holdout"]
    by_label: dict[str, Any] = {}
    total = 0
    for label in labels:
        label_root = root / label
        label_total, sources = count_sources(label_root)
        total += label_total
        by_label[label] = {"total_images": label_total, "sources": sources}

    downloads_total, download_sources = count_sources(root / "_downloads")
    raw_total, raw_sources = count_sources(root / "_raw")
    total_with_aux = total + downloads_total + raw_total
    return {
        "total_images": total,
        "total_images_including_auxiliary": total_with_aux,
        "by_label": by_label,
        "auxiliary": {
            "_downloads": {"total_images": downloads_total, "sources": download_sources},
            "_raw": {"total_images": raw_total, "sources": raw_sources},
        },
    }


def count_raw_manifests(root: Path) -> dict[str, Any]:
    return {
        "metadata": count_manifest_dir(root / "metadata"),
        "metadata_3class": count_manifest_dir(root / "metadata_3class"),
    }


def count_manifest_dir(metadata_dir: Path) -> dict[str, Any]:
    by_split: dict[str, Any] = {}
    total = 0
    for split in ["train", "val", "test"]:
        csv_path = metadata_dir / f"{split}.csv"
        split_count, by_label, by_source = count_manifest_csv(csv_path)
        total += split_count
        by_split[split] = {
            "total_images": split_count,
            "by_label": dict(sorted(by_label.items())),
            "by_source": dict(sorted(by_source.items())),
        }
    return {
        "path": str(metadata_dir.resolve()),
        "total_images": total,
        "by_split": by_split,
    }


def count_manifest_csv(csv_path: Path) -> tuple[int, Counter[str], Counter[str]]:
    by_label: Counter[str] = Counter()
    by_source: Counter[str] = Counter()
    row_count = 0
    if not csv_path.is_file():
        return row_count, by_label, by_source

    with csv_path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            image_path = row.get("image_path") or ""
            if Path(image_path).suffix.lower() not in IMAGE_EXTENSIONS:
                continue
            row_count += 1
            by_label[row.get("label") or "unknown"] += 1
            by_source[row.get("source") or "unknown"] += 1
    return row_count, by_label, by_source


def count_sources(root: Path) -> tuple[int, list[dict[str, Any]]]:
    if not root.is_dir():
        return 0, []

    sources: list[dict[str, Any]] = []
    total = 0
    for child in sorted(item for item in root.iterdir() if item.is_dir()):
        count, by_ext = count_images(child)
        total += count
        sources.append({"name": child.name, "path": str(child), "image_count": count, "by_extension": dict(sorted(by_ext.items()))})

    direct_count, direct_ext = count_images_direct(root)
    if direct_count:
        total += direct_count
        sources.insert(0, {"name": "_direct_files", "path": str(root), "image_count": direct_count, "by_extension": dict(sorted(direct_ext.items()))})
    return total, sources


def count_images(root: Path) -> tuple[int, Counter[str]]:
    total = 0
    by_ext: Counter[str] = Counter()
    for dirpath, _dirnames, filenames in os.walk(root):
        for filename in filenames:
            ext = Path(filename).suffix.lower()
            if ext in IMAGE_EXTENSIONS:
                total += 1
                by_ext[ext] += 1
    return total, by_ext


def count_images_direct(root: Path) -> tuple[int, Counter[str]]:
    total = 0
    by_ext: Counter[str] = Counter()
    for item in root.iterdir():
        if not item.is_file():
            continue
        ext = item.suffix.lower()
        if ext in IMAGE_EXTENSIONS:
            total += 1
            by_ext[ext] += 1
    return total, by_ext


def count_ready_dataset(root: Path) -> dict[str, Any]:
    metadata_dir = root / "metadata"
    by_split: dict[str, Any] = {}
    by_label: Counter[str] = Counter()
    by_source: Counter[str] = Counter()
    total = 0

    for split in ["train", "val", "test"]:
        csv_path = metadata_dir / f"{split}.csv"
        split_counter: Counter[str] = Counter()
        source_counter: Counter[str] = Counter()
        row_count = 0
        if csv_path.is_file():
            with csv_path.open(newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    image_path = root / (row.get("image_path") or "")
                    if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
                        continue
                    row_count += 1
                    label = row.get("label") or "unknown"
                    source = row.get("source") or "unknown"
                    split_counter[label] += 1
                    source_counter[source] += 1
                    by_label[label] += 1
                    by_source[source] += 1
        total += row_count
        by_split[split] = {
            "total_images": row_count,
            "by_label": dict(sorted(split_counter.items())),
            "by_source": dict(sorted(source_counter.items())),
        }

    filesystem_total, filesystem_ext = count_images(root)
    return {
        "total_images": total,
        "filesystem_total_images": filesystem_total,
        "by_split": by_split,
        "by_label": dict(sorted(by_label.items())),
        "by_source": dict(sorted(by_source.items())),
        "by_extension": dict(sorted(filesystem_ext.items())),
    }


def _summary(inventory: dict[str, Any]) -> dict[str, Any]:
    datasets = inventory["xabarnavis_datasets"]
    ready = inventory["data/ready/image"]
    return {
        "output": str(OUTPUT_PATH),
        "data/raw/xabarnavis_datasets_total": datasets["total_images"],
        "data/raw/xabarnavis_datasets_including_auxiliary": datasets["total_images_including_auxiliary"],
        "ready_dataset_total": ready["total_images"],
        "grand_total_images": inventory["grand_total_images"],
    }


if __name__ == "__main__":
    main()






