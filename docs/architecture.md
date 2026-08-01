# Xabarnavis AI Architecture

## Goal

Xabarnavis AI should behave like a local forensic platform, not a simple "AI or real" classifier. The target report combines four evidence groups:

1. AI-generated image detector
2. Frequency and noise artifact detector
3. Manipulation localization detector
4. Metadata and provenance analyzer

The MVP implements the API and forensic interfaces now, with heuristic scoring in place of trained models.

## Pipeline

```text
Upload image
  -> SHA256 hash
  -> metadata extraction
  -> frequency/noise signal analysis
  -> ELA and residual heatmap artifact generation
  -> AI detector interface
  -> manipulation detector interface
  -> fusion model
  -> JSON/PDF/DOCX report
```

## Production Model Targets

### Model 1: AI-Generated Classifier

- Input: 384x384 or 512x512 RGB image
- Backbone: CLIP ViT-L/14, CLIP ViT-B/16, ConvNeXt-B, or EfficientNet-B4
- Output: `real_score`, `ai_generated_score`, `generator_family`

### Model 2: Frequency/Noise Detector

- Inputs: FFT spectrum, DCT high-frequency patches, SRM residuals, JPEG blocking map
- Output: `frequency_anomaly_score`

### Model 3: Manipulation Localization

- Backbone: SegFormer-B2, U-Net++, HRNet, or ConvNeXt encoder/decoder
- Inputs: RGB image, ELA image, residual map, JPEG artifact map
- Output: edited region mask, heatmap, `manipulation_score`

### Model 4: Metadata Analyzer

- Checks EXIF presence, camera model, software tag, timestamps, JPEG quantization, thumbnail consistency
- Important rule: missing EXIF is only one weak signal because Telegram, Instagram, screenshots, and many editors remove it.

## Fusion

Use logistic regression first because it is explainable. Later, compare against XGBoost, LightGBM, and a small MLP.

Current MVP fusion fields:

- `real_score`
- `ai_score`
- `manipulated_score`
- `metadata_anomaly_score`
- `frequency_anomaly_score`
- `jpeg_blocking_score`
- `ela_anomaly_score`

The current MVP writes two visual artifacts beside the JSON report:

- `case-{id}-ela.jpg`: error-level-analysis residual preview
- `case-{id}-heatmap.jpg`: colorized residual map for report/demo use

These are heuristic visualization aids, not pixel-accurate manipulation masks. The production manipulation localizer should replace or complement them with a trained segmentation mask.

## Report Language

Avoid absolute claims. Use forensic probability language:

```text
The image is highly likely to be AI-generated.
Confidence: 91.8%.
This conclusion is based on visual, frequency-domain, metadata, and model-based forensic indicators.
```



