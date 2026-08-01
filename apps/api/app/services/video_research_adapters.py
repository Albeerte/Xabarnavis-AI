from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.services.external_paths import external_model_path


@dataclass(frozen=True)
class VideoResearchModel:
    model_id: str
    name: str
    family: str
    purpose: str
    repository: str
    local_path: Path
    install_command: str
    usage_note: str


VIDEO_RESEARCH_MODELS = [
    VideoResearchModel(
        model_id="xabarnavis_video_0_3",
        name="Xabarnavis Video 0.3 DeepfakeBench",
        family="video_deepfake_benchmark_suite",
        purpose="DeepfakeBench benchmark framework for multiple video deepfake detectors and datasets.",
        repository="https://github.com/SCLBD/DeepfakeBench",
        local_path=external_model_path("video", "deepfakebench"),
        install_command="cd artifacts\models\external\\video\\deepfakebench && bash install.sh",
        usage_note="Benchmark/training framework. Configure dataset and detector checkpoints before direct inference.",
    ),
    VideoResearchModel(
        model_id="xabarnavis_video_0_4",
        name="Xabarnavis Video 0.4 M2F2-Det",
        family="video_multimodal_deepfake_detector",
        purpose="M2F2-Det multimodal deepfake detection research code with staged inference scripts.",
        repository="https://github.com/chelsea234/m2f2_det",
        local_path=external_model_path("video", "m2f2_det"),
        install_command="cd artifacts\models\external\\video\\m2f2_det && conda env create -f environment.yml",
        usage_note="Research pipeline. Checkpoints and environment must be prepared before production inference.",
    ),
    VideoResearchModel(
        model_id="xabarnavis_video_0_5",
        name="Xabarnavis Video 0.5 DFDC Challenge",
        family="video_dfdc_challenge_detector",
        purpose="DFDC deepfake challenge baseline/training and prediction scripts.",
        repository="https://github.com/selimsef/dfdc_deepfake_challenge",
        local_path=external_model_path("video", "dfdc_deepfake_challenge"),
        install_command="cd artifacts\models\external\\video\\dfdc_deepfake_challenge && bash download_weights.sh",
        usage_note="Competition solution repository. Download weights and adapt predict_folder.py for local inference.",
    ),
    VideoResearchModel(
        model_id="xabarnavis_video_0_6",
        name="Xabarnavis Video 0.6 FaceForensics++",
        family="video_faceforensics_dataset_tools",
        purpose="FaceForensics++ dataset and classification tooling for manipulated face video forensics.",
        repository="https://github.com/ondyari/FaceForensics",
        local_path=external_model_path("video", "faceforensics"),
        install_command="cd artifacts\models\external\\video\\faceforensics",
        usage_note="Dataset/classification toolkit. It is mainly a dataset/preparation resource, not a ready local inference checkpoint.",
    ),
]


def video_research_status(model: VideoResearchModel) -> str:
    if not model.local_path.exists():
        return "not installed"
    if model.model_id == "xabarnavis_video_0_4" and (model.local_path / "environment.yml").is_file():
        return "installed needs environment"
    if model.model_id == "xabarnavis_video_0_5" and (model.local_path / "weights").exists():
        weight_files = list((model.local_path / "weights").glob("*"))
        return "installed needs weights" if not weight_files else "installed research adapter"
    return "installed research adapter"


def video_research_model_results() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for model in VIDEO_RESEARCH_MODELS:
        status = video_research_status(model)
        results.append(
            {
                "model_id": model.model_id,
                "name": model.name,
                "status": status,
                "verdict": "Research model registered for video forensic workflow. Direct inference is not enabled yet.",
                "real_score": None,
                "ai_score": None,
                "manipulated_score": None,
                "confidence": None,
                "details": {
                    "family": model.family,
                    "purpose": model.purpose,
                    "repository": model.repository,
                    "local_path": str(model.local_path),
                    "install_command": model.install_command,
                    "usage_note": model.usage_note,
                },
                "error": None if model.local_path.exists() else "Repository is not cloned yet.",
            }
        )
    return results





