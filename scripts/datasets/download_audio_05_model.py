from __future__ import annotations

from pathlib import Path

from huggingface_hub import snapshot_download


ROOT = Path(__file__).resolve().parents[2]
MODEL_ID = "Hemgg/Deepfake-audio-detection"
TARGET = ROOT / "artifacts" / "models" / "external" / "audio" / "xabarnavis_audio_0_5_hemgg_deepfake_audio" / "model"


def main() -> None:
    TARGET.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {MODEL_ID} -> {TARGET}")
    snapshot_download(
        repo_id=MODEL_ID,
        local_dir=str(TARGET),
        local_dir_use_symlinks=False,
        ignore_patterns=["*.md", ".gitattributes"],
    )
    print("Xabarnavis Audio 0.5 model is ready.")
    print(f"Local path: {TARGET}")


if __name__ == "__main__":
    main()





