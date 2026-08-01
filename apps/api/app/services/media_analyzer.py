from __future__ import annotations

import json
import math
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.db import CaseStore
from app.schemas import MediaAnalysisResponse
from app.services.audio_04_dataset import audio_04_details, audio_04_status
from app.services.audio_02_adapter import run_audio_02
from app.services.audio_05_adapter import run_audio_05
from app.services.audio_visuals import create_audio_artifacts
from app.services.docx_report import write_docx_report
from app.services.genconvit_adapter import run_genconvit
from app.services.jabberjay_adapter import run_jabberjay
from app.services.naman_video_adapter import run_naman_video
from app.services.rawgat_st_adapter import run_rawgat_st
from app.services.spectra_aasist3_adapter import run_spectra_aasist3
from app.services.utils import sha256_file
from app.services.video_models.video_audio_extractor import extract_audio_track, extract_video_metadata
from app.services.video_models.video_ensemble import combine_video_scores, model_status_json
from app.services.video_models.video_segment_forensics import analyze_video_segments
from app.services.video_research_adapters import video_research_model_results


MODEL_VERSION = "xabarnavis-multimodal-mvp-0.3-audio02"


class MediaAnalyzer:
    def __init__(self, upload_dir: Path, report_dir: Path, store: CaseStore) -> None:
        self.upload_dir = upload_dir
        self.report_dir = report_dir
        self.store = store

    async def analyze_audio(self, upload: UploadFile, user_id: int) -> MediaAnalysisResponse:
        stored_path = self._store_upload(upload, "audio")
        file_hash = sha256_file(stored_path)
        size_score = _bounded_score(math.log10(max(stored_path.stat().st_size, 1)) / 8)
        extension_score = 0.20 if stored_path.suffix.lower() in {".wav", ".flac"} else 0.36
        heuristic_ai_score = _clamp(0.30 + 0.35 * extension_score + 0.20 * size_score)
        jabberjay = run_jabberjay(stored_path)
        audio_02 = run_audio_02(stored_path)
        audio_05 = run_audio_05(stored_path)
        rawgat_st = run_rawgat_st(stored_path)
        spectra_aasist3 = run_spectra_aasist3(stored_path)
        ready_scores = [
            score
            for score in [
                audio_05.ai_score if audio_05.status == "ready" else None,
                spectra_aasist3.ai_score if spectra_aasist3.status == "ready" else None,
                rawgat_st.ai_score if rawgat_st.status == "ready" else None,
                jabberjay.ai_score if jabberjay.status == "ready" else None,
                audio_02.ai_score if audio_02.status == "ready" else None,
            ]
            if score is not None
        ]
        ai_score = _clamp(sum(ready_scores) / len(ready_scores)) if ready_scores else heuristic_ai_score
        real_score = _clamp(1.0 - ai_score)
        scores = {
            "real_voice_score": real_score,
            "ai_voice_score": ai_score,
            "speaker_spoof_score": _clamp(ai_score * 0.82),
            "watermark_score": 0.0,
        }
        reasons = [
            "Jabberjay synthetic voice detector adapter was executed",
            f"Jabberjay status: {jabberjay.status}",
            "Xabarnavis Audio 0.2 Wav2Vec2 detector adapter was executed",
            f"Xabarnavis Audio 0.2 status: {audio_02.status}",
            "Xabarnavis Audio 0.5 Hemgg Wav2Vec2 detector adapter was executed",
            f"Xabarnavis Audio 0.5 status: {audio_05.status}",
            "Xabarnavis Audio 0.6 RawGAT-ST anti-spoofing detector adapter was executed",
            f"Xabarnavis Audio 0.6 status: {rawgat_st.status}",
            "Xabarnavis Audio 0.7 Spectra-AASIST3 anti-spoofing detector adapter was executed",
            f"Xabarnavis Audio 0.7 status: {spectra_aasist3.status}",
            f"Xabarnavis Audio 0.4 dataset status: {audio_04_status()}",
            "audio was hashed and stored locally for user-linked report history",
        ]
        suspicious_count = len((jabberjay.details or {}).get("suspicious_segments", []))
        segment_count = len((jabberjay.details or {}).get("segment_analysis", []))
        if segment_count:
            reasons.append(f"Jabberjay segment timeline: {suspicious_count} suspicious segment(s) out of {segment_count}")
        if jabberjay.error:
            reasons.append(f"Jabberjay note: {jabberjay.error}")
        audio02_suspicious_count = len((audio_02.details or {}).get("suspicious_segments", []))
        audio02_segment_count = len((audio_02.details or {}).get("segment_analysis", []))
        if audio02_segment_count:
            reasons.append(f"Xabarnavis Audio 0.2 segment timeline: {audio02_suspicious_count} suspicious segment(s) out of {audio02_segment_count}")
        if audio_02.error:
            reasons.append(f"Xabarnavis Audio 0.2 note: {audio_02.error}")
        audio05_suspicious_count = len((audio_05.details or {}).get("suspicious_segments", []))
        audio05_segment_count = len((audio_05.details or {}).get("segment_analysis", []))
        if audio05_segment_count:
            reasons.append(f"Xabarnavis Audio 0.5 segment timeline: {audio05_suspicious_count} suspicious segment(s) out of {audio05_segment_count}")
        if audio_05.error:
            reasons.append(f"Xabarnavis Audio 0.5 note: {audio_05.error}")
        rawgat_suspicious_count = len((rawgat_st.details or {}).get("suspicious_segments", []))
        rawgat_segment_count = len((rawgat_st.details or {}).get("segment_analysis", []))
        if rawgat_segment_count:
            reasons.append(f"Xabarnavis Audio 0.6 RawGAT-ST segment timeline: {rawgat_suspicious_count} suspicious segment(s) out of {rawgat_segment_count}")
        if rawgat_st.error:
            reasons.append(f"Xabarnavis Audio 0.6 note: {rawgat_st.error}")
        spectra_suspicious_count = len((spectra_aasist3.details or {}).get("suspicious_segments", []))
        spectra_segment_count = len((spectra_aasist3.details or {}).get("segment_analysis", []))
        if spectra_segment_count:
            reasons.append(f"Xabarnavis Audio 0.7 Spectra-AASIST3 segment timeline: {spectra_suspicious_count} suspicious segment(s) out of {spectra_segment_count}")
        if spectra_aasist3.error:
            reasons.append(f"Xabarnavis Audio 0.7 note: {spectra_aasist3.error}")
        model_results = [
            {
                "model_id": "xabarnavis_audio_0_5",
                "name": "Xabarnavis Audio 0.5",
                "status": audio_05.status,
                "verdict": audio_05.verdict,
                "real_score": audio_05.real_score,
                "ai_score": audio_05.ai_score,
                "manipulated_score": audio_05.ai_score,
                "confidence": audio_05.confidence,
                "details": audio_05.details or {},
                "error": audio_05.error,
            },
            {
                "model_id": "xabarnavis_audio_0_7",
                "name": "Xabarnavis Audio 0.7 Spectra-AASIST3",
                "status": spectra_aasist3.status,
                "verdict": spectra_aasist3.verdict,
                "real_score": spectra_aasist3.real_score,
                "ai_score": spectra_aasist3.ai_score,
                "manipulated_score": spectra_aasist3.ai_score,
                "confidence": spectra_aasist3.confidence,
                "details": spectra_aasist3.details or {},
                "error": spectra_aasist3.error,
            },
            {
                "model_id": "xabarnavis_audio_0_6",
                "name": "Xabarnavis Audio 0.6 RawGAT-ST",
                "status": rawgat_st.status,
                "verdict": rawgat_st.verdict,
                "real_score": rawgat_st.real_score,
                "ai_score": rawgat_st.ai_score,
                "manipulated_score": rawgat_st.ai_score,
                "confidence": rawgat_st.confidence,
                "details": rawgat_st.details or {},
                "error": rawgat_st.error,
            },
            {
                "model_id": "jabberjay",
                "name": "Jabberjay Synthetic Voice Detector",
                "status": jabberjay.status,
                "verdict": jabberjay.verdict,
                "real_score": jabberjay.real_score,
                "ai_score": jabberjay.ai_score,
                "manipulated_score": jabberjay.ai_score,
                "confidence": jabberjay.confidence,
                "details": jabberjay.details or {},
                "error": jabberjay.error,
            },
            {
                "model_id": "xabarnavis_audio_0_2",
                "name": "Xabarnavis Audio 0.2",
                "status": audio_02.status,
                "verdict": audio_02.verdict,
                "real_score": audio_02.real_score,
                "ai_score": audio_02.ai_score,
                "manipulated_score": audio_02.ai_score,
                "confidence": audio_02.confidence,
                "details": audio_02.details or {},
                "error": audio_02.error,
            },
            {
                "model_id": "audio_heuristic_mvp",
                "name": "Xabarnavis Audio Heuristic Fallback",
                "status": "ready",
                "verdict": "Fallback signal used" if jabberjay.status != "ready" else "Supporting heuristic signal",
                "real_score": _clamp(1.0 - heuristic_ai_score),
                "ai_score": heuristic_ai_score,
                "manipulated_score": _clamp(heuristic_ai_score * 0.82),
                "confidence": "Medium",
                "details": {
                    "file_size_bytes": stored_path.stat().st_size,
                    "extension": stored_path.suffix.lower(),
                    "rule": "File-size and format based MVP fallback, not a trained detector.",
                },
            },
            {
                "model_id": "xabarnavis_audio_0_4",
                "name": "Xabarnavis Audio 0.4 Dataset",
                "status": audio_04_status(),
                "verdict": "Kaggle fake vs real speech dataset is registered for training/evaluation, not direct inference.",
                "real_score": None,
                "ai_score": None,
                "manipulated_score": None,
                "confidence": None,
                "details": audio_04_details(),
                "error": None,
            },
        ]
        return self._save_media_result(
            "audio",
            upload.filename or stored_path.name,
            stored_path,
            file_hash,
            scores,
            reasons,
            user_id,
            selected_models=["xabarnavis_audio_0_5", "xabarnavis_audio_0_7", "xabarnavis_audio_0_6", "jabberjay", "xabarnavis_audio_0_2", "audio_heuristic_mvp", "xabarnavis_audio_0_4"],
            model_results=model_results,
        )

    async def analyze_video(self, upload: UploadFile, user_id: int) -> MediaAnalysisResponse:
        stored_path = self._store_upload(upload, "video")
        file_hash = sha256_file(stored_path)
        video_metadata = extract_video_metadata(stored_path)
        size_score = _bounded_score(math.log10(max(stored_path.stat().st_size, 1)) / 9)
        extension_score = 0.28 if stored_path.suffix.lower() in {".mp4", ".mov"} else 0.42
        metadata_risk = _clamp(0.32 + 0.30 * extension_score + 0.22 * size_score)
        genconvit = run_genconvit(stored_path)
        naman_video = run_naman_video(stored_path)
        extracted_audio = extract_audio_track(stored_path, self.upload_dir / "video_audio", stored_path.stem)
        spectra_audio = None
        if extracted_audio.audio_extracted and extracted_audio.wav_path:
            spectra_audio = run_spectra_aasist3(extracted_audio.wav_path)
        segment_forensics = analyze_video_segments(stored_path, self.report_dir, f"case-video-{stored_path.stem}")
        segment_risks = [
            float(item["risk_score"])
            for item in segment_forensics.segments
            if isinstance(item.get("risk_score"), int | float)
        ]
        segment_risk = _clamp(sum(segment_risks) / len(segment_risks)) if segment_risks else None
        ensemble = combine_video_scores(
            genconvit_score=genconvit.fake_score if genconvit.status == "ready" else None,
            naman712_score=naman_video.fake_score if naman_video.status == "ready" else None,
            spectra_audio_score=spectra_audio.ai_score if spectra_audio and spectra_audio.status == "ready" else None,
            metadata_risk_score=_clamp((metadata_risk + segment_risk) / 2) if segment_risk is not None else metadata_risk,
        )
        fake_score = ensemble.fake_score
        real_score = ensemble.real_score
        scores = {
            "video_real_score": real_score,
            "video_fake_score": fake_score,
            "face_manipulation_score": _clamp(fake_score * 0.76),
            "temporal_artifact_score": _clamp(fake_score * 0.68),
            "audio_deepfake_score": spectra_audio.ai_score if spectra_audio and spectra_audio.ai_score is not None else 0.0,
            "metadata_compression_risk": metadata_risk,
            "segment_visual_risk": segment_risk or 0.0,
        }
        reasons = [
            "video metadata and compression risk analysis completed",
            "Xabarnavis Video 0.1 GenConViT adapter was executed",
            f"Xabarnavis Video 0.1 status: {genconvit.status}",
            "Xabarnavis Video 0.2 Naman712 ResNext50 + LSTM adapter was executed",
            f"Xabarnavis Video 0.2 status: {naman_video.status}",
            "Video audio track extraction was attempted for Spectra-AASIST3 audio deepfake forensics",
            f"Audio extraction status: {extracted_audio.status}",
            f"Spectra-AASIST3 audio status: {spectra_audio.status if spectra_audio else 'not available'}",
            f"Video segment forensics status: {segment_forensics.status}",
            f"Video segment count: {len(segment_forensics.segments)}",
            f"Video ensemble weights used: {ensemble.weights_used}",
            "video was hashed and stored locally for user-linked report history",
        ]
        if genconvit.error:
            reasons.append(f"Xabarnavis Video 0.1 note: {genconvit.error}")
        if naman_video.error:
            reasons.append(f"Xabarnavis Video 0.2 note: {naman_video.error}")
        if extracted_audio.error:
            reasons.append(f"Audio extraction note: {extracted_audio.error}")
        if spectra_audio and spectra_audio.error:
            reasons.append(f"Spectra-AASIST3 note: {spectra_audio.error}")
        if segment_forensics.error:
            reasons.append(f"Video segment forensics note: {segment_forensics.error}")
        top_segment = (segment_forensics.summary or {}).get("top_suspicious_segment")
        if isinstance(top_segment, dict):
            reasons.append(
                f"Most suspicious video part: segment {top_segment.get('index')} "
                f"({top_segment.get('start_seconds')}s-{top_segment.get('end_seconds')}s), "
                f"risk {top_segment.get('risk_percent')}%."
            )
        model_results = [
            {
                "model_id": "xabarnavis_video_0_1",
                "name": "Xabarnavis Video 0.1 GenConViT",
                "status": genconvit.status,
                "verdict": genconvit.verdict,
                "real_score": genconvit.real_score,
                "ai_score": genconvit.fake_score,
                "manipulated_score": genconvit.fake_score,
                "confidence": genconvit.confidence,
                "details": genconvit.details or {},
                "error": genconvit.error,
            },
            {
                "model_id": "xabarnavis_video_0_2",
                "name": "Xabarnavis Video 0.2 Naman712",
                "status": naman_video.status,
                "verdict": naman_video.verdict,
                "real_score": naman_video.real_score,
                "ai_score": naman_video.fake_score,
                "manipulated_score": naman_video.fake_score,
                "confidence": naman_video.confidence,
                "details": naman_video.details or {},
                "error": naman_video.error,
            },
            {
                "model_id": "xabarnavis_audio_0_7_video_track",
                "name": "Spectra-AASIST3 Audio Deepfake Forensics",
                "status": spectra_audio.status if spectra_audio else "not available",
                "verdict": spectra_audio.verdict if spectra_audio else "Video audio track was not available or could not be extracted.",
                "real_score": spectra_audio.real_score if spectra_audio else None,
                "ai_score": spectra_audio.ai_score if spectra_audio else None,
                "manipulated_score": spectra_audio.ai_score if spectra_audio else None,
                "confidence": spectra_audio.confidence if spectra_audio else None,
                "details": {
                    **(spectra_audio.details if spectra_audio and spectra_audio.details else {}),
                    "audio_extraction": {
                        "status": extracted_audio.status,
                        "audio_extracted": extracted_audio.audio_extracted,
                        "sample_rate_hz": extracted_audio.sample_rate_hz,
                        "channels": extracted_audio.channels,
                        "wav_path": str(extracted_audio.wav_path) if extracted_audio.wav_path else None,
                    },
                },
                "error": spectra_audio.error if spectra_audio else extracted_audio.error,
            },
            {
                "model_id": "video_heuristic_mvp",
                "name": "Xabarnavis Video Heuristic Fallback",
                "status": "ready",
                "verdict": "Fallback signal used" if genconvit.status != "ready" else "Supporting heuristic signal",
                "real_score": _clamp(1.0 - metadata_risk),
                "ai_score": metadata_risk,
                "manipulated_score": _clamp(metadata_risk * 0.76),
                "confidence": "Medium",
                "details": {
                    "file_size_bytes": stored_path.stat().st_size,
                    "extension": stored_path.suffix.lower(),
                    "rule": "File-size, format, metadata, and compression-risk fallback. It is not a trained detector.",
                    "technical_metadata": video_metadata,
                    "segment_forensics": segment_forensics.summary,
                },
            },
            {
                "model_id": "video_ensemble",
                "name": "Xabarnavis Video Ensemble",
                "status": "ready",
                "verdict": ensemble.verdict,
                "real_score": ensemble.real_score,
                "ai_score": ensemble.fake_score,
                "manipulated_score": _clamp(ensemble.fake_score * 0.76),
                "confidence": ensemble.confidence,
                "details": {
                    "formula": "0.50*GenConViT + 0.25*Naman712 + 0.20*Spectra-AASIST3 audio + 0.05*metadata/compression risk; unavailable models are re-normalized.",
                    "weights_used": ensemble.weights_used,
                    "available_scores": ensemble.available_scores,
                    "segment_visual_risk": segment_risk,
                },
            },
            *video_research_model_results(),
        ]
        return self._save_media_result(
            "video",
            upload.filename or stored_path.name,
            stored_path,
            file_hash,
            scores,
            reasons,
            user_id,
            selected_models=[
                "xabarnavis_video_0_1",
                "xabarnavis_video_0_2",
                "xabarnavis_audio_0_7_video_track",
                "video_heuristic_mvp",
                "video_ensemble",
                "xabarnavis_video_0_3",
                "xabarnavis_video_0_4",
                "xabarnavis_video_0_5",
                "xabarnavis_video_0_6",
            ],
            model_results=model_results,
            extra_payload={
                "technical_metadata": video_metadata,
                "forensic_artifacts": segment_forensics.artifacts,
                "video_segment_forensics": {
                    "status": segment_forensics.status,
                    "segments": segment_forensics.segments,
                    "summary": segment_forensics.summary,
                    "artifacts": segment_forensics.artifacts,
                    "error": segment_forensics.error,
                },
                "video_model_status": [
                    model_status_json("GenConViT", genconvit.status, genconvit.error, genconvit.details),
                    model_status_json("Naman712", naman_video.status, naman_video.error, naman_video.details),
                    model_status_json("Spectra-AASIST3 Audio", spectra_audio.status if spectra_audio else "not available", spectra_audio.error if spectra_audio else extracted_audio.error, spectra_audio.details if spectra_audio else extracted_audio.details),
                ],
                "audio_deepfake_forensics": {
                    "audio_extracted": extracted_audio.audio_extracted,
                    "sample_rate_hz": extracted_audio.sample_rate_hz,
                    "channels": extracted_audio.channels,
                    "wav_path": str(extracted_audio.wav_path) if extracted_audio.wav_path else None,
                    "spectra_fake_score": spectra_audio.ai_score if spectra_audio else None,
                    "spectra_real_score": spectra_audio.real_score if spectra_audio else None,
                    "audio_verdict": spectra_audio.verdict if spectra_audio else "not available",
                    "status": spectra_audio.status if spectra_audio else extracted_audio.status,
                },
                "ensemble": {
                    "weights_used": ensemble.weights_used,
                    "available_scores": ensemble.available_scores,
                    "formula": "0.50*GenConViT + 0.25*Naman712 + 0.20*Spectra-AASIST3 audio + 0.05*metadata/compression risk, with re-normalized available weights.",
                },
            },
        )

    def analyze_text(self, text: str, user_id: int, title: str = "text-evidence.txt") -> MediaAnalysisResponse:
        safe_title = title.strip() or "text-evidence.txt"
        if not safe_title.lower().endswith(".txt"):
            safe_title = f"{safe_title}.txt"
        stored_path = self.upload_dir / "text" / f"{uuid4().hex}.txt"
        stored_path.parent.mkdir(parents=True, exist_ok=True)
        stored_path.write_text(text, encoding="utf-8")
        file_hash = sha256_file(stored_path)

        words = re.findall(r"\b[\w'-]+\b", text.lower())
        unique_ratio = len(set(words)) / max(len(words), 1)
        avg_word_len = sum(len(word) for word in words) / max(len(words), 1)
        ai_markers = sum(1 for item in ["therefore", "moreover", "in conclusion", "as an ai", "overall"] if item in text.lower())
        ai_score = _clamp(0.22 + (1 - unique_ratio) * 0.35 + min(avg_word_len / 18, 0.25) + ai_markers * 0.08)
        fake_news_score = _clamp(0.18 + min(len(re.findall(r"!|\b100%\b|\bshocking\b|\bbreaking\b", text.lower())) * 0.08, 0.34))
        human_score = _clamp(1.0 - max(ai_score, fake_news_score * 0.8))
        scores = {
            "human_written_score": human_score,
            "ai_text_score": ai_score,
            "fake_news_score": fake_news_score,
            "claim_risk_score": _clamp((ai_score + fake_news_score) / 2),
        }
        reasons = [
            "text MVP heuristic analysis completed",
            "BERT / multilingual transformer adapter slot is prepared but not yet connected",
            f"{len(words)} words analyzed with lexical diversity score {unique_ratio:.2f}",
        ]
        return self._save_media_result("text", safe_title, stored_path, file_hash, scores, reasons, user_id)

    def _store_upload(self, upload: UploadFile, media_type: str) -> Path:
        suffix = Path(upload.filename or f"{media_type}-upload").suffix.lower()
        stored_path = self.upload_dir / media_type / f"{uuid4().hex}{suffix}"
        stored_path.parent.mkdir(parents=True, exist_ok=True)
        with stored_path.open("wb") as out_file:
            shutil.copyfileobj(upload.file, out_file)
        return stored_path

    def _save_media_result(
        self,
        media_type: str,
        original_filename: str,
        stored_path: Path,
        file_hash: str,
        scores: dict[str, float],
        reasons: list[str],
        user_id: int,
        selected_models: list[str] | None = None,
        model_results: list[dict] | None = None,
        extra_payload: dict | None = None,
    ) -> MediaAnalysisResponse:
        primary_score = max(scores.values()) if scores else 0.0
        final_verdict = _verdict(media_type, scores)
        confidence = "High" if primary_score >= 0.75 else "Medium" if primary_score >= 0.50 else "Low"
        case_id = self.store.create_case(original_filename, stored_path, file_hash, user_id, media_type=media_type)
        report_path = self.report_dir / f"case-{case_id}.json"
        forensic_artifacts = {}
        if media_type == "audio":
            forensic_artifacts = create_audio_artifacts(stored_path, self.report_dir, case_id, model_results or [])
        payload = {
            "case_id": case_id,
            "media_type": media_type,
            "original_filename": original_filename,
            "sha256": file_hash,
            "evidence_image_path": "",
            "image_description": f"{media_type.title()} authenticity analysis",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "final_verdict": final_verdict,
            "confidence": confidence,
            "scores": scores,
            "detected_signs": reasons,
            "metadata_analysis": {},
            "frequency_and_noise_analysis": {},
            "forensic_artifacts": forensic_artifacts,
            "selected_models": selected_models or [f"{media_type}_heuristic_mvp"],
            "model_results": model_results or [
                {
                    "model_id": f"{media_type}_heuristic_mvp",
                    "name": f"Xabarnavis {media_type.title()} MVP Analyzer",
                    "status": "ready",
                    "verdict": final_verdict,
                    "confidence": confidence,
                    "details": {"stored_path": str(stored_path), "adapter_status": "placeholder"},
                }
            ],
            "legal_report": {
                "title": f"Xabarnavis AI {media_type.title()} Forensic Legal Report",
                "evidence_hash_algorithm": "SHA-256",
                "chain_of_custody_note": "The uploaded evidence was copied into local storage and analyzed without modifying the original upload bytes.",
                "intended_use": "Technical forensic screening report for investigator review. It is not a standalone court verdict.",
                "recommended_human_review": True,
            },
            "model_version": MODEL_VERSION,
            "limitations": [
                "This MVP uses heuristic signals until trained PyTorch/ONNX detectors are connected.",
                "The result is a screening signal, not a definitive legal conclusion.",
                "Use cautious language such as likely, suspicious, or inconclusive.",
            ],
        }
        if extra_payload:
            payload.update(extra_payload)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        write_docx_report(report_path, payload)
        self.store.save_analysis(
            case_id=case_id,
            scores={
                "real_score": scores.get("human_written_score") or scores.get("real_voice_score") or scores.get("video_real_score") or 0.0,
                "ai_score": scores.get("ai_text_score") or scores.get("ai_voice_score") or scores.get("video_fake_score") or 0.0,
                "manipulated_score": scores.get("claim_risk_score") or scores.get("speaker_spoof_score") or scores.get("face_manipulation_score") or 0.0,
            },
            final_verdict=final_verdict,
            confidence=confidence,
            reasons=reasons,
            report_path=report_path,
            model_version=MODEL_VERSION,
            model_results=model_results,
        )
        return MediaAnalysisResponse(
            case_id=case_id,
            media_type=media_type,
            original_filename=original_filename,
            file_hash=file_hash,
            final_verdict=final_verdict,
            confidence=confidence,
            scores=scores,
            detected_signs=reasons,
            report_path=str(report_path),
            report_docx_path=str(report_path.with_suffix(".docx")),
            model_version=MODEL_VERSION,
        )


def _verdict(media_type: str, scores: dict[str, float]) -> str:
    if media_type == "text":
        if scores.get("ai_text_score", 0) >= 0.62:
            return "Likely AI-generated text"
        if scores.get("fake_news_score", 0) >= 0.55:
            return "Suspicious claim risk"
        return "Likely human-written text"
    if media_type == "audio":
        if scores.get("ai_voice_score", 0) >= 0.62:
            return "Likely synthetic or spoofed voice"
        return "Likely real voice"
    if media_type == "video":
        fake_score = scores.get("video_fake_score", 0)
        if fake_score <= 0.35:
            return "Likely Real"
        if fake_score <= 0.60:
            return "Suspicious"
        if fake_score <= 0.80:
            return "Likely AI / Deepfake"
        return "Strong Deepfake Signal"
    return "Inconclusive"


def _bounded_score(value: float) -> float:
    return _clamp(value)


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 4)





