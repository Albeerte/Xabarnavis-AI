# Xabarnavis: to‘liq dataset, model va storage arxitekturasi

Bu hujjat Xabarnavis image-forensics moduli uchun tavsiya etilgan production tuzilma. Hajmlar dataset versiyasi, arxiv formati, rasm rezolyutsiyasi va ajratilgan frame soniga qarab o‘zgaradi. `Storage budget` ustuni server rejalashtirish uchun taxmin, dataset provayderining kafolatlangan download hajmi emas.

## 1. Asosiy katalog daraxti

```text
Xabarnavis .01/
├── data/
│   ├── raw/xabarnavis_datasets/             # original, o‘zgartirilmagan datasetlar
│   │   ├── _downloads/                      # zip/tar/parquet arxivlar
│   │   ├── _quarantine/                     # corrupt yoki labeli noaniq fayllar
│   │   ├── dataset_cards/                   # license, URL, revision, SHA-256
│   │   ├── real/
│   │   │   ├── local_uz_camera/
│   │   │   │   ├── iphone/
│   │   │   │   ├── samsung/
│   │   │   │   ├── redmi/
│   │   │   │   ├── pixel/
│   │   │   │   ├── dslr/
│   │   │   │   └── documents/
│   │   │   ├── coco/
│   │   │   ├── imagenet/
│   │   │   ├── open_images/
│   │   │   ├── places365/
│   │   │   ├── raise/
│   │   │   ├── vision_camera/
│   │   │   ├── dresden/
│   │   │   ├── ffhq/
│   │   │   └── genimage_real/
│   │   ├── ai_generated/
│   │   │   ├── genimage/
│   │   │   │   ├── stable_diffusion_1_4/
│   │   │   │   ├── stable_diffusion_1_5/
│   │   │   │   ├── midjourney/
│   │   │   │   ├── adm/
│   │   │   │   ├── glide/
│   │   │   │   ├── wukong/
│   │   │   │   ├── vqdm/
│   │   │   │   └── biggan/
│   │   │   ├── wildfake/
│   │   │   ├── community_forensics/
│   │   │   ├── synthbuster/
│   │   │   ├── forensynths/
│   │   │   ├── artifact/
│   │   │   ├── cifake/
│   │   │   ├── diffusiondb/
│   │   │   ├── journeydb/
│   │   │   └── local_generated/
│   │   │       ├── flux/
│   │   │       ├── sdxl/
│   │   │       ├── dalle/
│   │   │       ├── firefly/
│   │   │       └── gpt_image/
│   │   ├── manipulated/
│   │   │   ├── casia_v2/
│   │   │   │   ├── authentic/
│   │   │   │   ├── tampered/
│   │   │   │   └── masks/
│   │   │   ├── imd2020/{authentic,tampered,masks}/
│   │   │   ├── defacto/
│   │   │   │   ├── copy_move/{images,probe_masks,donor_masks}/
│   │   │   │   ├── splicing/{images,probe_masks,donor_masks}/
│   │   │   │   ├── removal/{images,probe_masks,inpaint_masks}/
│   │   │   │   └── morphing/{images,probe_masks,donor_masks}/
│   │   │   ├── comofod/{images,masks}/
│   │   │   ├── coverage/{images,source_masks,target_masks}/
│   │   │   ├── columbia/{authentic,spliced,masks}/
│   │   │   ├── cocoglide/{images,masks}/
│   │   │   ├── doc_tamper/{images,masks,ocr}/
│   │   │   └── realistic_tampering/{images,masks}/
│   │   ├── face_forgery/
│   │   │   ├── faceforensics_pp/{videos,frames,faces,metadata}/
│   │   │   ├── celeb_df_v2/{videos,frames,faces,metadata}/
│   │   │   ├── dfdc/{videos,frames,faces,metadata}/
│   │   │   ├── openforensics/{images,masks,bboxes}/
│   │   │   ├── forgerynet/{videos,frames,faces,masks}/
│   │   │   ├── diffusionface/{images,faces,metadata}/
│   │   │   └── df40/{videos,frames,faces,metadata}/
│   │   ├── robustness/
│   │   │   ├── jpeg_95/
│   │   │   ├── jpeg_85/
│   │   │   ├── jpeg_70/
│   │   │   ├── resize_075/
│   │   │   ├── resize_050/
│   │   │   ├── blur/
│   │   │   ├── screenshots/
│   │   │   ├── webp/
│   │   │   └── social_media_simulation/
│   │   └── metadata/
│   │       ├── master.csv
│   │       ├── train.csv
│   │       ├── val.csv
│   │       ├── calibration.csv
│   │       ├── test_internal.csv
│   │       ├── test_unseen_generator.csv
│   │       ├── test_cross_dataset.csv
│   │       └── robustness_test.csv
│   ├── processed/image/                    # verify, decode va deduplicate qilingan
│   ├── ready/image/                        # training-ready shardlar
│   │   ├── global_ai_224/
│   │   ├── patch_ai_256/
│   │   ├── localization_512/
│   │   ├── faces_224/
│   │   └── calibration/
│   └── holdout/image/                      # trening jarayonidan yopiq test
├── artifacts/
│   ├── runs/image/                         # config, metric, checkpoint
│   ├── models/image/
│   │   ├── global_ai/
│   │   ├── patch_spectral/
│   │   ├── manipulation/
│   │   ├── localization/
│   │   ├── face_forgery/
│   │   ├── calibration/
│   │   └── fusion/
│   └── reports/image/
└── ml/registry/image_models.yaml
```

