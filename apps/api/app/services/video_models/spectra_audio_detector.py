from __future__ import annotations

from pathlib import Path

from app.services.spectra_aasist3_adapter import SpectraAASIST3Result, run_spectra_aasist3


def run_spectra_audio_detector(audio_path: Path) -> SpectraAASIST3Result:
    return run_spectra_aasist3(audio_path)





