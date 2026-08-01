# Step-by-Step Xabarnavis Image Training

Run every command from the repository root:

```powershell
Set-Location "C:\Users\User2\Documents\Xabarnavis .01"
```

## Step 1 — check Python and GPU

```powershell
python --version
nvidia-smi
```

Python 3.11 is supported by this repository. `nvidia-smi` is optional; use CPU for the fixture test if CUDA is unavailable.

## Step 2 — create an isolated environment

```powershell
python -m venv .venv-training
.\.venv-training\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install torch==2.11.0 torchvision==0.26.0 --index-url https://download.pytorch.org/whl/cu128
python -m pip install -r requirements-training.txt
python -m pip install -r requirements-datasets.txt
```

Verify PyTorch:

```powershell
python -c "import torch; print(torch.__version__); print('CUDA build:', torch.version.cuda); print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'none')"
```

`requirements-training.txt` also installs `onnx` and `onnxscript`, which are required by current PyTorch versions for the final ONNX export.

## Step 3 — prove the pipeline works

This creates 80 synthetic fixture images. These are only for testing code, never for measuring model quality.

```powershell
powershell -ExecutionPolicy Bypass -File scripts\training\run_image_training_pipeline.ps1 `
  -Stage fixture `
  -Device cpu
```

Expected output folder:

```text
artifacts/runs/image/fixture-smoke/
```

Confirm that `best.pt`, `metrics.csv`, `test_metrics.json`, and the ONNX file exist before continuing.

## Step 4 — inspect supported automatic downloads

```powershell
python scripts\datasets\download_external_datasets.py --list
python scripts\datasets\download_minimum_datasets.py --list
```

The first practical bundle is Synthbuster plus COCO real images. It is about 30 GB compressed/working data depending on extraction.

```powershell
python scripts\datasets\download_minimum_datasets.py minimum_20gb --extract
```

The downloader supports resume. Re-run the same command after an interruption.

For CIFAKE:

```powershell
python scripts\datasets\download_external_datasets.py cifake
python scripts\datasets\organize_cifake.py
```

Do not download access-controlled datasets by bypassing their form. Request DEFACTO, FaceForensics++, and similar datasets through their official pages and review commercial-use terms.

## Step 5 — place manually downloaded data

Use this structure:

```text
data/raw/xabarnavis_datasets/
  real/
    local_camera_real/
    coco_real/
    genimage_real/
  ai_generated/
    genimage/
      stable_diffusion_v1_4/
      midjourney/
      biggan/
    synthbuster/
    local_generated/
  metadata/
```

Never copy generated images into a real folder. Keep untouched archives under `_downloads` and record license, source URL, revision, date, and SHA-256.

## Step 6 — add local real-camera images

Copy original, consented camera files into device-specific folders:

```text
data/raw/xabarnavis_datasets/real/local_camera_real/
  iphone_15/
  samsung_s24/
  redmi_note/
  canon/
```

Include indoor/outdoor, day/night, faces, documents, landscapes, low light, HDR, portrait mode, screenshots, and social-media recompressions. Do not label web images as verified camera originals unless their provenance is known.

## Step 7 — build validated manifests

```powershell
python scripts\datasets\build_ai_real_manifest.py --balance
```

The script now:

1. scans supported folders;
2. decodes and verifies every image;
3. excludes corrupt files;
4. computes SHA-256;
5. removes exact duplicates;
6. records `base_id` and hash;
7. creates balanced train, validation, and test CSV files.

Outputs:

```text
data/raw/xabarnavis_datasets/metadata/train.csv
data/raw/xabarnavis_datasets/metadata/val.csv
data/raw/xabarnavis_datasets/metadata/test.csv
```

To reserve complete generators for unseen-generator testing:

```powershell
python scripts\datasets\build_ai_real_manifest.py `
  --balance `
  --holdout-generators midjourney flux
```

Use generator names printed in the manifest’s `generator` column. The held-out test may be class-imbalanced; judge it with ROC-AUC, precision, recall, F1, and confusion matrix rather than accuracy alone.

## Step 8 — inspect the CSV files

```powershell
Import-Csv data\raw\xabarnavis_datasets\metadata\train.csv |
  Group-Object label,source,generator |
  Sort-Object Count -Descending |
  Select-Object Count,Name
```

Verify that:

- both labels exist;
- one source does not dominate;
- the held-out generators appear only in `test.csv`;
- derived versions of one source image are not split across sets;
- formats and resolutions are balanced across labels.

