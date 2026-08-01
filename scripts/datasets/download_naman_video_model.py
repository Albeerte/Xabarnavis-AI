from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - dependency may be installed later
    load_dotenv = None

from huggingface_hub import hf_hub_download
from huggingface_hub.errors import GatedRepoError, HfHubHTTPError


ROOT = Path(__file__).resolve().parents[2]
MODEL_ID = "Naman712/Deep-fake-detection"
TARGET = ROOT / "artifacts" / "models" / "hf" / "naman712_video"
FILES = [
    "config.json",
    "inference.py",
    "modeling.py",
    "modeling_deepfake.py",
    "processor_deepfake.py",
    "requirements.txt",
    "model_87_acc_20_frames_final_data.pt",
]


def main() -> int:
    if load_dotenv:
        load_dotenv(ROOT / ".env")
    token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN")
    if not token:
        print("Naman712 modeli gated. Avval Hugging Face sahifasida access shartlarini tasdiqlang va HF_TOKEN kiriting.")
        print("PowerShell:")
        print('$env:HF_TOKEN="hf_YOUR_TOKEN_HERE"')
        return 2

    TARGET.mkdir(parents=True, exist_ok=True)
    downloaded: list[str] = []
    missing: list[str] = []
    try:
        for filename in FILES:
            try:
                hf_hub_download(
                    repo_id=MODEL_ID,
                    filename=filename,
                    local_dir=str(TARGET),
                    local_dir_use_symlinks=False,
                    token=token,
                )
                downloaded.append(filename)
            except GatedRepoError:
                raise
            except HfHubHTTPError as exc:
                if getattr(exc.response, "status_code", None) in {401, 403}:
                    raise GatedRepoError(str(exc)) from exc
                missing.append(filename)
            except Exception as exc:
                missing.append(f"{filename}: {exc}")
    except GatedRepoError:
        print("Naman712 modeli gated. Avval Hugging Face sahifasida access shartlarini tasdiqlang va HF_TOKEN kiriting.")
        print("Model sahifasi: https://huggingface.co/Naman712/Deep-fake-detection")
        return 3

    print(f"Naman712 local path: {TARGET}")
    print(f"Downloaded: {len(downloaded)} file(s)")
    for item in downloaded:
        print(f"  OK {item}")
    if missing:
        print("Missing / failed files:")
        for item in missing:
            print(f"  - {item}")
        print("Troubleshooting: token to'g'ri ekanini, access accept qilinganini va internet ishlayotganini tekshiring.")
        return 1
    print("Naman712: downloaded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())





