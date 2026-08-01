from __future__ import annotations

import argparse
import shutil
import sys
import time
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATASET_ROOT = ROOT / "data" / "raw" / "xabarnavis_datasets"
DOWNLOAD_ROOT = DATASET_ROOT / "_downloads"


@dataclass(frozen=True)
class DatasetSpec:
    key: str
    title: str
    url: str
    compressed_gb: float
    target_dir: Path
    purpose: str


DATASETS = {
    "synthbuster": DatasetSpec(
        key="synthbuster",
        title="Synthbuster diffusion-image benchmark",
        url="https://zenodo.org/api/records/10066460/files/synthbuster.zip/content",
        compressed_gb=11.52,
        target_dir=DATASET_ROOT / "ai_generated" / "synthbuster",
        purpose="AI-generated detection, Fourier/frequency stress test",
    ),
    "coco_train2017": DatasetSpec(
        key="coco_train2017",
        title="MS COCO 2017 train images",
        url="http://images.cocodataset.org/zips/train2017.zip",
        compressed_gb=18.0,
        target_dir=DATASET_ROOT / "real" / "coco_real",
        purpose="Real-photo baseline for AI vs real training",
    ),
    "coco_val2017": DatasetSpec(
        key="coco_val2017",
        title="MS COCO 2017 validation images",
        url="http://images.cocodataset.org/zips/val2017.zip",
        compressed_gb=1.0,
        target_dir=DATASET_ROOT / "test_holdout" / "real_coco_val2017",
        purpose="Real-photo validation and smoke testing",
    ),
    "coco_annotations2017": DatasetSpec(
        key="coco_annotations2017",
        title="MS COCO 2017 annotations",
        url="http://images.cocodataset.org/annotations/annotations_trainval2017.zip",
        compressed_gb=0.24,
        target_dir=DATASET_ROOT / "metadata" / "coco_annotations2017",
        purpose="Optional labels/captions for filtering real-photo categories",
    ),
}

MINIMUM_20GB_KEYS = ("synthbuster", "coco_train2017")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download the minimum open datasets for Xabarnavis local forensic MVP."
    )
    parser.add_argument(
        "datasets",
        nargs="*",
        help="Dataset keys to download. Use 'minimum_20gb' for the recommended first bundle.",
    )
    parser.add_argument("--extract", action="store_true", help="Extract zip files after download.")
    parser.add_argument("--list", action="store_true", help="Show available datasets and exit.")
    args = parser.parse_args()

    if args.list:
        print_plan()
        return

    keys = expand_keys(args.datasets or ["minimum_20gb"])
    DATASET_ROOT.mkdir(parents=True, exist_ok=True)
    DOWNLOAD_ROOT.mkdir(parents=True, exist_ok=True)

    print(f"Download folder: {DOWNLOAD_ROOT}")
    print(f"Selected compressed size: {sum(DATASETS[key].compressed_gb for key in keys):.2f} GB")

    for key in keys:
        spec = DATASETS[key]
        archive_path = DOWNLOAD_ROOT / f"{spec.key}.zip"
        print(f"\n== {spec.title} ==")
        print(f"Purpose: {spec.purpose}")
        print(f"URL: {spec.url}")
        download_with_resume(spec.url, archive_path)

        if args.extract:
            extract_zip(archive_path, spec.target_dir)


def print_plan() -> None:
    print("Available datasets:")
    for spec in DATASETS.values():
        print(f"- {spec.key}: {spec.title} ({spec.compressed_gb:.2f} GB)")
        print(f"  Target: {spec.target_dir}")
        print(f"  Purpose: {spec.purpose}")
    minimum_size = sum(DATASETS[key].compressed_gb for key in MINIMUM_20GB_KEYS)
    print("\nRecommended minimum_20gb bundle:")
    print(", ".join(MINIMUM_20GB_KEYS))
    print(f"Compressed total: {minimum_size:.2f} GB")


def expand_keys(raw_keys: list[str]) -> list[str]:
    keys: list[str] = []
    for key in raw_keys:
        if key == "minimum_20gb":
            keys.extend(MINIMUM_20GB_KEYS)
            continue
        if key not in DATASETS:
            valid = ", ".join(["minimum_20gb", *DATASETS.keys()])
            raise SystemExit(f"Unknown dataset key '{key}'. Valid keys: {valid}")
        keys.append(key)
    return list(dict.fromkeys(keys))


def download_with_resume(url: str, destination: Path) -> None:
    part_path = destination.with_suffix(destination.suffix + ".part")
    existing_size = part_path.stat().st_size if part_path.exists() else 0
    if destination.exists():
        print(f"Already downloaded: {destination}")
        return

    request = urllib.request.Request(url)
    if existing_size:
        request.add_header("Range", f"bytes={existing_size}-")
        print(f"Resuming from {existing_size / 1024**3:.2f} GB")

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            mode = "ab" if existing_size else "wb"
            total_size = _total_size(response, existing_size)
            stream_to_file(response, part_path, mode, existing_size, total_size)
    except urllib.error.HTTPError as exc:
        if existing_size and exc.code == 416:
            part_path.rename(destination)
            print(f"Download complete: {destination}")
            return
        raise

    part_path.rename(destination)
    print(f"Download complete: {destination}")


def _total_size(response: object, existing_size: int) -> int | None:
    length = response.headers.get("Content-Length")
    if length is None:
        return None
    return int(length) + existing_size


def stream_to_file(response: object, path: Path, mode: str, existing_size: int, total_size: int | None) -> None:
    downloaded = existing_size
    started = time.time()
    last_print = 0.0
    with path.open(mode + "") as file:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            file.write(chunk)
            downloaded += len(chunk)
            now = time.time()
            if now - last_print >= 2:
                last_print = now
                elapsed = max(now - started, 0.001)
                speed = (downloaded - existing_size) / elapsed / 1024**2
                if total_size:
                    percent = downloaded / total_size * 100
                    print(
                        f"  {downloaded / 1024**3:.2f}/{total_size / 1024**3:.2f} GB "
                        f"({percent:.1f}%) at {speed:.1f} MB/s"
                    )
                else:
                    print(f"  {downloaded / 1024**3:.2f} GB at {speed:.1f} MB/s")


def extract_zip(archive_path: Path, target_dir: Path) -> None:
    if not archive_path.exists():
        raise SystemExit(f"Cannot extract missing archive: {archive_path}")
    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"Extracting to: {target_dir}")
    with zipfile.ZipFile(archive_path) as archive:
        archive.extractall(target_dir)
    print(f"Extracted: {target_dir}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted. Re-run the same command to resume the current download.")
        sys.exit(130)
    except shutil.Error as exc:
        raise SystemExit(str(exc)) from exc





