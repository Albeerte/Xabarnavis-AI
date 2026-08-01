from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
DATASET_ROOT = ROOT / "data" / "raw" / "xabarnavis_datasets"
RAW_ROOT = DATASET_ROOT / "_raw" / "hf_midjourney_dalle_sd_nano"
REAL_TARGET = DATASET_ROOT / "real" / "hf_real_midjourney_dalle_sd_nano"
AI_TARGET = DATASET_ROOT / "ai_generated" / "hf_midjourney_dalle_sd_nano"

REPO_ID = "julienlucas/midjourney-dalle-sd-nanobananapro-dataset"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Download and organize a Hugging Face AI-vs-real dataset.")
    parser.add_argument("--repo-id", default=REPO_ID)
    parser.add_argument("--max-images", type=int, default=0, help="0 means all images.")
    parser.add_argument("--max-per-class", type=int, default=0, help="0 means no per-class limit.")
    parser.add_argument("--reset-targets", action="store_true", help="Delete existing extracted images first.")
    parser.add_argument("--split", choices=["all", "train", "test"], default="all")
    args = parser.parse_args()

    RAW_ROOT.mkdir(parents=True, exist_ok=True)
    if args.reset_targets:
        reset_targets()
    REAL_TARGET.mkdir(parents=True, exist_ok=True)
    AI_TARGET.mkdir(parents=True, exist_ok=True)

    parquet_files = list_parquet_files(args.repo_id, args.split)
    print(f"Dataset: {args.repo_id}")
    print(f"Parquet files: {len(parquet_files)}")

    downloaded = []
    for parquet_path in parquet_files:
        local_path = hf_hub_download(
            repo_id=args.repo_id,
            filename=parquet_path,
            repo_type="dataset",
            local_dir=RAW_ROOT,
            local_dir_use_symlinks=False,
        )
        downloaded.append(Path(local_path))
        print(f"Downloaded: {parquet_path}")

    real_count, ai_count = extract_images(downloaded, args.max_images, args.max_per_class)
    print(f"Extracted real images: {real_count} -> {REAL_TARGET}")
    print(f"Extracted AI images: {ai_count} -> {AI_TARGET}")
    print("Next:")
    print("  python scripts\\datasets\\build_ai_real_manifest.py --balance")
    print("  python scripts\\training\\train_ai_real.py --pretrained --epochs 5 --batch-size 32 --output-dir artifacts\runs\legacy\\ai_real_v2_hf")


def list_parquet_files(repo_id: str, split: str) -> list[str]:
    url = f"https://huggingface.co/api/datasets/{repo_id}/tree/main?recursive=1"
    with urllib.request.urlopen(url) as response:
        items = json.load(response)
    parquet_files = [
        item["path"]
        for item in items
        if item.get("type") == "file" and str(item.get("path", "")).endswith(".parquet")
    ]
    if split != "all":
        parquet_files = [path for path in parquet_files if Path(path).name.startswith(f"{split}-")]
    return sorted(parquet_files)


def reset_targets() -> None:
    for target in (REAL_TARGET, AI_TARGET):
        if target.exists():
            for image_path in target.iterdir():
                if image_path.is_file() and image_path.suffix.lower() in IMAGE_EXTENSIONS:
                    image_path.unlink()


def extract_images(parquet_paths: list[Path], max_images: int, max_per_class: int) -> tuple[int, int]:
    real_count = count_existing(REAL_TARGET)
    ai_count = count_existing(AI_TARGET)
    written = 0

    for parquet_path in parquet_paths:
        table = pq.read_table(parquet_path)
        columns = table.column_names
        image_column = find_image_column(columns)
        label_column = find_label_column(columns)
        generator_column = find_generator_column(columns)

        data = table.to_pylist()
        print(
            f"Extracting {parquet_path.name}: rows={len(data)}, "
            f"image={image_column}, label={label_column}, generator={generator_column}"
        )
        for row in data:
            if max_images and written >= max_images:
                return real_count, ai_count

            image_value = row.get(image_column)
            label_value = row.get(label_column) if label_column else None
            generator_value = row.get(generator_column) if generator_column else None
            is_ai = infer_is_ai(label_value, generator_value, row)
            if max_per_class:
                if is_ai and ai_count >= max_per_class:
                    continue
                if not is_ai and real_count >= max_per_class:
                    continue
            target_dir = AI_TARGET if is_ai else REAL_TARGET
            index = ai_count if is_ai else real_count
            suffix = infer_suffix(image_value)
            target_path = target_dir / f"{'ai' if is_ai else 'real'}_{index:06d}{suffix}"
            if target_path.exists():
                if is_ai:
                    ai_count += 1
                else:
                    real_count += 1
                continue
            save_image_value(image_value, target_path)
            if is_ai:
                ai_count += 1
            else:
                real_count += 1
            written += 1

    return real_count, ai_count


def find_image_column(columns: list[str]) -> str:
    for candidate in ("image", "img", "jpg", "png"):
        if candidate in columns:
            return candidate
    for column in columns:
        if "image" in column.lower():
            return column
    raise SystemExit(f"Could not find image column. Columns: {columns}")


def find_label_column(columns: list[str]) -> str | None:
    for candidate in ("label", "labels", "class", "category", "is_ai", "fake"):
        if candidate in columns:
            return candidate
    return None


def find_generator_column(columns: list[str]) -> str | None:
    for candidate in ("generator", "model", "source", "origin"):
        if candidate in columns:
            return candidate
    return None


def infer_is_ai(label_value: object, generator_value: object, row: dict[str, object]) -> bool:
    text = " ".join(str(value).lower() for value in (label_value, generator_value) if value is not None)
    if any(token in text for token in ("fake", "ai", "synthetic", "midjourney", "dalle", "stable", "sd", "nano")):
        return True
    if any(token in text for token in ("real", "human", "natural")):
        return False
    if isinstance(label_value, bool):
        return label_value
    if isinstance(label_value, int):
        return label_value == 1
    for key, value in row.items():
        key_text = str(key).lower()
        value_text = str(value).lower()
        if "fake" in key_text and value in (1, True):
            return True
        if "label" in key_text and any(token in value_text for token in ("fake", "ai", "synthetic")):
            return True
    return False


def infer_suffix(image_value: object) -> str:
    if isinstance(image_value, dict):
        path = image_value.get("path")
        if path:
            suffix = Path(str(path)).suffix.lower()
            if suffix in IMAGE_EXTENSIONS:
                return suffix
    return ".jpg"


def save_image_value(image_value: object, target_path: Path) -> None:
    if isinstance(image_value, dict):
        if "bytes" in image_value and image_value["bytes"]:
            target_path.write_bytes(image_value["bytes"])
            return
        if "path" in image_value and image_value["path"]:
            source = Path(str(image_value["path"]))
            if source.exists():
                target_path.write_bytes(source.read_bytes())
                return
    if isinstance(image_value, bytes):
        target_path.write_bytes(image_value)
        return
    if isinstance(image_value, Image.Image):
        image_value.convert("RGB").save(target_path, quality=95)
        return
    raise ValueError(f"Unsupported image value type: {type(image_value)!r}")


def count_existing(path: Path) -> int:
    return sum(1 for item in path.glob("*") if item.suffix.lower() in IMAGE_EXTENSIONS)


if __name__ == "__main__":
    main()





