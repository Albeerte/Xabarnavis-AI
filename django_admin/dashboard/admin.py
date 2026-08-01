from __future__ import annotations

from django.contrib import admin

from .models import (
    ForensicFeature,
    ImageAnalysis,
    ImageCase,
    ManipulationMask,
    ModelAdminSetting,
    ReportFile,
    UserSession,
    XabarnavisUser,
)


@admin.register(XabarnavisUser)
class XabarnavisUserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "first_name", "last_name", "email", "role", "organization", "created_at")
    search_fields = ("username", "first_name", "last_name", "email", "organization", "role")
    list_filter = ("role", "organization")
    readonly_fields = ("id", "password_hash", "created_at")


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "ip_address", "browser", "os", "device_type", "login_at", "logout_at", "last_active_at")
    search_fields = ("user__username", "ip_address", "browser", "os", "device_name", "user_agent")
    list_filter = ("browser", "os", "device_type")
    readonly_fields = ("token", "created_at")


@admin.register(ImageCase)
class ImageCaseAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "media_type", "original_filename", "status", "uploaded_at")
    search_fields = ("original_filename", "file_hash", "stored_path", "user__username")
    list_filter = ("media_type", "status")
    readonly_fields = ("id", "file_hash", "uploaded_at")


@admin.register(ImageAnalysis)
class ImageAnalysisAdmin(admin.ModelAdmin):
    list_display = ("id", "case", "final_verdict", "confidence", "real_score", "ai_score", "manipulated_score", "model_version", "created_at")
    search_fields = ("case__original_filename", "final_verdict", "confidence", "report_path", "model_version")
    list_filter = ("final_verdict", "confidence", "model_version")
    readonly_fields = ("id", "created_at")


@admin.register(ReportFile)
class ReportFileAdmin(admin.ModelAdmin):
    list_display = ("id", "case", "json_path", "docx_path", "pdf_path", "created_at")
    search_fields = ("json_path", "docx_path", "pdf_path", "case__original_filename")
    readonly_fields = ("id", "created_at")


@admin.register(ForensicFeature)
class ForensicFeatureAdmin(admin.ModelAdmin):
    list_display = ("id", "case", "jpeg_quality", "has_camera_model", "software_tag", "metadata_anomaly_score", "frequency_anomaly_score")
    search_fields = ("case__original_filename", "software_tag", "exif_json")
    list_filter = ("has_camera_model",)


@admin.register(ManipulationMask)
class ManipulationMaskAdmin(admin.ModelAdmin):
    list_display = ("id", "case", "mask_path", "heatmap_path", "edited_area_percent")
    search_fields = ("case__original_filename", "mask_path", "heatmap_path")


@admin.register(ModelAdminSetting)
class ModelAdminSettingAdmin(admin.ModelAdmin):
    list_display = ("sort_order", "model_id", "display_name", "enabled", "media_type", "family", "status_snapshot")
    list_display_links = ("model_id",)
    list_editable = ("display_name", "enabled", "sort_order")
    search_fields = ("model_id", "display_name", "family", "purpose", "repository", "local_path")
    list_filter = ("enabled", "media_type", "family", "status_snapshot")
    readonly_fields = ("model_id", "family", "media_type", "status_snapshot", "purpose", "repository", "local_path", "created_at", "updated_at")
    actions = ("enable_models", "disable_models")

    @admin.action(description="Enable selected models")
    def enable_models(self, request, queryset):
        queryset.update(enabled=True)

    @admin.action(description="Disable selected models")
    def disable_models(self, request, queryset):
        queryset.update(enabled=False)
