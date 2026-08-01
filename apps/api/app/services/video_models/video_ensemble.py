from __future__ import annotations

from dataclasses import dataclass
from typing import Any


DEFAULT_WEIGHTS = {
    "genconvit": 0.50,
    "naman712": 0.25,
    "spectra_audio": 0.20,
    "metadata": 0.05,
}


@dataclass(frozen=True)
class VideoEnsembleResult:
    fake_score: float
    real_score: float
    confidence: str
    verdict: str
    weights_used: dict[str, float]
    available_scores: dict[str, float]


def combine_video_scores(
    *,
    genconvit_score: float | None,
    naman712_score: float | None,
    spectra_audio_score: float | None,
    metadata_risk_score: float | None,
) -> VideoEnsembleResult:
    candidates = {
        "genconvit": genconvit_score,
        "naman712": naman712_score,
        "spectra_audio": spectra_audio_score,
        "metadata": metadata_risk_score,
    }
    available_scores = {
        key: _clamp(float(value))
        for key, value in candidates.items()
        if value is not None
    }
    if not available_scores:
        available_scores["metadata"] = 0.35
    raw_weight_total = sum(DEFAULT_WEIGHTS[key] for key in available_scores)
    weights_used = {
        key: round(DEFAULT_WEIGHTS[key] / raw_weight_total, 4)
        for key in available_scores
    }
    fake_score = _clamp(sum(available_scores[key] * weights_used[key] for key in available_scores))
    real_score = _clamp(1.0 - fake_score)
    confidence_value = max(fake_score, real_score)
    return VideoEnsembleResult(
        fake_score=fake_score,
        real_score=real_score,
        confidence="High" if confidence_value >= 0.75 else "Medium" if confidence_value >= 0.55 else "Low",
        verdict=_video_verdict(fake_score),
        weights_used=weights_used,
        available_scores=available_scores,
    )


def model_status_json(name: str, status: str, error: str | None = None, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "name": name,
        "status": status,
        "available": status in {"ready", "ready local", "ready downloads on first use"},
        "error": error,
        "details": details or {},
    }


def _video_verdict(fake_score: float) -> str:
    if fake_score <= 0.35:
        return "Likely Real"
    if fake_score <= 0.60:
        return "Suspicious"
    if fake_score <= 0.80:
        return "Likely AI / Deepfake"
    return "Strong Deepfake Signal"


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 4)






