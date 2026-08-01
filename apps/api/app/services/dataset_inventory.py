from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
STORAGE_DIR = ROOT / "storage"
INVENTORY_PATH = STORAGE_DIR / "dataset_inventory.json"


def load_dataset_inventory(path: Path = INVENTORY_PATH) -> dict[str, Any]:
    if not path.is_file():
        return {
            "status": "not_calculated",
            "language": "uz",
            "note_uz": (
                "Datasetlar soni hali hisoblanmagan. Yangilash uchun "
                "`python scripts\\datasets\\count_image_datasets.py` buyrug'ini ishga tushiring."
            ),
        }

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "status": "error",
            "language": "uz",
            "error": str(exc),
            "note_uz": "Dataset inventory cache faylini o'qib bo'lmadi.",
        }

    if isinstance(payload, dict):
        payload.setdefault("language", "uz")
        return payload
    return {
        "status": "error",
        "language": "uz",
        "note_uz": "Dataset inventory cache noto'g'ri formatda.",
    }





