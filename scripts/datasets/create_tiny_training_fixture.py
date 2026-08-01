from __future__ import annotations

import csv
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[2]
DATASET_ROOT = ROOT / "data" / "raw" / "xabarnavis_datasets"


def main() -> None:
    random.seed(42)
    real_dir = DATASET_ROOT / "real" / "local_camera_real" / "tiny_fixture"
    ai_dir = DATASET_ROOT / "ai_generated" / "local_generated" / "tiny_fixture"
    real_dir.mkdir(parents=True, exist_ok=True)
    ai_dir.mkdir(parents=True, exist_ok=True)

    for index in range(40):
        make_real_like(real_dir / f"real_{index:03d}.jpg", index)
        make_ai_like(ai_dir / f"ai_{index:03d}.jpg", index)

    write_fixture_manifests(real_dir, ai_dir)
    print("Created tiny fixture dataset and manifests.")


def make_real_like(path: Path, seed: int) -> None:
    rng = random.Random(seed)
    image = Image.new("RGB", (192, 192), (rng.randrange(40, 180), rng.randrange(40, 180), rng.randrange(40, 180)))
    draw = ImageDraw.Draw(image)
    for _ in range(32):
        xy = [rng.randrange(0, 192), rng.randrange(0, 192), rng.randrange(0, 192), rng.randrange(0, 192)]
        color = (rng.randrange(0, 255), rng.randrange(0, 255), rng.randrange(0, 255))
        draw.line(xy, fill=color, width=rng.randrange(1, 4))
    image = image.filter(ImageFilter.GaussianBlur(radius=0.4))
    image.save(path, quality=88)


def make_ai_like(path: Path, seed: int) -> None:
    rng = random.Random(10_000 + seed)
    image = Image.new("RGB", (192, 192))
    pixels = image.load()
    for y in range(192):
        for x in range(192):
            value = int((x / 191) * 180 + (y / 191) * 60)
            pixels[x, y] = (
                min(255, value + rng.randrange(0, 18)),
                min(255, 80 + value // 2 + rng.randrange(0, 12)),
                min(255, 160 + rng.randrange(0, 35)),
            )
    image = image.filter(ImageFilter.SMOOTH_MORE)
    image.save(path, quality=95)


def write_fixture_manifests(real_dir: Path, ai_dir: Path) -> None:
    metadata_dir = DATASET_ROOT / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for path in sorted(real_dir.glob("*.jpg")):
        rows.append((path, "real", "tiny_fixture_real", "none"))
    for path in sorted(ai_dir.glob("*.jpg")):
        rows.append((path, "ai_generated", "tiny_fixture_ai", "tiny_fixture"))
    random.shuffle(rows)

    splits = {
        "train": rows[:56],
        "val": rows[56:68],
        "test": rows[68:],
    }
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
    for split, split_rows in splits.items():
        with (metadata_dir / f"{split}.csv").open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(header)
            for path, label, source, generator in split_rows:
                writer.writerow(
                    [
                        path.relative_to(DATASET_ROOT).as_posix(),
                        label,
                        source,
                        generator,
                        "none",
                        "0",
                        "",
                        "missing",
                        split,
                    ]
                )


if __name__ == "__main__":
    main()





