# Xabarnavis Next Datasets To Train

Current trained model:

```text
real: COCO
ai_generated: Synthbuster
```

This is a good first model, but the next model needs more generator diversity. Do not only add more COCO/Synthbuster; add unseen generators and edited/manipulated datasets.

## Priority 1: AI-Generated Generalization

### 1. GenImage

Best long-term dataset for AI-vs-real detection.

Why:

```text
real/fake pairs
multiple generators
ImageNet-style classes
good for cross-generator training
```

Generators:

```text
Midjourney
Stable Diffusion
ADM
GLIDE
Wukong
VQDM
BigGAN
```

Use it like this:

```text
Train:
  Stable Diffusion
  ADM
  GLIDE
  BigGAN

Validation:
  Wukong
  VQDM

Test:
  Midjourney
```

Do not download the full dataset first if disk is limited. Start with 1-2 generator folders.

Link:

```text
https://github.com/GenImage-Dataset/GenImage
```

### 2. WildFake

Good for real-world style variation and harder AI images.

Why:

```text
large-scale
hierarchical generator categories
more diverse than simple benchmark data
good for robustness
```

Link:

```text
https://github.com/hy-zpg/AIGC-Image-Detection-Dataset
https://modelscope.cn/datasets/hy2628982280/WildFake/summary
```

### 3. AIGC Detection Benchmark

Use mainly for testing and benchmarking, not only training.

Why:

```text
good benchmark repo
useful for comparing detector behavior
helps avoid overfitting to one dataset
```

Link:

```text
https://github.com/Ekko-zn/AIGCDetectBenchmark
```

### 4. CIFAKE

Small and easy starter dataset, but low-resolution CIFAR-style images.

Why:

```text
easy to download from Kaggle
60k real + 60k AI
useful for quick experiments
```

Weakness:

```text
32x32 CIFAR images are not like real user uploads
do not use it as your main forensic dataset
```

Link:

```text
https://www.kaggle.com/datasets/birdy654/cifake-real-and-ai-generated-synthetic-images
```

### 5. ArtiFact

Useful additional Kaggle dataset with real and synthetic images.

Link:

```text
https://www.kaggle.com/datasets/awsaf49/artifact-dataset
```

## Priority 2: Manipulated / Edited Detection

These are needed for Xabarnavis to detect Photoshop/inpainting/splicing/copy-move, not only AI images.

### 1. CASIA v2

Classic image tampering dataset.

Use for:

```text
splicing
copy-move
edited/not-edited classifier
```

Links:

```text
https://www.kaggle.com/datasets/divg07/casia-20-image-tampering-detection-dataset
https://github.com/namtpham/casia2groundtruth
```

### 2. IMD2020

Real-life manipulated images.

Use for:

```text
real-world edited image detection
validation
forensic benchmark
```

Link:

```text
https://staff.utia.cas.cz/novozada/db/
```

### 3. COVERAGE

Copy-move forgery dataset.

Use for:

```text
copy-move detection
mask/heatmap validation
```

Link:

```text
https://github.com/wenbihan/coverage
```

### 4. Columbia Splicing

Small but clean splicing dataset.

Use for:

```text
splicing smoke tests
classical forensic comparison
```

Link:

```text
https://www.ee.columbia.edu/ln/dvmm/downloads/AuthSplicedDataSet/AuthSplicedDataSet.htm
```

## Recommended Next Training Mix

### Model v2: AI vs Real

```text
real:
  COCO
  local phone photos
  RAISE-1k if available

ai_generated:
  Synthbuster
  GenImage selected generators
  WildFake
  local Midjourney/SDXL/DALL-E/Flux samples
```

Suggested balance:

```text
real: 40%
Synthbuster: 20%
GenImage: 25%
WildFake/local generators: 15%
```

### Model v3: Real vs AI vs Manipulated

```text
real:
  COCO + local camera

ai_generated:
  Synthbuster + GenImage + WildFake

manipulated:
  CASIA v2 + IMD2020 + COVERAGE
```

Suggested balance:

```text
real: 35%
ai_generated: 40%
manipulated: 25%
```

## Important Testing Rule

Never test on the same generator family used in training only.

Bad:

```text
train Stable Diffusion
test Stable Diffusion
```

Better:

```text
train Stable Diffusion + BigGAN + GLIDE
test Midjourney + SDXL + DALL-E + Flux
```

## Practical Next Step

For your next run, do this order:

```text
1. Add GenImage subset
2. Add WildFake if download works
3. Add CASIA v2 for manipulated images
4. Rebuild manifests
5. Train v2 AI-vs-real
6. Then train 3-class model
```




