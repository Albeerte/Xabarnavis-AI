from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATASET_ROOT = ROOT / "data" / "raw" / "xabarnavis_datasets"
RAW_CASIA = DATASET_ROOT / "_raw" / "casia_v2"
AUTHENTIC_TARGET = DATASET_ROOT / "real" / "casia_authentic"
TAMPERED_TARGET = DATASET_ROOT / "manipulated" / "casia_v2"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


def main() -> None:
    casia_root = find_casia_root()
    authentic_source = casia_root / "Au"
    tampered_source = casia_root / "Tp"
    if not authentic_source.exists() or not tampered_source.exists():
        raise SystemExit(f"Expected Au and Tp folders under {casia_root}")

    authentic_count = copy_images(authentic_source, AUTHENTIC_TARGET)
    tampered_count = copy_images(tampered_source, TAMPERED_TARGET)

    print(f"Copied {authentic_count} authentic images -> {AUTHENTIC_TARGET}")
    print(f"Copied {tampered_count} tampered images -> {TAMPERED_TARGET}")
    print("Next for AI-vs-real manifests:")
    print("  python scripts\\datasets\\build_ai_real_manifest.py --balance")
    print("For manipulated training, create a 3-class manifest next.")


def find_casia_root() -> Path:
    direct = RAW_CASIA / "CASIA2"
    if direct.exists():
        return direct
    candidates = [path for path in RAW_CASIA.rglob("*") if path.is_dir() and path.name == "CASIA2"]
    if candidates:
        return candidates[0]
    raise SystemExit(f"CASIA2 folder not found under {RAW_CASIA}")


def copy_images(source_dir: Path, target_dir: Path) -> int:
    target_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    skipped_existing = 0
    skipped_missing = 0
    for image_path in sorted(source_dir.rglob("*")):
        if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        target_path = target_dir / image_path.name
        if target_path.exists():
            skipped_existing += 1
            continue
        if not image_path.exists():
            skipped_missing += 1
            continue
        try:
            shutil.copy2(image_path, target_path)
        except FileNotFoundError:
            skipped_missing += 1
            continue
        count += 1
    if skipped_existing:
        print(f"Skipped {skipped_existing} existing files in {target_dir}")
    if skipped_missing:
        print(f"Skipped {skipped_missing} missing source files from {source_dir}")
    return count


if __name__ == "__main__":
    main()





