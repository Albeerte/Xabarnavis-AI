from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
JABBERJAY_DIR = ROOT / "artifacts" / "models" / "external" / "audio" / "jabberjay"
if not JABBERJAY_DIR.exists():
    JABBERJAY_DIR = ROOT / "artifacts" / "models" / "external" / "jabberjay"
JABBERJAY_SRC = JABBERJAY_DIR / "src"
SAMPLE_AUDIO = JABBERJAY_DIR / "res" / "spoof" / "spoof.flac"


SELF_CONTAINED_MODELS = [
    ("Spectra0", None, None),
    ("SpectraAASIST", None, None),
    ("SpectraAASIST3", None, None),
    ("Wav2Vec2", None, None),
    ("HuBERT", None, None),
    ("WavLM", None, None),
    ("RawNet2", None, None),
    ("Classical", None, None),
]

AST_MODELS = [
    ("AST", "ASVspoof2019", None),
    ("AST", "ASVspoof5", None),
    ("AST", "VoxCelebSpoof", None),
]

VIT_MODELS = [
    ("VIT", dataset, visualisation)
    for dataset in ("ASVspoof2019", "ASVspoof5", "VoxCelebSpoof")
    for visualisation in ("ConstantQ", "MelSpectrogram", "MFCC")
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Warm/download Jabberjay models into local Hugging Face cache.")
    parser.add_argument("--all", action="store_true", help="Download/warm all supported Jabberjay model combinations.")
    parser.add_argument("--vit-all", action="store_true", help="Warm all VIT dataset/visualisation combinations.")
    parser.add_argument("--ast-all", action="store_true", help="Warm all AST dataset combinations.")
    parser.add_argument("--self-contained", action="store_true", help="Warm Spectra/Wav2Vec2/HuBERT/WavLM/RawNet2/Classical.")
    parser.add_argument("--model", default="VIT", help="Single model for quick warmup. Default: VIT.")
    parser.add_argument("--dataset", default="VoxCelebSpoof", help="Dataset for VIT/AST quick warmup.")
    parser.add_argument("--visualisation", default="ConstantQ", help="Visualisation for VIT quick warmup.")
    parser.add_argument("--audio", default=str(SAMPLE_AUDIO), help="Audio file used to trigger downloads.")
    args = parser.parse_args()

    if not JABBERJAY_SRC.exists():
        raise SystemExit(f"Jabberjay source not found: {JABBERJAY_SRC}")
    sys.path.insert(0, str(JABBERJAY_SRC))

    try:
        from Jabberjay import Jabberjay
    except Exception as exc:
        raise SystemExit(
            "Jabberjay dependencies are not installed. Run:\n"
            "  python -m pip install -e artifacts\models\external\\audio\\jabberjay\n\n"
            f"Import error: {exc}"
        ) from exc

    audio_path = Path(args.audio)
    if not audio_path.is_file():
        raise SystemExit(f"Audio warmup file not found: {audio_path}")

    jobs: list[tuple[str, str | None, str | None]]
    if args.all:
        jobs = [*VIT_MODELS, *AST_MODELS, *SELF_CONTAINED_MODELS]
    elif args.vit_all:
        jobs = VIT_MODELS
    elif args.ast_all:
        jobs = AST_MODELS
    elif args.self_contained:
        jobs = SELF_CONTAINED_MODELS
    else:
        jobs = [(args.model, args.dataset, args.visualisation)]

    detector = Jabberjay()
    audio = detector.load(audio_path)
    failures = []
    for model, dataset, visualisation in jobs:
        print(f"\n== Warming {model} dataset={dataset or '-'} visualisation={visualisation or '-'} ==")
        try:
            result = detector.detect(audio, model=model, dataset=dataset, visualisation=visualisation)
            print(f"OK: {result}")
        except Exception as exc:
            print(f"FAILED: {exc}")
            failures.append((model, dataset, visualisation, str(exc)))

    print("\nDone.")
    if failures:
        print("Some models failed:")
        for model, dataset, visualisation, error in failures:
            print(f"- {model} dataset={dataset or '-'} visualisation={visualisation or '-'}: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()





