from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LOCAL_MODEL_DIR = ROOT / "artifacts" / "models" / "external" / "audio" / "deepfake_voice_detection_public" / "model"
DEFAULT_MODEL_ID = "garystafford/wav2vec2-deepfake-voice-detector"


def main() -> None:
    parser = argparse.ArgumentParser(description="Download Xabarnavis Audio 0.2 Wav2Vec2 model for local inference.")
    parser.add_argument("--repo-id", default=DEFAULT_MODEL_ID, help="Hugging Face model id.")
    parser.add_argument("--local-dir", default=str(LOCAL_MODEL_DIR), help="Local model output directory.")
    args = parser.parse_args()

    try:
        from huggingface_hub import snapshot_download
    except Exception as exc:
        raise SystemExit(
            "huggingface_hub is required. Install dependencies first:\n"
            "  python -m pip install -r artifacts\models\external\\audio\\deepfake_voice_detection_public\\code\\requirements.txt\n\n"
            f"Import error: {exc}"
        ) from exc

    local_dir = Path(args.local_dir)
    local_dir.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {args.repo_id} -> {local_dir}")
    snapshot_download(
        repo_id=args.repo_id,
        local_dir=str(local_dir),
        local_dir_use_symlinks=False,
    )
    print("Done. Xabarnavis Audio 0.2 can now run from local model files.")


if __name__ == "__main__":
    main()





