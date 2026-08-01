from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATASET_ROOT = ROOT / "data" / "raw" / "xabarnavis_datasets"

FOLDERS = [
    "real/imagenet_real",
    "real/coco_real",
    "real/raise1k_real",
    "real/local_camera_real",
    "real/local_social_real",
    "ai_generated/genimage/midjourney",
    "ai_generated/genimage/stable_diffusion",
    "ai_generated/genimage/glide",
    "ai_generated/genimage/adm",
    "ai_generated/genimage/wukong",
    "ai_generated/genimage/biggan",
    "ai_generated/genimage/vqdm",
    "ai_generated/wildfake",
    "ai_generated/synthbuster",
    "ai_generated/aigc_benchmark",
    "ai_generated/ms_cocoai",
    "ai_generated/local_generated",
    "manipulated/casia_v2",
    "manipulated/nist_mfc",
    "manipulated/imd2020",
    "manipulated/coverage",
    "manipulated/defacto",
    "manipulated/local_photoshop",
    "test_holdout/unseen_generators",
    "test_holdout/telegram_compressed",
    "test_holdout/instagram_compressed",
    "test_holdout/screenshots",
    "test_holdout/chameleon_hard",
    "metadata",
]

CSV_HEADER = [
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


def main() -> None:
    for folder in FOLDERS:
        (DATASET_ROOT / folder).mkdir(parents=True, exist_ok=True)

    for split in ("train", "val", "test"):
        csv_path = DATASET_ROOT / "metadata" / f"{split}.csv"
        if not csv_path.exists():
            with csv_path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(CSV_HEADER)

    print(f"Dataset tree initialized at: {DATASET_ROOT}")


if __name__ == "__main__":
    main()






