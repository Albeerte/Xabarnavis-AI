from __future__ import annotations

import shutil
import os
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from app.db import CaseStore
from app.schemas import AnalysisResponse, EvidenceIntakeResponse, ForensicArtifacts, ScoreBreakdown
from app.services.evidence_intake import inspect_evidence
from app.services.fusion import FusionResult, fuse_scores
from app.services.metadata import extract_metadata_signals
from app.services.model_registry import ModelRegistry, results_as_dicts
from app.services.report import write_json_report
from app.services.signal_analysis import create_forensic_artifacts, extract_signal_scores


MODEL_VERSION = "xabarnavis-mvp-0.1-heuristic"


class ImageAnalyzer:
    def __init__(self, upload_dir: Path, report_dir: Path, store: CaseStore) -> None:
        self.upload_dir = upload_dir
        self.report_dir = report_dir
        self.store = store
        self.model_registry = ModelRegistry()

    async def analyze_upload(
        self,
        upload: UploadFile,
        selected_models: list[str] | None = None,
        image_description: str | None = None,
        user_id: int = 0,
    ) -> AnalysisResponse:
        if selected_models is None:
            deep_scan = os.getenv("XABARNAVIS_DEEP_SCAN", "").lower() in {"1", "true", "yes"}
            selected_models = self.model_registry.deep_scan_ids() if deep_scan else self.model_registry.default_selected_ids()
        suffix = Path(upload.filename or "upload").suffix.lower()
        stored_path = self.upload_dir / f"{uuid4().hex}{suffix}"

        with stored_path.open("wb") as out_file:
            shutil.copyfileobj(upload.file, out_file)

        intake = inspect_evidence(
            stored_path,
            original_filename=upload.filename or stored_path.name,
            declared_mime_type=upload.content_type,
            analysis_version=MODEL_VERSION,
        )
        if not intake.detected_mime_type.startswith("image/"):
            stored_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=400,
                detail="Uploaded bytes do not contain a supported image signature.",
            )
        file_hash = intake.sha256
        case_id = self.store.create_case(upload.filename or stored_path.name, stored_path, file_hash, user_id)

        metadata = extract_metadata_signals(stored_path)
        signals = extract_signal_scores(stored_path)
        fusion = fuse_scores(metadata, signals)
        model_results = self.model_registry.run_selected(stored_path, selected_models)
        fusion = blend_model_results(fusion, model_results)
        artifacts = create_forensic_artifacts(stored_path, self.report_dir, case_id)

        report_path = write_json_report(
            self.report_dir,
            case_id,
            upload.filename or stored_path.name,
            file_hash,
            metadata,
            signals,
            fusion,
            MODEL_VERSION,
            artifacts,
            selected_models=selected_models,
            model_results=results_as_dicts(model_results),
            evidence_image_path=stored_path,
            image_description=image_description,
            evidence_intake=intake,
        )

        self.store.save_analysis(
            case_id=case_id,
            scores=fusion.scores,
            final_verdict=fusion.final_verdict,
            confidence=fusion.confidence,
            reasons=fusion.reasons,
            report_path=report_path,
            model_version=MODEL_VERSION,
            model_results=results_as_dicts(model_results),
        )

        return AnalysisResponse(
            case_id=case_id,
            original_filename=upload.filename or stored_path.name,
            file_hash=file_hash,
            evidence_intake=EvidenceIntakeResponse(**{
                key: value
                for key, value in intake.to_dict().items()
                if key not in {"original_filename", "stored_filename", "sha256"}
            }),
            final_verdict=fusion.final_verdict,
            confidence=fusion.confidence,
            scores=ScoreBreakdown(
                real_score=fusion.scores["real_score"],
                ai_score=fusion.scores["ai_score"],
                manipulated_score=fusion.scores["manipulated_score"],
                metadata_anomaly_score=metadata.anomaly_score,
                frequency_anomaly_score=signals.frequency_anomaly_score,
                jpeg_blocking_score=signals.jpeg_blocking_score,
                ela_anomaly_score=signals.ela_anomaly_score,
            ),
            detected_signs=fusion.reasons,
            artifacts=ForensicArtifacts(**artifacts),
            report_path=str(report_path),
            report_docx_path=str(report_path.with_suffix(".docx")),
            model_version=MODEL_VERSION,
            selected_models=selected_models,
            model_results=results_as_dicts(model_results),
        )


def blend_model_results(fusion: FusionResult, model_results: list[object]) -> FusionResult:
    primary_result = next(
        (
            result
            for result in model_results
            if getattr(result, "status", None) == "ready"
            and str(getattr(result, "model_id", "")) == "xabarnavis_0_5"
            and getattr(result, "ai_score", None) is not None
        ),
        None,
    )
    if primary_result is not None:
        ai_score = _clamp(float(primary_result.ai_score))
        real_score = _clamp(
            float(primary_result.real_score)
            if getattr(primary_result, "real_score", None) is not None
            else 1.0 - ai_score
        )
        top_score = max(ai_score, real_score)
        final_verdict = "Highly likely AI-generated" if ai_score >= real_score else "Likely real camera photo"
        confidence = "High" if top_score >= 0.80 else "Medium" if top_score >= 0.60 else "Low"
        reasons = [
            *fusion.reasons,
            "Final decision is based only on Xabarnavis 0.5 (Ateeqq/ai-vs-human-image-detector)",
            "Manipulation and forensic signals are reported as supporting evidence only",
        ]
        return FusionResult(
            final_verdict,
            confidence,
            {
                "real_score": real_score,
                "ai_score": ai_score,
                "manipulated_score": 0.0,
            },
            reasons,
        )

    weighted_sum = 0.0
    total_weight = 0.0
    fallback_scores: list[float] = []
    weights = {
        "xabarnavis_0_5": 0.60,
        "xabarnavis_0_1": 0.08,
        "xabarnavis_0_2": 0.08,
        "xabarnavis_0_6": 0.12,
        "xabarnavis_0_7": 0.12,
        "xabarnavis_0_4": 0.06,
    }

    for result in model_results:
        if getattr(result, "status", None) != "ready" or getattr(result, "ai_score", None) is None:
            continue
        ai_score_value = float(result.ai_score)
        fallback_scores.append(ai_score_value)
        weight = weights.get(str(getattr(result, "model_id", "")))
        if weight is not None:
            weighted_sum += ai_score_value * weight
            total_weight += weight

    if total_weight > 0:
        model_ai_score = weighted_sum / total_weight
    elif fallback_scores:
        model_ai_score = sum(fallback_scores) / len(fallback_scores)
    else:
        return fusion

    ai_score = _clamp(0.15 * fusion.scores["ai_score"] + 0.85 * model_ai_score)
    manipulated_score = fusion.scores["manipulated_score"]
    real_score = _clamp(min(1.0 - ai_score, fusion.scores["real_score"]))
    scores = {
        "real_score": real_score,
        "ai_score": ai_score,
        "manipulated_score": manipulated_score,
    }
    verdict_key = max(scores, key=scores.get)
    final_verdict = {
        "real_score": "Likely real camera photo",
        "ai_score": "Highly likely AI-generated" if ai_score >= 0.70 else "Possibly AI-generated",
        "manipulated_score": "Likely manipulated or edited",
    }[verdict_key]
    top_score = scores[verdict_key]
    confidence = "High" if top_score >= 0.75 else "Medium" if top_score >= 0.55 else "Low"
    reasons = [*fusion.reasons, "Xabarnavis 0.5 is the primary AI-vs-human model in final fusion"]
    return FusionResult(final_verdict, confidence, scores, reasons)


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 4)





