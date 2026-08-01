from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATASET_ROOT = ROOT / "data" / "raw" / "xabarnavis_datasets"
RAW_CIFAKE = DATASET_ROOT / "_raw" / "cifake"
REAL_TARGET = DATASET_ROOT / "real" / "cifake_real"
AI_TARGET = DATASET_ROOT / "ai_generated" / "cifake"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def main() -> None:
    if not RAW_CIFAKE.exists():
        raise SystemExit(
            f"CIFAKE raw folder not found: {RAW_CIFAKE}\n"
            "Run: python scripts\\datasets\\download_external_datasets.py cifake"
        )

    real_sources = find_named_dirs(RAW_CIFAKE, {"real", "REAL"})
    fake_sources = find_named_dirs(RAW_CIFAKE, {"fake", "FAKE"})
    if not real_sources or not fake_sources:
        raise SystemExit(
            "Could not find REAL/FAKE folders inside CIFAKE raw data. "
            f"Inspect manually: {RAW_CIFAKE}"
        )

    real_count = copy_images(real_sources, REAL_TARGET, prefix="cifake_real")
    fake_count = copy_images(fake_sources, AI_TARGET, prefix="cifake_ai")

    print(f"Copied {real_count} real images -> {REAL_TARGET}")
    print(f"Copied {fake_count} AI images -> {AI_TARGET}")
    print("Next: python scripts\\datasets\\build_ai_real_manifest.py --balance")


def find_named_dirs(root: Path, names: set[str]) -> list[Path]:
    return [path for path in root.rglob("*") if path.is_dir() and path.name in names]


def copy_images(source_dirs: list[Path], target_dir: Path, prefix: str) -> int:
    target_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for source_dir in source_dirs:
        split_name = source_dir.parent.name.lower()
        for image_path in sorted(source_dir.iterdir()):
            if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
                continue
            target_path = target_dir / f"{prefix}_{split_name}_{count:06d}{image_path.suffix.lower()}"
            if not target_path.exists():
                shutil.copy2(image_path, target_path)
            count += 1
    return count


if __name__ == "__main__":
    main()





