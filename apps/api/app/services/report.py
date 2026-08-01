from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.services.fusion import FusionResult
from app.services.dataset_inventory import load_dataset_inventory
from app.services.image_reasoning import build_image_reasoning_uz
from app.services.metadata import MetadataSignals
from app.services.osint_enrichment import build_image_osint_analysis
from app.services.signal_analysis import ImageSignalScores
from app.services.docx_report import write_docx_report
from app.services.evidence_intake import EvidenceIntake


def write_json_report(
    report_dir: Path,
    case_id: int,
    original_filename: str,
    file_hash: str,
    metadata: MetadataSignals,
    signals: ImageSignalScores,
    fusion: FusionResult,
    model_version: str,
    artifacts: dict[str, str] | None = None,
    selected_models: list[str] | None = None,
    model_results: list[dict[str, Any]] | None = None,
    evidence_image_path: Path | None = None,
    image_description: str | None = None,
    evidence_intake: EvidenceIntake | None = None,
) -> Path:
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"case-{case_id}.json"
    image_reasoning_uz = build_image_reasoning_uz(
        metadata=metadata,
        signals=signals,
        fusion=fusion,
        model_results=model_results or [],
        evidence_image_path=evidence_image_path,
        image_description=image_description,
    )
    payload: dict[str, Any] = {
        "case_id": case_id,
        "original_filename": original_filename,
        "sha256": file_hash,
        "evidence_intake": evidence_intake.to_dict() if evidence_intake else {},
        "evidence_image_path": str(evidence_image_path) if evidence_image_path else "",
        "image_description": image_description or "",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "final_verdict": fusion.final_verdict,
        "confidence": fusion.confidence,
        "scores": fusion.scores,
        "detected_signs": fusion.reasons,
        "detected_signs_uz": image_reasoning_uz["detected_signs_uz"],
        "image_reasoning_uz": image_reasoning_uz,
        "metadata_analysis": metadata.to_dict(),
        "osint_analysis": build_image_osint_analysis(
            original_filename=original_filename,
            file_hash=file_hash,
            metadata=metadata,
            signals=signals,
        ),
        "frequency_and_noise_analysis": signals.to_dict(),
        "forensic_artifacts": artifacts or {},
        "selected_models": selected_models or [],
        "model_results": model_results or [],
        "image_dataset_inventory": load_dataset_inventory(),
        "legal_report": {
            "title": "Xabarnavis AI Image Forensic Legal Report",
            "evidence_hash_algorithm": "SHA-256",
            "chain_of_custody_note": "Yuklangan rasm lokal storage ichiga ko'chirildi va asl upload baytlarini o'zgartirmasdan tahlil qilindi.",
            "intended_use": "Tergovchi yoki ekspert ko'rib chiqishi uchun texnik forensic screening report. Bu mustaqil sud hukmi emas.",
            "recommended_human_review": True,
            "provenance_interpretation": "Content Credentials mavjud emasligi rasm soxta yoki AI orqali yaratilganini anglatmaydi.",
        },
        "model_slots": {
            "ai_detector": "placeholder: install CLIP/ViT or ConvNeXt ONNX detector",
            "frequency_detector": "placeholder: install frequency/noise ONNX detector",
            "manipulation_localizer": "placeholder: install SegFormer/U-Net heatmap model",
            "fusion_model": "heuristic MVP; replace with logistic regression after labeled data is ready",
        },
        "model_version": model_version,
        "limitations": [
            "Trained ONNX/PyTorch detectorlar to'liq sozlanmaguncha ayrim xulosalar heuristic signallarga tayanadi.",
            "EXIF yo'qligi yolg'iz o'zi AI generatsiya yoki manipulyatsiya isboti emas.",
            "Ijtimoiy tarmoqlardagi siqish provenance ma'lumotlarini olib tashlashi va forensic artefaktlarni o'zgartirishi mumkin.",
        ],
    }
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_docx_report(report_path, payload)
    return report_path





