from __future__ import annotations

import argparse
import shutil
import subprocess
import zipfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATASET_ROOT = ROOT / "data" / "raw" / "xabarnavis_datasets"
DOWNLOAD_ROOT = DATASET_ROOT / "_downloads"


@dataclass(frozen=True)
class KaggleDataset:
    key: str
    slug: str
    archive_name: str
    target_dir: Path
    purpose: str
    after_download: str


KAGGLE_DATASETS = {
    "cifake": KaggleDataset(
        key="cifake",
        slug="birdy654/cifake-real-and-ai-generated-synthetic-images",
        archive_name="cifake-real-and-ai-generated-synthetic-images.zip",
        target_dir=DATASET_ROOT / "_raw" / "cifake",
        purpose="Quick AI-vs-real experiment dataset. Low-resolution; not final forensic quality.",
        after_download="Run: python scripts\\datasets\\organize_cifake.py",
    ),
    "casia_v2": KaggleDataset(
        key="casia_v2",
        slug="divg07/casia-20-image-tampering-detection-dataset",
        archive_name="casia-20-image-tampering-detection-dataset.zip",
        target_dir=DATASET_ROOT / "_raw" / "casia_v2",
        purpose="Manipulated/edited image detection: splicing and copy-move.",
        after_download="Place authentic images under real/casia_authentic and tampered images under manipulated/casia_v2.",
    ),
    "artifact": KaggleDataset(
        key="artifact",
        slug="awsaf49/artifact-dataset",
        archive_name="artifact-dataset.zip",
        target_dir=DATASET_ROOT / "_raw" / "artifact",
        purpose="Additional real/synthetic AI-image data for generalization experiments.",
        after_download="Inspect folders, then place real images in real/artifact_real and fake images in ai_generated/artifact.",
    ),
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Download external datasets for Xabarnavis.")
    parser.add_argument("datasets", nargs="*", help="Dataset keys, or 'all_kaggle'.")
    parser.add_argument("--list", action="store_true", help="List supported datasets.")
    parser.add_argument("--no-extract", action="store_true", help="Download zip files only.")
    args = parser.parse_args()

    if args.list:
        list_datasets()
        return

    keys = expand_keys(args.datasets or ["cifake"])
    ensure_kaggle_available()
    DOWNLOAD_ROOT.mkdir(parents=True, exist_ok=True)

    for key in keys:
        spec = KAGGLE_DATASETS[key]
        zip_path = DOWNLOAD_ROOT / spec.archive_name
        print(f"\n== {spec.key}: {spec.purpose} ==")
        download_kaggle_dataset(spec, zip_path)
        if not args.no_extract:
            extract_zip(zip_path, spec.target_dir)
        print(spec.after_download)


def list_datasets() -> None:
    print("Supported Kaggle datasets:")
    for spec in KAGGLE_DATASETS.values():
        print(f"- {spec.key}")
        print(f"  Kaggle: {spec.slug}")
        print(f"  Target: {spec.target_dir}")
        print(f"  Purpose: {spec.purpose}")
        print(f"  Next: {spec.after_download}")

    print("\nManual datasets:")
    print("- genimage: https://github.com/GenImage-Dataset/GenImage")
    print("  Put real images under data/raw/xabarnavis_datasets/real/genimage_real")
    print("  Put fake images under data/raw/xabarnavis_datasets/ai_generated/genimage/<generator>")
    print("- wildfake: https://github.com/hy-zpg/AIGC-Image-Detection-Dataset")
    print("  Put fake images under data/raw/xabarnavis_datasets/ai_generated/wildfake")
    print("- imd2020: https://staff.utia.cas.cz/novozada/db/")
    print("  Put images under data/raw/xabarnavis_datasets/manipulated/imd2020")
    print("- coverage: https://github.com/wenbihan/coverage")
    print("  Put images under data/raw/xabarnavis_datasets/manipulated/coverage")


def expand_keys(raw_keys: list[str]) -> list[str]:
    keys: list[str] = []
    for key in raw_keys:
        if key == "all_kaggle":
            keys.extend(KAGGLE_DATASETS.keys())
            continue
        if key not in KAGGLE_DATASETS:
            valid = ", ".join(["all_kaggle", *KAGGLE_DATASETS.keys()])
            raise SystemExit(f"Unknown dataset key '{key}'. Valid keys: {valid}")
        keys.append(key)
    return list(dict.fromkeys(keys))


def ensure_kaggle_available() -> None:
    if shutil.which("kaggle") is None:
        raise SystemExit(
            "Kaggle CLI not found. Run:\n"
            "  pip install -r requirements-datasets.txt\n\n"
            "Then create Kaggle API token:\n"
            "  1. Kaggle.com -> Account -> Create New API Token\n"
            "  2. Put kaggle.json in C:\\Users\\User2\\.kaggle\\kaggle.json"
        )


def download_kaggle_dataset(spec: KaggleDataset, zip_path: Path) -> None:
    if zip_path.exists():
        print(f"Already downloaded: {zip_path}")
        return
    command = [
        "kaggle",
        "datasets",
        "download",
        "-d",
        spec.slug,
        "-p",
        str(DOWNLOAD_ROOT),
    ]
    fallback_command = [
        "kaggle",
        "datasets",
        "download",
        "-d",
        spec.slug,
        "-p",
        str(DOWNLOAD_ROOT),
    ]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError:
        subprocess.run(fallback_command, check=True)


def extract_zip(zip_path: Path, target_dir: Path) -> None:
    if not zip_path.exists():
        raise SystemExit(
            f"Expected zip file not found: {zip_path}\n"
            "Run the download command again, then retry extraction."
        )

    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"Extracting {zip_path} -> {target_dir}")
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(target_dir)
    print(f"Extracted: {target_dir}")


if __name__ == "__main__":
    main()





