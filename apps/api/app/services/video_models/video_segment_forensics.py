from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


@dataclass(frozen=True)
class VideoSegmentForensicsResult:
    status: str
    segments: list[dict[str, Any]]
    artifacts: dict[str, str]
    summary: dict[str, Any]
    error: str | None = None


def analyze_video_segments(video_path: Path, report_dir: Path, case_hint: str, *, max_segments: int = 12) -> VideoSegmentForensicsResult:
    try:
        import cv2
        import numpy as np
    except Exception as exc:
        return VideoSegmentForensicsResult(
            status="unavailable",
            segments=[],
            artifacts={},
            summary={},
            error=f"OpenCV/Numpy import xatosi: {exc}",
        )

    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        return VideoSegmentForensicsResult(
            status="failed",
            segments=[],
            artifacts={},
            summary={},
            error="Video fayl OpenCV orqali ochilmadi.",
        )

    fps = float(capture.get(cv2.CAP_PROP_FPS) or 0) or 25.0
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration = frame_count / fps if frame_count else 0.0
    if duration <= 0:
        capture.release()
        return VideoSegmentForensicsResult(
            status="failed",
            segments=[],
            artifacts={},
            summary={},
            error="Video davomiyligi aniqlanmadi.",
        )

    segment_count = max(1, min(max_segments, math.ceil(duration / 8)))
    segment_seconds = duration / segment_count
    previous_gray = None
    segments: list[dict[str, Any]] = []
    frames: list[dict[str, Any]] = []

    for index in range(segment_count):
        start = index * segment_seconds
        end = min(duration, (index + 1) * segment_seconds)
        midpoint = (start + end) / 2
        capture.set(cv2.CAP_PROP_POS_MSEC, midpoint * 1000)
        ok, frame = capture.read()
        if not ok or frame is None:
            segments.append(_segment_error(index, start, end, "Kadr o'qilmadi."))
            continue

        resized = cv2.resize(frame, (320, 180), interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        blur_value = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        edge_density = float((cv2.Canny(gray, 80, 160) > 0).mean())
        if previous_gray is None:
            temporal_delta = 0.0
        else:
            temporal_delta = float(np.mean(cv2.absdiff(gray, previous_gray)) / 255.0)
        previous_gray = gray

        compression_risk = _clamp01((edge_density - 0.045) * 5.8)
        blur_risk = _clamp01((75.0 - blur_value) / 100.0)
        temporal_risk = _clamp01(temporal_delta * 2.4)
        color_risk = _color_cast_risk(resized)
        risk = _clamp01(0.34 * temporal_risk + 0.26 * compression_risk + 0.22 * blur_risk + 0.18 * color_risk)
        label = "High suspicion" if risk >= 0.70 else "Review required" if risk >= 0.45 else "Low signal"
        explanation = _explain_segment(risk, temporal_risk, compression_risk, blur_risk, color_risk)
        frame_path = report_dir / f"{case_hint}-segment-{index + 1:02d}.jpg"
        Image.fromarray(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)).save(frame_path, quality=88)
        frames.append({"path": frame_path, "index": index + 1, "risk": risk, "time": midpoint, "label": label})
        segments.append(
            {
                "index": index + 1,
                "start_seconds": round(start, 2),
                "end_seconds": round(end, 2),
                "midpoint_seconds": round(midpoint, 2),
                "risk_score": round(risk, 4),
                "risk_percent": round(risk * 100),
                "label": label,
                "evidence": explanation,
                "signals": {
                    "temporal_inconsistency": round(temporal_risk, 4),
                    "compression_artifact": round(compression_risk, 4),
                    "blur_or_resampling": round(blur_risk, 4),
                    "color_cast_shift": round(color_risk, 4),
                    "laplacian_blur_value": round(blur_value, 3),
                    "edge_density": round(edge_density, 4),
                },
                "frame_path": str(frame_path),
            }
        )
    capture.release()

    report_dir.mkdir(parents=True, exist_ok=True)
    timeline_path = report_dir / f"{case_hint}-video-timeline.png"
    contact_sheet_path = report_dir / f"{case_hint}-video-contact-sheet.png"
    _draw_timeline(timeline_path, segments, duration)
    _draw_contact_sheet(contact_sheet_path, frames)
    high = [item for item in segments if item.get("risk_score", 0) >= 0.70]
    medium = [item for item in segments if 0.45 <= item.get("risk_score", 0) < 0.70]
    top = max(segments, key=lambda item: item.get("risk_score", 0), default=None)
    return VideoSegmentForensicsResult(
        status="ready",
        segments=segments,
        artifacts={
            "video_timeline_path": str(timeline_path),
            "video_contact_sheet_path": str(contact_sheet_path),
        },
        summary={
            "duration_seconds": round(duration, 2),
            "fps": round(fps, 3),
            "segment_count": len(segments),
            "high_suspicion_segments": len(high),
            "review_required_segments": len(medium),
            "top_suspicious_segment": top,
        },
    )


