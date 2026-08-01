from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.services.external_paths import external_model_path

ROOT = Path(__file__).resolve().parents[4]
JABBERJAY_REPO = external_model_path("audio", "jabberjay")
JABBERJAY_SRC = JABBERJAY_REPO / "src"


@dataclass(frozen=True)
class JabberjayAudioResult:
    status: str
    verdict: str
    real_score: float | None = None
    ai_score: float | None = None
    confidence: str | None = None
    details: dict[str, Any] | None = None
    error: str | None = None


def jabberjay_status() -> str:
    if not JABBERJAY_REPO.exists():
        return "not installed"
    try:
        _import_jabberjay()
    except Exception:
        return "installed needs dependencies"
    return "ready"


def run_jabberjay(audio_path: Path) -> JabberjayAudioResult:
    try:
        Jabberjay = _import_jabberjay()
    except Exception as exc:
        return JabberjayAudioResult(
            status="unavailable",
            verdict="Jabberjay dependency is not installed; audio heuristic fallback was used.",
            error=str(exc),
            details={
                "repository": "https://github.com/MattyB95/Jabberjay",
                "local_path": str(JABBERJAY_REPO),
                "install_command": "python -m pip install -e artifacts\models\external\\audio\\jabberjay",
            },
        )

    model = os.getenv("JABBERJAY_MODEL", "VIT")
    dataset = os.getenv("JABBERJAY_DATASET", "VoxCelebSpoof")
    visualisation = os.getenv("JABBERJAY_VISUALISATION", "ConstantQ")

    try:
        detector = Jabberjay()
        audio = detector.load(audio_path)
        result = detector.detect(
            audio,
            model=model,
            dataset=dataset,
            visualisation=visualisation,
        )
        segment_analysis = _segment_analysis(detector, audio, model, dataset, visualisation)
    except Exception as exc:
        return JabberjayAudioResult(
            status="error",
            verdict="Jabberjay could not analyze this audio file; audio heuristic fallback was used.",
            error=str(exc),
            details={
                "model": model,
                "dataset": dataset,
                "visualisation": visualisation,
                "repository": "https://github.com/MattyB95/Jabberjay",
            },
        )

    real_score, ai_score = _scores_from_result(result)
    verdict = "Likely real human voice" if result.is_bonafide else "Likely synthetic or spoofed voice"
    suspicious_segments = [item for item in segment_analysis if item["ai_score"] >= 0.55]
    return JabberjayAudioResult(
        status="ready",
        verdict=verdict,
        real_score=real_score,
        ai_score=ai_score,
        confidence=_confidence(max(real_score, ai_score)),
        details={
            "label": result.label,
            "is_bonafide": bool(result.is_bonafide),
            "raw_confidence": round(float(result.confidence), 4),
            "model": getattr(result.model, "value", str(result.model)),
            "dataset": dataset,
            "visualisation": visualisation,
            "scores": _serialise_scores(result.scores),
            "segment_seconds": _segment_seconds(),
            "segment_analysis": segment_analysis,
            "suspicious_segments": suspicious_segments,
            "repository": "https://github.com/MattyB95/Jabberjay",
            "local_path": str(JABBERJAY_REPO),
            "decision_rule": "Bonafide maps to real_voice_score; Spoof maps to ai_voice_score.",
        },
    )


def _import_jabberjay():
    if JABBERJAY_SRC.exists():
        src = str(JABBERJAY_SRC)
        if src not in sys.path:
            sys.path.insert(0, src)
    from Jabberjay import Jabberjay  # type: ignore

    return Jabberjay


def _segment_analysis(detector: Any, audio: Any, model: str, dataset: str, visualisation: str) -> list[dict[str, Any]]:
    y, sr = audio
    total_samples = len(y)
    if total_samples == 0 or sr <= 0:
        return []

    segment_seconds = _segment_seconds()
    max_segments = _max_segments()
    segment_samples = max(int(sr * segment_seconds), 1)
    min_samples = max(int(sr * 1.25), 1)
    segments: list[dict[str, Any]] = []

    for index, start in enumerate(range(0, total_samples, segment_samples)):
        if index >= max_segments:
            break
        end = min(start + segment_samples, total_samples)
        if end - start < min_samples:
            continue

        chunk = y[start:end]
        start_seconds = start / sr
        end_seconds = end / sr
        try:
            result = detector.detect(
                (chunk, sr),
                model=model,
                dataset=dataset,
                visualisation=visualisation,
            )
            real_score, ai_score = _scores_from_result(result)
            segments.append(
                {
                    "index": index + 1,
                    "start_seconds": round(float(start_seconds), 2),
                    "end_seconds": round(float(end_seconds), 2),
                    "label": result.label,
                    "is_bonafide": bool(result.is_bonafide),
                    "confidence": round(float(result.confidence), 4),
                    "real_score": real_score,
                    "ai_score": ai_score,
                    "risk": "high" if ai_score >= 0.70 else "medium" if ai_score >= 0.55 else "low",
                }
            )
        except Exception as exc:
            segments.append(
                {
                    "index": index + 1,
                    "start_seconds": round(float(start_seconds), 2),
                    "end_seconds": round(float(end_seconds), 2),
                    "label": "error",
                    "is_bonafide": None,
                    "confidence": None,
                    "real_score": None,
                    "ai_score": None,
                    "risk": "unknown",
                    "error": str(exc),
                }
            )
    return segments


def _segment_seconds() -> float:
    try:
        value = float(os.getenv("JABBERJAY_SEGMENT_SECONDS", "5"))
    except ValueError:
        value = 5.0
    return max(2.0, min(value, 30.0))


def _max_segments() -> int:
    try:
        value = int(os.getenv("JABBERJAY_MAX_SEGMENTS", "24"))
    except ValueError:
        value = 24
    return max(1, min(value, 120))


def _scores_from_result(result: Any) -> tuple[float, float]:
    scores = _serialise_scores(getattr(result, "scores", None))
    real_score = _find_label_score(scores, {"bonafide", "bona fide", "real", "genuine"})
    ai_score = _find_label_score(scores, {"spoof", "fake", "synthetic", "ai"})
    confidence = float(getattr(result, "confidence", 0.0) or 0.0)

    if real_score is None and ai_score is None:
        if bool(getattr(result, "is_bonafide", False)):
            real_score = confidence
            ai_score = 1.0 - confidence
        else:
            ai_score = confidence
            real_score = 1.0 - confidence
    elif real_score is None:
        real_score = 1.0 - float(ai_score)
    elif ai_score is None:
        ai_score = 1.0 - float(real_score)

    return _clamp(float(real_score)), _clamp(float(ai_score))


def _serialise_scores(raw_scores: Any) -> list[dict[str, Any]]:
    if not raw_scores:
        return []
    serialised: list[dict[str, Any]] = []
    for item in raw_scores:
        label = str(item.get("label", "unknown")) if isinstance(item, dict) else str(getattr(item, "label", "unknown"))
        score = item.get("score") if isinstance(item, dict) else getattr(item, "score", None)
        serialised.append({"label": label, "score": _clamp(float(score or 0.0))})
    return serialised


def _find_label_score(scores: list[dict[str, Any]], labels: set[str]) -> float | None:
    for item in scores:
        label = str(item.get("label", "")).lower()
        if any(token in label for token in labels):
            return _clamp(float(item.get("score", 0.0) or 0.0))
    return None


def _confidence(score: float) -> str:
    return "High" if score >= 0.75 else "Medium" if score >= 0.55 else "Low"


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 4)





