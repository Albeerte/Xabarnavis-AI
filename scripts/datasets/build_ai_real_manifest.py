from __future__ import annotations

import argparse
import csv
import hashlib
import random
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
DATASET_ROOT = ROOT / "data" / "raw" / "xabarnavis_datasets"
METADATA_DIR = DATASET_ROOT / "metadata"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


@dataclass(frozen=True)
class ImageRecord:
    path: Path
    label: str
    source: str
    generator: str
    sha256: str = ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Build AI-vs-real CSV manifests for Xabarnavis training.")
    parser.add_argument("--dataset-root", type=Path, default=DATASET_ROOT)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--val-ratio", type=float, default=0.10)
    parser.add_argument("--test-ratio", type=float, default=0.10)
    parser.add_argument("--max-per-class", type=int, default=0, help="0 means no limit.")
    parser.add_argument(
        "--balance",
        action="store_true",
        help="Limit each class to the smaller class count before splitting.",
    )
    parser.add_argument(
        "--holdout-generators",
        nargs="*",
        default=[],
        help="AI generator names reserved completely for the test split.",
    )
    args = parser.parse_args()

    dataset_root = args.dataset_root.resolve()
    records = validate_and_deduplicate(collect_records(dataset_root))
    if not records:
        raise SystemExit(
            "No images found. Download/extract datasets first, then re-run this script."
        )

    random.seed(args.seed)
    splits = split_records(
        records,
        args.val_ratio,
        args.test_ratio,
        args.max_per_class,
        args.balance,
        {normalize_name(item) for item in args.holdout_generators},
    )
    write_manifests(dataset_root, splits)

    for split_name, split_records_ in splits.items():
        real_count = sum(1 for item in split_records_ if item.label == "real")
        ai_count = sum(1 for item in split_records_ if item.label == "ai_generated")
        print(f"{split_name}: {len(split_records_)} images ({real_count} real, {ai_count} ai_generated)")


def collect_records(dataset_root: Path) -> list[ImageRecord]:
    records: list[ImageRecord] = []

    real_roots = [
        dataset_root / "real" / "coco_real",
        dataset_root / "real" / "local_camera_real",
        dataset_root / "real" / "local_social_real",
        dataset_root / "real" / "raise1k_real",
        dataset_root / "real" / "imagenet_real",
        dataset_root / "real" / "cifake_real",
        dataset_root / "real" / "genimage_real",
        dataset_root / "real" / "artifact_real",
        dataset_root / "real" / "casia_authentic",
        dataset_root / "real" / "hf_real_midjourney_dalle_sd_nano",
    ]
    ai_roots = [
        dataset_root / "ai_generated" / "synthbuster",
        dataset_root / "ai_generated" / "local_generated",
        dataset_root / "ai_generated" / "wildfake",
        dataset_root / "ai_generated" / "aigc_benchmark",
        dataset_root / "ai_generated" / "ms_cocoai",
        dataset_root / "ai_generated" / "genimage",
        dataset_root / "ai_generated" / "cifake",
        dataset_root / "ai_generated" / "artifact",
        dataset_root / "ai_generated" / "hf_midjourney_dalle_sd_nano",
    ]

    for root in real_roots:
        records.extend(
            ImageRecord(path=image_path, label="real", source=root.name, generator="none")
            for image_path in iter_images(root)
        )

    for root in ai_roots:
        for image_path in iter_images(root):
            records.append(
                ImageRecord(
                    path=image_path,
                    label="ai_generated",
                    source=_source_name(root, image_path),
                    generator=_generator_name(root, image_path),
                )
            )

    records.extend(collect_artifact_download_records(dataset_root))

    return records


def collect_artifact_download_records(dataset_root: Path) -> list[ImageRecord]:
    artifact_root = dataset_root / "_downloads"
    if not artifact_root.exists():
        return []

    metadata_records = collect_artifact_metadata_records(artifact_root)
    if metadata_records:
        return metadata_records

    records: list[ImageRecord] = []
    for label_dir in artifact_root.rglob("*"):
        if not label_dir.is_dir() or label_dir.name not in {"0_real", "1_fake"}:
            continue

        label = "real" if label_dir.name == "0_real" else "ai_generated"
        relative_parts = label_dir.relative_to(artifact_root).parts
        source_name = f"artifact_{normalize_name(relative_parts[0])}" if relative_parts else "artifact"
        generator = "none" if label == "real" else source_name.removeprefix("artifact_")

        records.extend(
            ImageRecord(
                path=image_path,
                label=label,
                source=source_name,
                generator=generator,
            )
            for image_path in iter_images(label_dir)
        )
    return records


