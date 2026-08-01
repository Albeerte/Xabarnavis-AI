from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    real_score: float = Field(ge=0, le=1)
    ai_score: float = Field(ge=0, le=1)
    manipulated_score: float = Field(ge=0, le=1)
    metadata_anomaly_score: float = Field(ge=0, le=1)
    frequency_anomaly_score: float = Field(ge=0, le=1)
    jpeg_blocking_score: float = Field(ge=0, le=1)
    ela_anomaly_score: float = Field(ge=0, le=1)


class ForensicArtifacts(BaseModel):
    ela_image_path: str | None = None
    heatmap_path: str | None = None
    anomaly_overlay_path: str | None = None
    anomaly_regions: list[dict] = Field(default_factory=list)


class EvidenceIntakeResponse(BaseModel):
    file_size: int = Field(ge=0)
    md5: str
    declared_mime_type: str | None = None
    detected_mime_type: str
    file_signature: str
    extension_matches_signature: bool
    received_at: str
    analysis_version: str
    original_bytes_preserved: bool
    content_credentials_status: str
    provenance_note: str


class ModelInfoResponse(BaseModel):
    id: str
    name: str
    family: str
    purpose: str
    status: str
    repository: str | None = None
    local_path: str | None = None


class ModelRunResponse(BaseModel):
    model_id: str
    name: str
    status: str
    verdict: str
    ai_score: float | None = None
    real_score: float | None = None
    manipulated_score: float | None = None
    confidence: str | None = None
    details: dict | None = None
    error: str | None = None


class ModelListResponse(BaseModel):
    models: list[ModelInfoResponse]


class AnalysisResponse(BaseModel):
    case_id: int
    original_filename: str
    file_hash: str
    evidence_intake: EvidenceIntakeResponse
    final_verdict: str
    confidence: str
    scores: ScoreBreakdown
    detected_signs: list[str]
    artifacts: ForensicArtifacts
    report_path: str
    report_docx_path: str | None = None
    model_version: str
    selected_models: list[str] = Field(default_factory=list)
    model_results: list[ModelRunResponse] = Field(default_factory=list)


class CaseSummary(BaseModel):
    id: int
    original_filename: str
    file_hash: str
    status: str
    media_type: str = "image"
    uploaded_at: str
    real_score: float | None = None
    ai_score: float | None = None
    manipulated_score: float | None = None
    final_verdict: str | None = None
    confidence: str | None = None
    model_results_json: str | None = None
    report_path: str | None = None
    model_version: str | None = None


class CaseListResponse(BaseModel):
    cases: list[CaseSummary]


class MediaAnalysisResponse(BaseModel):
    case_id: int
    media_type: str
    original_filename: str
    file_hash: str
    final_verdict: str
    confidence: str
    scores: dict[str, float]
    detected_signs: list[str]
    report_path: str
    report_docx_path: str | None = None
    model_version: str