## 2. Dataset hajmi va vazifasi

### A. Global AI-generated detection

| Dataset | Vazifa | Tavsiya qilingan foydalanish | Storage budget |
|---|---|---|---:|
| GenImage | GAN/diffusion real-vs-AI | Asosiy train + cross-generator test | 0.3–1.0 TB |
| Community Forensics Small | Ko‘p generatorli generalizatsiya | V2 train | taxminan 0.28 TB download |
| Community Forensics Full | Juda keng generator qamrovi | V3 katta server | taxminan 1.1 TB download |
| Community Forensics Eval | Tashqi benchmark | Yopiq test | taxminan 0.2 TB download |
| WildFake | In-the-wild generativ rasm | Cross-dataset test/fine-tune | 0.1–0.4 TB |
| Synthbuster | Diffusion/frequency benchmark | Spectral test | taxminan 12 GB archive |
| ForenSynths | GAN detection baseline | CNNSpot comparison | 50–150 GB |
| ArtiFact | Real va synthetic diversity | External validation | 50–250 GB |
| CIFAKE | Kichik smoke dataset | Kod testi, production metric emas | 1–3 GB |
| DiffusionDB subset | Stable Diffusion | Generator diversity | 0.1–1 TB subset |
| JourneyDB subset | Midjourney | Unseen-generator test | 0.1–0.5 TB subset |
| Local recent generators | Flux/SDXL/DALL-E/Firefly/GPT Image | 2025–2026 holdout | 50–300 GB |

Production uchun birinchi realistik target: **0.8–1.5 TB**, katta research target: **3–6 TB**.

### B. Real negative class

| Dataset | Vazifa | Target soni | Storage budget |
|---|---|---:|---:|
| MS COCO | Kundalik real sahnalar | 100k–120k | 20–30 GB |
| ImageNet subset | Keng obyekt kategoriyalari | 200k–500k | 50–200 GB |
| Open Images subset | Turli real kontent | 200k–500k | 100–400 GB |
| Places365 subset | Indoor/outdoor sahna | 100k–300k | 30–150 GB |
| RAISE | Yuqori sifatli camera/RAW | imkon qadar to‘liq | 0.5–1 TB |
| VISION/Dresden | Device/PRNU | to‘liq | 50–200 GB |
| FFHQ/VGGFace2 subset | Real yuzlar | 70k–500k | 20–200 GB |
| Local Uzbekistan | Mahalliy qurilma va sharoit | 50k minimum | 100–500 GB |

Muhim: real class AI class bilan format, rezolyutsiya va JPEG quality bo‘yicha balanslangan bo‘lishi kerak.

### C. Local manipulation va localization

