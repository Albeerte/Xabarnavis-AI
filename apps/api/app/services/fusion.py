from __future__ import annotations

from dataclasses import dataclass

from app.services.metadata import MetadataSignals
from app.services.signal_analysis import ImageSignalScores


@dataclass(frozen=True)
class FusionResult:
    final_verdict: str
    confidence: str
    scores: dict[str, float]
    reasons: list[str]


def fuse_scores(metadata: MetadataSignals, signals: ImageSignalScores) -> FusionResult:
    ai_score = _clamp(
        0.45 * signals.frequency_anomaly_score
        + 0.25 * signals.texture_uniformity_score
        + 0.20 * metadata.generator_software_score
        + 0.10 * metadata.anomaly_score
    )
    manipulated_score = _clamp(
        0.30 * signals.edge_inconsistency_score
        + 0.25 * signals.noise_inconsistency_score
        + 0.15 * signals.jpeg_blocking_score
        + 0.15 * signals.ela_anomaly_score
        + 0.15 * metadata.editor_software_score
        + 0.05 * metadata.anomaly_score
    )
    real_score = _clamp(1.0 - max(ai_score, manipulated_score) + 0.15 * metadata.camera_provenance_score)

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
    reasons = _build_reasons(metadata, signals, ai_score, manipulated_score, real_score)

    return FusionResult(final_verdict, confidence, scores, reasons)


def _build_reasons(
    metadata: MetadataSignals,
    signals: ImageSignalScores,
    ai_score: float,
    manipulated_score: float,
    real_score: float,
) -> list[str]:
    reasons: list[str] = []
    if metadata.has_camera_model:
        reasons.append("camera model metadata is present")
    if not metadata.has_exif:
        reasons.append("missing EXIF metadata")
    if metadata.software_tag:
        reasons.append(f"software metadata detected: {metadata.software_tag}")
    if signals.frequency_anomaly_score >= 0.60:
        reasons.append("abnormal frequency-domain artifacts")
    if signals.texture_uniformity_score >= 0.60:
        reasons.append("unusually uniform texture statistics")
    if signals.noise_inconsistency_score >= 0.60:
        reasons.append("localized noise inconsistency")
    if signals.edge_inconsistency_score >= 0.60:
        reasons.append("edge and compression inconsistency")
    if signals.jpeg_blocking_score >= 0.60:
        reasons.append("strong JPEG block-boundary artifacts")
    if signals.ela_anomaly_score >= 0.60:
        reasons.append("elevated error-level-analysis residuals")
    if ai_score >= 0.70:
        reasons.append("combined indicators lean toward AI generation")
    if manipulated_score >= 0.70:
        reasons.append("combined indicators lean toward image editing")
    if real_score >= 0.70:
        reasons.append("combined indicators are consistent with a real camera photo")
    return reasons or ["no strong forensic indicator exceeded the MVP threshold"]


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 4)





