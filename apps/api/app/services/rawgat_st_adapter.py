from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.services.external_paths import external_model_path


RAWGAT_REPO = external_model_path("audio", "rawgat_st_antispoofing")
DEFAULT_WEIGHTS = RAWGAT_REPO / "Pre_trained_models" / "RawGAT_ST_mul" / "Best_epoch.pth"
CONFIG_PATH = RAWGAT_REPO / "model_config_RawGAT_ST.yaml"
SAMPLE_RATE = 16000
MAX_LEN = 64600


@dataclass(frozen=True)
class RawGATResult:
    status: str
    verdict: str
    real_score: float | None = None
    ai_score: float | None = None
    confidence: str | None = None
    details: dict[str, Any] | None = None
    error: str | None = None


def rawgat_status() -> str:
    if not RAWGAT_REPO.exists():
        return "not installed"
    if not DEFAULT_WEIGHTS.is_file():
        return "installed no weights"
    try:
        import librosa  # noqa: F401
        import torch  # noqa: F401
        import yaml  # noqa: F401
    except Exception:
        return "installed needs dependencies"
    return "ready local"


def run_rawgat_st(audio_path: Path) -> RawGATResult:
    try:
        import librosa
    except Exception as exc:
        return RawGATResult(
            status="unavailable",
            verdict="RawGAT-ST dependencies are not installed.",
            error=str(exc),
            details=_base_details(),
        )

    try:
        detector = _get_detector()
        audio, sr = librosa.load(str(audio_path), sr=SAMPLE_RATE, mono=True)
        prediction = detector.detect(audio, sr)
        segment_analysis = _segment_analysis(detector, audio, sr)
    except Exception as exc:
        return RawGATResult(
            status="error",
            verdict="RawGAT-ST could not analyze this audio file.",
            error=str(exc),
            details=_base_details(),
        )

    real_score = _clamp(float(prediction["bonafide_score"]))
    ai_score = _clamp(float(prediction["spoof_score"]))
    suspicious_segments = [item for item in segment_analysis if item["ai_score"] >= 0.55]
    return RawGATResult(
        status="ready",
        verdict="Likely spoofed or synthetic voice" if ai_score >= real_score else "Likely bonafide human voice",
        real_score=real_score,
        ai_score=ai_score,
        confidence=_confidence(max(real_score, ai_score)),
        details={
            **_base_details(),
            "prediction": prediction["label"],
            "probabilities": {
                "spoof": ai_score,
                "bonafide": real_score,
            },
            "segment_seconds": _segment_seconds(),
            "segment_analysis": segment_analysis,
            "suspicious_segments": suspicious_segments,
            "decision_rule": "RawGAT-ST output index 0 maps to spoof/AI; output index 1 maps to bonafide/real.",
        },
    )


@lru_cache(maxsize=1)
def _get_detector() -> "_RawGATDetector":
    return _RawGATDetector()


class _RawGATDetector:
    def __init__(self) -> None:
        import torch
        import yaml

        repo = str(RAWGAT_REPO)
        if repo not in sys.path:
            sys.path.insert(0, repo)
        from model import RawGAT_ST  # type: ignore

        with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)

        self.torch = torch
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = RawGAT_ST(config["model"], self.device).to(self.device)
        weights = Path(os.getenv("XABARNAVIS_RAWGAT_ST_WEIGHTS", str(DEFAULT_WEIGHTS)))
        self.model.load_state_dict(torch.load(weights, map_location=self.device))
        self.model.eval()

    def detect(self, audio: Any, sample_rate: int) -> dict[str, Any]:
        import numpy as np

        if sample_rate != SAMPLE_RATE:
            raise ValueError(f"Expected {SAMPLE_RATE} Hz audio, got {sample_rate}.")
        if len(audio) == 0:
            raise ValueError("Audio array is empty.")
        padded = _pad(np.asarray(audio, dtype=np.float32))
        tensor = self.torch.tensor(padded, dtype=self.torch.float32, device=self.device).unsqueeze(0)
        with self.torch.no_grad():
            logits = self.model(tensor, Freq_aug=False)
            probs = self.torch.nn.functional.softmax(logits, dim=-1)[0].detach().cpu().tolist()
        spoof_score = _clamp(float(probs[0]))
        bonafide_score = _clamp(float(probs[1]))
        return {
            "label": "bonafide" if bonafide_score >= spoof_score else "spoof",
            "spoof_score": spoof_score,
            "bonafide_score": bonafide_score,
        }


def _segment_analysis(detector: _RawGATDetector, audio: Any, sr: int) -> list[dict[str, Any]]:
    segment_seconds = _segment_seconds()
    max_segments = _max_segments()
    segment_samples = max(int(sr * segment_seconds), 1)
    min_samples = max(int(sr * 1.25), 1)
    segments: list[dict[str, Any]] = []
    for index, start in enumerate(range(0, len(audio), segment_samples)):
        if index >= max_segments:
            break
        end = min(start + segment_samples, len(audio))
        if end - start < min_samples:
            continue
        try:
            prediction = detector.detect(audio[start:end], sr)
            real_score = _clamp(float(prediction["bonafide_score"]))
            ai_score = _clamp(float(prediction["spoof_score"]))
            segments.append(
                {
                    "index": index + 1,
                    "start_seconds": round(float(start / sr), 2),
                    "end_seconds": round(float(end / sr), 2),
                    "label": prediction["label"],
                    "confidence": max(real_score, ai_score),
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


def _pad(audio: Any) -> Any:
    import numpy as np

    audio_len = audio.shape[0]
    if audio_len >= MAX_LEN:
        return audio[:MAX_LEN]
    repeats = int(MAX_LEN / max(audio_len, 1)) + 1
    return np.tile(audio, repeats)[:MAX_LEN]


def _base_details() -> dict[str, Any]:
    return {
        "repository": "https://github.com/eurecom-asp/RawGAT-ST-antispoofing",
        "paper": "https://arxiv.org/abs/2107.12710",
        "local_path": str(RAWGAT_REPO),
        "weights_path": str(DEFAULT_WEIGHTS),
        "architecture": "End-to-End Spectro-Temporal Graph Attention Network",
        "training_dataset": "ASVspoof 2019 Logical Access partition",
        "install_command": "python -m pip install -r artifacts\models\external\\audio\\rawgat_st_antispoofing\\requirements.txt",
        "eval_command": "python artifacts\models\external\\audio\\rawgat_st_antispoofing\\main.py --track=logical --loss=WCE --is_eval --eval --model_path=Pre_trained_models\\RawGAT_ST_mul\\Best_epoch.pth --eval_output=RawGAT_ST_mul_LA_eval_CM_scores.txt",
    }


def _segment_seconds() -> float:
    try:
        value = float(os.getenv("XABARNAVIS_RAWGAT_ST_SEGMENT_SECONDS", os.getenv("JABBERJAY_SEGMENT_SECONDS", "5")))
    except ValueError:
        value = 5.0
    return max(2.0, min(value, 30.0))


def _max_segments() -> int:
    try:
        value = int(os.getenv("XABARNAVIS_RAWGAT_ST_MAX_SEGMENTS", os.getenv("JABBERJAY_MAX_SEGMENTS", "24")))
    except ValueError:
        value = 24
    return max(1, min(value, 120))


def _confidence(score: float) -> str:
    return "High" if score >= 0.75 else "Medium" if score >= 0.55 else "Low"


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 4)