def collect_artifact_metadata_records(artifact_root: Path) -> list[ImageRecord]:
    records: list[ImageRecord] = []
    for metadata_path in sorted(artifact_root.rglob("metadata.csv")):
        source_root = metadata_path.parent
        source_name = f"artifact_{normalize_name(source_root.name)}"
        with metadata_path.open(newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                relative_image = row.get("image_path", "")
                if not relative_image:
                    continue
                image_path = source_root / relative_image
                if not image_path.exists() or image_path.suffix.lower() not in IMAGE_EXTENSIONS:
                    continue

                target = str(row.get("target", "")).strip()
                label = "real" if target in {"0", "0.0"} else "ai_generated"
                records.append(
                    ImageRecord(
                        path=image_path,
                        label=label,
                        source=source_name,
                        generator="none" if label == "real" else normalize_name(source_root.name),
                    )
                )
    return records


def iter_images(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*") if path.suffix.lower() in IMAGE_EXTENSIONS)


def validate_and_deduplicate(records: list[ImageRecord]) -> list[ImageRecord]:
    unique: list[ImageRecord] = []
    seen_hashes: set[str] = set()
    corrupt = 0
    duplicates = 0
    for record in records:
        try:
            with Image.open(record.path) as image:
                image.verify()
            digest = sha256_file(record.path)
        except (OSError, ValueError):
            corrupt += 1
            continue
        if digest in seen_hashes:
            duplicates += 1
            continue
        seen_hashes.add(digest)
        unique.append(ImageRecord(record.path, record.label, record.source, record.generator, digest))
    print(f"Validation: {len(unique)} unique, {duplicates} exact duplicates, {corrupt} corrupt")
    return unique


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_name(root: Path, image_path: Path) -> str:
    try:
        first_part = image_path.relative_to(root).parts[0]
    except (ValueError, IndexError):
        first_part = root.name
    return root.name if root.name != "genimage" else f"genimage_{first_part}"


def _generator_name(root: Path, image_path: Path) -> str:
    try:
        relative = image_path.relative_to(root)
    except ValueError:
        return "unknown"
    if root.name == "synthbuster" and relative.parts:
        return normalize_name(relative.parts[0])
    if root.name == "genimage" and relative.parts:
        return normalize_name(relative.parts[0])
    return "unknown"


def normalize_name(value: str) -> str:
    return value.strip().lower().replace(" ", "_").replace("-", "_")


def split_records(
    records: list[ImageRecord],
    val_ratio: float,
    test_ratio: float,
    max_per_class: int,
    balance: bool,
    holdout_generators: set[str] | None = None,
) -> dict[str, list[ImageRecord]]:
    holdout_generators = holdout_generators or set()
    holdout = [
        record
        for record in records
        if record.label == "ai_generated" and normalize_name(record.generator) in holdout_generators
    ]
    records = [record for record in records if record not in holdout]
    by_label = {
        "real": [record for record in records if record.label == "real"],
        "ai_generated": [record for record in records if record.label == "ai_generated"],
    }

    if not by_label["real"] or not by_label["ai_generated"]:
        raise SystemExit(
            f"Need both classes. Found {len(by_label['real'])} real and "
            f"{len(by_label['ai_generated'])} ai_generated images."
        )

    class_limit = min(len(by_label["real"]), len(by_label["ai_generated"])) if balance else 0
    if max_per_class > 0:
        class_limit = min(class_limit, max_per_class) if class_limit else max_per_class

    splits = {"train": [], "val": [], "test": list(holdout)}
    for label_records in by_label.values():
        random.shuffle(label_records)
        if class_limit > 0:
            label_records = label_records[:class_limit]
        test_count = int(len(label_records) * test_ratio)
        val_count = int(len(label_records) * val_ratio)
        splits["test"].extend(label_records[:test_count])
        splits["val"].extend(label_records[test_count : test_count + val_count])
        splits["train"].extend(label_records[test_count + val_count :])

    for split_records_ in splits.values():
        random.shuffle(split_records_)
    return splits


def write_manifests(dataset_root: Path, splits: dict[str, list[ImageRecord]]) -> None:
    metadata_dir = dataset_root / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    header = [
        "image_path",
        "label",
        "source",
        "generator",
        "base_id",
        "sha256",
        "manipulation_type",
        "has_mask",
        "mask_path",
        "exif_status",
        "split",
    ]

    for split_name, records in splits.items():
        csv_path = metadata_dir / f"{split_name}.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(header)
            for record in records:
                writer.writerow(
                    [
                        record.path.relative_to(dataset_root).as_posix(),
                        record.label,
                        record.source,
                        record.generator,
                        record.sha256,
                        record.sha256,
                        "none",
                        "0",
                        "",
                        "unknown",
                        split_name,
                    ]
                )


if __name__ == "__main__":
    main()





