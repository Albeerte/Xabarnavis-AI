# Xabarnavis Image Dataset and Training Guide

This guide covers dataset acquisition, reproducible manifests, the training method already implemented in Xabarnavis, and the recommended path from a baseline classifier to a production forensic ensemble.

> Do not download every dataset immediately. First train a reproducible baseline on a small, balanced subset, verify unseen-generator performance, then scale.

## 1. Separate the forensic tasks

Train separate models because their labels and outputs are different:

| Model | Input | Output | Recommended method |
|---|---|---|---|
| Global AI detector | Whole image | `real`, `ai_generated` | EfficientNet/ConvNeXt/SigLIP classifier |
| Manipulation classifier | Whole image | authentic, splice, copy-move, removal, inpainting | Multi-class ConvNeXt |
| Manipulation localizer | Image + mask | Pixel probability mask | U-Net/SegFormer, BCE + Dice loss |
| Face forgery model | Aligned face crop | real, swap, reenactment, synthetic | EfficientNet/ViT classifier |
| Fusion/calibration | Model scores + forensic features | Calibrated probabilities | Logistic regression or gradient boosting |

Do not put `ai_generated` and `locally_manipulated` into one binary class. A camera photo edited in Photoshop is not the same training target as a fully generated image.

## 2. Download order

### Tier 1: first working baseline