| Dataset | Asosiy label | Mask | Storage budget |
|---|---|---|---:|
| CASIA v2 | Splicing/copy-move | Alohida GT kerak | 5–20 GB |
| IMD2020 | Real-life manipulation | Ha | 5–20 GB |
| DEFACTO | Copy-move/splice/removal/morph | Ha | 50–200 GB |
| CoMoFoD | Copy-move + degradation | Ha | 5–20 GB |
| COVERAGE | Copy-move | Source/target | 1–5 GB |
| Columbia | Splicing | Ha | 1–10 GB |
| CocoGlide | Generative local edit | Ha | 10–100 GB |
| Realistic Tampering | Insertion/removal | Ha | 5–50 GB |
| DocTamper | Hujjat va matn almashtirish | Ha + OCR | 20–100 GB |
| ForgeryNet images | Ko‘p forgery turi | Ha | 0.5–3 TB |

Localization uchun boshlang‘ich target: **100k–300k image-mask pair**, production target: **0.5–2 million pair**.

### D. Face forgery

| Dataset | Vazifa | Raw + extracted budget |
|---|---|---:|
| FaceForensics++ | swap/reenactment/neural texture | 0.1–0.5 TB |
| Celeb-DF v2 | yuqori sifatli deepfake | 50–200 GB |
| DFDC subset | ko‘p face-swap video | 0.5–3 TB |
| OpenForensics | multi-face mask/bbox | 50–300 GB |
| ForgeryNet | classification/localization | 1–5 TB |
| DiffusionFace | diffusion yuz forgery | 50–300 GB |
| DF40 | 40 forgery usuli | 1–5 TB |

Videodan barcha frame olinmaydi. Tavsiya: 1–3 FPS sampling, scene-aware sampling va har identity/video faqat bitta splitda.

## 3. Master manifest sxemasi

```csv
image_path,mask_path,label,subtype,source,generator,device,identity_id,video_id,base_id,sha256,width,height,format,jpeg_quality,license_id,split
real/local_uz_camera/samsung/001.jpg,,real,camera,local_uz,none,samsung_s24,,,uz001,abc...,4032,3024,JPEG,94,consent_v1,train
ai_generated/genimage/midjourney/001.png,,ai_generated,diffusion,genimage,midjourney,,,,gen001,def...,1024,1024,PNG,,genimage_license,test_unseen_generator
manipulated/imd2020/tampered/001.jpg,manipulated/imd2020/masks/001.png,manipulated,splicing,imd2020,none,,,,imd001,987...,1280,720,JPEG,88,imd2020_license,test_cross_dataset
```

`base_id`, `identity_id` va `video_id` leakage oldini olish uchun ishlatiladi. Bir originalning crop/JPEG/screenshot variantlari bitta splitda qoladi.

## 4. Tavsiya etilgan model stack

| ID | Model | Input | Output | Parametr | FP32 checkpoint | FP16 checkpoint | RTX 5070 train batch |
|---|---|---:|---|---:|---:|---:|---:|
| XIMG-G1 | EfficientNet-B0 baseline | 224² | real/AI logits | ~5.3M | ~21 MB | ~11 MB | 64–128 |
| XIMG-G2 | ConvNeXt-Tiny global | 384² | real/GAN/diffusion/unknown | ~28.6M | ~115 MB | ~58 MB | 8–16 |
| XIMG-G3 | SigLIP/CLIP visual detector | 384² | embedding + AI logit | modelga bog‘liq | ~0.3–1.5 GB | ~0.15–0.75 GB | 4–16 |
| XIMG-P1 | Patch ConvNeXt-Tiny | 256² patches | patch AI map | ~28.6M | ~115 MB | ~58 MB | 32–64 patches |
| XIMG-S1 | Spectral CNN | 256² FFT/DCT | spectral anomaly | 5–15M | 20–60 MB | 10–30 MB | 32–64 |
| XIMG-M1 | Manipulation ConvNeXt | 384² | 7-class manipulation | ~28.6M | ~115 MB | ~58 MB | 8–16 |
| XIMG-L1 | SegFormer-B0 | 512² | pixel mask + reliability | ~3.7M | ~15–30 MB | ~8–15 MB | 4–8 |
| XIMG-L2 | SegFormer-B2 | 512² | yuqori sifatli mask | ~25M | ~100–150 MB | ~50–75 MB | 2–4 |
| XIMG-F1 | EfficientNet-B0 face | 224² face | real/swap/reenact/synthetic | ~5.3M | ~21 MB | ~11 MB | 64–128 |
| XIMG-C1 | Calibration | logits/features | calibrated probability | <0.1M | <1 MB | <1 MB | CPU |
| XIMG-U1 | Fusion MLP | 20–100 feature | final multi-score | <1M | 1–5 MB | <3 MB | CPU/GPU |

