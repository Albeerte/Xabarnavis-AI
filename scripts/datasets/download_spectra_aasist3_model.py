from __future__ import annotations

from pathlib import Path

from huggingface_hub import hf_hub_download


ROOT = Path(__file__).resolve().parents[2]
MODEL_ID = "lab260/Spectra-AASIST3"
TARGET = ROOT / "artifacts" / "models" / "hf" / "spectra_aasist3_audio"
FILES = [
    "config.json",
    "model.py",
    "model.safetensors",
    "README.md",
]


def main() -> int:
    TARGET.mkdir(parents=True, exist_ok=True)
    downloaded: list[str] = []
    missing: list[str] = []
    for filename in FILES:
        try:
            hf_hub_download(
                repo_id=MODEL_ID,
                filename=filename,
                local_dir=str(TARGET),
                local_dir_use_symlinks=False,
            )
            downloaded.append(filename)
        except Exception as exc:
            missing.append(f"{filename}: {exc}")

    print(f"Spectra-AASIST3 local path: {TARGET}")
    for item in downloaded:
        print(f"  OK {item}")
    if missing:
        print("Missing / failed files:")
        for item in missing:
            print(f"  - {item}")
        print("Troubleshooting: internet ulanishi va huggingface_hub versiyasini tekshiring.")
        return 1
    print("Spectra-AASIST3: downloaded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())





