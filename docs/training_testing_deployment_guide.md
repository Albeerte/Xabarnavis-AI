# Xabarnavis Training, Testing, and Deployment Guide

This guide is for the local forensic MVP. It starts with the current heuristic API, then shows how to move toward trained AI/real/manipulated models.

## 1. Prepare The Dataset

Initialize the folder tree:

```powershell
python scripts\datasets\init_dataset_tree.py
```

Download the first 20GB+ bundle:

```powershell
python scripts\datasets\download_minimum_datasets.py minimum_20gb --extract
```

Recommended first structure:

```text
data/raw/xabarnavis_datasets/
  real/
    coco_real/
  ai_generated/
    synthbuster/
  manipulated/
    casia_v2/
    imd2020/
    coverage/
  metadata/
    train.csv
    val.csv
    test.csv
```

For the first model, use only:

```text
0 = real
1 = ai_generated
```

After that, add:

```text
2 = manipulated
```

## 2. Build CSV Manifests

Use this format:

```csv
image_path,label,source,generator,manipulation_type,has_mask,mask_path,exif_status,split
real/coco_real/train2017/000000000009.jpg,real,coco,none,none,0,,missing,train
ai_generated/synthbuster/dalle2/0001.png,ai_generated,synthbuster,dalle2,none,0,,missing,train
manipulated/casia_v2/Tp/001.jpg,manipulated,casia,none,splicing,1,manipulated/casia_v2/masks/001.png,partial,train
```

Important rule: do not random-split everything. Keep some generators completely unseen in test.

Example:

```text
Train:
  real: COCO train2017
  ai: Synthbuster selected generators

Validation:
  real: COCO val2017
  ai: held-out Synthbuster generators

Test:
  AI generators not used in training
  Telegram/Instagram compressed images
  local phone photos
```

## 3. Training Plan

### Stage 1: AI vs Real Classifier

Goal:

```text
Input: image
Output: real_score, ai_score
```

Start with one backbone:

```text
EfficientNet-B0/B4
ConvNeXt-Tiny/Base
CLIP ViT-B/16 feature extractor + small classifier
```

Recommended first target:

```text
accuracy: 85%+
AUC: 0.90+
false positive rate on real photos: low
```

Later target:

```text
accuracy: 90-95%
AUC: 0.95+
tested on unseen generators
```

Install training dependencies:

```powershell
pip install -r requirements-training.txt
```

Build manifests after downloading/extracting datasets:

```powershell
python scripts\datasets\build_ai_real_manifest.py
```

Train EfficientNet-B0:

```powershell
python scripts\training\train_ai_real.py `
  --pretrained `
  --epochs 10 `
  --batch-size 32 `
  --image-size 224 `
  --output-dir artifacts\runs\legacy\ai_real_effnet_b0
```

Quick CPU/GPU smoke test before using the full dataset:

```powershell
python scripts\datasets\create_tiny_training_fixture.py
python scripts\training\train_ai_real.py `
  --epochs 1 `
  --batch-size 8 `
  --num-workers 0 `
  --output-dir artifacts\runs\legacy\tiny_ai_real_test
```

Resume training:

```powershell
python scripts\training\train_ai_real.py `
  --resume artifacts\runs\legacy\ai_real_effnet_b0\last.pt `
  --epochs 20 `
  --output-dir artifacts\runs\legacy\ai_real_effnet_b0
```

Export ONNX after training:

```powershell
python scripts\training\train_ai_real.py `
  --resume artifacts\runs\legacy\ai_real_effnet_b0\best.pt `
  --epochs 10 `
  --output-dir artifacts\runs\legacy\ai_real_effnet_b0 `
  --export-onnx
```

Training outputs:

```text
artifacts/runs/legacy/ai_real_effnet_b0/
  best.pt
  last.pt
  metrics.csv
  test_metrics.json
  config.json
  model_metadata.json
  ai_detector_effnet_b0.onnx
```

### Stage 2: Manipulated vs Not Manipulated

Goal:

