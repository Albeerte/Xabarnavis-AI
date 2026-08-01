from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import importlib.util
import sqlite3
from csv import DictReader
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any

from PIL import Image

from app.services.audio_04_dataset import AUDIO_04_DIR, audio_04_details, audio_04_status
from app.services.audio_05_adapter import AUDIO_05_DIR, audio_05_status
from app.services.audio_02_adapter import audio_02_status
from app.services.external_paths import external_model_path
from app.services.genconvit_adapter import GENCONVIT_REPO, genconvit_status
from app.services.jabberjay_adapter import jabberjay_status
from app.services.naman_video_adapter import HF_MODEL_DIR as NAMAN_VIDEO_HF_DIR, naman_video_status
from app.services.osint_enrichment import osint_status
from app.services.rawgat_st_adapter import RAWGAT_REPO, rawgat_status
from app.services.spectra_aasist3_adapter import HF_SPECTRA_MODEL_DIR, spectra_aasist3_status
from app.services.video_research_adapters import VIDEO_RESEARCH_MODELS, video_research_status


ROOT = Path(__file__).resolve().parents[4]
RUNS_DIR = ROOT / "artifacts" / "runs" / "legacy"
SCHEMA_RUNS_DIR = ROOT / "artifacts" / "runs"
STORAGE_DIR = ROOT / "storage"
DISABLED_MODEL_IDS = {"xabarnavis_0_3", "clip_synthetic", "xabarnavis_03"}


def photo_model_path(folder_name: str) -> Path:
    return external_model_path("photo", folder_name)


def audio_model_path(folder_name: str) -> Path:
    return external_model_path("audio", folder_name)


def video_model_path(folder_name: str) -> Path:
    return external_model_path("video", folder_name)


@dataclass(frozen=True)
class ModelInfo:
    id: str
    name: str
    family: str
    purpose: str
    status: str
    repository: str | None = None
    local_path: str | None = None


@dataclass(frozen=True)
class ModelRunResult:
    model_id: str
    name: str
    status: str
    verdict: str
    ai_score: float | None = None
    real_score: float | None = None
    manipulated_score: float | None = None
    confidence: str | None = None
    details: dict[str, Any] | None = None
    error: str | None = None