Checkpoint hajmlari optimizer state kiritilmagan inference weight uchun taxmin. AdamW training checkpoint odatda model weightdan **3–5 baravar katta** bo‘ladi.

## 5. Har modelning label va loss’i

### XIMG-G2: global generation

```text
Labels:
0 real
1 gan_generated
2 diffusion_generated
3 autoregressive_generated
4 unknown_synthetic

Loss:
weighted cross entropy
+ optional supervised contrastive loss
```

### XIMG-M1: manipulation classifier

```text
0 authentic
1 copy_move
2 splicing
3 object_removal
4 inpainting
5 global_edit
6 local_ai_edit
```

### XIMG-L1/L2: localization

```text
Input:  RGB 512 × 512
Target: binary mask 512 × 512
Loss:   0.5 BCEWithLogits + 0.5 DiceLoss
Metric: pixel F1, IoU, MCC, image AUC
```

### XIMG-F1: face forgery

```text
0 real_face
1 face_swap
2 face_reenactment
3 gan_face
4 diffusion_face
5 spoof_attack
```

## 6. RTX 5070 12 GB uchun amaliy konfiguratsiya

| Model | Resolution | Batch | AMP | Gradient accumulation |
|---|---:|---:|---|---:|
| EfficientNet-B0 | 224 | 64 | ha | 1 |
| ConvNeXt-Tiny | 384 | 8–16 | ha | 2–4 |
| Patch model | 256 | 32–64 | ha | 1–2 |
| SegFormer-B0 | 512 | 4–8 | ha | 4 |
| SegFormer-B2 | 512 | 2–4 | ha | 8 |
| SigLIP/CLIP fine-tune | 384 | 4–8 | ha | 4–8 |

Aniq batch driver, PyTorch versiyasi, augmentation va model implementatsiyasiga bog‘liq. OOM bo‘lsa batchni yarmiga tushiring.

## 7. To‘liq storage rejasi

| Profil | Raw datasets | Processed/ready | Models/runs | Jami tavsiya |
|---|---:|---:|---:|---:|
| MVP | 0.5–1 TB | 0.3–0.7 TB | 0.1 TB | 1–2 TB NVMe |
| Competition | 2–4 TB | 1–3 TB | 0.2–0.5 TB | 6–8 TB NVMe/HDD |
| Research | 8–15 TB | 5–12 TB | 0.5–2 TB | 20–30 TB storage |
| Full video-heavy | 20–50 TB | 10–30 TB | 1–3 TB | 50–100 TB storage |

Raw dataset, extracted frames va augmented variantlarni bir diskda nazoratsiz ko‘paytirish mumkin emas. Robustness variantlarini oldindan to‘liq nusxalash o‘rniga training paytida on-the-fly yaratish storage’ni tejaydi.

## 8. Tavsiya etilgan bosqichlar

1. **V0.1:** 100k real + 100k AI, EfficientNet-B0, 1–2 TB disk.
2. **V0.2:** GenImage + WildFake + local recent generators, ConvNeXt global model.
3. **V0.3:** IMD2020 + CoMoFoD + DEFACTO, SegFormer-B0 localization.
4. **V0.4:** FaceForensics++ + Celeb-DF + OpenForensics, face model.
5. **V0.5:** patch + spectral branches va robustness training.
6. **V1.0:** frozen base models, calibration dataset va learned fusion.

Bir bosqich benchmark va license gate’dan o‘tmasdan keyingisiga o‘tilmaydi.
