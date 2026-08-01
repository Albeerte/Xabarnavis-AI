from __future__ import annotations

from pathlib import Path
from typing import Any

DATASET_ID = "jayjoshi37/deepfake-audio-dataset-fake-vs-real-speech"
ROOT = Path(__file__).resolve().parents[4]
AUDIO_04_DIR = ROOT / "data" / "datasets" / "audio" / "xabarnavis_audio_0_4_deepfake_audio_dataset"


def audio_04_status() -> str:
    if _has_audio_files(AUDIO_04_DIR):
        return "ready dataset"
    if AUDIO_04_DIR.exists():
        return "dataset folder ready"
    return "not_installed"


def audio_04_details() -> dict[str, Any]:
    return {
        "dataset_id": DATASET_ID,
        "local_path": str(AUDIO_04_DIR),
        "purpose": "Training/evaluation dataset for fake vs real speech detection. This is a dataset resource, not an inference model.",
        "download_command": "python scripts\\datasets\\download_audio_04_dataset.py",
        "kagglehub_code": (
            "import kagglehub\n"
            f"path = kagglehub.dataset_download('{DATASET_ID}')\n"
            "print('Path to dataset files:', path)"
        ),
    }


def _has_audio_files(path: Path) -> bool:
    if not path.exists():
        return False
    audio_exts = {".wav", ".mp3", ".flac", ".m4a", ".ogg"}
    try:
        return any(item.is_file() and item.suffix.lower() in audio_exts for item in path.rglob("*"))
    except OSError:
        return False





