from __future__ import annotations

from pathlib import Path
import shutil

from huggingface_hub import hf_hub_download


ROOT = Path(__file__).resolve().parents[2]
MODEL_ID = "Deressa/GenConViT"
TARGET = ROOT / "artifacts" / "models" / "external" / "video" / "genconvit" / "weight"
FILES = ["genconvit_ed_inference.pth", "genconvit_vae_inference.pth"]


def main() -> None:
    TARGET.mkdir(parents=True, exist_ok=True)
    for filename in FILES:
        print(f"Downloading {MODEL_ID}/{filename} -> {TARGET}")
        downloaded = hf_hub_download(repo_id=MODEL_ID, filename=filename)
        target = TARGET / filename
        if target.exists() and target.stat().st_size == Path(downloaded).stat().st_size:
            print(f"Already ready: {target}")
            continue
        shutil.copyfile(downloaded, target)
        print(f"Saved: {target}")
    print("Xabarnavis Video 0.1 GenConViT weights are ready.")


if __name__ == "__main__":
    main()





