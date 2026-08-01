from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.services.external_paths import external_model_path

ROOT = Path(__file__).resolve().parents[4]
AUDIO_02_REPO = external_model_path("audio", "deepfake_voice_detection_public")
AUDIO_02_LOCAL_MODEL = AUDIO_02_REPO / "model"
DEFAULT_MODEL_ID = "garystafford/wav2vec2-deepfake-voice-detector"
SAMPLE_RATE = 16000


@dataclass(frozen=True)
class Audio02Result:
    status: str
    verdict: str
    real_score: float | None = None
    ai_score: float | None = None
    confidence: str | None = None
    details: dict[str, Any] | None = None
    error: str | None = None


def audio_02_status() -> str:
    if not AUDIO_02_REPO.exists():
        return "not installed"
    try:
        import librosa  # noqa: F401
        import torch  # noqa: F401
        from transformers import AutoFeatureExtractor, AutoModelForAudioClassification  # noqa: F401
    except Exception:
        return "installed needs dependencies"
    if (AUDIO_02_LOCAL_MODEL / "config.json").is_file():
        return "ready local"
    return "ready downloads on first use"


def run_audio_02(audio_path: Path) -> Audio02Result:
    try:
        import librosa
    except Exception as exc:
        return Audio02Result(
            status="unavailable",
            verdict="Xabarnavis Audio 0.2 dependencies are not installed.",
            error=str(exc),
            details=_base_details(),
        )

    try:
        detector = _get_detector()
        audio, sr = librosa.load(str(audio_path), sr=SAMPLE_RATE, mono=True)
        prediction = detector.detect(audio, sr)
        segment_analysis = _segment_analysis(detector, audio, sr)
    except Exception as exc:
        return Audio02Result(
            status="error",
            verdict="Xabarnavis Audio 0.2 could not analyze this audio file.",
            error=str(exc),
            details=_base_details(),
        )

    real_score, ai_score = _scores_from_prediction(prediction)
    is_fake = ai_score >= real_score
    suspicious_segments = [item for item in segment_analysis if item["ai_score"] >= 0.55]
    return Audio02Result(
        status="ready",
        verdict="Likely AI-generated or deepfake voice" if is_fake else "Likely real human voice",
        real_score=real_score,
        ai_score=ai_score,
        confidence=_confidence(max(real_score, ai_score)),
        details={
            **_base_details(),
            "prediction": prediction.get("prediction"),
            "raw_confidence": _clamp(float(prediction.get("confidence") or 0.0)),
            "probabilities": prediction.get("probabilities") or {},
            "segment_seconds": _segment_seconds(),
            "segment_analysis": segment_analysis,
            "suspicious_segments": suspicious_segments,
            "decision_rule": "fake/deepfake labels map to ai_voice_score; real/bonafide labels map to real_voice_score.",
        },
    )


@lru_cache(maxsize=1)
def _get_detector() -> "_Audio02Detector":
    return _Audio02Detector(_model_source())


def _model_source() -> str:
    override = os.getenv("XABARNAVIS_AUDIO_02_MODEL")
    if override:
        return override
    if (AUDIO_02_LOCAL_MODEL / "config.json").is_file():
        return str(AUDIO_02_LOCAL_MODEL)
    return DEFAULT_MODEL_ID


class _Audio02Detector:
    def __init__(self, model_source: str) -> None:
        import torch
        from transformers import AutoFeatureExtractor, AutoModelForAudioClassification

        self.torch = torch
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        local_only = Path(model_source).exists()
        self.feature_extractor = AutoFeatureExtractor.from_pretrained(model_source, local_files_only=local_only)
        self.model = AutoModelForAudioClassification.from_pretrained(model_source, local_files_only=local_only).to(self.device)
        self.model.eval()
        self.id2label: dict[int, str] = {}
        raw = getattr(getattr(self.model, "config", None), "id2label", None)
        if isinstance(raw, dict):
            for key, value in raw.items():
                try:
                    self.id2label[int(key)] = str(value)
                except Exception:
                    continue

    def detect(self, audio: Any, sample_rate: int) -> dict[str, Any]:
        import numpy as np

        if sample_rate != SAMPLE_RATE:
            raise ValueError(f"Expected {SAMPLE_RATE} Hz audio, got {sample_rate}.")
        if len(audio) == 0:
            raise ValueError("Audio array is empty.")
        audio_array = np.asarray(audio, dtype=np.float32)
        max_samples = SAMPLE_RATE * 30
        if len(audio_array) > max_samples:
            audio_array = audio_array[:max_samples]
        inputs = self.feature_extractor(audio_array, sampling_rate=SAMPLE_RATE, return_tensors="pt", padding=True)
        inputs = {key: value.to(self.device) for key, value in inputs.items()}
        with self.torch.no_grad():
            outputs = self.model(**inputs)
            probs = self.torch.nn.functional.softmax(outputs.logits, dim=-1)
        predicted_class = int(self.torch.argmax(probs, dim=1).item())
        confidence = float(probs[0][predicted_class].item())
        row = probs[0].detach().cpu().tolist()
        probabilities = {
            self.id2label.get(index, str(index)): float(score)
            for index, score in enumerate(row)
        }
        return {
            "prediction": self.id2label.get(predicted_class, str(predicted_class)),
            "confidence": confidence,
            "probabilities": probabilities,
        }


