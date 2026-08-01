# Internetdan yangi forensic dataset yuklash promptlari

## 1. Muhit

```powershell
Set-Location "C:\Users\User2\Documents\Xabarnavis .01"
.\.venv-training\Scripts\Activate.ps1
python -m pip install --upgrade huggingface_hub kaggle kagglehub gdown
hf auth login
```

## 2. Disk joyini tekshirish

```powershell
Get-PSDrive -PSProvider FileSystem | Select-Object Name,Used,Free
```

Community Forensics Full uchun terabayt miqyosidagi joy talab qilinishi mumkin. Download va extraction uchun alohida zaxira qoldiring.

## 3. Community Forensics — avval dry-run

```powershell
powershell -ExecutionPolicy Bypass `
  -File scripts\datasets\download_new_forensics_datasets.ps1 `
  -Dataset community_forensics
```

Hajm va fayllarni tekshirgandan keyin download:

```powershell
powershell -ExecutionPolicy Bypass `
  -File scripts\datasets\download_new_forensics_datasets.ps1 `
  -Dataset community_forensics `
  -Execute
```

Download target:

```text
data/raw/xabarnavis_datasets/_incoming/community_forensics/
```

## 4. Community Forensics Eval

Eval dataset rasmiy sahifasida non-commercial research/educational cheklovi ko‘rsatilgan. Uni train emas, yopiq evaluation sifatida saqlang.

```powershell
powershell -ExecutionPolicy Bypass `
  -File scripts\datasets\download_new_forensics_datasets.ps1 `
  -Dataset community_forensics_eval
```

Download:

```powershell
powershell -ExecutionPolicy Bypass `
  -File scripts\datasets\download_new_forensics_datasets.ps1 `
  -Dataset community_forensics_eval `
  -Execute
```

## 5. HF Midjourney/DALL-E/SD/Nano mix

Cheklangan test download:

```powershell
python scripts\datasets\download_hf_ai_dataset.py `
  --max-per-class 5000
```

To‘liq download:

```powershell
python scripts\datasets\download_hf_ai_dataset.py
```

## 6. CIFAKE, CASIA va ArtiFact

Avval ro‘yxat:

```powershell
python scripts\datasets\download_external_datasets.py --list
```

Download:

```powershell
python scripts\datasets\download_external_datasets.py cifake casia_v2 artifact
```

CIFAKE organization:

```powershell
python scripts\datasets\organize_cifake.py
```

CASIA organization:

```powershell
python scripts\datasets\organize_casia_v2.py
```

## 7. Synthbuster va COCO

```powershell
python scripts\datasets\download_minimum_datasets.py minimum_20gb --extract
```

## 8. GenImage

Official code va dataset ko‘rsatmalarini klonlash:

```powershell
git clone https://github.com/GenImage-Dataset/GenImage.git `
  data\raw\xabarnavis_datasets\_incoming\genimage_official
```

Repo ichidagi rasmiy Google Drive linkidan datasetni yuklang. Google Drive papkasi ruxsat bersa:

```powershell
gdown --folder "https://drive.google.com/drive/folders/1jGt10bwTbhEZuGXLyvrCuxOI0cBqQ1FS" `
  -O data\raw\xabarnavis_datasets\_incoming\genimage
```

Download muvaffaqiyatsiz bo‘lsa brauzer orqali rasmiy linkdan yuklang. Datasetni avtomatik ravishda label papkalariga ko‘chirmang; avval folder sxemasini audit qiling.

## 9. SIDA social-media dataset

```powershell
git clone https://github.com/hzlsaber/SIDA.git `
  data\raw\xabarnavis_datasets\_incoming\sida_official
```

Bu buyruq kod/repozitoriyni oladi. Dataset access va download bo‘yicha aynan rasmiy README ko‘rsatmasiga amal qiling.

## 10. Access-form datasetlar

Quyidagilarni credential yoki formani chetlab o‘tib avtomatik yuklamang:

- FaceForensics++;
- DEFACTO;
- Celeb-DF;
- DFDC;
- ForgeryNet’ning access talab qiladigan qismlari;
- DocTamper.

Rasmiy formani to‘ldiring, ruxsat oling va archive’ni `_incoming` ichiga qo‘ying.

## 11. Har downloaddan keyingi audit

```powershell
Get-ChildItem data\raw\xabarnavis_datasets\_incoming -Recurse -File |
  Measure-Object -Property Length -Sum
```

Archive hash:

```powershell
Get-FileHash -Algorithm SHA256 "PATH\TO\DATASET.zip"
```

Har dataset uchun license/source/revision/checksum yozilmaguncha uni training manifestiga qo‘shmang.

## 12. Organization va clean manifest

Yangi dataset uchun label mapping tekshirilgandan keyin tegishli papkaga ko‘chiring:

```text
real/<dataset>/
ai_generated/<dataset>/<generator>/
manipulated/<dataset>/
```

So‘ng clean manifestni qayta yarating:

```powershell
python scripts\datasets\build_image_3class_manifest.py `
  --balance `
  --metadata-dir-name metadata_3class_clean_v2
```

Trainingni yangi manifest bilan boshlang; oldingi checkpointni yangi dataset kompozitsiyasi bilan resume qilmang.