def _segment_error(index: int, start: float, end: float, message: str) -> dict[str, Any]:
    return {
        "index": index + 1,
        "start_seconds": round(start, 2),
        "end_seconds": round(end, 2),
        "risk_score": None,
        "risk_percent": None,
        "label": "Not available",
        "evidence": message,
        "signals": {},
    }


def _color_cast_risk(frame: Any) -> float:
    import numpy as np

    channel_means = np.mean(frame, axis=(0, 1))
    spread = float(np.max(channel_means) - np.min(channel_means))
    return _clamp01(spread / 85.0)


def _explain_segment(risk: float, temporal: float, compression: float, blur: float, color: float) -> str:
    signals = [
        ("temporal uzilish", temporal),
        ("siqish artefakti", compression),
        ("blur/resampling", blur),
        ("rang siljishi", color),
    ]
    strongest = sorted(signals, key=lambda item: item[1], reverse=True)[:2]
    if risk >= 0.70:
        prefix = "Kuchli shubha: "
    elif risk >= 0.45:
        prefix = "Qo'shimcha tekshiruv kerak: "
    else:
        prefix = "Past signal: "
    return prefix + ", ".join(f"{name} {round(value * 100)}%" for name, value in strongest)


def _draw_timeline(path: Path, segments: list[dict[str, Any]], duration: float) -> None:
    width = 1200
    height = 260
    image = Image.new("RGB", (width, height), "#08111f")
    draw = ImageDraw.Draw(image)
    font = _font(24)
    small = _font(18)
    draw.text((32, 24), "Video segment forensic timeline", fill="#ffffff", font=font)
    draw.text((32, 58), f"Duration: {duration:.2f}s | segments: {len(segments)}", fill="#9fb3c8", font=small)
    left, top, bar_w, bar_h = 40, 120, width - 80, 46
    count = max(len(segments), 1)
    for item in segments:
        idx = int(item.get("index") or 1) - 1
        x0 = left + int(bar_w * idx / count)
        x1 = left + int(bar_w * (idx + 1) / count) - 3
        risk = item.get("risk_score")
        color = _risk_color(float(risk or 0))
        draw.rounded_rectangle((x0, top, x1, top + bar_h), radius=10, fill=color)
        draw.text((x0 + 6, top + 12), str(item.get("index")), fill="#06111f", font=small)
        draw.text((x0, top + 58), f"{item.get('start_seconds')}s", fill="#9fb3c8", font=_font(14))
    draw.text((40, 210), "Green: low signal   Yellow: review   Red: high suspicion", fill="#d5e3f2", font=small)
    image.save(path)


def _draw_contact_sheet(path: Path, frames: list[dict[str, Any]]) -> None:
    if not frames:
        Image.new("RGB", (900, 220), "#08111f").save(path)
        return
    thumb_w, thumb_h = 240, 135
    cols = 3
    rows = math.ceil(len(frames) / cols)
    pad = 24
    header = 70
    image = Image.new("RGB", (cols * thumb_w + (cols + 1) * pad, rows * (thumb_h + 62) + header), "#08111f")
    draw = ImageDraw.Draw(image)
    draw.text((pad, 22), "Key frame evidence sheet", fill="#ffffff", font=_font(24))
    for i, item in enumerate(frames):
        row = i // cols
        col = i % cols
        x = pad + col * (thumb_w + pad)
        y = header + row * (thumb_h + 62)
        try:
            thumb = Image.open(item["path"]).resize((thumb_w, thumb_h))
            image.paste(thumb, (x, y))
        except Exception:
            draw.rectangle((x, y, x + thumb_w, y + thumb_h), fill="#162236")
        risk = float(item.get("risk") or 0)
        draw.rectangle((x, y, x + thumb_w, y + 8), fill=_risk_color(risk))
        draw.text((x, y + thumb_h + 10), f"S{item.get('index')} | {item.get('time'):.1f}s | risk {round(risk * 100)}%", fill="#d5e3f2", font=_font(17))
        draw.text((x, y + thumb_h + 34), str(item.get("label")), fill="#9fb3c8", font=_font(15))
    image.save(path)


def _risk_color(risk: float) -> str:
    if risk >= 0.70:
        return "#ef4444"
    if risk >= 0.45:
        return "#f59e0b"
    return "#22c55e"


def _font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))





