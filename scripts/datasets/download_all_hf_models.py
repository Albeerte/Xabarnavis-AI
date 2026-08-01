from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _run(script: str) -> str:
    completed = subprocess.run([sys.executable, str(ROOT / "scripts" / "datasets" / script)], cwd=ROOT, text=True)
    if completed.returncode == 0:
        return "downloaded"
    if script == "download_naman_video_model.py" and completed.returncode in {2, 3}:
        return "gated"
    return "failed"


def main() -> int:
    statuses = {
        "Naman712": _run("download_naman_video_model.py"),
        "Spectra-AASIST3": _run("download_spectra_aasist3_model.py"),
    }
    print("\nHF model download status:")
    for name, status in statuses.items():
        print(f"  {name}: {status}")
    return 0 if all(status == "downloaded" for status in statuses.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())





