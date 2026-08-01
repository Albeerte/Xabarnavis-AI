from __future__ import annotations

import os
from datetime import datetime

from django.core.management.base import BaseCommand

from dashboard.models import ModelAdminSetting


def infer_media_type(model_id: str, family: str, local_path: str | None) -> str:
    text = " ".join([model_id, family, local_path or ""]).lower()
    if "audio" in text or "jabberjay" in text or "rawgat" in text or "spectra" in text:
        return "audio"
    if "video" in text or "genconvit" in text or "deepfakebench" in text or "faceforensics" in text:
        return "video"
    if "text" in text:
        return "text"
    return "photo"


class Command(BaseCommand):
    help = "Sync registered FastAPI models into Django admin model controls."

    def handle(self, *args, **options) -> None:
        os.environ["XABARNAVIS_IGNORE_MODEL_ADMIN_SETTINGS"] = "1"
        from app.services.model_registry import ModelRegistry

        now = datetime.now().isoformat(timespec="seconds")
        registry = ModelRegistry()
        created = 0
        updated = 0
        for index, model in enumerate(registry.list_models(), start=1):
            defaults = {
                "display_name": model.name,
                "family": model.family,
                "media_type": infer_media_type(model.id, model.family, model.local_path),
                "status_snapshot": model.status,
                "purpose": model.purpose,
                "repository": model.repository or "",
                "local_path": model.local_path or "",
                "sort_order": index,
                "updated_at": now,
            }
            obj, was_created = ModelAdminSetting.objects.get_or_create(
                model_id=model.id,
                defaults={**defaults, "enabled": True, "created_at": now},
            )
            if was_created:
                created += 1
                continue
            for key, value in defaults.items():
                if key == "display_name" and obj.display_name and obj.display_name != model.name:
                    continue
                setattr(obj, key, value)
            obj.save()
            updated += 1

        self.stdout.write(self.style.SUCCESS(f"Synced model controls: created={created}, updated={updated}"))