Exact SHA-256 deduplication cannot detect resized or recompressed copies. Before a scientific benchmark, add perceptual-hash or embedding-based near-duplicate grouping and assign all variants one `base_id`.

## Step 9 — run a 2-epoch real-data smoke test

```powershell
powershell -ExecutionPolicy Bypass -File scripts\training\run_image_training_pipeline.ps1 `
  -Stage smoke `
  -Device auto `
  -OutputDir artifacts\runs\image\real-data-smoke
```

This limits each class to 1,000 images and runs at most two epochs. Fix data-loading and GPU errors here before a long run.

## Step 10 — train the full baseline

```powershell
powershell -ExecutionPolicy Bypass -File scripts\training\run_image_training_pipeline.ps1 `
  -Stage full `
  -Device cuda `
  -Epochs 20 `
  -BatchSize 32 `
  -HoldoutGenerators midjourney,flux `
  -OutputDir artifacts\runs\image\effnet-b0-v1
```

If GPU memory is insufficient, reduce `-BatchSize` to 16 or 8. Use `-Device cpu` only for small tests; full training will be slow.

## Step 11 — understand the implemented method

The current training code is `scripts/training/train_ai_real.py`:

```text
Image
  → random resized crop / flip / mild color jitter
  → ImageNet normalization
  → ImageNet-pretrained EfficientNet-B0
  → two-class linear head
  → weighted cross-entropy
  → AdamW optimizer
  → CUDA mixed precision
  → best validation ROC-AUC checkpoint
```

Default hyperparameters:

```text
Input size:       224 × 224
Batch size:       32
Learning rate:    3e-4
Weight decay:     1e-4
Loss:             weighted CrossEntropyLoss
Optimizer:        AdamW
Best checkpoint:  highest validation ROC-AUC
```

This model answers only “globally AI-generated or real-like?” It does not localize Photoshop edits, verify provenance, or prove authenticity.

## Step 12 — inspect results

```powershell
Get-Content artifacts\runs\image\effnet-b0-v1\test_metrics.json
Import-Csv artifacts\runs\image\effnet-b0-v1\metrics.csv | Format-Table
```

Required review:

- ROC-AUC;
- AI precision, recall, and F1;
- confusion matrix;
- false positives on local camera photos;
- metrics for every generator and source;
- performance after JPEG-70, resizing and screenshot simulation.

Do not publish the best validation score as the final test score.

## Step 13 — resume an interrupted run

Direct trainer command:

```powershell
python scripts\training\train_ai_real.py `
  --pretrained `
  --device cuda `
  --epochs 20 `
  --output-dir artifacts\runs\image\effnet-b0-v1 `
  --resume artifacts\runs\image\effnet-b0-v1\last.pt
```

Keep all architecture and optimizer arguments identical to the original run.

## Step 14 — deploy the exported model

The full pipeline includes `--export-onnx` and produces:

```text
ai_detector_effnet_b0.onnx
```

Do not replace the production detector until the candidate passes unseen-generator, local-camera false-positive, robustness, calibration, and license gates described in `docs/training_guide.md`.

## Step 15 — train localization separately

After the global baseline works, download IMD2020, CoMoFoD, and another mask dataset. Build image/mask pairs and train a separate SegFormer-B0 or U-Net model:

```text
Input:  512 × 512 RGB patch
Target: 512 × 512 binary manipulation mask
Loss:   0.5 × BCEWithLogits + 0.5 × DiceLoss
Output: manipulation probability map
```

Evaluate pixel F1, IoU, MCC, image-level AUC, and manipulated-area percentage. Do not reuse the global binary classifier as a localization model.

## Quick command summary

```powershell
# 1. Environment
python -m venv .venv-training
.\.venv-training\Scripts\Activate.ps1
python -m pip install -r requirements-training.txt
python -m pip install -r requirements-datasets.txt

# 2. Code-only test
powershell -ExecutionPolicy Bypass -File scripts\training\run_image_training_pipeline.ps1 -Stage fixture -Device cpu

# 3. Download an initial open bundle
python scripts\datasets\download_minimum_datasets.py minimum_20gb --extract

# 4. Build safe manifests
python scripts\datasets\build_ai_real_manifest.py --balance --holdout-generators midjourney flux

# 5. Real-data smoke test
powershell -ExecutionPolicy Bypass -File scripts\training\run_image_training_pipeline.ps1 -Stage smoke -Device auto

# 6. Full baseline
powershell -ExecutionPolicy Bypass -File scripts\training\run_image_training_pipeline.ps1 -Stage full -Device cuda -Epochs 20 -BatchSize 32
```
