from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
EXTERNAL_MODELS = ROOT / "artifacts" / "models" / "external"
HF_MODELS = ROOT / "artifacts" / "models" / "hf"
AUDIO_MODELS = EXTERNAL_MODELS / "audio"
PHOTO_MODELS = EXTERNAL_MODELS / "photo"
VIDEO_MODELS = EXTERNAL_MODELS / "video"
TEXT_MODELS = EXTERNAL_MODELS / "text"


def external_model_path(media_type: str, folder_name: str) -> Path:
    media_roots = {
        "audio": AUDIO_MODELS,
        "photo": PHOTO_MODELS,
        "image": PHOTO_MODELS,
        "video": VIDEO_MODELS,
        "text": TEXT_MODELS,
    }
    preferred_root = media_roots.get(media_type, EXTERNAL_MODELS)
    preferred = preferred_root / folder_name
    if preferred.exists():
        return preferred
    legacy = EXTERNAL_MODELS / folder_name
    if legacy.exists():
        return legacy
    return preferred


def hf_model_path(folder_name: str) -> Path:
    return HF_MODELS / folder_name





