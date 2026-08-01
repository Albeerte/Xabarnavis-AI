from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from app.services.genconvit_adapter import run_genconvit
from app.services.naman_video_adapter import run_naman_video
from app.services.spectra_aasist3_adapter import run_spectra_aasist3
from app.services.video_models.video_audio_extractor import extract_audio_track, extract_video_metadata
from app.services.video_models.video_ensemble import combine_video_scores


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: py scripts\\test_video_full_pipeline.py "path\\to\\test_video.mp4"')
        return 2
    video_path = Path(sys.argv[1])
    if not video_path.is_file():
        print(f"Video topilmadi: {video_path}")
        return 2
    print("Technical metadata:")
    metadata = extract_video_metadata(video_path)
    print(metadata)
    genconvit = run_genconvit(video_path)
    print("GenConViT:", genconvit)
    naman = run_naman_video(video_path)
    print("Naman712:", naman)
    audio = extract_audio_track(video_path, ROOT / "storage" / "temp_audio", video_path.stem)
    print("Audio extraction:", audio)
    spectra_score = None
    if audio.audio_extracted and audio.wav_path:
        spectra = run_spectra_aasist3(audio.wav_path)
        print("Spectra-AASIST3:", spectra)
        spectra_score = spectra.ai_score if spectra.status == "ready" else None
    ensemble = combine_video_scores(
        genconvit_score=genconvit.fake_score if genconvit.status == "ready" else None,
        naman712_score=naman.fake_score if naman.status == "ready" else None,
        spectra_audio_score=spectra_score,
        metadata_risk_score=0.35,
    )
    print("Final ensemble:", ensemble)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())





