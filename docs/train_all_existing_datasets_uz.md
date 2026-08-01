# Barcha mavjud image datasetlar bilan training

Disk inventarizatsiyasida 2.49 million auxiliary rasm va asosiy kataloglarda 152 mingdan ortiq rasm mavjud. Ular real, AI-generated va manipulated vazifalariga ajratiladi.

## Tavsiya etilgan rejim: barcha source, balanslangan class

Bu rejim integrity auditdan o'tgan `metadata_3class_clean` ichidagi 335,484 namunani ishlatadi:

```text
train: 268,392
validation: 33,546
test: 33,546
```

Har splitda real, AI-generated va manipulated classlar teng. AFHQ, BigGAN, CelebA-HQ, CIPS, COCO, CycleGAN, DDPM, diffusion GAN, face synthetics, FFHQ, GANsFormer, GauGAN, GLIDE, ImageNet, LSUN, ProGAN, ProjectedGAN, Stable Diffusion, StarGAN, StyleGAN 1/2/3, Taming Transformer, VQ Diffusion, Synthbuster, CASIA va mavjud inpainting dataset source’lari qamrab olinadi.

```powershell
powershell -ExecutionPolicy Bypass `
  -File scripts\training\train_image_forensics_advanced.ps1 `
  -Task three_class `
  -MetadataDir metadata_3class_clean `
  -Epochs 30 `
  -BatchSize 8 `
  -AccumulationSteps 4 `
  -ImageSize 384 `
  -OutputDir artifacts\runs\image\all-sources-balanced-v1
```

## Literal rejim: barcha fayllar

Yangi balanslanmagan manifest yarating:

```powershell
python scripts\datasets\build_image_3class_manifest.py `
  --metadata-dir-name metadata_all_images `
  --val-ratio 0.05 `
  --test-ratio 0.05
```

Muhim: `--balance` yozilmaydi. Shunda topilgan barcha fayllar manifestga kiradi.

Training:

```powershell
powershell -ExecutionPolicy Bypass `
  -File scripts\training\train_image_forensics_advanced.ps1 `
  -Task three_class `
  -MetadataDir metadata_all_images `
  -Epochs 15 `
  -BatchSize 8 `
  -AccumulationSteps 4 `
  -ImageSize 384 `
  -OutputDir artifacts\runs\image\all-images-v1
```

Trainer inverse-frequency class weights ishlatadi. Shunga qaramay, StyleGAN2 yoki LSUN kabi juda katta source’lar bir class ichida dominant bo‘lishi mumkin. Eng ishonchli production model uchun source-balanced sampler keyingi zarur bosqichdir.

Eski `metadata_3class` manifestidan foydalanmang. Unda bir xil inpainting fayllari qarama-qarshi label bilan takrorlangan eski leakage muammosi mavjud. Toza manifest auditi: 335,484 unique path, 0 duplicate, 0 conflicting label va 0 cross-split path.

## Model vazifasi

```text
Input
  ├── ConvNeXt-Tiny RGB branch
  └── FFT spectral CNN branch
             ↓
          Fusion
             ↓
  real / ai_generated / manipulated
```

Training method:

- ImageNet-pretrained ConvNeXt-Tiny;
- FFT frequency branch;
- weighted label-smoothed cross-entropy;
- JPEG 50–95, resize, blur, crop va color robustness;
- AdamW;
- backbone uchun past learning rate;
- warmup + cosine decay;
- CUDA AMP;
- gradient accumulation;
- gradient clipping;
- EMA checkpoint;
- validation macro ROC-AUC bo‘yicha best model;
- early stopping;
- source va generator bo‘yicha test metric.

## Monitoring

```powershell
nvidia-smi -l 2
```

```powershell
Get-Content artifacts\runs\image\all-sources-balanced-v1\test_metrics.json
```

## Cheklov

Ushbu 3-class model manipulated classni rasm darajasida aniqlaydi. Dataset maskalaridan pixel-level heatmap o‘rgatish uchun alohida localization trainer kerak. Maskali va masksiz datasetlarni bir segmentation lossga majburan qo‘shish mumkin emas.
