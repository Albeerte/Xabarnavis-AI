from __future__ import annotations

from django.apps import AppConfig


class DashboardConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "dashboard"
    verbose_name = "Xabarnavis Data"
