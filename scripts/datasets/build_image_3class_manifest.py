from __future__ import annotations

import argparse
import csv
import random
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATASET_ROOT = ROOT / "data" / "raw" / "xabarnavis_datasets"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


@dataclass(frozen=True)
class ImageRecord:
    path: Path
    label: str
    source: str
    generator: str
    manipulation_type: str
    has_mask: str = "0"
    mask_path: str = ""
    exif_status: str = "unknown"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build 3-class image manifests: real, AI-generated, manipulated.")
    parser.add_argument("--dataset-root", type=Path, default=DATASET_ROOT)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--val-ratio", type=float, default=0.10)
    parser.add_argument("--test-ratio", type=float, default=0.10)
    parser.add_argument("--max-per-class", type=int, default=0, help="0 means no limit.")
    parser.add_argument("--balance", action="store_true", help="Limit all classes to the smallest class count.")
    parser.add_argument("--metadata-dir-name", default="metadata_3class")
    args = parser.parse_args()

    dataset_root = args.dataset_root.resolve()
    records = deduplicate_records(collect_records(dataset_root))
    splits = split_records(records, args.val_ratio, args.test_ratio, args.max_per_class, args.balance, args.seed)
    write_manifests(dataset_root, args.metadata_dir_name, splits)

    for split_name, split_records_ in splits.items():
        counts = {label: sum(1 for item in split_records_ if item.label == label) for label in LABELS}
        print(f"{split_name}: {len(split_records_)} images ({format_counts(counts)})")


LABELS = ("real", "ai_generated", "manipulated")


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
    manipulated_roots = [
        (dataset_root / "manipulated" / "casia_v2", "casia_v2", "splicing"),
        (dataset_root / "manipulated" / "local_photoshop", "local_photoshop", "unknown"),
        (dataset_root / "manipulated" / "coverage", "coverage", "copy_move"),
        (dataset_root / "manipulated" / "defacto", "defacto", "unknown"),
        (dataset_root / "manipulated" / "imd2020", "imd2020", "unknown"),
        (dataset_root / "manipulated" / "nist_mfc", "nist_mfc", "unknown"),
        (dataset_root / "_downloads" / "generative_inpainting", "artifact_generative_inpainting", "inpainting"),
        (dataset_root / "_downloads" / "lama", "artifact_lama", "inpainting"),
        (dataset_root / "_downloads" / "mat", "artifact_mat", "inpainting"),
    ]

    for root in real_roots:
        records.extend(
            ImageRecord(path=image_path, label="real", source=root.name, generator="none", manipulation_type="none")
            for image_path in iter_images(root)
        )

    for root in ai_roots:
        for image_path in iter_images(root):
            records.append(
                ImageRecord(
                    path=image_path,
                    label="ai_generated",
                    source=source_name(root, image_path),
                    generator=generator_name(root, image_path),
                    manipulation_type="none",
                )
            )

    for root, source, manipulation_type in manipulated_roots:
        records.extend(
            ImageRecord(
                path=image_path,
                label="manipulated",
                source=source,
                generator="none",
                manipulation_type=manipulation_type,
            )
            for image_path in iter_images(root)
        )

    records.extend(collect_artifact_metadata_records(dataset_root / "_downloads"))
    return records


def collect_artifact_metadata_records(artifact_root: Path) -> list[ImageRecord]:
    records: list[ImageRecord] = []
    if not artifact_root.exists():
        return records

    for metadata_path in sorted(artifact_root.rglob("metadata.csv")):
        source_root = metadata_path.parent
        relative_parts = {part.lower() for part in metadata_path.relative_to(artifact_root).parts}
        # These sources are explicitly collected as local manipulation datasets
        # above. Their numeric metadata targets are manipulation-family IDs, not
        # binary real/AI labels. Reading them again as AI would create conflicting
        # labels and cross-split leakage for identical files.
        if relative_parts & {"generative_inpainting", "lama", "mat"}:
            continue
        source = f"artifact_{normalize_name(source_root.name)}"
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
                        source=source,
                        generator="none" if label == "real" else normalize_name(source_root.name),
                        manipulation_type="none",
                    )
                )
    return records


def deduplicate_records(records: list[ImageRecord]) -> list[ImageRecord]:
    by_path: dict[Path, ImageRecord] = {}
    conflicts: set[Path] = set()
    duplicates = 0
    for record in records:
        # Roots are already based on the single resolved dataset root. Avoid
        # Path.resolve() here: millions of Windows filesystem resolution calls
        # make integrity checks unnecessarily slow.
        key = record.path
        existing = by_path.get(key)
        if existing is None:
            by_path[key] = record
            continue
        duplicates += 1
        if existing.label != record.label:
            conflicts.add(key)

    # Ambiguous files are safer to exclude than to assign an invented label.
    clean = [record for path, record in by_path.items() if path not in conflicts]
    print(
        f"Manifest integrity: {len(clean)} unique paths, "
        f"{duplicates} duplicate rows, {len(conflicts)} conflicting paths excluded"
    )
    return clean


def iter_images(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*") if path.suffix.lower() in IMAGE_EXTENSIONS)


def source_name(root: Path, image_path: Path) -> str:
    try:
        first_part = image_path.relative_to(root).parts[0]
    except (ValueError, IndexError):
        first_part = root.name
    return root.name if root.name != "genimage" else f"genimage_{first_part}"


def generator_name(root: Path, image_path: Path) -> str:
    try:
        relative = image_path.relative_to(root)
    except ValueError:
        return "unknown"
    if root.name in {"synthbuster", "genimage"} and relative.parts:
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
    seed: int,
) -> dict[str, list[ImageRecord]]:
    random.seed(seed)
    by_label = {label: [record for record in records if record.label == label] for label in LABELS}
    missing = [label for label, items in by_label.items() if not items]
    if missing:
        counts = ", ".join(f"{label}={len(items)}" for label, items in by_label.items())
        raise SystemExit(f"Need all three classes. Missing: {', '.join(missing)}. Counts: {counts}")

    class_limit = min(len(items) for items in by_label.values()) if balance else 0
    if max_per_class > 0:
        class_limit = min(class_limit, max_per_class) if class_limit else max_per_class

    splits = {"train": [], "val": [], "test": []}
    for label_records in by_label.values():
        random.shuffle(label_records)
        if class_limit > 0:
            label_records = label_records[:class_limit]
        test_count = int(len(label_records) * test_ratio)
        val_count = int(len(label_records) * val_ratio)
        splits["test"].extend(label_records[:test_count])
        splits["val"].extend(label_records[test_count : test_count + val_count])
        splits["train"].extend(label_records[test_count + val_count :])

    for items in splits.values():
        random.shuffle(items)
    return splits


def write_manifests(dataset_root: Path, metadata_dir_name: str, splits: dict[str, list[ImageRecord]]) -> None:
    metadata_dir = dataset_root / metadata_dir_name
    metadata_dir.mkdir(parents=True, exist_ok=True)
    header = [
        "image_path",
        "label",
        "source",
        "generator",
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
                        record.manipulation_type,
                        record.has_mask,
                        record.mask_path,
                        record.exif_status,
                        split_name,
                    ]
                )


def format_counts(counts: dict[str, int]) -> str:
    return ", ".join(f"{label} {counts[label]}" for label in LABELS)


if __name__ == "__main__":
    main()
