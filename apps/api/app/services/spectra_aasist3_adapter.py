from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.services.external_paths import external_model_path, hf_model_path


MODEL_ID = "lab260/Spectra-AASIST3"
SPECTRA_DIR = external_model_path("audio", "spectra_aasist3")
HF_SPECTRA_MODEL_DIR = hf_model_path("spectra_aasist3_audio")
LEGACY_SPECTRA_MODEL_DIR = SPECTRA_DIR / "model"
SPECTRA_MODEL_DIR = HF_SPECTRA_MODEL_DIR if (HF_SPECTRA_MODEL_DIR / "model.py").is_file() else LEGACY_SPECTRA_MODEL_DIR
SAMPLE_RATE = 16000
MAX_LEN = 64600
DEFAULT_THRESHOLD = -1.0625009


@dataclass(frozen=True)
class SpectraAASIST3Result:
    status: str
    verdict: str
    real_score: float | None = None
    ai_score: float | None = None
    confidence: str | None = None
    details: dict[str, Any] | None = None
    error: str | None = None


def spectra_aasist3_status() -> str:
    if not SPECTRA_DIR.exists() and not HF_SPECTRA_MODEL_DIR.exists():
        return "not installed"
    model_dir = _model_dir()
    if not (model_dir / "model.py").is_file():
        return "installed no adapter code"
    if not (model_dir / "model.safetensors").is_file():
        return "installed no weights"
    try:
        import librosa  # noqa: F401
        import safetensors  # noqa: F401
        import torch  # noqa: F401
        import transformers  # noqa: F401
    except Exception:
        return "installed needs dependencies"
    return "ready local"


def run_spectra_aasist3(audio_path: Path) -> SpectraAASIST3Result:
    try:
        import librosa
    except Exception as exc:
        return SpectraAASIST3Result(
            status="unavailable",
            verdict="Spectra-AASIST3 dependencies are not installed.",
            error=str(exc),
            details=_base_details(),
        )

    try:
        detector = _get_detector()
        audio, sr = librosa.load(str(audio_path), sr=SAMPLE_RATE, mono=True)
        prediction = detector.detect(audio, sr)
        segment_analysis = _segment_analysis(detector, audio, sr)
    except Exception as exc:
        return SpectraAASIST3Result(
            status="error",
            verdict="Spectra-AASIST3 could not analyze this audio file.",
            error=str(exc),
            details=_base_details(),
        )

    real_score = _clamp(float(prediction["bonafide_probability"]))
    ai_score = _clamp(1.0 - real_score)
    suspicious_segments = [item for item in segment_analysis if item["ai_score"] >= 0.55]
    return SpectraAASIST3Result(
        status="ready",
        verdict="Likely bona fide human voice" if real_score >= ai_score else "Likely spoofed or synthetic voice",
        real_score=real_score,
        ai_score=ai_score,
        confidence=_confidence(max(real_score, ai_score)),
        details={
            **_base_details(),
            "prediction": "bonafide" if real_score >= ai_score else "spoof",
            "raw_bonafide_logit": prediction["bonafide_logit"],
            "threshold": prediction["threshold"],
            "probabilities": {
                "bonafide": real_score,
                "spoof": ai_score,
            },
            "segment_seconds": _segment_seconds(),
            "segment_analysis": segment_analysis,
            "suspicious_segments": suspicious_segments,
            "decision_rule": "Spectra-AASIST3 returns a bona-fide logit at index 1; sigmoid(logit - threshold) is used as real_voice_score.",
        },
    )


@lru_cache(maxsize=1)
def _get_detector() -> "_SpectraDetector":
    return _SpectraDetector()


