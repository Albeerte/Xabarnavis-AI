from __future__ import annotations

from django.db import models


class XabarnavisUser(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, unique=True)
    password_hash = models.TextField()
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=64, blank=True)
    organization = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    avatar_path = models.TextField(blank=True, null=True)
    created_at = models.CharField(max_length=64, blank=True)

    class Meta:
        managed = False
        db_table = "users"
        verbose_name = "User profile"
        verbose_name_plural = "User profiles"

    def __str__(self) -> str:
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.username


class UserSession(models.Model):
    token = models.TextField(primary_key=True)
    user = models.ForeignKey(XabarnavisUser, db_column="user_id", on_delete=models.DO_NOTHING)
    expires_at = models.CharField(max_length=64)
    ip_address = models.CharField(max_length=255, blank=True)
    user_agent = models.TextField(blank=True)
    browser = models.CharField(max_length=120, blank=True)
    os = models.CharField(max_length=120, blank=True)
    device_type = models.CharField(max_length=80, blank=True)
    device_name = models.CharField(max_length=255, blank=True)
    login_at = models.CharField(max_length=64, blank=True)
    logout_at = models.CharField(max_length=64, blank=True, null=True)
    last_active_at = models.CharField(max_length=64, blank=True)
    created_at = models.CharField(max_length=64, blank=True)

    class Meta:
        managed = False
        db_table = "user_sessions"
        verbose_name = "Login history"
        verbose_name_plural = "Login history"

    def __str__(self) -> str:
        return f"{self.user} - {self.login_at}"


class ImageCase(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(XabarnavisUser, db_column="user_id", on_delete=models.DO_NOTHING, null=True, blank=True)
    original_filename = models.TextField()
    stored_path = models.TextField()
    file_hash = models.TextField()
    status = models.CharField(max_length=80)
    media_type = models.CharField(max_length=80)
    uploaded_at = models.CharField(max_length=64, blank=True)

    class Meta:
        managed = False
        db_table = "image_cases"
        verbose_name = "Media case"
        verbose_name_plural = "Media cases"

    def __str__(self) -> str:
        return f"#{self.id} {self.media_type}: {self.original_filename}"


class ImageAnalysis(models.Model):
    id = models.AutoField(primary_key=True)
    case = models.ForeignKey(ImageCase, db_column="case_id", on_delete=models.DO_NOTHING)
    real_score = models.FloatField()
    ai_score = models.FloatField()
    manipulated_score = models.FloatField()
    final_verdict = models.CharField(max_length=255)
    confidence = models.CharField(max_length=100)
    reasons_json = models.TextField()
    model_results_json = models.TextField()
    report_path = models.TextField()
    model_version = models.CharField(max_length=120)
    created_at = models.CharField(max_length=64, blank=True)

    class Meta:
        managed = False
        db_table = "image_analysis"
        verbose_name = "User report"
        verbose_name_plural = "User reports"

    def __str__(self) -> str:
        return f"Report #{self.id} for case #{self.case_id}: {self.final_verdict}"


class ReportFile(models.Model):
    id = models.AutoField(primary_key=True)
    case = models.ForeignKey(ImageCase, db_column="case_id", on_delete=models.DO_NOTHING)
    pdf_path = models.TextField(blank=True, null=True)
    docx_path = models.TextField(blank=True, null=True)
    json_path = models.TextField(blank=True, null=True)
    created_at = models.CharField(max_length=64, blank=True)

    class Meta:
        managed = False
        db_table = "reports"
        verbose_name = "Report file"
        verbose_name_plural = "Report files"

    def __str__(self) -> str:
        return f"Files for case #{self.case_id}"


class ForensicFeature(models.Model):
    id = models.AutoField(primary_key=True)
    case = models.ForeignKey(ImageCase, db_column="case_id", on_delete=models.DO_NOTHING)
    exif_json = models.TextField(blank=True, null=True)
    jpeg_quality = models.FloatField(blank=True, null=True)
    has_camera_model = models.BooleanField(blank=True, null=True)
    software_tag = models.TextField(blank=True, null=True)
    metadata_anomaly_score = models.FloatField(blank=True, null=True)
    frequency_anomaly_score = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "forensic_features"
        verbose_name = "Forensic feature"
        verbose_name_plural = "Forensic features"

    def __str__(self) -> str:
        return f"Forensic features for case #{self.case_id}"


class ManipulationMask(models.Model):
    id = models.AutoField(primary_key=True)
    case = models.ForeignKey(ImageCase, db_column="case_id", on_delete=models.DO_NOTHING)
    mask_path = models.TextField(blank=True, null=True)
    heatmap_path = models.TextField(blank=True, null=True)
    edited_area_percent = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "manipulation_masks"
        verbose_name = "Manipulation mask"
        verbose_name_plural = "Manipulation masks"

    def __str__(self) -> str:
        return f"Mask for case #{self.case_id}"


class ModelAdminSetting(models.Model):
    model_id = models.CharField(max_length=160, primary_key=True)
    display_name = models.CharField(max_length=255)
    enabled = models.BooleanField(default=True)
    family = models.CharField(max_length=160, blank=True)
    media_type = models.CharField(max_length=80, blank=True)
    status_snapshot = models.CharField(max_length=160, blank=True)
    purpose = models.TextField(blank=True)
    repository = models.TextField(blank=True)
    local_path = models.TextField(blank=True)
    sort_order = models.IntegerField(default=1000)
    created_at = models.CharField(max_length=64, blank=True)
    updated_at = models.CharField(max_length=64, blank=True)

    class Meta:
        managed = False
        db_table = "model_admin_settings"
        ordering = ("sort_order", "model_id")
        verbose_name = "Model control"
        verbose_name_plural = "Model controls"

    def __str__(self) -> str:
        state = "enabled" if self.enabled else "disabled"
        return f"{self.display_name} ({state})"
