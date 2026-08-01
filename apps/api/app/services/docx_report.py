from __future__ import annotations

import html
import json
import zipfile
from pathlib import Path
from typing import Any

from PIL import Image


EMU_PER_INCH = 914400
MAX_IMAGE_WIDTH_EMU = int(6.2 * EMU_PER_INCH)


def write_docx_report(report_path: Path, payload: dict[str, Any]) -> Path:
    docx_path = report_path.with_suffix(".docx")
    media_items = _collect_media(payload)
    document_xml = _build_document_xml(payload, media_items)

    with zipfile.ZipFile(docx_path, "w", zipfile.ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", _content_types_xml(media_items))
        docx.writestr("_rels/.rels", _root_rels_xml())
        docx.writestr("word/_rels/document.xml.rels", _document_rels_xml(media_items))
        docx.writestr("word/document.xml", document_xml)
        docx.writestr("word/styles.xml", _styles_xml())
        for item in media_items:
            docx.write(item["path"], f"word/media/{item['name']}")
    return docx_path


def _collect_media(payload: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = [
        ("Original evidence image", payload.get("evidence_image_path")),
        ("ELA artifact", payload.get("forensic_artifacts", {}).get("ela_image_path")),
        ("Forensic heatmap", payload.get("forensic_artifacts", {}).get("heatmap_path")),
        ("Audio forensic waveform", payload.get("forensic_artifacts", {}).get("audio_waveform_path")),
        ("Audio segment timeline", payload.get("forensic_artifacts", {}).get("audio_timeline_path")),
        ("Video segment timeline", payload.get("forensic_artifacts", {}).get("video_timeline_path")),
        ("Video key frame evidence sheet", payload.get("forensic_artifacts", {}).get("video_contact_sheet_path")),
    ]
    media_items: list[dict[str, Any]] = []
    rid = 1
    for label, raw_path in candidates:
        if not raw_path:
            continue
        path = Path(str(raw_path))
        if not path.is_file():
            continue
        ext = path.suffix.lower()
        if ext not in {".jpg", ".jpeg", ".png"}:
            continue
        name = f"image{rid}{'.jpg' if ext == '.jpeg' else ext}"
        width, height = _image_size_emu(path)
        media_items.append(
            {
                "label": label,
                "path": path,
                "name": name,
                "rid": f"rId{rid}",
                "width": width,
                "height": height,
                "content_type": "image/png" if ext == ".png" else "image/jpeg",
            }
        )
        rid += 1
    return media_items


def _image_size_emu(path: Path) -> tuple[int, int]:
    with Image.open(path) as image:
        width_px, height_px = image.size
    width_emu = width_px * 9525
    height_emu = height_px * 9525
    if width_emu > MAX_IMAGE_WIDTH_EMU:
        ratio = MAX_IMAGE_WIDTH_EMU / width_emu
        width_emu = MAX_IMAGE_WIDTH_EMU
        height_emu = int(height_emu * ratio)
    return int(width_emu), int(height_emu)


def _build_document_xml(payload: dict[str, Any], media_items: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    media_type = str(payload.get("media_type") or "image").lower()
    report_label = {
        "image": "Image",
        "audio": "Audio",
        "video": "Video",
        "text": "Text",
    }.get(media_type, media_type.title())
    parts.append(_paragraph(f"Xabarnavis AI {report_label} Forensic Legal Report", style="Title"))
    parts.append(_paragraph(f"Case #{payload.get('case_id', '-')}", style="Subtitle"))
    parts.append(_paragraph("This report is a technical forensic screening document for investigator review. It is not a standalone court verdict."))

    parts.append(_heading("1. Executive Summary", 1))
    summary_rows = [
        ("Final verdict", payload.get("final_verdict")),
        ("Confidence", payload.get("confidence")),
        ("SHA-256", payload.get("sha256")),
        ("Original filename", payload.get("original_filename")),
        ("Media type", report_label),
        ("Created at", payload.get("created_at")),
        ("Model version", payload.get("model_version")),
    ]
    parts.append(_table(summary_rows))

    parts.append(_heading(f"2. {report_label} Evidence Description", 1))
    description = payload.get("image_description") or f"No investigator {report_label.lower()} description was provided in the upload form."
    parts.append(_paragraph(str(description)))

    if media_items:
        parts.append(_heading("3. Visual Evidence and Forensic Artifacts", 1))
        for item in media_items:
            parts.append(_paragraph(str(item["label"]), style="Caption"))
            parts.append(_image_xml(item))

    if media_type == "audio":
        parts.append(_heading("4. Audio Authenticity Scores", 1))
        scores = payload.get("scores", {})
        parts.append(_table([
            ("Real voice score", _score(scores.get("real_voice_score"))),
            ("AI / spoof voice score", _score(scores.get("ai_voice_score"))),
            ("Speaker spoof score", _score(scores.get("speaker_spoof_score"))),
            ("Watermark score", _score(scores.get("watermark_score"))),
        ]))
        parts.append(_paragraph("Audio reports do not use image EXIF, ELA, heatmap, or camera metadata sections. The core evidence is the audio hash, model score, model label, and chain-of-custody record."))
        segments = _audio_segments(payload)
        if segments:
            parts.append(_heading("5. Segment Timeline: Possible AI / Spoof Regions", 1))
            rows = [("Time range", "Label / confidence / AI-spoof score")]
            for item in segments:
                time_range = f"{_time_label(item.get('start_seconds'))} - {_time_label(item.get('end_seconds'))}"
                rows.append(
                    (
                        time_range,
                        f"{item.get('label', 'unknown')} | confidence {_score(item.get('confidence'))} | AI/Spoof {_score(item.get('ai_score'))} | Real {_score(item.get('real_score'))}",
                    )
                )
            parts.append(_table(rows, has_header=True))
    elif media_type == "image":
        parts.append(_heading("4. Camera and Metadata Analysis", 1))
        metadata = payload.get("metadata_analysis", {})
        metadata_rows = [
            ("EXIF present", _yes_no(metadata.get("has_exif"))),
            ("Camera model present", _yes_no(metadata.get("has_camera_model"))),
            ("Camera make", metadata.get("camera_make") or "Not found"),
            ("Camera model", metadata.get("camera_model") or "Not found"),
            ("Captured at", metadata.get("captured_at") or "Not found"),
            ("Software tag", metadata.get("software_tag") or "Not found"),
            ("GPS present", _yes_no(metadata.get("has_gps"))),
            ("GPS coordinates", f"{metadata.get('gps_latitude')}, {metadata.get('gps_longitude')}" if metadata.get("has_gps") else "Not found"),
            ("Estimated JPEG quality", metadata.get("jpeg_quality") if metadata.get("jpeg_quality") is not None else "Not available"),
            ("Metadata anomaly score", _score(metadata.get("anomaly_score"))),
            ("Camera provenance score", _score(metadata.get("camera_provenance_score"))),
            ("Generator software score", _score(metadata.get("generator_software_score"))),
            ("Editor software score", _score(metadata.get("editor_software_score"))),
        ]
        parts.append(_table(metadata_rows))

        parts.append(_heading("5. Signal, ELA, Noise, and Heatmap Scores", 1))
        signals = payload.get("frequency_and_noise_analysis", {})
        signal_rows = [
            ("Frequency anomaly", _score(signals.get("frequency_anomaly_score"))),
            ("Texture uniformity", _score(signals.get("texture_uniformity_score"))),
            ("Noise inconsistency", _score(signals.get("noise_inconsistency_score"))),
            ("Edge inconsistency", _score(signals.get("edge_inconsistency_score"))),
            ("JPEG blocking", _score(signals.get("jpeg_blocking_score"))),
            ("ELA anomaly", _score(signals.get("ela_anomaly_score"))),
        ]
        parts.append(_table(signal_rows))

        reasoning = payload.get("image_reasoning_uz") if isinstance(payload.get("image_reasoning_uz"), dict) else {}
        parts.append(_heading("6. Uzbek Image Reasoning", 1))
        if reasoning:
            parts.append(_paragraph(str(reasoning.get("summary_uz") or "Reasoning summary mavjud emas.")))
            steps = reasoning.get("reasoning_steps_uz") if isinstance(reasoning.get("reasoning_steps_uz"), list) else []
            for item in steps:
                parts.append(_bullet(str(item)))
            cosmos = reasoning.get("cosmos3_nano_reasoner") if isinstance(reasoning.get("cosmos3_nano_reasoner"), dict) else {}
            if cosmos:
                parts.append(_table([
                    ("Cosmos3 Nano Reasoner status", cosmos.get("status") or "Not available"),
                    ("Model", cosmos.get("model") or "nvidia/cosmos3-nano-reasoner"),
                    ("Note", cosmos.get("note_uz") or cosmos.get("error") or "Not available"),
                ]))
                if cosmos.get("reasoning_uz"):
                    parts.append(_paragraph(str(cosmos.get("reasoning_uz"))))
            minicpm = reasoning.get("minicpm_v_2_6_int4") if isinstance(reasoning.get("minicpm_v_2_6_int4"), dict) else {}
            if minicpm:
                parts.append(_heading("6.0.1 MiniCPM-V-2.6 Int4 Reasoning", 2))
                parts.append(_table([
                    ("MiniCPM status", minicpm.get("status") or "Not available"),
                    ("Model", minicpm.get("model") or "openbmb/MiniCPM-V-2_6-int4"),
                    ("Source", minicpm.get("source") or "Not available"),
                    ("Note", minicpm.get("note_uz") or minicpm.get("error") or "Not available"),
                ]))
                minicpm_text = minicpm.get("reasoning_uz") or minicpm.get("fallback_reasoning_uz")
                if minicpm_text:
                    parts.append(_paragraph(str(minicpm_text)))
        else:
            parts.append(_paragraph("O'zbekcha image reasoning bu reportda saqlanmagan."))

        inventory = payload.get("image_dataset_inventory") if isinstance(payload.get("image_dataset_inventory"), dict) else {}
        parts.append(_heading("6.1 Image Dataset Inventory", 1))
        parts.append(_table(_dataset_inventory_rows(inventory)))

        osint = payload.get("osint_analysis") or {}
        if isinstance(osint, dict):
            parts.append(_heading("6.2 OSINT Source Verification", 1))
            evidence = osint.get("evidence") if isinstance(osint.get("evidence"), dict) else {}
            parts.append(_table([
                ("Source repository", osint.get("source_repository") or "https://github.com/rawfilejson/awesome-osint-arsenal"),
                ("Local repository path", osint.get("local_path") or "Not available"),
                ("OSINT status", osint.get("status") or "Not available"),
                ("Evidence filename", evidence.get("filename") or payload.get("original_filename")),
                ("Evidence SHA-256", evidence.get("sha256") or payload.get("sha256")),
                ("Camera model", evidence.get("camera_model") or "Not found"),
                ("Captured at", evidence.get("captured_at") or "Not found"),
            ]))
            rows = [("Area", "Tool / purpose / link")]
            for tool in _osint_tools(osint):
                rows.append(
                    (
                        str(tool.get("area") or "OSINT"),
                        f"{tool.get('name') or 'Tool'} | {tool.get('description') or 'verification'} | {tool.get('url') or 'manual'}",
                    )
                )
            if len(rows) > 1:
                parts.append(_table(rows, has_header=True))
            checklist = osint.get("automated_checks") if isinstance(osint.get("automated_checks"), list) else osint.get("checklist") if isinstance(osint.get("checklist"), list) else []
            if checklist:
                parts.append(_paragraph("Xabarnavis automated OSINT checks:", style="Caption"))
                for item in checklist:
                    parts.append(_bullet(str(item)))
            parts.append(_paragraph(str(osint.get("legal_note") or "OSINT findings must be documented with URL, screenshot, timestamp, and source platform.")))
    elif media_type == "video":
        parts.append(_heading("4. Video Forensic Summary", 1))
        scores = payload.get("scores", {})
        parts.append(_table([
            ("Final verdict", payload.get("final_verdict")),
            ("Confidence", payload.get("confidence")),
            ("Real video score", _score(scores.get("video_real_score"))),
            ("Deepfake / fake video score", _score(scores.get("video_fake_score"))),
            ("Face manipulation score", _score(scores.get("face_manipulation_score"))),
            ("Temporal artifact score", _score(scores.get("temporal_artifact_score"))),
            ("Metadata / compression risk", _score(scores.get("metadata_compression_risk"))),
        ]))
        parts.append(_paragraph("Video reports do not use image EXIF, ELA, heatmap, or camera metadata sections. The core evidence is the video hash, frame/temporal model score, model label, and chain-of-custody record."))
        parts.append(_heading("5. Model Status", 1))
        status_rows = [("Model", "Status / availability / note")]
        for item in payload.get("video_model_status") or []:
            details = item.get("details") or {}
            status_rows.append((
                item.get("name") or "Video model",
                f"{item.get('status')} | available: {_yes_no(item.get('available'))} | {item.get('error') or details.get('model_access') or details.get('architecture') or 'No error'}",
            ))
        if len(status_rows) == 1:
            status_rows.append(("Model status", "No video model status JSON was saved for this report."))
        parts.append(_table(status_rows, has_header=True))

        parts.append(_heading("6. Video Model Results", 1))
        rows = [("Model", "Status / command / note")]
        for result in payload.get("model_results") or []:
            if "audio" in str(result.get("model_id", "")).lower():
                continue
            details = result.get("details") or {}
            commands = " | ".join(
                item
                for item in [
                    details.get("download_command"),
                    details.get("install_command"),
                ]
                if item
            )
            rows.append(
                (
                    result.get("name") or result.get("model_id"),
                    f"{result.get('status')} | {result.get('error') or result.get('verdict') or 'No error'} | {commands or 'No command required'}",
                )
            )
        parts.append(_table(rows, has_header=True))

        segment_forensics = payload.get("video_segment_forensics") or {}
        segments = segment_forensics.get("segments") if isinstance(segment_forensics.get("segments"), list) else []
        summary = segment_forensics.get("summary") if isinstance(segment_forensics.get("summary"), dict) else {}
        parts.append(_heading("7. Segment-by-Segment Visual Forensics", 1))
        parts.append(_table([
            ("Segment analysis status", segment_forensics.get("status") or "Not available"),
            ("Segment count", summary.get("segment_count") if summary.get("segment_count") is not None else len(segments)),
            ("High suspicion segments", summary.get("high_suspicion_segments") if summary.get("high_suspicion_segments") is not None else "Not available"),
            ("Review required segments", summary.get("review_required_segments") if summary.get("review_required_segments") is not None else "Not available"),
            ("Error", segment_forensics.get("error") or "None"),
        ]))
        if segments:
            segment_rows = [("Time range", "Risk / label / evidence")]
            for item in segments:
                risk = item.get("risk_score")
                segment_rows.append(
                    (
                        f"{_time_label(item.get('start_seconds'))} - {_time_label(item.get('end_seconds'))}",
                        f"{_score(risk)} | {item.get('label') or 'unknown'} | {item.get('evidence') or 'No note'}",
                    )
                )
            parts.append(_table(segment_rows, has_header=True))

        audio_forensics = payload.get("audio_deepfake_forensics") or {}
        parts.append(_heading("8. Audio Deepfake Forensics", 1))
        parts.append(_table([
            ("Audio extracted", _yes_no(audio_forensics.get("audio_extracted"))),
            ("Sample rate", f"{audio_forensics.get('sample_rate_hz')} Hz" if audio_forensics.get("sample_rate_hz") else "Not available"),
            ("Channels", audio_forensics.get("channels") or "Not available"),
            ("Spectra-AASIST3 fake score", _score(audio_forensics.get("spectra_fake_score"))),
            ("Spectra-AASIST3 real score", _score(audio_forensics.get("spectra_real_score"))),
            ("Audio verdict", audio_forensics.get("audio_verdict") or "Not available"),
            ("Status", audio_forensics.get("status") or "Not available"),
        ]))

        technical = payload.get("technical_metadata") or {}
        parts.append(_heading("9. Technical Metadata", 1))
        parts.append(_table([
            ("Duration", f"{technical.get('duration_seconds')} sec" if technical.get("duration_seconds") is not None else "Not available"),
            ("FPS", technical.get("fps") if technical.get("fps") is not None else "Not available"),
            ("Resolution", technical.get("resolution") or "Not available"),
            ("Codec", technical.get("codec") or "Not available"),
            ("Bitrate", technical.get("bitrate") if technical.get("bitrate") is not None else "Not available"),
            ("File size", technical.get("file_size_bytes") if technical.get("file_size_bytes") is not None else "Not available"),
            ("Audio stream present", _yes_no(technical.get("has_audio"))),
            ("Created/uploaded time", payload.get("created_at")),
        ]))
    elif media_type == "text":
        parts.append(_heading("4. Text Authenticity Scores", 1))
        scores = payload.get("scores", {})
        parts.append(_table([
            ("Human-written score", _score(scores.get("human_written_score"))),
            ("AI text score", _score(scores.get("ai_text_score"))),
            ("Fake-news / claim risk score", _score(scores.get("fake_news_score"))),
            ("Claim risk score", _score(scores.get("claim_risk_score"))),
        ]))
        parts.append(_paragraph("Text reports do not use image EXIF, ELA, heatmap, or camera metadata sections. The core evidence is the text hash, lexical model score, detected writing signals, and chain-of-custody record."))

    parts.append(_heading("7. Model-by-Model Results", 1))
    model_results = payload.get("model_results") or []
    if model_results:
        rows = [("Model", "Verdict / confidence / primary scores")]
        for result in model_results:
            details = result.get("details") or {}
            score_text = ", ".join(
                item
                for item in [
                    f"real {_percent(result.get('real_score'))}" if result.get("real_score") is not None else "",
                    f"AI {_percent(result.get('ai_score'))}" if result.get("ai_score") is not None else "",
                    f"manipulated {_percent(result.get('manipulated_score'))}" if result.get("manipulated_score") is not None else "",
                    f"LLR {details.get('llr')}" if details.get("llr") is not None else "",
                ]
                if item
            )
            rows.append(
                (
                    result.get("name") or result.get("model_id"),
                    f"{result.get('status')} | {result.get('verdict')} | confidence {result.get('confidence') or 'n/a'} | {score_text}",
                )
            )
        parts.append(_table(rows, has_header=True))
        parts.append(_paragraph("Detailed result from every selected model:", style="Caption"))
        for index, result in enumerate(model_results, start=1):
            details = result.get("details") or {}
            parts.append(_heading(f"7.{index}. {result.get('name') or result.get('model_id')}", 2))
            detail_rows = [
                ("Model ID", result.get("model_id")),
                ("Model name", result.get("name")),
                ("Status", result.get("status")),
                ("Verdict", result.get("verdict")),
                ("Confidence", result.get("confidence") or "Not available"),
                ("Real score", _score(result.get("real_score"))),
                ("AI-generated score", _score(result.get("ai_score"))),
                ("Manipulated score", _score(result.get("manipulated_score"))),
                ("LLR / raw score", details.get("llr") if details.get("llr") is not None else "Not available"),
                ("Upstream model", details.get("upstream_model") or "Not available"),
                ("Device", details.get("device") or "Not available"),
                ("Checkpoint", details.get("checkpoint") or "Not available"),
                ("Decision rule", details.get("rule") or "Not available"),
                ("Error", result.get("error") or "None"),
            ]
            parts.append(_table(detail_rows))
    else:
        parts.append(_paragraph("No external or trained model results were returned for this case."))

    parts.append(_heading("8. Detected Signs", 1))
    for sign in payload.get("detected_signs", []):
        parts.append(_bullet(str(sign)))

    parts.append(_heading("9. Legal and Chain-of-Custody Notes", 1))
    legal = payload.get("legal_report", {})
    legal_rows = [
        ("Evidence hash algorithm", legal.get("evidence_hash_algorithm")),
        ("Chain of custody note", legal.get("chain_of_custody_note")),
        ("Intended use", legal.get("intended_use")),
        ("Recommended human review", _yes_no(legal.get("recommended_human_review"))),
    ]
    parts.append(_table(legal_rows))

    parts.append(_heading("10. Limitations", 1))
    for limitation in payload.get("limitations", []):
        parts.append(_bullet(str(limitation)))

    body = "".join(parts)
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
  <w:body>
    {body}
    <w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1080" w:right="1080" w:bottom="1080" w:left="1080" w:header="720" w:footer="720" w:gutter="0"/></w:sectPr>
  </w:body>
</w:document>"""


def _paragraph(text: str, style: str | None = None) -> str:
    style_xml = f'<w:pStyle w:val="{style}"/>' if style else ""
    return f"<w:p><w:pPr>{style_xml}</w:pPr><w:r><w:t>{_e(text)}</w:t></w:r></w:p>"


def _audio_segments(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for result in payload.get("model_results") or []:
        if result.get("model_id") != "jabberjay":
            continue
        details = result.get("details") or {}
        segments = details.get("segment_analysis") or []
        return [item for item in segments if isinstance(item, dict)]
    return []


def _osint_tools(osint: dict[str, Any]) -> list[dict[str, Any]]:
    groups = osint.get("tools")
    if not isinstance(groups, dict):
        return []
    area_names = {
        "reverse_image": "Reverse image search",
        "metadata": "Metadata / EXIF",
        "forensics": "Forensic verification",
        "geolocation": "Geolocation",
    }
    tools: list[dict[str, Any]] = []
    for area, items in groups.items():
        if not isinstance(items, list):
            continue
        for item in items[:5]:
            if not isinstance(item, dict):
                continue
            copied = dict(item)
            copied["area"] = area_names.get(str(area), str(area))
            tools.append(copied)
    return tools


def _dataset_inventory_rows(inventory: dict[str, Any]) -> list[tuple[Any, Any]]:
    if not inventory:
        return [("Status", "Dataset inventory mavjud emas.")]
    rows: list[tuple[Any, Any]] = [
        ("Status", inventory.get("status") or "unknown"),
        ("Generated at", inventory.get("generated_at") or "Not calculated"),
        ("Note", inventory.get("note_uz") or "Not available"),
        ("Grand total images", inventory.get("grand_total_images") if inventory.get("grand_total_images") is not None else "Not calculated"),
    ]
    datasets = inventory.get("xabarnavis_datasets") if isinstance(inventory.get("xabarnavis_datasets"), dict) else {}
    ready = inventory.get("data/ready/image") if isinstance(inventory.get("data/ready/image"), dict) else {}
    if datasets:
        rows.append(("Training dataset images", datasets.get("total_images")))
        rows.append(("Training images including auxiliary", datasets.get("total_images_including_auxiliary")))
        by_label = datasets.get("by_label") if isinstance(datasets.get("by_label"), dict) else {}
        for label, details in by_label.items():
            if isinstance(details, dict):
                rows.append((f"data/raw/xabarnavis_datasets/{label}", details.get("total_images")))
    if ready:
        rows.append(("Ready dataset images", ready.get("total_images")))
        by_split = ready.get("by_split") if isinstance(ready.get("by_split"), dict) else {}
        for split, details in by_split.items():
            if isinstance(details, dict):
                rows.append((f"ready/{split}", details.get("total_images")))
    return rows


def _time_label(value: Any) -> str:
    try:
        seconds = max(0, int(round(float(value or 0))))
    except (TypeError, ValueError):
        seconds = 0
    return f"{seconds // 60}:{seconds % 60:02d}"


def _heading(text: str, level: int) -> str:
    return _paragraph(text, style=f"Heading{level}")


def _bullet(text: str) -> str:
    return f'<w:p><w:pPr><w:ind w:left="360" w:hanging="180"/></w:pPr><w:r><w:t>- {_e(text)}</w:t></w:r></w:p>'


def _table(rows: list[tuple[Any, Any]], has_header: bool = False) -> str:
    tr_items = []
    for index, (left, right) in enumerate(rows):
        fill = '<w:shd w:fill="EAF2F8"/>' if has_header and index == 0 else ""
        tr_items.append(
            f"<w:tr>{_cell(str(left), fill)}{_cell(str(right), fill)}</w:tr>"
        )
    return (
        '<w:tbl><w:tblPr><w:tblW w:w="9360" w:type="dxa"/>'
        '<w:tblBorders><w:top w:val="single" w:sz="4" w:color="D9E0E5"/>'
        '<w:left w:val="single" w:sz="4" w:color="D9E0E5"/>'
        '<w:bottom w:val="single" w:sz="4" w:color="D9E0E5"/>'
        '<w:right w:val="single" w:sz="4" w:color="D9E0E5"/>'
        '<w:insideH w:val="single" w:sz="4" w:color="D9E0E5"/>'
        '<w:insideV w:val="single" w:sz="4" w:color="D9E0E5"/></w:tblBorders></w:tblPr>'
        '<w:tblGrid><w:gridCol w:w="2800"/><w:gridCol w:w="6560"/></w:tblGrid>'
        + "".join(tr_items)
        + "</w:tbl>"
    )


def _cell(text: str, fill: str = "") -> str:
    return f'<w:tc><w:tcPr><w:tcW w:w="4680" w:type="dxa"/>{fill}<w:tcMar><w:top w:w="120" w:type="dxa"/><w:left w:w="120" w:type="dxa"/><w:bottom w:w="120" w:type="dxa"/><w:right w:w="120" w:type="dxa"/></w:tcMar></w:tcPr><w:p><w:r><w:t>{_e(text)}</w:t></w:r></w:p></w:tc>'


def _image_xml(item: dict[str, Any]) -> str:
    return f"""<w:p><w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{item['width']}" cy="{item['height']}"/><wp:docPr id="{item['rid'][3:]}" name="{_e(item['label'])}"/><a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic><pic:nvPicPr><pic:cNvPr id="0" name="{_e(item['name'])}"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="{item['rid']}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{item['width']}" cy="{item['height']}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>"""


def _content_types_xml(media_items: list[dict[str, Any]]) -> str:
    defaults = {
        "rels": "application/vnd.openxmlformats-package.relationships+xml",
        "xml": "application/xml",
        "jpg": "image/jpeg",
        "png": "image/png",
    }
    default_xml = "".join(f'<Default Extension="{ext}" ContentType="{ctype}"/>' for ext, ctype in defaults.items())
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">{default_xml}<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>"""


def _root_rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>"""


def _document_rels_xml(media_items: list[dict[str, Any]]) -> str:
    rels = ['<Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>']
    for item in media_items:
        rels.append(f'<Relationship Id="{item["rid"]}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{item["name"]}"/>')
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{''.join(rels)}</Relationships>"""


def _styles_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="22"/></w:rPr><w:pPr><w:spacing w:after="120"/></w:pPr></w:style><w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:b/><w:sz w:val="34"/></w:rPr><w:pPr><w:spacing w:after="160"/></w:pPr></w:style><w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:color w:val="66727D"/><w:sz w:val="24"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:b/><w:sz w:val="28"/></w:rPr><w:pPr><w:spacing w:before="280" w:after="120"/></w:pPr></w:style><w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:b/><w:color w:val="0F766E"/><w:sz w:val="24"/></w:rPr><w:pPr><w:spacing w:before="180" w:after="100"/></w:pPr></w:style><w:style w:type="paragraph" w:styleId="Caption"><w:name w:val="Caption"/><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:i/><w:color w:val="66727D"/><w:sz w:val="20"/></w:rPr></w:style></w:styles>"""


def _e(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _score(value: Any) -> str:
    if isinstance(value, int | float):
        return f"{value:.4f} ({value:.1%})"
    return "Not available"


def _percent(value: Any) -> str:
    if isinstance(value, int | float):
        return f"{value:.0%}"
    return "n/a"


def _yes_no(value: Any) -> str:
    if value is True:
        return "Yes"
    if value is False:
        return "No"
    return "Not available"


def load_report(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))






