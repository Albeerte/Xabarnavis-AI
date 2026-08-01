# Dataset Download And Placement Guide

This guide explains how to download extra datasets and where to place them in Xabarnavis.

## 1. Install Dataset Tools

```powershell
pip install -r requirements-datasets.txt
```

For Kaggle datasets, create an API token:

```text
Kaggle.com -> Account -> Create New API Token
```

Put the downloaded file here:

```text
C:\Users\User2\.kaggle\kaggle.json
```

Then test:

```powershell
kaggle datasets list -s cifake
```

## 2. Show Supported Dataset Downloads

```powershell
python scripts\datasets\download_external_datasets.py --list
```

## 3. Easy Kaggle Downloads

### CIFAKE

Good for quick AI-vs-real experiments.

Download:

```powershell
python scripts\datasets\download_external_datasets.py cifake
```

Organize into Xabarnavis folders:

```powershell
python scripts\datasets\organize_cifake.py
```

Final placement:

```text
data/raw/xabarnavis_datasets/
  real/
    cifake_real/
  ai_generated/
    cifake/
```

Then rebuild manifest:

```powershell
python scripts\datasets\build_ai_real_manifest.py --balance
```

### CASIA v2

Good for manipulated/edited detection.

Download:

```powershell
python scripts\datasets\download_external_datasets.py casia_v2
```

Raw files go here:

```text
data/raw/xabarnavis_datasets/_raw/casia_v2/
```

Automatic placement:

```powershell
python scripts\datasets\organize_casia_v2.py
```

Final placement:

```text
authentic/original images -> data/raw/xabarnavis_datasets/real/casia_authentic/
tampered/edited images   -> data/raw/xabarnavis_datasets/manipulated/casia_v2/
masks/groundtruth        -> data/raw/xabarnavis_datasets/manipulated/casia_v2/masks/
```

CASIA folder names differ by mirror, but commonly:

```text
Au or authentic -> real/casia_authentic
Tp or tampered  -> manipulated/casia_v2
```

### ArtiFact

Additional real/synthetic images.

Download:

```powershell
python scripts\datasets\download_external_datasets.py artifact
```

Raw files go here:

```text
data/raw/xabarnavis_datasets/_raw/artifact/
```

Manual placement:

```text
real images -> data/raw/xabarnavis_datasets/real/artifact_real/
fake images -> data/raw/xabarnavis_datasets/ai_generated/artifact/
```

## 4. Manual Downloads

Some datasets are too large or require platform-specific access, so download them manually.

### GenImage

Link:

```text
https://github.com/GenImage-Dataset/GenImage
```

Recommended placement:

```text
data/raw/xabarnavis_datasets/
  real/
    genimage_real/
  ai_generated/
    genimage/
      stable_diffusion/
      midjourney/
      adm/
      glide/
      wukong/
      biggan/
      vqdm/
```

If GenImage has folders like:

```text
imagenet_ai_0419_sdv4/train/ai
imagenet_ai_0419_sdv4/train/nature
```

Place them like:

```text
train/nature -> real/genimage_real/stable_diffusion/
train/ai     -> ai_generated/genimage/stable_diffusion/
```

Do this per generator.

### WildFake

Links:

```text
https://github.com/hy-zpg/AIGC-Image-Detection-Dataset
https://modelscope.cn/datasets/hy2628982280/WildFake/summary
```

Placement:

```text
data/raw/xabarnavis_datasets/ai_generated/wildfake/
```

If it includes real images too:

```text
real images -> data/raw/xabarnavis_datasets/real/wildfake_real/
fake images -> data/raw/xabarnavis_datasets/ai_generated/wildfake/
```

If you add `real/wildfake_real`, also add that folder to `scripts/datasets/build_ai_real_manifest.py`.

### IMD2020

Link:

```text
https://staff.utia.cas.cz/novozada/db/
```

Placement:

```text
data/raw/xabarnavis_datasets/manipulated/imd2020/
data/raw/xabarnavis_datasets/manipulated/imd2020/masks/
```

### COVERAGE

Link:

```text
https://github.com/wenbihan/coverage
```

Placement:

```text
data/raw/xabarnavis_datasets/manipulated/coverage/
data/raw/xabarnavis_datasets/manipulated/coverage/masks/
```

## 5. After Adding Datasets

For AI-vs-real training:

```powershell
python scripts\datasets\build_ai_real_manifest.py --balance
python scripts\training\train_ai_real.py --pretrained --epochs 10 --batch-size 32 --output-dir artifacts\runs\legacy\ai_real_v2
```

For quick test:

```powershell
python scripts\datasets\build_ai_real_manifest.py --balance --max-per-class 2000
python scripts\training\train_ai_real.py --pretrained --epochs 2 --batch-size 32 --output-dir artifacts\runs\legacy\ai_real_v2_quick
```

## 6. Current Best Next Step

Start with this:

```powershell
pip install -r requirements-datasets.txt
python scripts\datasets\download_external_datasets.py cifake
python scripts\datasets\organize_cifake.py
python scripts\datasets\build_ai_real_manifest.py --balance
python scripts\training\train_ai_real.py --pretrained --epochs 5 --batch-size 32 --output-dir artifacts\runs\legacy\ai_real_coco_synthbuster_cifake
```

Then add CASIA v2 for manipulated-image training.



