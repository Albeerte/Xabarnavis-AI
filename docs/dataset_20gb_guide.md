# Xabarnavis Minimum 20GB Dataset Guide

This is the safest first dataset bundle for the local MVP because it uses direct, open downloads and does not require Kaggle, Google Drive, or university account approval.

## Recommended First Bundle

| Dataset | Class | Compressed size | Why it is useful |
| --- | --- | ---: | --- |
| Synthbuster | AI-generated | 11.52 GB | Diffusion-generated images from multiple generators; good for frequency and robustness testing. |
| MS COCO 2017 train | Real | about 18 GB | Large real-photo baseline for AI-vs-real training and validation. |

Total compressed size: about 29.5 GB.

This clears the 20GB minimum and gives Xabarnavis a strong first split:

```text
real/
  coco_real/
ai_generated/
  synthbuster/
```

## Download Commands

List available direct-download datasets:

```powershell
python scripts\datasets\download_minimum_datasets.py --list
```

Download the recommended 20GB+ bundle:

```powershell
python scripts\datasets\download_minimum_datasets.py minimum_20gb
```

Download and extract:

```powershell
python scripts\datasets\download_minimum_datasets.py minimum_20gb --extract
```

If the download stops, run the same command again. The script keeps a `.part` file and resumes when the server supports byte ranges.

## Optional Additions After The First 20GB

For manipulation detection, add these next:

| Dataset | Class | Notes |
| --- | --- | --- |
| CASIA v2 | manipulated | Classic splicing/copy-move dataset. Check masks carefully before training. |
| COVERAGE | manipulated | Copy-move forgery pairs and masks. Small but useful. |
| IMD2020 | manipulated | Real-life manipulated images with originals/masks. |
| NIST MFC/OpenMFC | manipulated | Strong forensic benchmark, but access and size are less convenient. |

For stronger AI detection later:

| Dataset | Class | Notes |
| --- | --- | --- |
| GenImage | AI-generated + real pairs | Best long-term base, but full data is very large. Start with selected generators only. |
| WildFake | AI-generated | Useful for real-world generalization. |
| CIFAKE | AI-generated + real | Easy Kaggle/Hugging Face starter if you already have credentials. |

## Suggested Training Split

Do not random split by image only. Keep some generators unseen:

```text
Train:
  real: COCO train2017
  ai: Synthbuster subset from selected generators

Validation:
  real: COCO val2017
  ai: held-out Synthbuster generators

Test:
  social-media-compressed local images
  unseen generators such as Midjourney, SDXL, DALL-E, Flux, Firefly
```

## Disk Space Rule

For a 20GB compressed download, plan for at least 60GB free:

```text
archive zip files
+ extracted image folders
+ generated resized/cache files
+ reports and manifests
```

Your current C: drive has enough room for this bundle, but keep the archives in `data/raw/xabarnavis_datasets/_downloads` so they are easy to delete after extraction.