class ModelRegistry:
    def __init__(self) -> None:
        self._local_detectors: dict[Path, LocalEfficientNetDetector] = {}
        self._hf_detectors: dict[str, HuggingFaceImageClassifier] = {}

    def list_models(self) -> list[ModelInfo]:
        models = [
            *self._local_trained_models(),
            ModelInfo(
                id="xabarnavis_heuristic",
                name="Xabarnavis Forensic Heuristics",
                family="forensic_signals",
                purpose="Metadata, ELA, noise, frequency, and JPEG artifact analysis",
                status="ready",
            ),
            ModelInfo(
                id="xabarnavis_0_3",
                name="Xabarnavis 0.3",
                family="external_ai_checker",
                purpose="General synthetic image detection with CLIP features",
                status=self._external_status("clip_synthetic"),
                repository="https://github.com/grip-unina/ClipBased-SyntheticImageDetection",
                local_path=str(photo_model_path("clip_synthetic")),
            ),
            ModelInfo(
                id="xabarnavis_0_4",
                name="Xabarnavis 0.4",
                family="external_ai_checker",
                purpose="Classic CNN-generated image detector baseline",
                status=self._external_status("cnnspot"),
                repository="https://github.com/peterwang512/CNNDetection",
                local_path=str(photo_model_path("cnnspot")),
            ),
            ModelInfo(
                id="fatformer",
                name="FatFormer",
                family="github_external",
                purpose="CVPR 2024 forgery-aware adaptive transformer for GAN and diffusion image detection",
                status=self._external_status("fatformer"),
                repository="https://github.com/Michel-liu/FatFormer",
                local_path=str(photo_model_path("fatformer")),
            ),
            ModelInfo(
                id="xabarnavis_0_5",
                name="Xabarnavis 0.5",
                family="huggingface_image_classifier",
                purpose="Ateeqq SigLIP AI-vs-human image detector fine-tuned on 60k AI + 60k human images",
                status=self._hf_status("hf_ateeq_ai_vs_human"),
                repository="https://huggingface.co/Ateeqq/ai-vs-human-image-detector",
                local_path=str(photo_model_path("hf_ateeq_ai_vs_human")),
            ),
            ModelInfo(
                id="xabarnavis_0_6",
                name="Xabarnavis 0.6",
                family="huggingface_image_classifier",
                purpose="PRITHIVSAKTHIUR / prithivMLmods SigLIP deepfake detector model v1",
                status=self._hf_status("prithiv_deepfake_detector"),
                repository="https://github.com/PRITHIVSAKTHIUR/deepfake-detector-model-v1",
                local_path=str(photo_model_path("prithiv_deepfake_detector")),
            ),
            ModelInfo(
                id="xabarnavis_0_7",
                name="Xabarnavis 0.7",
                family="huggingface_image_classifier",
                purpose="CapCheck ViT AI image detection model for Real/Fake classification",
                status=self._hf_status("hf_capcheck_ai_image_detection"),
                repository="https://huggingface.co/capcheck/ai-image-detection",
                local_path=str(photo_model_path("hf_capcheck_ai_image_detection")),
            ),
            ModelInfo(
                id="siglip2_finetuning_reference",
                name="SigLIP2 Fine-Tuning Reference",
                family="training_reference",
                purpose="Reference guide for fine-tuning SigLIP2 style image classifiers for Xabarnavis",
                status="ready",
                repository="https://exnrt.com/blog/ai/fine-tuning-siglip2/",
                local_path=str(photo_model_path("siglip2_finetuning_reference")),
            ),
            ModelInfo(
                id="safe",
                name="SAFE",
                family="github_external",
                purpose="Synthetic image detection generalization",
                status=self._external_status("safe"),
                repository="https://github.com/ouxiang-li/safe",
                local_path=str(photo_model_path("safe")),
            ),
            ModelInfo(
                id="dm_image_detection",
                name="DMimageDetection",
                family="github_external",
                purpose="Diffusion model image detection",
                status=self._external_status("dm_image_detection"),
                repository="https://github.com/grip-unina/DMimageDetection",
                local_path=str(photo_model_path("dm_image_detection")),
            ),
            ModelInfo(
                id="zed",
                name="ZED",
                family="github_external",
                purpose="Zero-shot AI-generated image detection",
                status=self._external_status("zed"),
                repository="https://github.com/grip-unina/ZED",
                local_path=str(photo_model_path("zed")),
            ),
            ModelInfo(
                id="mantranet",
                name="ManTraNet PyTorch",
                family="github_external",
                purpose="Image manipulation localization",
                status=self._external_status("mantranet_pytorch"),
                repository="https://github.com/RonyAbecidan/ManTraNet-pytorch",
                local_path=str(photo_model_path("mantranet_pytorch")),
            ),
            ModelInfo(
                id="awesome_osint_arsenal",
                name="Awesome OSINT Arsenal",
                family="image_osint_reference",
                purpose="Image source verification, reverse image search, EXIF/metadata, geolocation, and forensic investigation checklist",
                status=osint_status(),
                repository="https://github.com/rawfilejson/awesome-osint-arsenal",
                local_path=str(photo_model_path("awesome_osint_arsenal")),
            ),
            ModelInfo(
                id="jabberjay",
                name="Jabberjay",
                family="audio_synthetic_voice_detector",
                purpose="Synthetic voice / spoofed audio detection with VIT, AST, Spectra, Wav2Vec2, HuBERT, WavLM, RawNet2, and classical models",
                status=jabberjay_status(),
                repository="https://github.com/MattyB95/Jabberjay",
                local_path=str(audio_model_path("jabberjay")),
            ),
            ModelInfo(
                id="xabarnavis_audio_0_2",
                name="Xabarnavis Audio 0.2",
                family="audio_wav2vec2_deepfake_detector",
                purpose="Gary Stafford Wav2Vec2 fine-tuned real/fake voice detector with segment timeline analysis",
                status=audio_02_status(),
                repository="https://github.com/garystafford/deepfake-voice-detection-public",
                local_path=str(audio_model_path("deepfake_voice_detection_public")),
            ),
            ModelInfo(
                id="xabarnavis_audio_0_4",
                name="Xabarnavis Audio 0.4",
                family="audio_training_dataset",
                purpose="Kaggle deepfake audio dataset for fake vs real speech training and evaluation",
                status=audio_04_status(),
                repository="https://www.kaggle.com/datasets/jayjoshi37/deepfake-audio-dataset-fake-vs-real-speech",
                local_path=str(AUDIO_04_DIR),
            ),
            ModelInfo(
                id="xabarnavis_audio_0_5",
                name="Xabarnavis Audio 0.5",
                family="audio_wav2vec2_deepfake_detector",
                purpose="Hemgg wav2vec2 audio classifier for AI voice vs human voice detection",
                status=audio_05_status(),
                repository="https://huggingface.co/Hemgg/Deepfake-audio-detection",
                local_path=str(AUDIO_05_DIR),
            ),
            ModelInfo(
                id="xabarnavis_audio_0_6",
                name="Xabarnavis Audio 0.6",
                family="audio_rawgat_st_antispoofing",
                purpose="RawGAT-ST spectro-temporal graph attention anti-spoofing detector for speech deepfake detection",
                status=rawgat_status(),
                repository="https://github.com/eurecom-asp/RawGAT-ST-antispoofing",
                local_path=str(RAWGAT_REPO),
            ),
            ModelInfo(
                id="xabarnavis_audio_0_7",
                name="Xabarnavis Audio 0.7",
                family="audio_spectra_aasist3_antispoofing",
                purpose="Spectra-AASIST3 wav2vec2 XLS-R + KAN-AASIST speech anti-spoofing detector",
                status=spectra_aasist3_status(),
                repository="https://huggingface.co/lab260/Spectra-AASIST3",
                local_path=str(HF_SPECTRA_MODEL_DIR),
            ),
            ModelInfo(
                id="xabarnavis_video_0_1",
                name="Xabarnavis Video 0.1",
                family="video_genconvit_deepfake_detector",
                purpose="GenConViT deepfake video detection using ConvNeXt, Swin Transformer, Autoencoder, and VAE signals",
                status=genconvit_status(),
                repository="https://github.com/erprogs/GenConViT",
                local_path=str(GENCONVIT_REPO),
            ),
            ModelInfo(
                id="xabarnavis_video_0_2",
                name="Xabarnavis Video 0.2",
                family="video_resnext_lstm_deepfake_detector",
                purpose="Naman712 ResNext50 + LSTM video deepfake detector for real/fake classification",
                status=naman_video_status(),
                repository="https://huggingface.co/Naman712/Deep-fake-detection",
                local_path=str(NAMAN_VIDEO_HF_DIR),
            ),
            *[
                ModelInfo(
                    id=model.model_id,
                    name=model.name,
                    family=model.family,
                    purpose=model.purpose,
                    status=video_research_status(model),
                    repository=model.repository,
                    local_path=str(model.local_path),
                )
                for model in VIDEO_RESEARCH_MODELS
            ],
        ]
        return self._apply_admin_settings(models)

    def _apply_admin_settings(self, models: list[ModelInfo]) -> list[ModelInfo]:
        if os.getenv("XABARNAVIS_IGNORE_MODEL_ADMIN_SETTINGS", "").lower() in {"1", "true", "yes"}:
            return models

        settings = self._load_admin_settings()
        if not settings:
            return models

        visible_models: list[ModelInfo] = []
        for model in models:
            setting = settings.get(model.id)
            if setting and not bool(setting.get("enabled", True)):
                continue
            if setting and setting.get("display_name"):
                model = replace(model, name=str(setting["display_name"]))
            visible_models.append(model)
        return sorted(
            visible_models,
            key=lambda model: (
                int(settings.get(model.id, {}).get("sort_order") or 1000),
                model.id,
            ),
        )

    def _load_admin_settings(self) -> dict[str, dict[str, Any]]:
        db_path = STORAGE_DIR / "xabarnavis.sqlite3"
        if not db_path.exists():
            return {}
        try:
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                exists = conn.execute(
                    "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'model_admin_settings'"
                ).fetchone()
                if not exists:
                    return {}
                rows = conn.execute(
                    "SELECT model_id, display_name, enabled, sort_order FROM model_admin_settings"
                ).fetchall()
        except sqlite3.Error:
            return {}
        return {str(row["model_id"]): dict(row) for row in rows}

    def run_selected(self, image_path: Path, selected_model_ids: list[str]) -> list[ModelRunResult]:
        available = {model.id: model for model in self.list_models()}
        aliases = {
            "clip_synthetic": "xabarnavis_0_3",
            "cnnspot": "xabarnavis_0_4",
            "Ateeqq/ai-vs-human-image-detector": "xabarnavis_0_5",
            "prithivMLmods/deepfake-detector-model-v1": "xabarnavis_0_6",
            "capcheck/ai-image-detection": "xabarnavis_0_7",
            "xabarnavis_03": "xabarnavis_0_3",
            "xabarnavis_04": "xabarnavis_0_4",
            "xabarnavis_05": "xabarnavis_0_5",
            "xabarnavis_06": "xabarnavis_0_6",
            "xabarnavis_07": "xabarnavis_0_7",
        }
        results: list[ModelRunResult] = []
        for model_id in selected_model_ids:
            if model_id in DISABLED_MODEL_IDS:
                continue
            if model_id == "xabarnavis_effnet_b0":
                model_id = self.default_local_model_id() or model_id
            model_id = aliases.get(model_id, model_id)
            if model_id in DISABLED_MODEL_IDS:
                continue
            model = available.get(model_id)
            if model is None:
                results.append(
                    ModelRunResult(
                        model_id=model_id,
                        name=model_id,
                        status="unknown",
                        verdict="Model is not registered.",
                        error="Unknown model id.",
                    )
                )
                continue

            if model.family in {"github_external", "external_ai_checker", "huggingface_image_classifier"} and model.status != "ready":
                results.append(
                    ModelRunResult(
                        model_id=model.id,
                        name=model.name,
                        status=model.status,
                        verdict="External model is registered but not ready for inference.",
                        details={
                            "repository": model.repository,
                            "local_path": model.local_path,
                            "next_step": "Install weights/dependencies and add or enable the adapter before running inference.",
                        },
                    )
                )
                continue

            if model.family == "local_pytorch":
                results.append(self._run_local_effnet(image_path, model))
            elif model_id == "xabarnavis_heuristic":
                continue
            elif model_id == "xabarnavis_0_3":
                results.append(self._run_clip_synthetic(image_path, model))
            elif model_id == "xabarnavis_0_4":
                results.append(self._run_cnnspot(image_path, model))
            elif model_id in {"xabarnavis_0_5", "xabarnavis_0_6", "xabarnavis_0_7"}:
                results.append(self._run_huggingface_classifier(image_path, model))
            elif model_id == "fatformer":
                results.append(self._run_fatformer(image_path, model))
            elif model.family == "training_reference":
                results.append(
                    ModelRunResult(
                        model_id=model.id,
                        name=model.name,
                        status="reference",
                        verdict="Training reference only; no inference adapter is required.",
                        details={"repository": model.repository, "local_path": model.local_path},
                    )
                )
            else:
                results.append(
                    ModelRunResult(
                        model_id=model.id,
                        name=model.name,
                        status=model.status,
                        verdict="External GitHub model is registered but not installed yet.",
                        details={
                            "repository": model.repository,
                            "local_path": model.local_path,
                            "next_step": "Clone the repository and add an adapter before using it in production analysis.",
                        },
                    )
                )
        return results

    def default_selected_ids(self) -> list[str]:
        ready_ids = [model.id for model in self.list_models() if model.status == "ready"]
        ordered = [
            "xabarnavis_image_0_1",
            "xabarnavis_0_5",
            "xabarnavis_0_1",
            "xabarnavis_0_2",
            "xabarnavis_heuristic",
            "xabarnavis_0_4",
            "xabarnavis_0_6",
            "xabarnavis_0_7",
        ]
        return [model_id for model_id in ordered if model_id in ready_ids]

    def deep_scan_ids(self) -> list[str]:
        ready_ids = [model.id for model in self.list_models() if model.status == "ready"]
        ordered = [
            "xabarnavis_image_0_1",
            "xabarnavis_0_5",
            "xabarnavis_0_1",
            "xabarnavis_0_2",
            "xabarnavis_heuristic",
            "xabarnavis_0_4",
            "xabarnavis_0_6",
            "xabarnavis_0_7",
        ]
        return [model_id for model_id in ordered if model_id in ready_ids]

    def all_model_ids(self) -> list[str]:
        return [model.id for model in self.list_models()]

    def default_local_model_id(self) -> str | None:
        local_models = self._local_trained_models()
        return local_models[-1].id if local_models else None

    def _local_trained_models(self) -> list[ModelInfo]:
        production_checkpoints = [
            (
                "xabarnavis_image_0_1",
                "Xabarnavis Image 0.1",
                SCHEMA_RUNS_DIR / "photo" / "milliy" / "xabarnavis_image_0.1" / "ai_real_gpu" / "best.pt",
            ),
            (
                "xabarnavis_0_1",
                "Xabarnavis 0.1",
                RUNS_DIR / "ai_real_effnet_b0_balanced" / "best.pt",
            ),
            (
                "xabarnavis_0_2",
                "Xabarnavis 0.2",
                RUNS_DIR / "ai_real_v2_hf" / "best.pt",
            ),
        ]
        models: list[ModelInfo] = []
        for model_id, model_name, checkpoint in production_checkpoints:
            if not checkpoint.is_file():
                continue
            run_name = checkpoint.parent.name
            test_summary = self._test_summary(checkpoint.parent)
            purpose = "AI-generated vs real image classification"
            if test_summary:
                purpose = f"{purpose} | {test_summary}"
            models.append(
                ModelInfo(
                    id=model_id,
                    name=model_name,
                    family="local_pytorch",
                    purpose=f"{purpose} | run: {run_name}",
                    status="ready",
                    local_path=str(checkpoint),
                )
            )
        return models

    def _test_summary(self, run_dir: Path) -> str:
        metrics_path = run_dir / "test_metrics.json"
        if not metrics_path.exists():
            return ""
        try:
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return ""
        accuracy = metrics.get("test_accuracy")
        auc = metrics.get("test_auc")
        parts = []
        if isinstance(accuracy, int | float):
            parts.append(f"accuracy {accuracy:.2%}")
        if isinstance(auc, int | float):
            parts.append(f"AUC {auc:.2%}")
        return ", ".join(parts)

    def _external_status(self, folder_name: str) -> str:
        folder = photo_model_path(folder_name)
        if not folder.exists():
            return "not_installed"
        if folder_name == "clip_synthetic":
            main_py = folder / "main.py"
            weight = folder / "weights" / "Corvi2023" / "weights.pth"
            return "ready" if main_py.exists() and weight.exists() and weight.stat().st_size > 1_000_000 else "installed_no_adapter"
        if folder_name == "cnnspot":
            demo_py = folder / "demo.py"
            weight = folder / "weights" / "blur_jpg_prob0.5.pth"
            return "ready" if demo_py.exists() and weight.exists() and weight.stat().st_size > 1_000_000 else "not_installed"
        if folder_name == "fatformer":
            main_py = folder / "main.py"
            clip_weight = folder / "pretrained" / "ViT-L-14.pt"
            checkpoint_candidates = list(folder.glob("**/*.pth")) + list(folder.glob("**/*.pt"))
            has_fatformer_checkpoint = any(path != clip_weight and path.stat().st_size > 1_000_000 for path in checkpoint_candidates)
            if main_py.exists() and clip_weight.exists() and has_fatformer_checkpoint:
                return "installed_needs_adapter"
            return "installed_no_adapter" if main_py.exists() else "not_installed"
        repo_markers = [folder / "main.py", folder / "LICENSE.md", folder / "Dockerfile"]
        if any(path.exists() for path in repo_markers):
            return "installed_no_adapter"
        return "not_installed"

    def _hf_status(self, folder_name: str) -> str:
        folder = photo_model_path(folder_name)
        if not folder.exists():
            return "not_installed"
        if importlib.util.find_spec("transformers") is None:
            return "installed_no_adapter"
        return "ready"

    def _run_local_effnet(self, image_path: Path, model: ModelInfo) -> ModelRunResult:
        checkpoint = Path(model.local_path).resolve() if model.local_path else None
        if checkpoint is None:
            return ModelRunResult(
                model_id=model.id,
                name=model.name,
                status="missing_checkpoint",
                verdict="Local checkpoint was not found.",
                error="No best.pt checkpoint exists in artifacts/runs/legacy/ai_real_*.",
            )
        try:
            if checkpoint not in self._local_detectors:
                self._local_detectors[checkpoint] = LocalEfficientNetDetector(checkpoint)
            prediction = self._local_detectors[checkpoint].predict(image_path)
        except Exception as exc:  # pragma: no cover - protects API when optional ML deps fail.
            return ModelRunResult(
                model_id=model.id,
                name=model.name,
                status="error",
                verdict="Local model failed during inference.",
                error=str(exc),
            )
        return ModelRunResult(model_id=model.id, name=model.name, status="ready", **prediction)

    def _run_clip_synthetic(self, image_path: Path, model: ModelInfo) -> ModelRunResult:
        repo_dir = photo_model_path("clip_synthetic")
        run_dir = STORAGE_DIR / "external_model_runs" / "clip_synthetic"
        run_dir.mkdir(parents=True, exist_ok=True)
        input_csv = run_dir / f"{image_path.stem}-input.csv"
        output_csv = run_dir / f"{image_path.stem}-output.csv"
        input_csv.write_text(f"filename\n{image_path.resolve()}\n", encoding="utf-8")

        device = "cuda:0" if self._cuda_available() else "cpu"
        command = [
            sys.executable,
            str(repo_dir / "main.py"),
            "--in_csv",
            str(input_csv),
            "--out_csv",
            str(output_csv),
            "--weights_dir",
            str(repo_dir / "weights"),
            "--models",
            "Corvi2023",
            "--device",
            device,
        ]
        try:
            completed = subprocess.run(
                command,
                cwd=str(ROOT),
                env=self._subprocess_env(repo_dir),
                check=True,
                capture_output=True,
                text=True,
                timeout=int(os.getenv("XABARNAVIS_EXTERNAL_MODEL_TIMEOUT", "35")),
            )
            with output_csv.open(newline="", encoding="utf-8") as file:
                row = next(DictReader(file))
            llr = float(row.get("fusion") or row.get("Corvi2023") or 0.0)
        except Exception as exc:  # pragma: no cover - external model isolation.
            return ModelRunResult(
                model_id=model.id,
                name=model.name,
                status="error",
                verdict="CLIP-based detector failed during inference.",
                error=str(exc),
            )

        ai_score = round(1.0 / (1.0 + math.exp(-llr)), 4)
        real_score = round(1.0 - ai_score, 4)
        verdict = "Synthetic / AI-generated" if llr > 0 else "Real camera/photo-like"
        confidence_base = max(ai_score, real_score)
        confidence = "High" if confidence_base >= 0.80 else "Medium" if confidence_base >= 0.60 else "Low"
        return ModelRunResult(
            model_id=model.id,
            name=f"{model.name} (CLIP-Based Synthetic Image Detection)",
            status="ready",
            verdict=verdict,
            ai_score=ai_score,
            real_score=real_score,
            manipulated_score=None,
            confidence=confidence,
            details={
                "llr": round(llr, 6),
                "rule": "LLR > 0 means synthetic according to the upstream repository.",
                "upstream_model": "Corvi2023",
                "device": device,
                "stdout_tail": completed.stdout[-800:],
            },
        )

    def _run_fatformer(self, image_path: Path, model: ModelInfo) -> ModelRunResult:
        repo_dir = photo_model_path("fatformer")
        clip_weight = repo_dir / "pretrained" / "ViT-L-14.pt"
        checkpoint_candidates = [
            path
            for path in [*repo_dir.glob("**/*.pth"), *repo_dir.glob("**/*.pt")]
            if path != clip_weight and path.stat().st_size > 1_000_000
        ]
        missing: list[str] = []
        if not clip_weight.exists():
            missing.append("CLIP ViT-L/14 checkpoint at artifacts/models/external/photo/fatformer/pretrained/ViT-L-14.pt")
        if not checkpoint_candidates:
            missing.append("official FatFormer checkpoint from the upstream Model Zoo")

        status = "installed_needs_adapter" if not missing else "installed_no_adapter"
        return ModelRunResult(
            model_id=model.id,
            name=f"{model.name} (CNNDetection / CNNSpot)",
            status=status,
            verdict="FatFormer is registered in Xabarnavis, but single-image inference is not enabled yet.",
            ai_score=None,
            real_score=None,
            manipulated_score=None,
            confidence=None,
            details={
                "repository": model.repository,
                "local_path": model.local_path,
                "paper": "Forgery-aware Adaptive Transformer for Generalizable Synthetic Image Detection, CVPR 2024",
                "reported_results": {
                    "gan_mean": "98.4% ACC / 99.7% AP on GAN benchmark in upstream README",
                    "diffusion_mean": "95.0% ACC / 98.8% AP on diffusion benchmark in upstream README",
                },
                "current_image": str(image_path),
                "missing": missing,
                "next_step": (
                    "Download the CLIP ViT-L/14 checkpoint and official FatFormer checkpoint, "
                    "then add a Xabarnavis single-image adapter that creates the dataset structure "
                    "expected by artifacts/models/external/photo/fatformer/main.py."
                ),
                "guide": str(repo_dir / "XABARNAVIS_INSTALL.md"),
            },
        )

    def _run_huggingface_classifier(self, image_path: Path, model: ModelInfo) -> ModelRunResult:
        model_ids = {
            "xabarnavis_0_5": "Ateeqq/ai-vs-human-image-detector",
            "xabarnavis_0_6": "prithivMLmods/deepfake-detector-model-v1",
            "xabarnavis_0_7": "capcheck/ai-image-detection",
        }
        hf_model_id = model_ids.get(model.id)
        if hf_model_id is None:
            return ModelRunResult(
                model_id=model.id,
                name=model.name,
                status="unknown",
                verdict="HuggingFace model id is not configured.",
                error="Missing HuggingFace model mapping.",
            )

        try:
            if hf_model_id not in self._hf_detectors:
                self._hf_detectors[hf_model_id] = HuggingFaceImageClassifier(hf_model_id)
            prediction = self._hf_detectors[hf_model_id].predict(image_path)
        except Exception as exc:  # pragma: no cover - optional HuggingFace deps/network/cache.
            return ModelRunResult(
                model_id=model.id,
                name=model.name,
                status="error",
                verdict="HuggingFace detector failed during inference.",
                error=str(exc),
                details={"repository": model.repository, "hf_model_id": hf_model_id},
            )

        return ModelRunResult(
            model_id=model.id,
            name=f"{model.name} ({hf_model_id})",
            status="ready",
            **prediction,
        )

    def _run_cnnspot(self, image_path: Path, model: ModelInfo) -> ModelRunResult:
        repo_dir = photo_model_path("cnnspot")
        weight_path = repo_dir / "weights" / "blur_jpg_prob0.5.pth"
        device = "cuda" if self._cuda_available() else "cpu"
        command = [
            sys.executable,
            "demo.py",
            "--file",
            str(image_path.resolve()),
            "--model_path",
            str(weight_path),
        ]
        if device == "cpu":
            command.append("--use_cpu")
        try:
            completed = subprocess.run(
                command,
                cwd=str(repo_dir),
                env=self._subprocess_env(repo_dir),
                check=True,
                capture_output=True,
                text=True,
                timeout=int(os.getenv("XABARNAVIS_EXTERNAL_MODEL_TIMEOUT", "35")),
            )
            probability = _parse_cnnspot_probability(completed.stdout)
        except Exception as exc:  # pragma: no cover - external model isolation.
            return ModelRunResult(
                model_id=model.id,
                name=model.name,
                status="error",
                verdict="CNNSpot detector failed during inference.",
                error=str(exc),
            )

        ai_score = round(probability, 4)
        real_score = round(1.0 - ai_score, 4)
        verdict = "Synthetic / CNN-generated" if ai_score >= 0.50 else "Real camera/photo-like"
        confidence_base = max(ai_score, real_score)
        confidence = "High" if confidence_base >= 0.80 else "Medium" if confidence_base >= 0.60 else "Low"
        return ModelRunResult(
            model_id=model.id,
            name=model.name,
            status="ready",
            verdict=verdict,
            ai_score=ai_score,
            real_score=real_score,
            manipulated_score=None,
            confidence=confidence,
            details={
                "upstream_model": "CNNDetection Blur+JPEG(0.5)",
                "checkpoint": str(weight_path),
                "device": device,
                "rule": "Synthetic probability >= 0.50 means synthetic according to the Xabarnavis adapter.",
                "stdout_tail": completed.stdout[-800:],
            },
        )

    def _cuda_available(self) -> bool:
        return torch_cuda_is_usable()

    def _subprocess_env(self, *paths: Path) -> dict[str, str]:
        env = os.environ.copy()
        model_paths = [str(path.resolve()) for path in paths]
        model_paths.append(str((ROOT / "artifacts/models/external").resolve()))
        model_paths.append(str((ROOT / "artifacts/models/external" / "photo").resolve()))
        model_paths.append(str((ROOT / "artifacts/models/external" / "audio").resolve()))
        model_paths.append(str((ROOT / "artifacts/models/external" / "video").resolve()))
        model_paths.append(str((ROOT / "artifacts/models/external" / "text").resolve()))
        model_paths.append(str(ROOT.resolve()))
        existing = env.get("PYTHONPATH")
        env["PYTHONPATH"] = os.pathsep.join([*model_paths, existing] if existing else model_paths)
        return env


