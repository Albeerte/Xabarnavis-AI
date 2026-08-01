from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class VideoAudioExtractionResult:
    status: str
    audio_extracted: bool
    wav_path: Path | None
    sample_rate_hz: int | None
    channels: int | None
    details: dict[str, Any]
    error: str | None = None


def extract_video_metadata(video_path: Path) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "file_size_bytes": video_path.stat().st_size if video_path.is_file() else None,
        "duration_seconds": None,
        "fps": None,
        "resolution": None,
        "codec": None,
        "bitrate": None,
        "has_audio": None,
    }
    ffprobe = shutil.which("ffprobe")
    if ffprobe:
        try:
            completed = subprocess.run(
                [
                    ffprobe,
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration,bit_rate:stream=codec_type,codec_name,width,height,r_frame_rate",
                    "-of",
                    "json",
                    str(video_path),
                ],
                capture_output=True,
                text=True,
                timeout=45,
                check=False,
            )
            if completed.returncode == 0 and completed.stdout:
                payload = json.loads(completed.stdout)
                fmt = payload.get("format") or {}
                streams = payload.get("streams") or []
                video_stream = next((item for item in streams if item.get("codec_type") == "video"), {})
                audio_stream = next((item for item in streams if item.get("codec_type") == "audio"), None)
                metadata.update(
                    {
                        "duration_seconds": _float_or_none(fmt.get("duration")),
                        "fps": _parse_fps(video_stream.get("r_frame_rate")),
                        "resolution": _resolution(video_stream.get("width"), video_stream.get("height")),
                        "codec": video_stream.get("codec_name"),
                        "bitrate": _int_or_none(fmt.get("bit_rate")),
                        "has_audio": audio_stream is not None,
                    }
                )
                return metadata
        except Exception as exc:
            metadata["ffprobe_error"] = str(exc)

    try:
        import cv2

        capture = cv2.VideoCapture(str(video_path))
        if capture.isOpened():
            fps = float(capture.get(cv2.CAP_PROP_FPS) or 0.0)
            frame_count = float(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0.0)
            width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
            height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
            metadata.update(
                {
                    "duration_seconds": round(frame_count / fps, 3) if fps > 0 else None,
                    "fps": round(fps, 3) if fps > 0 else None,
                    "resolution": _resolution(width, height),
                    "has_audio": None,
                }
            )
        capture.release()
    except Exception as exc:
        metadata["opencv_metadata_error"] = str(exc)
    return metadata


def extract_audio_track(video_path: Path, output_dir: Path, case_hint: str) -> VideoAudioExtractionResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    wav_path = output_dir / f"{case_hint}-audio-16khz-mono.wav"
    metadata = extract_video_metadata(video_path)
    ffmpeg = _ffmpeg_path()
    if not ffmpeg:
        return VideoAudioExtractionResult(
            status="missing ffmpeg",
            audio_extracted=False,
            wav_path=None,
            sample_rate_hz=None,
            channels=None,
            details={**metadata, "install_command": "winget install Gyan.FFmpeg"},
            error="ffmpeg topilmadi. Video audio trackini ajratish uchun ffmpeg kerak.",
        )
    try:
        completed = subprocess.run(
            [
                ffmpeg,
                "-y",
                "-i",
                str(video_path),
                "-vn",
                "-ac",
                "1",
                "-ar",
                "16000",
                "-f",
                "wav",
                str(wav_path),
            ],
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
    except Exception as exc:
        return VideoAudioExtractionResult(
            status="failed",
            audio_extracted=False,
            wav_path=None,
            sample_rate_hz=None,
            channels=None,
            details=metadata,
            error=str(exc),
        )
    if completed.returncode != 0 or not wav_path.is_file() or wav_path.stat().st_size == 0:
        return VideoAudioExtractionResult(
            status="no audio" if metadata.get("has_audio") is False else "failed",
            audio_extracted=False,
            wav_path=None,
            sample_rate_hz=None,
            channels=None,
            details={**metadata, "ffmpeg_stderr": completed.stderr[-2000:]},
            error=completed.stderr[-600:] or "Audio track ajratilmadi.",
        )
    return VideoAudioExtractionResult(
        status="ready",
        audio_extracted=True,
        wav_path=wav_path,
        sample_rate_hz=16000,
        channels=1,
        details={**metadata, "audio_wav_path": str(wav_path)},
    )


def _ffmpeg_path() -> str | None:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return ffmpeg
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def _parse_fps(raw: Any) -> float | None:
    if not raw:
        return None
    text = str(raw)
    try:
        if "/" in text:
            left, right = text.split("/", 1)
            denominator = float(right)
            return round(float(left) / denominator, 3) if denominator else None
        return round(float(text), 3)
    except Exception:
        return None


def _resolution(width: Any, height: Any) -> str | None:
    try:
        w = int(width or 0)
        h = int(height or 0)
    except Exception:
        return None
    return f"{w}x{h}" if w and h else None


def _float_or_none(value: Any) -> float | None:
    try:
        return round(float(value), 3)
    except Exception:
        return None


def _int_or_none(value: Any) -> int | None:
    try:
        return int(float(value))
    except Exception:
        return None





