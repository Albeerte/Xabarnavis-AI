from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from app.services.spectra_aasist3_adapter import run_spectra_aasist3, spectra_aasist3_status


def main() -> int:
    print(f"Spectra-AASIST3 status: {spectra_aasist3_status()}")
    if len(sys.argv) < 2:
        print("Usage: py scripts\\test_spectra_audio_model.py path\\to\\audio.wav")
        return 0
    result = run_spectra_aasist3(Path(sys.argv[1]))
    print(result)
    return 0 if result.status == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())