def torch_cuda_is_usable() -> bool:
    """Return true only when PyTorch can actually execute on this GPU."""
    try:
        try:
            import torch
        except Exception:
            return False

        if not torch.cuda.is_available():
            return False

        major, minor = torch.cuda.get_device_capability(0)
        arch = f"sm_{major}{minor}"
        arch_list = set(torch.cuda.get_arch_list()) if hasattr(torch.cuda, "get_arch_list") else set()
        if arch_list and arch not in arch_list:
            return False

        torch.zeros(1, device="cuda").cpu()
        return True
    except Exception:
        return False


class HuggingFaceImageClassifier:
    AI_WORDS = {"ai", "fake", "deepfake", "generated", "synthetic", "artificial", "gan", "diffusion"}
    REAL_WORDS = {"real", "human", "hum", "authentic", "natural", "photo", "photograph", "realism"}

    def __init__(self, model_id: str) -> None:
        self._disable_broken_torchaudio_for_image_pipeline()
        from transformers import pipeline

        self.model_id = model_id
        self.device = 0 if torch_cuda_is_usable() else -1
        self.pipe = pipeline("image-classification", model=model_id, device=self.device)

    def _disable_broken_torchaudio_for_image_pipeline(self) -> None:
        """Keep image-only HF pipelines from importing a broken torchaudio install."""
        try:
            import transformers.utils as transformers_utils
            import transformers.utils.import_utils as import_utils

            transformers_utils.is_torchaudio_available = lambda: False
            import_utils.is_torchaudio_available = lambda: False
        except Exception:
            pass

    def predict(self, image_path: Path) -> dict[str, Any]:
        with Image.open(image_path) as image:
            rgb_image = image.convert("RGB")
            try:
                raw_outputs = self.pipe(rgb_image, top_k=None)
            except TypeError:
                raw_outputs = self.pipe(rgb_image)

        outputs = self._normalize_outputs(raw_outputs)
        ai_score = self._ai_probability(outputs)
        real_score = round(1.0 - ai_score, 4)
        verdict = "Synthetic / AI-generated" if ai_score >= 0.50 else "Real camera/photo-like"
        confidence_base = max(ai_score, real_score)
        confidence = "High" if confidence_base >= 0.80 else "Medium" if confidence_base >= 0.60 else "Low"
        return {
            "verdict": verdict,
            "ai_score": ai_score,
            "real_score": real_score,
            "manipulated_score": None,
            "confidence": confidence,
            "details": {
                "hf_model_id": self.model_id,
                "device": "cuda" if self.device == 0 else "cpu",
                "raw_output": outputs,
                "rule": "Labels containing fake/ai/synthetic increase AI score; labels containing real/human/photo increase real score.",
            },
        }

    def _normalize_outputs(self, raw_outputs: Any) -> list[dict[str, Any]]:
        if isinstance(raw_outputs, list) and raw_outputs and isinstance(raw_outputs[0], list):
            raw_outputs = raw_outputs[0]
        clean: list[dict[str, Any]] = []
        if not isinstance(raw_outputs, list):
            return clean
        for item in raw_outputs:
            if not isinstance(item, dict):
                continue
            clean.append({"label": str(item.get("label", "")), "score": float(item.get("score", 0.0))})
        return clean

    def _ai_probability(self, outputs: list[dict[str, Any]]) -> float:
        ai_score = 0.0
        real_score = 0.0
        for item in outputs:
            label = str(item["label"]).lower()
            score = float(item["score"])
            if any(word in label for word in self.AI_WORDS):
                ai_score += score
            if any(word in label for word in self.REAL_WORDS):
                real_score += score
        if ai_score > 0 and real_score > 0:
            return round(ai_score / (ai_score + real_score), 4)
        if ai_score > 0:
            return round(min(ai_score, 1.0), 4)
        if real_score > 0:
            return round(max(0.0, 1.0 - real_score), 4)
        return 0.5


