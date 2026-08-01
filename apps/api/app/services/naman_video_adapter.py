from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.services.external_paths import external_model_path, hf_model_path


MODEL_ID = "Naman712/Deep-fake-detection"
GITHUB_REPO = external_model_path("video", "deepfake_detector_naman")
HF_MODEL_DIR = hf_model_path("naman712_video")
LEGACY_MODEL_DIR = GITHUB_REPO / "model"
MODEL_DIR = HF_MODEL_DIR if (HF_MODEL_DIR / "config.json").is_file() else LEGACY_MODEL_DIR


@dataclass(frozen=True)
class NamanVideoResult:
    status: str
    verdict: str
    real_score: float | None = None
    fake_score: float | None = None
    confidence: str | None = None
    details: dict[str, Any] | None = None
    error: str | None = None


def naman_video_status() -> str:
    if not GITHUB_REPO.exists() and not HF_MODEL_DIR.exists():
        return "not installed"
    model_dir = _model_dir()
    if (model_dir / "config.json").is_file() or (model_dir / "model_87_acc_20_frames_final_data.pt").is_file():
        missing = _missing_dependencies()
        if missing:
            return "installed needs dependencies"
        return "ready local"
    if not _hf_token():
        return "requires huggingface access"
    missing = _missing_dependencies()
    if missing:
        return "installed needs dependencies"
    return "ready downloads on first use"


def run_naman_video(video_path: Path) -> NamanVideoResult:
    status = naman_video_status()
    if status not in {"ready local", "ready downloads on first use"}:
        return NamanVideoResult(
            status=status,
            verdict="Naman712 ResNext50 + LSTM video detector is registered but cannot run yet.",
            details=_base_details(),
            error=_status_error(status),
        )

    try:
        detector = _get_detector()
        raw = detector(video_path)
        parsed = _parse_pipeline_result(raw)
    except Exception as exc:
        return NamanVideoResult(
            status="error",
            verdict="Naman712 video detector could not analyze this video file.",
            details=_base_details(),
            error=str(exc),
        )

    fake_score = parsed["fake_score"]
    real_score = _clamp(1.0 - fake_score)
    return NamanVideoResult(
        status="ready",
        verdict="Likely deepfake or manipulated video" if fake_score >= real_score else "Likely real video",
        real_score=real_score,
        fake_score=fake_score,
        confidence=_confidence(max(real_score, fake_score)),
        details={
            **_base_details(),
            "raw_prediction": parsed,
            "decision_rule": "Labels containing fake/deepfake map to video_fake_score; real/authentic labels map to video_real_score.",
        },
    )


@lru_cache(maxsize=1)
def _get_detector():
    from transformers import pipeline

    model_dir = _model_dir()
    model_source = str(model_dir) if (model_dir / "config.json").is_file() else MODEL_ID
    token = _hf_token()
    kwargs: dict[str, Any] = {}
    if token:
        kwargs["token"] = token
    return pipeline("video-classification", model=model_source, **kwargs)


def _parse_pipeline_result(raw: Any) -> dict[str, Any]:
    items = raw if isinstance(raw, list) else [raw]
    best_label = "unknown"
    best_score = 0.5
    fake_score = None
    real_score = None
    for item in items:
        if not isinstance(item, dict):
            continue
        label = str(item.get("label", "")).lower()
        score = _clamp(float(item.get("score", 0.0) or 0.0))
        if score >= best_score:
            best_label = label
            best_score = score
        if any(token in label for token in ("fake", "deepfake", "manipulated")):
            fake_score = score if fake_score is None else max(fake_score, score)
        if any(token in label for token in ("real", "authentic", "genuine")):
            real_score = score if real_score is None else max(real_score, score)
    if fake_score is None and real_score is None:
        if any(token in best_label for token in ("fake", "deepfake", "manipulated")):
            fake_score = best_score
        else:
            real_score = best_score
    if fake_score is None:
        fake_score = 1.0 - float(real_score)
    return {
        "label": best_label,
        "score": best_score,
        "fake_score": _clamp(float(fake_score)),
        "all_scores": items,
    }


def _missing_dependencies() -> list[str]:
    missing: list[str] = []
    for module_name in ["torch", "torchvision", "transformers"]:
        try:
            __import__(module_name)
        except Exception:
            missing.append(module_name)
    return missing


def _hf_token() -> str | None:
    return os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN")


def _status_error(status: str) -> str | None:
    if status == "requires huggingface access":
        return "This Hugging Face model is gated. Accept the model conditions on Hugging Face and set HF_TOKEN before downloading or inference."
    if status == "installed needs dependencies":
        return f"Install missing Python dependencies: {', '.join(_missing_dependencies())}"
    if status == "not installed":
        return "Clone namandhakad712/Deepfake-detector into artifacts\models\external\\video\\deepfake_detector_naman."
    return None


def _base_details() -> dict[str, Any]:
    model_dir = _model_dir()
    return {
        "repository": "https://github.com/namandhakad712/Deepfake-detector",
        "huggingface_model": "https://huggingface.co/Naman712/Deep-fake-detection",
        "local_path": str(GITHUB_REPO),
        "local_model_path": str(model_dir),
        "preferred_hf_path": str(HF_MODEL_DIR),
        "architecture": "ResNext50 spatial feature extractor with LSTM temporal sequence analyzer",
        "task": "Binary video deepfake detection: real vs fake",
        "model_access": "Gated Hugging Face model; accept conditions and set HF_TOKEN.",
        "download_command": "py scripts\\download_naman_video_model.py",
        "install_command": "python -m pip install transformers torch torchvision",
        "recommended_sequence_length": "20 frames",
    }


def _model_dir() -> Path:
    if (HF_MODEL_DIR / "config.json").is_file() or (HF_MODEL_DIR / "model_87_acc_20_frames_final_data.pt").is_file():
        return HF_MODEL_DIR
    return LEGACY_MODEL_DIR


def _confidence(score: float) -> str:
    return "High" if score >= 0.75 else "Medium" if score >= 0.55 else "Low"


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 4)