class _SpectraDetector:
    def __init__(self) -> None:
        import torch

        model_dir = _model_dir()
        if not (model_dir / "model.py").is_file():
            raise FileNotFoundError(f"Missing model.py in {model_dir}")
        if not (model_dir / "model.safetensors").is_file():
            raise FileNotFoundError(f"Missing model.safetensors in {model_dir}")

        spec = importlib.util.spec_from_file_location("xabarnavis_spectra_aasist3_model", model_dir / "model.py")
        if spec is None or spec.loader is None:
            raise ImportError("Could not import Spectra-AASIST3 model.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        SpectraAASIST3 = getattr(module, "SpectraAASIST3")

        self.torch = torch
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.threshold = float(os.getenv("XABARNAVIS_SPECTRA_AASIST3_THRESHOLD", str(DEFAULT_THRESHOLD)))
        self.model = SpectraAASIST3.from_pretrained(str(model_dir)).to(self.device)
        self.model.eval()

    def detect(self, audio: Any, sample_rate: int) -> dict[str, Any]:
        import numpy as np

        if sample_rate != SAMPLE_RATE:
            raise ValueError(f"Expected {SAMPLE_RATE} Hz audio, got {sample_rate}.")
        if len(audio) == 0:
            raise ValueError("Audio array is empty.")
        prepared = _prepare(np.asarray(audio, dtype=np.float32))
        tensor = self.torch.tensor(prepared, dtype=self.torch.float32, device=self.device).unsqueeze(0)
        with self.torch.inference_mode():
            logits = self.model(tensor)
            bonafide_logit = float(logits[:, 1].detach().cpu().item())
            bonafide_probability = float(self.torch.sigmoid(self.torch.tensor(bonafide_logit - self.threshold)).item())
        return {
            "bonafide_logit": round(bonafide_logit, 6),
            "bonafide_probability": bonafide_probability,
            "threshold": self.threshold,
        }


def _segment_analysis(detector: _SpectraDetector, audio: Any, sr: int) -> list[dict[str, Any]]:
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
            real_score = _clamp(float(prediction["bonafide_probability"]))
            ai_score = _clamp(1.0 - real_score)
            segments.append(
                {
                    "index": index + 1,
                    "start_seconds": round(float(start / sr), 2),
                    "end_seconds": round(float(end / sr), 2),
                    "label": "bonafide" if real_score >= ai_score else "spoof",
                    "confidence": max(real_score, ai_score),
                    "real_score": real_score,
                    "ai_score": ai_score,
                    "raw_bonafide_logit": prediction["bonafide_logit"],
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


def _prepare(audio: Any) -> Any:
    import numpy as np

    if audio.shape[0] > 1:
        audio = np.append(audio[0], audio[1:] - 0.97 * audio[:-1])
    if audio.shape[0] >= MAX_LEN:
        return audio[:MAX_LEN]
    repeats = int(MAX_LEN / max(audio.shape[0], 1)) + 1
    return np.tile(audio, repeats)[:MAX_LEN]


def _base_details() -> dict[str, Any]:
    model_dir = _model_dir()
    return {
        "repository": "https://huggingface.co/lab260/Spectra-AASIST3",
        "local_path": str(SPECTRA_DIR),
        "local_model_path": str(model_dir),
        "preferred_hf_path": str(HF_SPECTRA_MODEL_DIR),
        "architecture": "wav2vec2 XLS-R-300m front-end with KAN-enhanced AASIST back-end",
        "input_sample_rate_hz": SAMPLE_RATE,
        "score_meaning": "Higher score means more bona fide / real human voice.",
        "download_command": "py scripts\\download_spectra_aasist3_model.py",
        "install_command": "python -m pip install huggingface_hub transformers torch torchaudio librosa soundfile safetensors",
    }


def _model_dir() -> Path:
    if (HF_SPECTRA_MODEL_DIR / "model.py").is_file() or (HF_SPECTRA_MODEL_DIR / "model.safetensors").is_file():
        return HF_SPECTRA_MODEL_DIR
    return LEGACY_SPECTRA_MODEL_DIR


def _segment_seconds() -> float:
    try:
        value = float(os.getenv("XABARNAVIS_SPECTRA_AASIST3_SEGMENT_SECONDS", os.getenv("JABBERJAY_SEGMENT_SECONDS", "5")))
    except ValueError:
        value = 5.0
    return max(2.0, min(value, 30.0))


def _max_segments() -> int:
    try:
        value = int(os.getenv("XABARNAVIS_SPECTRA_AASIST3_MAX_SEGMENTS", os.getenv("JABBERJAY_MAX_SEGMENTS", "12")))
    except ValueError:
        value = 12
    return max(1, min(value, 48))


def _confidence(score: float) -> str:
    return "High" if score >= 0.75 else "Medium" if score >= 0.55 else "Low"


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 4)





