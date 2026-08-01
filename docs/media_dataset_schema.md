# Xabarnavis Media Dataset Schema

Initialize the media layout with:

```powershell
python scripts\datasets\init_media_schema.py
```

Canonical raw dataset layout:

```text
data/raw/xabarnavis_media/
  photo/
    external/xabarnavis_photo_external_0.1/
    milliy/xabarnavis_image_0.1/
  video/
    external/xabarnavis_video_external_0.1/
    milliy/xabarnavis_video_0.1/
  audio/
    external/xabarnavis_audio_external_0.1/
    milliy/xabarnavis_audio_0.1/
  text/
    external/xabarnavis_text_external_0.1/
    milliy/xabarnavis_text_0.1/
```

Each dataset folder contains a `schema.json`. Training and model artifacts follow the same shape:

```text
artifacts/runs/photo/milliy/xabarnavis_image_0.1/ai_real_gpu/
artifacts/models/photo/milliy/xabarnavis_image_0.1/
```

GPU training defaults to `photo/milliy/xabarnavis_image_0.1`:

```powershell
.\scripts\training\train_gpu.ps1 -Pretrained -Epochs 10 -BatchSize 64 -NumWorkers 4
```

You can switch the namespace without changing the trainer:

```powershell
.\scripts\training\train_gpu.ps1 -MediaType photo -DatasetOrigin external -ModelName xabarnavis_photo_external_0.1
```
