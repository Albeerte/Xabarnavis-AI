# Xabarnavis Model Research

Research date: 2026-06-30

This file tracks the first MVP model candidates for Xabarnavis AI. The goal is not to merge external repositories into the main codebase, but to connect them through isolated adapters under `modules/<media_type>/...` or `app/services/...`.

Recommended implementation order:

1. Photo
2. Audio
3. Text
4. Video
5. Central fusion and report

## 1. GenImage

Repository: https://github.com/GenImage-Dataset/GenImage

Module: Photo Analysis

Task: AI-generated image detection dataset and benchmark.

Input: Real and AI-generated image folders, organized by generator/source.

Output: Training/evaluation data for real-vs-AI image classifiers.

Use in Xabarnavis: Use as the main large-scale dataset source for improving Xabarnavis 0.x photo AI detectors. It is useful for training and benchmarking, not a direct inference adapter.

Notes:

- GenImage is described as a million-scale benchmark for AI-generated image detection.
- It contains real/fake pairs and uses ImageNet-like class coverage.
- It includes images from advanced generators such as Midjourney, Stable Diffusion, ADM, GLIDE, Wukong, VQDM, and BigGAN.
- Xabarnavis should use it to build robust train/test splits across generator families.
- Storage is large, so downloads should be scripted with resume support and dataset manifests.

Adapter idea:

```text
scripts/download_genimage.py
scripts/build_genimage_manifest.py
modules/photo/genimage_dataset.py
```

## 2. AIDE

Repository: https://github.com/shilinyan99/AIDE

Module: Photo Analysis

Task: AI-generated image detection with hybrid visual artifact and noise-pattern features.

Input: Image dataset or single image after adapter wrapping.

Output: AI-generated probability and model-level confidence.

Use in Xabarnavis: Create `modules/photo/aide_adapter.py` as a detector that can return `ai_generated_score`, `real_score`, `confidence`, and evidence such as `visual_artifacts` and `noise_pattern`.

Notes:

- AIDE is an ICLR 2025 AI-generated image detector.
- The method uses multiple experts for visual artifacts and noise patterns.
- It provides training and evaluation scripts plus checkpoint links.
- The repository references CNNSpot, AIGCDetectBenchmark, GenImage, and DNF.
- The Chameleon dataset license is academic-only, so usage limits must be documented in reports.

Adapter idea:

```json
{
  "module": "photo",
  "model": "AIDE",
  "score": 0.0,
  "label": "REAL_OR_AI_GENERATED",
  "confidence": "LOW_MEDIUM_HIGH",
  "evidence": ["visual_artifacts", "noise_pattern"]
}
```

## 3. PhotoHolmes

Repository: https://github.com/photoholmes/photoholmes

Module: Photo Analysis

Task: Digital image forgery detection, benchmarking, and single-image forensic method execution.

Input: Image path.

Output: Method-specific forgery score, mask/heatmap if the selected method supports localization, and benchmark metrics.

Use in Xabarnavis: Create `modules/photo/photoholmes_adapter.py` to run selected forgery/localization methods and normalize output into `edited_score`, `manipulation_heatmap`, and `evidence`.

Notes:

- PhotoHolmes is a Python library for digital image forgery detection.
- It supports benchmarking methods, datasets, and metrics through a unified interface.
- It has a CLI for evaluating single images.
- It can download some method weights through CLI tooling.
- Some included methods have more restrictive licenses, so adapter metadata must store license notes.

Adapter idea:

```text
modules/photo/photoholmes_adapter.py
storage/artifacts/heatmaps/<case_id>_photoholmes.png
```

## 4. DeepfakeBench

Repository: https://github.com/SCLBD/DeepfakeBench

Module: Video Analysis

Task: Deepfake image/video benchmark and detector framework.

Input: Preprocessed face frames, frame folders, LMDB datasets, or video-derived frames through a Xabarnavis frame extractor.

Output: Frame-level fake score, video-level fake score, AUC/ACC/EER metrics during evaluation.

Use in Xabarnavis: Create `modules/video/deepfakebench_adapter.py` for frame-level inference and `modules/video/frame_extractor.py` for sampling frames before detection.

Notes:

- DeepfakeBench is a comprehensive benchmark for deepfake detection.
- It supports many detectors across image, spatial, frequency, and video categories.
- It includes training, data loading, preprocessing, and evaluation workflows.
- Metrics include frame-level/video-level AUC, ACC, EER, PR, and AP.
- It is powerful but heavy, so it should be integrated after the photo/audio/text MVP is stable.

Adapter idea:

```json
{
  "module": "video",
  "model": "DeepfakeBench",
  "frame_scores": [],
  "video_fake_score": 0.0,
  "evidence": ["face_region", "temporal_artifacts"]
}
```

## 5. HongguLiu/Deepfake-Detection

Repository: https://github.com/HongguLiu/Deepfake-Detection

Module: Video Analysis

Task: FaceForensics++-based deepfake detection using XceptionNet and MesoNet.

Input: Video path or extracted face images.

