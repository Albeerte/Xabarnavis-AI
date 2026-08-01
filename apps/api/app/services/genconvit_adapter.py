from __future__ import annotations

import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.services.external_paths import external_model_path


GENCONVIT_REPO = external_model_path("video", "genconvit")
WEIGHT_DIR = GENCONVIT_REPO / "weight"
ED_WEIGHT = WEIGHT_DIR / "genconvit_ed_inference.pth"
VAE_WEIGHT = WEIGHT_DIR / "genconvit_vae_inference.pth"


@dataclass(frozen=True)
class GenConViTResult:
    status: str
    verdict: str
    real_score: float | None = None
    fake_score: float | None = None
    confidence: str | None = None
    details: dict[str, Any] | None = None
    error: str | None = None


def genconvit_status() -> str:
    if not GENCONVIT_REPO.exists():
        return "not installed"
    if not ED_WEIGHT.is_file() or not VAE_WEIGHT.is_file():
        return "installed no weights"
    missing = _missing_dependencies()
    if missing:
        return "installed needs dependencies"
    return "ready local"


def run_genconvit(video_path: Path) -> GenConViTResult:
    status = genconvit_status()
    if status != "ready local":
        return GenConViTResult(
            status=status,
            verdict="GenConViT is registered for video deepfake analysis but cannot run yet.",
            details=_base_details(),
            error=_status_error(status),
        )

    work_dir = GENCONVIT_REPO / "xabarnavis_runtime" / uuid4().hex
    input_dir = work_dir / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    copied_video = input_dir / video_path.name
    shutil.copy2(video_path, copied_video)
    before = set((GENCONVIT_REPO / "result").glob("prediction_other_genconvit_*.json"))

    command = [
        sys.executable,
        "prediction.py",
        "--p",
        str(input_dir),
        "--e",
        "--v",
        "--f",
        "10",
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=GENCONVIT_REPO,
            capture_output=True,
            text=True,
            timeout=900,
            check=False,
        )
        if completed.returncode != 0:
            return GenConViTResult(
                status="error",
                verdict="GenConViT runtime returned an error.",
                details={**_base_details(), "command": " ".join(command), "stderr": completed.stderr[-4000:], "stdout": completed.stdout[-4000:]},
                error=completed.stderr[-1000:] or completed.stdout[-1000:] or f"Exit code {completed.returncode}",
            )
        output_path = _latest_result(before)
        parsed = _parse_result(output_path)
    except Exception as exc:
        return GenConViTResult(
            status="error",
            verdict="GenConViT could not analyze this video file.",
            details={**_base_details(), "command": " ".join(command)},
            error=str(exc),
        )
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)

    fake_score = parsed["fake_score"]
    real_score = 1.0 - fake_score
    return GenConViTResult(
        status="ready",
        verdict="Likely deepfake or manipulated video" if fake_score >= real_score else "Likely real video",
        real_score=_clamp(real_score),
        fake_score=_clamp(fake_score),
        confidence=_confidence(max(real_score, fake_score)),
        details={
            **_base_details(),
            "result_file": str(output_path),
            "raw_prediction": parsed,
            "decision_rule": "GenConViT pred_label FAKE maps to video_fake_score; REAL maps to video_real_score. Confidence comes from prediction score when available.",
        },
    )


def _latest_result(before: set[Path]) -> Path:
    result_dir = GENCONVIT_REPO / "result"
    after = set(result_dir.glob("prediction_other_genconvit_*.json"))
    candidates = list(after - before) or list(after)
    if not candidates:
        raise FileNotFoundError("GenConViT did not create a prediction JSON file.")
    return max(candidates, key=lambda path: path.stat().st_mtime)


def _parse_result(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    video = payload.get("video") or {}
    labels = video.get("pred_label") or []
    predictions = video.get("prediction") or []
    names = video.get("name") or []
    label = str(labels[-1] if labels else "UNKNOWN").upper()
    raw_score = float(predictions[-1] if predictions else 0.5)
    fake_score = raw_score if label == "FAKE" else 1.0 - raw_score if label == "REAL" else 0.5
    return {
        "filename": names[-1] if names else None,
        "label": label,
        "raw_score": _clamp(raw_score),
        "fake_score": _clamp(fake_score),
    }


def _missing_dependencies() -> list[str]:
    missing: list[str] = []
    for module_name in ["decord", "dlib", "face_recognition", "timm"]:
        try:
            __import__(module_name)
        except Exception:
            missing.append(module_name)
    return missing


def _status_error(status: str) -> str | None:
    if status == "installed no weights":
        return "Download GenConViT ED and VAE weights before inference."
    if status == "installed needs dependencies":
        return f"Install missing Python dependencies: {', '.join(_missing_dependencies())}"
    if status == "not installed":
        return "Clone GenConViT into artifacts\models\external\\video\\genconvit."
    return None


def _base_details() -> dict[str, Any]:
    return {
        "repository": "https://github.com/erprogs/GenConViT",
        "weights_repository": "https://huggingface.co/Deressa/GenConViT",
        "local_path": str(GENCONVIT_REPO),
        "weight_dir": str(WEIGHT_DIR),
        "ed_weight": str(ED_WEIGHT),
        "vae_weight": str(VAE_WEIGHT),
        "architecture": "Generative Convolutional Vision Transformer with ConvNeXt, Swin Transformer, Autoencoder, and VAE branches",
        "download_command": "python scripts\\datasets\\download_genconvit_weights.py",
        "install_command": "python -m pip install -r artifacts\models\external\\video\\genconvit\\requirements.txt",
        "cli_command": "python prediction.py --p <folder-with-video> --e --v --f 10",
        "missing_dependencies": _missing_dependencies(),
    }


def _confidence(score: float) -> str:
    return "High" if score >= 0.75 else "Medium" if score >= 0.55 else "Low"


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 4)





