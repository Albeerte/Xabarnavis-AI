from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from PIL import Image, UnidentifiedImageError


GENERATOR_HINTS = ("midjourney", "stable diffusion", "dall", "flux", "firefly", "comfyui", "automatic1111")
EDITOR_HINTS = ("photoshop", "lightroom", "canva", "gimp", "affinity", "snapseed")


@dataclass(frozen=True)
class MetadataSignals:
    has_exif: bool
    has_camera_model: bool
    camera_make: str | None
    camera_model: str | None
    captured_at: str | None
    software_tag: str | None
    has_gps: bool
    gps_latitude: float | None
    gps_longitude: float | None
    jpeg_quality: int | None
    anomaly_score: float
    camera_provenance_score: float
    generator_software_score: float
    editor_software_score: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def extract_metadata_signals(image_path: Path) -> MetadataSignals:
    try:
        with Image.open(image_path) as image:
            exif = image.getexif()
            exif_dict = {ExifTags.get(tag, str(tag)): value for tag, value in exif.items()}
            software = _safe_lower(exif_dict.get("Software"))
            camera_make = _safe_text(exif_dict.get("Make"))
            camera_model = exif_dict.get("Model")
            captured_at = _safe_text(exif_dict.get("DateTimeOriginal") or exif_dict.get("DateTime"))
            gps_latitude, gps_longitude = _gps_coordinates(exif_dict.get("GPSInfo"))
            jpeg_quality = _estimate_jpeg_quality(image)
    except (UnidentifiedImageError, OSError):
        return MetadataSignals(False, False, None, None, None, None, False, None, None, None, 1.0, 0.0, 0.0, 0.0)

    has_exif = bool(exif_dict)
    has_camera_model = bool(camera_model)
    has_gps = gps_latitude is not None and gps_longitude is not None
    generator_score = 1.0 if software and any(hint in software for hint in GENERATOR_HINTS) else 0.0
    editor_score = 1.0 if software and any(hint in software for hint in EDITOR_HINTS) else 0.0

    anomaly = 0.0
    if not has_exif:
        anomaly += 0.45
    if has_exif and not has_camera_model:
        anomaly += 0.25
    if generator_score:
        anomaly += 0.40
    if editor_score:
        anomaly += 0.30

    camera_provenance = 1.0 if has_camera_model and not generator_score else 0.0
    return MetadataSignals(
        has_exif=has_exif,
        has_camera_model=has_camera_model,
        camera_make=camera_make,
        camera_model=_safe_text(camera_model),
        captured_at=captured_at,
        software_tag=software,
        has_gps=has_gps,
        gps_latitude=gps_latitude,
        gps_longitude=gps_longitude,
        jpeg_quality=jpeg_quality,
        anomaly_score=round(min(1.0, anomaly), 4),
        camera_provenance_score=camera_provenance,
        generator_software_score=generator_score,
        editor_software_score=editor_score,
    )


def _estimate_jpeg_quality(image: Image.Image) -> int | None:
    quantization = getattr(image, "quantization", None)
    if not quantization:
        return None

    values = [value for table in quantization.values() for value in table]
    if not values:
        return None

    avg = sum(values) / len(values)
    return max(1, min(100, int(100 - avg / 2)))


def _safe_lower(value: object) -> str | None:
    if value is None:
        return None
    return str(value).strip().lower()


def _safe_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _gps_coordinates(raw_gps: object) -> tuple[float | None, float | None]:
    if not isinstance(raw_gps, dict):
        return None, None
    gps = {GpsTags.get(key, key): value for key, value in raw_gps.items()}
    lat = _gps_decimal(gps.get("GPSLatitude"), gps.get("GPSLatitudeRef"))
    lon = _gps_decimal(gps.get("GPSLongitude"), gps.get("GPSLongitudeRef"))
    return lat, lon


def _gps_decimal(value: object, ref: object) -> float | None:
    if not isinstance(value, (tuple, list)) or len(value) != 3:
        return None
    try:
        degrees = float(value[0])
        minutes = float(value[1])
        seconds = float(value[2])
        result = degrees + minutes / 60.0 + seconds / 3600.0
        if str(ref or "").upper() in {"S", "W"}:
            result *= -1
        return round(result, 7)
    except Exception:
        return None


try:
    from PIL.ExifTags import TAGS as ExifTags
    from PIL.ExifTags import GPSTAGS as GpsTags
except ImportError:  # pragma: no cover
    ExifTags = {}
    GpsTags = {}





