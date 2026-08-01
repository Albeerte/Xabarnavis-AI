from __future__ import annotations

from django.db import migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.RunSQL(
            """
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER NOT NULL,
                pdf_path TEXT,
                docx_path TEXT,
                json_path TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS forensic_features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER NOT NULL,
                exif_json TEXT,
                jpeg_quality REAL,
                has_camera_model INTEGER,
                software_tag TEXT,
                metadata_anomaly_score REAL,
                frequency_anomaly_score REAL
            );
            CREATE TABLE IF NOT EXISTS manipulation_masks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER NOT NULL,
                mask_path TEXT,
                heatmap_path TEXT,
                edited_area_percent REAL
            );
            CREATE TABLE IF NOT EXISTS model_admin_settings (
                model_id TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                enabled INTEGER NOT NULL DEFAULT 1,
                family TEXT NOT NULL DEFAULT '',
                media_type TEXT NOT NULL DEFAULT '',
                status_snapshot TEXT NOT NULL DEFAULT '',
                purpose TEXT NOT NULL DEFAULT '',
                repository TEXT NOT NULL DEFAULT '',
                local_path TEXT NOT NULL DEFAULT '',
                sort_order INTEGER NOT NULL DEFAULT 1000,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """,
            reverse_sql=migrations.RunSQL.noop,
        )
    ]