class LocalEfficientNetDetector:
    def __init__(self, checkpoint_path: Path) -> None:
        import torch
        from torch import nn
        from torchvision import models, transforms

        self.torch = torch
        self.checkpoint_path = checkpoint_path
        self.device = "cuda" if torch_cuda_is_usable() else "cpu"
        self.transform = transforms.Compose(
            [
                transforms.Resize(257),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        )
        model = models.efficientnet_b0(weights=None)
        in_features = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(in_features, 2)
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        model.load_state_dict(checkpoint["model"])
        model.to(self.device)
        model.eval()
        self.model = model

    def predict(self, image_path: Path) -> dict[str, Any]:
        with Image.open(image_path) as image:
            tensor = self.transform(image.convert("RGB")).unsqueeze(0).to(self.device)
        with self.torch.no_grad():
            logits = self.model(tensor)
            probabilities = self.torch.softmax(logits, dim=1)[0].detach().cpu().tolist()
        real_score = round(float(probabilities[0]), 4)
        ai_score = round(float(probabilities[1]), 4)
        verdict = "AI-generated" if ai_score >= real_score else "Real camera/photo-like"
        top_score = max(real_score, ai_score)
        confidence = "High" if top_score >= 0.80 else "Medium" if top_score >= 0.60 else "Low"
        return {
            "verdict": verdict,
            "real_score": real_score,
            "ai_score": ai_score,
            "manipulated_score": None,
            "confidence": confidence,
            "details": {
                "checkpoint": str(self.checkpoint_path),
                "device": self.device,
                "labels": {"0": "real", "1": "ai_generated"},
            },
        }


def models_as_dicts(models: list[ModelInfo]) -> list[dict[str, Any]]:
    return [asdict(model) for model in models]


def results_as_dicts(results: list[ModelRunResult]) -> list[dict[str, Any]]:
    return [asdict(result) for result in results]


def write_external_model_registry(path: Path, models: list[ModelInfo]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(models_as_dicts(models), indent=2), encoding="utf-8")


def _parse_cnnspot_probability(stdout: str) -> float:
    marker = "probability of being synthetic:"
    for line in stdout.splitlines():
        if marker in line:
            raw = line.split(marker, 1)[1].strip().rstrip("%")
            return max(0.0, min(1.0, float(raw) / 100.0))
    raise ValueError(f"CNNSpot probability line not found in output: {stdout[-500:]}")





