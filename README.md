# Xabarnavis AI Forensic Platform

Xabarnavis is a research and product platform for media authenticity analysis across image, audio, video, and text. It combines forensic signals, AI model outputs, explainable scoring, report generation, and a web dashboard.

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py runserver
```

Open:

- Website: `http://127.0.0.1:3000`
- API health: `http://127.0.0.1:8000/health`
- Swagger UI: `http://127.0.0.1:8000/docs`

Backend only:

```powershell
cd apps\api
python -m uvicorn app.main:app --reload --port 8000
```

Frontend only:

```powershell
cd apps\web
pnpm install
pnpm dev
```

## Repository Rules

Git should contain source code, documentation, manifests, and lightweight metadata only. Large generated folders are local artifacts and are ignored:

- `apps/web/node_modules/` and `apps/web/.next/`
- `data/raw/`, `data/processed/`, `data/ready/`, `data/holdout/`
- `artifacts/models/`, `artifacts/runs/`, `artifacts/reports/`
- `storage/uploads/`, `storage/reports/`, `storage/profiles/`

Track datasets and models through:

- `docs/datasets.md`
- `docs/model_benchmarks.md`
- `ml/registry/models_registry.json`
- `storage/dataset_inventory.json`
- `scripts/datasets/`

## Project Layout

```text
apps/
  api/                    FastAPI backend
  web/                    Next.js frontend
ml/
  registry/               model registry and model-family metadata
  image/ audio/ video/    research adapters, configs, train/eval areas
data/                     local datasets, ignored by Git
artifacts/                model weights, runs, reports, logs, ignored by Git
storage/                  runtime uploads, reports, profiles, temp files
infra/                    Docker, nginx, postgres, systemd, deploy scripts
scripts/
  datasets/               dataset download, organize, inventory scripts
  training/               training scripts
  evaluation/             smoke/evaluation scripts
docs/                     architecture, API, dataset, security, deploy docs
database/                 PostgreSQL schema and future migrations
tests/                    api, ml, frontend, e2e test groups
```

## Current Capabilities

- Image upload and forensic analysis
- EXIF and metadata anomaly checks
- ELA, residual heatmap, frequency/noise heuristics
- Local and external model registry
- Audio/video/text analysis endpoints
- JSON and DOCX report generation
- Dashboard and report pages in Next.js
- PostgreSQL target schema with SQLite local development fallback

## Model Training

Start with the [step-by-step image training workflow](docs/step_by_step_image_training.md), then use the [full image dataset and training guide](docs/training_guide.md) for dataset strategy, licensing, localization, calibration, and release metrics.

The [full dataset, model, and storage architecture](docs/xabarnavis_full_dataset_architecture_uz.md) defines the production folder tree, dataset budgets, model inputs/outputs, checkpoint sizes, and RTX 5070 training settings.

For the strongest included binary image baseline, use `scripts/training/train_image_forensics_advanced.py` or its PowerShell launcher. It combines a pretrained ConvNeXt-Tiny RGB encoder with an FFT spectral branch, robust degradation augmentation, EMA, warmup/cosine scheduling, and per-source/per-generator evaluation.

Use the [all-existing-datasets training guide](docs/train_all_existing_datasets_uz.md) for the balanced 335k three-class run or the literal all-files run.

## Production Target

```text
User
  -> Next.js frontend
  -> FastAPI backend
  -> PostgreSQL + Redis
  -> Worker pipeline
  -> AI models
  -> PDF/DOCX official report
  -> QR/public report page
```

## Important Forensic Language

Reports should avoid absolute claims such as "100% fake". Use probability and confidence language:

> The image is highly likely to be AI-generated. This conclusion is based on visual, frequency-domain, metadata, and model-based forensic indicators.


