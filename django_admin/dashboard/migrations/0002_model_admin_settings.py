from __future__ import annotations

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("dashboard", "0001_aux_tables"),
    ]

    operations = [
        migrations.RunSQL(
            """
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