def _segment_analysis(detector: _Audio02Detector, audio: Any, sr: int) -> list[dict[str, Any]]:
    segment_seconds = _segment_seconds()
    max_segments = _max_segments()
    segment_samples = max(int(sr * segment_seconds), 1)
    min_samples = max(int(sr * 1.25), 1)
    total_samples = len(audio)
    segments: list[dict[str, Any]] = []

    for index, start in enumerate(range(0, total_samples, segment_samples)):
        if index >= max_segments:
            break
        end = min(start + segment_samples, total_samples)
        if end - start < min_samples:
            continue
        try:
            prediction = detector.detect(audio[start:end], sr)
            real_score, ai_score = _scores_from_prediction(prediction)
            segments.append(
                {
                    "index": index + 1,
                    "start_seconds": round(float(start / sr), 2),
                    "end_seconds": round(float(end / sr), 2),
                    "label": prediction.get("prediction"),
                    "confidence": _clamp(float(prediction.get("confidence") or 0.0)),
                    "real_score": real_score,
                    "ai_score": ai_score,
                    "risk": "high" if ai_score >= 0.70 else "medium" if ai_score >= 0.55 else "low",
                }
            )
        except Exception as exc:
            segments.append(
                {
                    "index": index + 1,
                    "start_seconds": round(float(start / sr), 2),
                    "end_seconds": round(float(end / sr), 2),
                    "label": "error",
                    "confidence": None,
                    "real_score": None,
                    "ai_score": None,
                    "risk": "unknown",
                    "error": str(exc),
                }
            )
    return segments


def _scores_from_prediction(prediction: dict[str, Any]) -> tuple[float, float]:
    probabilities = prediction.get("probabilities") or {}
    real_score = _find_probability(probabilities, {"real", "bonafide", "bona fide", "genuine", "human"})
    ai_score = _find_probability(probabilities, {"fake", "deepfake", "spoof", "ai", "synthetic"})
    confidence = float(prediction.get("confidence") or 0.0)
    label = str(prediction.get("prediction") or "").lower()
    if real_score is None and ai_score is None:
        if any(token in label for token in ("fake", "deepfake", "spoof", "ai", "synthetic")):
            ai_score = confidence
            real_score = 1.0 - confidence
        else:
            real_score = confidence
            ai_score = 1.0 - confidence
    elif real_score is None:
        real_score = 1.0 - float(ai_score)
    elif ai_score is None:
        ai_score = 1.0 - float(real_score)
    return _clamp(float(real_score)), _clamp(float(ai_score))


def _find_probability(probabilities: dict[str, Any], labels: set[str]) -> float | None:
    for label, score in probabilities.items():
        lower = str(label).lower()
        if any(token in lower for token in labels):
            return _clamp(float(score))
    return None


def _base_details() -> dict[str, Any]:
    return {
        "repository": "https://github.com/garystafford/deepfake-voice-detection-public",
        "huggingface_model": DEFAULT_MODEL_ID,
        "local_path": str(AUDIO_02_REPO),
        "local_model_path": str(AUDIO_02_LOCAL_MODEL),
        "install_command": "python -m pip install -r artifacts\models\external\\audio\\deepfake_voice_detection_public\\code\\requirements.txt",
        "download_command": "python scripts\\datasets\\predownload_audio_02_model.py",
    }


def _segment_seconds() -> float:
    try:
        value = float(os.getenv("XABARNAVIS_AUDIO_02_SEGMENT_SECONDS", os.getenv("JABBERJAY_SEGMENT_SECONDS", "5")))
    except ValueError:
        value = 5.0
    return max(2.0, min(value, 30.0))


def _max_segments() -> int:
    try:
        value = int(os.getenv("XABARNAVIS_AUDIO_02_MAX_SEGMENTS", os.getenv("JABBERJAY_MAX_SEGMENTS", "24")))
    except ValueError:
        value = 24
    return max(1, min(value, 120))


def _confidence(score: float) -> str:
    return "High" if score >= 0.75 else "Medium" if score >= 0.55 else "Low"


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 4)