Output: Image/video fake probability from XceptionNet or MesoNet.

Use in Xabarnavis: Create `modules/video/xception_mesonet_adapter.py` as a simpler baseline before full DeepfakeBench integration.

Notes:

- The implementation is PyTorch-based and references FaceForensics++.
- It supports video testing through `detect_from_video.py`.
- It supports image testing through `test_CNN.py`.
- The README recommends using face regions as input instead of full frames.
- Provided implementation is academic-purpose oriented, so production/legal use must be reviewed.

Adapter idea:

```text
modules/video/face_cropper.py
modules/video/xception_mesonet_adapter.py
```

## 6. AASIST

Repository: https://github.com/clovaai/aasist

Module: Audio Analysis

Task: Audio anti-spoofing and speech deepfake detection using spectro-temporal graph attention networks.

Input: Mono WAV audio, preferably prepared according to ASVspoof-style configuration.

Output: Spoof/bonafide score, EER metrics during evaluation, and confidence after adapter normalization.

Use in Xabarnavis: Create `modules/audio/aasist_adapter.py` and a preprocessing function to convert uploaded audio or extracted video audio to mono 16kHz WAV.

Notes:

- AASIST provides training and evaluation for audio anti-spoofing.
- It uses ASVspoof 2019 logical access data in the original workflow.
- Pretrained AASIST and AASIST-L models are provided.
- GPU training requirements are significant, but inference can be wrapped separately.
- It is a strong first audio detector candidate for Xabarnavis.

Adapter idea:

```json
{
  "module": "audio",
  "model": "AASIST",
  "real_voice_score": 0.0,
  "ai_voice_score": 0.0,
  "speaker_spoof_score": 0.0
}
```

## 7. SSL Anti-spoofing

Repository: https://github.com/TakHemlata/SSL_Anti-spoofing

Module: Audio Analysis

Task: wav2vec 2.0 based automatic speaker verification spoofing and deepfake detection.

Input: Audio prepared for ASVspoof LA/DF evaluation, typically WAV features through fairseq/wav2vec.

Output: LA/DF spoof score and evaluation metrics such as EER.

Use in Xabarnavis: Create `modules/audio/wav2vec_spoof_adapter.py` as a second audio detector for ensemble comparison with AASIST.

Notes:

- The repository implements wav2vec 2.0 plus data augmentation for spoof/deepfake detection.
- It reports strong ASVspoof 2021 LA and DF results.
- It requires older PyTorch/fairseq versions, so it should run in an isolated environment.
- Pretrained models are linked for LA and DF tracks.
- It is best used after AASIST as an ensemble or validation model.

Adapter idea:

```text
modules/audio/audio_preprocess.py
modules/audio/wav2vec_spoof_adapter.py
```

## 8. BERT Fake News Detector

Repository: https://github.com/AM1N8/BERT-Fake-News-Detector

Module: Text Analysis

Task: Fake-news detection with BERT/DistilBERT, plus evaluation and interpretability tools.

Input: Text article, claim, transcript, or user-provided statement.

Output: Fake probability, real probability, label, confidence, and optional explanation artifacts.

Use in Xabarnavis: Create `modules/text/fake_news_adapter.py` for text claim risk scoring and connect it to transcripts from audio/video modules.

Notes:

- The project supports BERT and DistilBERT architectures.
- It includes preprocessing, training, evaluation, inference, visualization, and tests.
- It supports LIAR and FakeNewsNet style datasets.
- It includes confidence scoring and an API-ready inference interface.
- For Uzbek or multilingual text, this should later be paired with XLM-RoBERTa or a multilingual MGT benchmark.

Adapter idea:

```json
{
  "module": "text",
  "model": "BERT-Fake-News-Detector",
  "human_written_score": 0.0,
  "ai_text_score": null,
  "fake_news_score": 0.0,
  "language": "unknown"
}
```

## MVP Adapter Contract

Every adapter should expose the same Python function shape:

```python
def analyze(input_path: str) -> dict:
    ...
```

For text-only models:

```python
def analyze_text(text: str) -> dict:
    ...
```

Recommended normalized output:

```json
{
  "module": "photo|video|audio|text",
  "model": "model_name",
  "score": 0.0,
  "label": "REAL|AI_GENERATED|MANIPULATED|SUSPICIOUS|INCONCLUSIVE",
  "confidence": "LOW|MEDIUM|HIGH",
  "evidence": [],
  "runtime_ms": 0,
  "raw": {}
}
```

## Next Engineering Tasks

1. Create `modules/photo`, `modules/video`, `modules/audio`, `modules/text`, and `modules/fusion` folders.
2. Add placeholder adapters for AIDE, PhotoHolmes, AASIST, SSL Anti-spoofing, BERT Fake News, and DeepfakeBench.
3. Add a central fusion schema so every module result can be saved in one format.
4. Extend the database with `module_results` for photo/video/audio/text outputs.
5. Keep external repositories under `external_models/<repo_name>` and never mix their source files into core Xabarnavis code.