```text
Input: image
Output: manipulated_score
Optional output: heatmap/mask
```

Datasets:

```text
CASIA v2
IMD2020
COVERAGE
NIST MFC
custom Photoshop/inpainting edits
```

Start simple:

```text
image-level classifier first
segmentation heatmap second
```

### Stage 3: Fusion Model

The API already expects these signals:

```text
real_score
ai_score
manipulated_score
metadata_anomaly_score
frequency_anomaly_score
jpeg_blocking_score
ela_anomaly_score
```

Train a small fusion model after you have labels:

```text
Logistic Regression first
XGBoost or LightGBM later
small MLP only after enough data
```

Fusion output:

```text
final_verdict
confidence
real_score
ai_score
manipulated_score
```

## 4. Testing Protocol

Do not trust only random validation accuracy.

Test groups:

```text
1. Clean real photos
2. Clean AI images
3. Edited/manipulated images
4. Social-media-compressed images
5. Screenshots
6. Unseen AI generators
7. Local Uzbek/news/social images
```

Minimum metrics:

```text
accuracy
precision
recall
F1
AUC
confusion matrix
false positive rate on real photos
```

For manipulation heatmaps:

```text
IoU
Dice score
pixel precision
pixel recall
```

A good test report should answer:

```text
How often does it call real photos fake?
How well does it detect unseen generators?
Does Telegram/Instagram compression break it?
Does it confuse edited real photos with AI-generated images?
```

## 5. Local API Testing

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run the API:

```powershell
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Analyze one image:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/analyze" `
  -F "file=@C:\path\to\image.jpg"
```

List cases:

```powershell
curl.exe "http://127.0.0.1:8000/api/cases"
```

Download report:

```powershell
curl.exe "http://127.0.0.1:8000/api/cases/1/report"
```

## 6. Model Export

For deployment, export trained models to ONNX:

```text
models/
  ai_detector.onnx
  manipulation_detector.onnx
  frequency_detector.onnx
  fusion_model.pkl
```

Recommended inference stack:

```text
ONNX Runtime
Pillow/OpenCV preprocessing
CPU fallback
GPU acceleration when available
```

Keep model metadata:

```text
model name
training dataset version
training date
metrics
thresholds
known limitations
```

## 7. Deployment Options

### Option A: Local Demo Deployment

Best for university demo or offline forensic workstation.

```powershell
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Pros:

```text
simple
private
works offline after setup
```

Cons:

```text
single machine only
manual startup
```

### Option B: Local Network Deployment

Run on one machine, access from other devices on the same network.

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Then open:

```text
http://YOUR_PC_IP:8000/docs
```

Use this only on a trusted network.

### Option C: Production Server

Recommended stack:

```text
FastAPI
Uvicorn/Gunicorn
PostgreSQL
Redis
Celery
object storage or protected local storage
Nginx reverse proxy
HTTPS
```

Production tasks:

```text
move from SQLite to PostgreSQL
add user authentication
limit upload size
validate image formats
store reports privately
log model versions
add background jobs for heavy inference
```

## 8. Deployment Checklist

Before real users:

```text
[ ] Trained model tested on unseen generators
[ ] Manipulated image test set evaluated
[ ] False positives on real photos measured
[ ] Upload file size limit added
[ ] Authentication added
[ ] Reports use probability language, not absolute claims
[ ] Model version appears in every report
[ ] SHA256 hash appears in every report
[ ] Backups configured
[ ] Storage cleanup policy configured
```

## 9. Suggested Roadmap

### Week 1

```text
download COCO + Synthbuster
create train/val/test CSVs
train AI vs real classifier
evaluate on held-out generators
```

### Week 2

```text
export first model to ONNX
connect ONNX inference to FastAPI
generate JSON reports with model scores
```

### Month 1

```text
add CASIA/IMD2020/COVERAGE
train manipulated image classifier
generate better heatmaps
add PDF report generation
```

### Month 2-3

```text
train fusion model
add social-media robustness tests
add Uzbek/local dataset
deploy local-network demo
```




