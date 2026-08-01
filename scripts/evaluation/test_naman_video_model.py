from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from app.services.naman_video_adapter import naman_video_status, run_naman_video


def main() -> int:
    print(f"Naman712 status: {naman_video_status()}")
    if len(sys.argv) < 2:
        print("Usage: py scripts\\test_naman_video_model.py path\\to\\video.mp4")
        return 0
    result = run_naman_video(Path(sys.argv[1]))
    print(result)
    return 0 if result.status == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())





