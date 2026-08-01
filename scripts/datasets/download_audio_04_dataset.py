from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATASET_ID = "jayjoshi37/deepfake-audio-dataset-fake-vs-real-speech"
TARGET_DIR = ROOT / "data" / "datasets" / "audio" / "xabarnavis_audio_0_4_deepfake_audio_dataset"


def main() -> None:
    try:
        import kagglehub
    except Exception as exc:
        raise SystemExit(
            "kagglehub is required. Install it with:\n"
            "  python -m pip install kagglehub\n\n"
            f"Import error: {exc}"
        ) from exc

    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading Kaggle dataset: {DATASET_ID}")
    source_path = Path(kagglehub.dataset_download(DATASET_ID))
    print(f"Kaggle cache path: {source_path}")
    print(f"Copying dataset to: {TARGET_DIR}")

    copied = 0
    for source in source_path.rglob("*"):
        if not source.is_file():
            continue
        relative = source.relative_to(source_path)
        target = TARGET_DIR / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.stat().st_size == source.stat().st_size:
            continue
        shutil.copy2(source, target)
        copied += 1

    print(f"Done. Copied/updated {copied} file(s).")
    print(f"Xabarnavis Audio 0.4 dataset path: {TARGET_DIR}")


if __name__ == "__main__":
    main()