1. **GenImage** — paired real/AI images across multiple GAN and diffusion generators. The official repository provides the dataset layout, download location, baseline code, and cross-generator evaluation protocol: [GenImage official repository](https://github.com/GenImage-Dataset/GenImage).
2. **CIFAKE** — small baseline/smoke-test dataset: [official CIFAKE repository](https://github.com/jordan-bird/CIFAKE-Real-and-AI-Generated-Synthetic-Images).
3. **Your Uzbekistan camera set** — original phone/camera files from varied devices, scenes, lighting, people, documents, and screenshots. Keep consent and provenance records.

Target for the first run:

- 50,000 real images;
- 50,000 AI-generated images;
- at least four generator families;
- a completely unseen generator family reserved for test.

### Tier 2: generalization and robustness

4. **WildFake** — diverse in-the-wild GAN/diffusion content; use it primarily for external validation: [WildFake paper](https://arxiv.org/abs/2402.11843).
5. **Community Forensics** — use Small before Full because the published collections are very large.
6. **Synthbuster / ForenSynths / ArtiFact** — add generator and compression diversity after the baseline is reproducible.
7. Recent generators produced under your own controlled pipeline. Record generator, version, prompt hash, seed, date, resolution, and any post-processing.

### Tier 3: local manipulation and masks

8. **IMD2020** — real-life manipulated images with annotations: [official IMD2020 page](https://staff.utia.cas.cz/novozada/db/).
9. **CoMoFoD** — copy-move with rotation, scaling, blur, noise, JPEG, and masks: [official CoMoFoD page](https://www.vcl.fer.hr/comofod/examples.html).
10. **DEFACTO** — copy-move, splicing, object removal, and morphing with masks; access requires a request and source-image terms still apply: [official DEFACTO page](https://defactodataset.github.io/).
11. **ForgeryNet** — large face-forgery classification and spatial-localization benchmark: [official ForgeryNet project](https://yinanhe.github.io/projects/forgerynet.html).
12. **OpenForensics** — multi-face forgery detection and segmentation: [OpenForensics paper and project reference](https://arxiv.org/abs/2107.14480).

## 3. License gate before download

For every dataset create `dataset_card.json`:

```json
{
  "dataset": "genimage",
  "source_url": "https://github.com/GenImage-Dataset/GenImage",
  "version_or_revision": "commit-or-release-id",
  "downloaded_at_utc": "2026-07-15T00:00:00Z",
  "license": "verify from official source",
  "commercial_use_allowed": null,
  "redistribution_allowed": null,
  "requires_registration": false,
  "archive_sha256": "fill-after-download",
  "reviewed_by": "name"
}
```

`null` means the dataset is blocked from production training until a human verifies the terms. Research access does not automatically grant commercial use.

## 4. Storage layout

Large data remains outside Git:

```text
data/raw/xabarnavis_datasets/
  genimage/
  wildfake/
  local_uz_camera/
  imd2020/
  comofod/
  defacto/
  metadata/
    master.csv
    train.csv
    val.csv
    test.csv
    robustness_test.csv
    dataset_cards/
```

The trainer resolves every `image_path` relative to `data/raw/xabarnavis_datasets/`.

Required manifest columns:

```csv
image_path,label,source,generator,base_id,manipulation_type,has_mask,mask_path,license_id,split
genimage/SD14/train/ai/1.png,ai_generated,genimage,sd_1_4,genimage-1,none,0,,genimage-license,train
local_uz_camera/phone_a/1.jpg,real,local_uz_camera,none,uz-phone-a-1,none,0,,consent-v1,train
imd2020/fake/1.jpg,manipulated,imd2020,none,imd-1,splicing,1,imd2020/masks/1.png,imd2020-license,test
```

`base_id` is mandatory. Original images, crops, JPEG versions, screenshots, and other derivatives of the same source must share one `base_id` and remain in the same split.

## 5. Download methods

### Official archive or access form

Use the official dataset page. Save the untouched archive, compute its hash, then extract it:

```powershell
Get-FileHash -Algorithm SHA256 "D:\datasets\download\dataset.zip"
Expand-Archive -LiteralPath "D:\datasets\download\dataset.zip" -DestinationPath "data\raw\xabarnavis_datasets\dataset_name"
```

Never automate access-form, authentication, or license acceptance steps.

### Hugging Face datasets

Install the official client:

```powershell
python -m pip install --upgrade huggingface_hub
hf auth login
```

Inspect size before downloading:

```powershell
hf download hf://datasets/OWNER/DATASET --dry-run
```

Download to an explicit location:

```powershell
hf download hf://datasets/OWNER/DATASET --local-dir "data\raw\xabarnavis_datasets\dataset_name"
```

Pin a revision for reproducibility when the repository supplies one. The official client supports `revision`, include/exclude filters, local directories, and dry runs: [Hugging Face download documentation](https://huggingface.co/docs/huggingface_hub/guides/download).

### Kaggle datasets

Only use Kaggle mirrors when the official source explicitly permits redistribution. Record both the original source and mirror:

```powershell
python -m pip install kaggle
kaggle datasets download -d OWNER/DATASET -p "data\raw\downloads" --unzip
```

## 6. Data quality checks

Before creating splits:

1. Decode every image and reject corrupt files.
2. Record SHA-256, dimensions, mode, format, and file size.
3. Remove exact duplicates by SHA-256.
4. Find near-duplicates using perceptual hashes or embeddings.
5. Verify each mask matches its image dimensions.
6. Balance file format, resolution, and JPEG quality across labels.
7. Review random contact sheets from every source and label.
8. Quarantine ambiguous or mislabeled examples instead of guessing.

Critical shortcut checks:

- real=JPEG and fake=PNG;
- real=high resolution and fake=512×512;
- a watermark exists only in one class;
- one dataset supplies all real images and another all fake images;
- filename or folder patterns leak the label.

## 7. Split protocol

Use grouped, source-aware splitting rather than random row splitting:

- **Train:** known generators and devices, 70–80% of base groups.
- **Validation:** different base groups from training sources, 10–15%.
- **Internal test:** remaining groups, 10–15%.
- **Unseen-generator test:** generator families never used in training.
- **Cross-dataset test:** complete datasets never used for optimization.
- **Robustness test:** JPEG 95/85/70, resize, blur, crop, screenshot and social-media-style transformations.

Never tune thresholds on the unseen-generator or cross-dataset test sets.

## 8. Method implemented in Xabarnavis today

Training code: `scripts/training/train_ai_real.py`.

The current baseline uses:

- task: binary `real` vs `ai_generated` classification;
- backbone: EfficientNet-B0 by default, ResNet-18 optional;
- initialization: ImageNet weights with `--pretrained`;
- input: 224×224 RGB;
- augmentation: random resized crop, horizontal flip, mild color jitter;
- normalization: ImageNet mean and standard deviation;
- loss: class-weighted cross-entropy;
- optimizer: AdamW, learning rate `3e-4`, weight decay `1e-4`;
- precision: CUDA automatic mixed precision when available;
- checkpoint selection: highest validation ROC-AUC;
- metrics: accuracy, AI precision/recall/F1, ROC-AUC, confusion matrix;
- export: optional ONNX opset 18.

This is a strong reproducible baseline, not yet the final forensic model. It does not currently implement a learning-rate scheduler, early stopping, probability calibration, patch training, spectral branches, or localization masks.

## 9. Training commands

Install training dependencies:

```powershell
python -m pip install -r requirements-training.txt
```

For the RTX 5070 on Windows, install the official CUDA 12.8 PyTorch build before the requirements file:

```powershell
python -m pip install torch==2.11.0 torchvision==0.26.0 --index-url https://download.pytorch.org/whl/cu128
```

### Run A: smoke test

Use a small manifest first:

```powershell
python scripts/training/train_ai_real.py `
  --train-csv data/raw/xabarnavis_datasets/metadata/train-small.csv `
  --val-csv data/raw/xabarnavis_datasets/metadata/val-small.csv `
  --test-csv data/raw/xabarnavis_datasets/metadata/test-small.csv `
  --output-dir artifacts/runs/image/baseline-smoke `
  --backbone resnet18 `
  --image-size 224 `
  --batch-size 16 `
  --epochs 2 `
  --pretrained
```

### Run B: baseline EfficientNet

```powershell
python scripts/training/train_ai_real.py `
  --dataset-root data/raw/xabarnavis_datasets `
  --train-csv data/raw/xabarnavis_datasets/metadata/train.csv `
  --val-csv data/raw/xabarnavis_datasets/metadata/val.csv `
  --test-csv data/raw/xabarnavis_datasets/metadata/test.csv `
  --output-dir artifacts/runs/image/effnet-b0-v1 `
  --backbone efficientnet_b0 `
  --image-size 224 `
  --batch-size 32 `
  --epochs 20 `
  --lr 0.0003 `
  --weight-decay 0.0001 `
  --class-weights balanced `
  --pretrained `
  --device cuda `
  --model-name xabarnavis_image_0.1 `
  --model-version 0.1 `
  --export-onnx
```

### Run C: two-stage transfer learning

First train only the classifier head:

```powershell
python scripts/training/train_ai_real.py `
  --output-dir artifacts/runs/image/effnet-head `
  --epochs 3 --lr 0.001 --pretrained --freeze-backbone --device cuda
```

Then start a full fine-tuning run without `--freeze-backbone`. The current script resumes only checkpoints with the same optimizer/model configuration, so use the normal full baseline command until explicit head-to-full checkpoint loading is added.

## 10. Recommended next training methods

### Global detector v2

- ConvNeXt-Tiny or SigLIP/CLIP visual encoder;
- whole-image branch plus random patch branch;
- JPEG/resize/blur augmentation applied with label-balanced probabilities;
- supervised cross-entropy plus optional supervised contrastive loss;
- cosine learning-rate schedule with warmup;
- exponential moving average weights;
- temperature scaling on a calibration-only split.

Do not report raw softmax as forensic confidence. Save logits and fit calibration after training.

### Manipulation localizer

Use datasets with pixel masks. Recommended baseline:

- SegFormer-B0 or U-Net encoder;
- 512×512 patches;
- loss: `0.5 × BCEWithLogits + 0.5 × DiceLoss`;
- oversample images with small manipulated regions;
- evaluate pixel F1, IoU, MCC and image-level AUC;
- keep authentic images with all-zero masks in training.

### Face forgery model

- detect and align faces before training;
- split by source identity/video, never random face crops;
- train on real, face-swap, reenactment and synthetic-face categories;
- evaluate both clean crops and compressed/full-frame detections.

### Fusion model

After all base models are frozen, train logistic regression or gradient boosting on an independent fusion set using:

- global-model logits;
- patch/spectral logits;
- localization area and reliability;
- metadata/C2PA/watermark status;
- JPEG quality and screenshot probability;
- face score;
- robustness variance;
- out-of-distribution score.

Never train fusion on the same predictions used to fit the base models.

## 11. Evaluation gates

A model is not production-ready because its random-split accuracy is high. Require:

- internal test ROC-AUC and F1;
- per-dataset and per-generator metrics;
- unseen-generator ROC-AUC;
- false-positive rate on local camera photos;
- JPEG/resize/screenshot degradation curves;
- expected calibration error and reliability diagram;
- inference time and peak VRAM;
- threshold chosen from the validation/calibration set;
- documented failure cases.

Suggested release gates for a candidate, not a scientific guarantee:

```text
Unseen-generator ROC-AUC     >= 0.90
Local-camera false positive <= 5%
JPEG-70 AUC drop            <= 0.10
Expected calibration error  <= 0.05
All dataset licenses        reviewed
```

## 12. Expected run artifacts

Each run creates:

```text
artifacts/runs/image/effnet-b0-v1/
  config.json
  metrics.csv
  last.pt
  best.pt
  test_metrics.json
  model_metadata.json
  ai_detector_effnet_b0.onnx
```

Also save the exact train/validation/test manifests, dataset-card snapshots, Git commit identifier, Python environment, GPU model, and calibration parameters beside the run. Without these, the result is not reproducible.

## 13. Recommended execution plan

1. Download CIFAKE and one GenImage generator subset.
2. Add an equal number of verified real-camera images.
3. Build deduplicated, group-safe CSV manifests.
4. Run the two-epoch smoke test.
5. Train EfficientNet-B0 for 20 epochs.
6. Evaluate on held-out GenImage generators and WildFake.
7. Fix dataset shortcuts before adding more scale.
8. Add IMD2020/CoMoFoD and build a separate localization trainer.
9. Add face datasets only after identity-safe splitting is implemented.
10. Calibrate and fuse frozen models on a separate dataset.

The most important rule is simple: more terabytes do not automatically produce a better forensic model. Generator diversity, clean labels, group-safe splits, balanced degradations, external tests, and calibration matter more than raw image count.
