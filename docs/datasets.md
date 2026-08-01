# Dataset Strategy

Large datasets are not stored in Git. Keep local raw and prepared datasets in `data/raw/xabarnavis_datasets/` and `data/ready/image/`, then track their source, split, and counts through documentation and manifests.

Recommended tracked files:

- `docs/datasets.md`
- `storage/dataset_inventory.json`
- `scripts/download_*.py`
- CSV manifests for reproducible training splits

Recommended external storage:

- DVC remote
- Hugging Face Dataset
- Google Drive or object storage
- dedicated local training disk

## Labels

Main class labels:

- `0 = real`
- `1 = ai_generated`
- `2 = manipulated`

Subtypes:

- generator: `stable_diffusion`, `midjourney`, `dalle`, `flux`, `firefly`, `biggan`, `unknown`
- manipulation type: `splicing`, `copy_move`, `inpainting`, `face_swap`, `object_remove`, `object_add`, `color_edit`, `unknown`

## CSV Format

```csv
image_path,label,source,generator,manipulation_type,has_mask,mask_path,exif_status,split
real/local_camera_real/001.jpg,real,local_camera,none,none,0,,valid,train
ai_generated/genimage/stable_diffusion/001.jpg,ai_generated,genimage,stable_diffusion,none,0,,missing,train
manipulated/casia_v2/001.jpg,manipulated,casia,none,splicing,1,masks/001.png,partial,train
```

## Recommended V1 Mix

- Real images: 35%
- AI-generated: 40%
- Manipulated/edited: 25%

AI-generated:

- GenImage
- WildFake
- Synthbuster
- AIGCDetectBenchmark
- MS COCOAI
- local Midjourney, SDXL, Flux, DALL-E generated images

Real:

- GenImage real pairs
- COCO real
- RAISE-1k real
- local smartphone photos
- local news/social-media images

Manipulated:

- CASIA v2
- NIST MFC
- IMD2020
- COVERAGE
- Defacto
- custom Photoshop/inpainting edits

## Split Rule

Do not random-split images from the same generator family into train and test. The final test split must include unseen generators and social-media-compressed images.

Example:

- Train: Stable Diffusion 1.5, BigGAN, GLIDE, ADM
- Validation: Midjourney v5, Wukong
- Test: SDXL, DALL-E 3, Flux, Firefly, Chameleon, Telegram-compressed images

## Robustness Augmentations

- JPEG quality: 30, 50, 70, 90
- resize: 512, 1024, 1920
- slight Gaussian blur
- random crop
- screenshot simulation
- Telegram, Instagram, WhatsApp compression
- watermark
- brightness/contrast changes



