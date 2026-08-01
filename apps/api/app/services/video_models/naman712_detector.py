from __future__ import annotations

from pathlib import Path

from app.services.naman_video_adapter import NamanVideoResult, run_naman_video


def run_naman712_detector(video_path: Path) -> NamanVideoResult:
    return run_naman_video(video_path)






