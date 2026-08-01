from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.services.metadata import MetadataSignals
from app.services.external_paths import external_model_path


ROOT = Path(__file__).resolve().parents[4]
OSINT_REPO = external_model_path("photo", "awesome_osint_arsenal")
TOOLS_JSON = OSINT_REPO / "tools.json"

CURATED_URLS = {
    "TinEye": "https://tineye.com/",
    "Yandex Images": "https://yandex.com/images",
    "ExifTool": "https://exiftool.org/",
    "FotoForensics": "https://fotoforensics.com/",
    "InVID": "https://www.invid-project.eu/",
}

IMPORTANT_TOOLS = {
    "TinEye",
    "Google Reverse Image",
    "Yandex Images",
    "Open-Source Intelligence (Reverse Image)",
    "ExifTool",
    "FotoForensics",
    "Metadata2Go",
    "Get-Metadata.com",
    "InVID",
}


def osint_status() -> str:
    return "ready" if TOOLS_JSON.is_file() else "not installed"


def build_image_osint_analysis(
    *,
    original_filename: str,
    file_hash: str,
    metadata: MetadataSignals,
    signals: Any | None = None,
) -> dict[str, Any]:
    tools = _load_relevant_tools()
    reverse_tools = [item for item in tools if item["purpose"] == "reverse_image"]
    metadata_tools = [item for item in tools if item["purpose"] == "metadata"]
    forensic_tools = [item for item in tools if item["purpose"] == "forensics"]
    geolocation_tools = [item for item in tools if item["purpose"] == "geolocation"]

    automated_checks = _automated_checks(original_filename, file_hash, metadata, signals)

    return {
        "source_repository": "https://github.com/rawfilejson/awesome-osint-arsenal",
        "local_path": str(OSINT_REPO),
        "status": osint_status(),
        "scope": "image_osint_enrichment",
        "evidence": {
            "filename": original_filename,
            "sha256": file_hash,
            "camera_make": metadata.camera_make,
            "camera_model": metadata.camera_model,
            "captured_at": metadata.captured_at,
            "software_tag": metadata.software_tag,
            "has_exif": metadata.has_exif,
            "has_gps": metadata.has_gps,
            "gps_latitude": metadata.gps_latitude,
            "gps_longitude": metadata.gps_longitude,
        },
        "tools": {
            "reverse_image": reverse_tools,
            "metadata": metadata_tools,
            "forensics": forensic_tools,
            "geolocation": geolocation_tools,
        },
        "automated_checks": automated_checks,
        "checklist": automated_checks,
        "legal_note": (
            "Xabarnavis OSINT bo'limida lokal metadata, GPS, hash, ELA, shovqin va forensic signal tekshiruvlari avtomatik bajarildi. "
            "Reverse-image qidiruv servislariga dalil faylini avtomatik yuborish maxfiylik sababli o'chirilgan; hisobotda faqat tayyor tashqi tekshiruv linklari saqlanadi."
        ),
    }


def _load_relevant_tools() -> list[dict[str, str]]:
    # Keep the report focused on image verification. The upstream arsenal has hundreds
    # of tools, many for disks, firmware, archives, or web pages, which are noisy here.
    return _fallback_tools()


def _automated_checks(
    original_filename: str,
    file_hash: str,
    metadata: MetadataSignals,
    signals: Any | None,
) -> list[str]:
    checks = [
        f"SHA-256 tekshirildi: {file_hash}. Dalil fayli '{original_filename}' shu hash orqali identifikatsiya qilindi.",
        "EXIF metadata tekshirildi: mavjud." if metadata.has_exif else "EXIF metadata tekshirildi: topilmadi.",
        f"Kamera modeli tekshirildi: {metadata.camera_model}." if metadata.camera_model else "Kamera modeli tekshirildi: topilmadi.",
        f"Kamera ishlab chiqaruvchisi tekshirildi: {metadata.camera_make}." if metadata.camera_make else "Kamera ishlab chiqaruvchisi tekshirildi: topilmadi.",
        f"Rasmga olingan vaqt tekshirildi: {metadata.captured_at}." if metadata.captured_at else "Rasmga olingan vaqt tekshirildi: EXIF ichida topilmadi.",
        f"Dasturiy tag tekshirildi: {metadata.software_tag}." if metadata.software_tag else "Dasturiy tag tekshirildi: topilmadi.",
        f"JPEG sifati hisoblandi: {metadata.jpeg_quality}." if metadata.jpeg_quality is not None else "JPEG sifati tekshirildi: aniqlanmadi.",
        (
            f"GPS metadata tekshirildi: {metadata.gps_latitude}, {metadata.gps_longitude}."
            if metadata.has_gps
            else "GPS metadata tekshirildi: koordinata topilmadi."
        ),
        (
            "AI generator software izi tekshirildi: EXIF ichida generator nomi topildi."
            if metadata.generator_software_score > 0
            else "AI generator software izi tekshirildi: EXIF ichida generator nomi topilmadi."
        ),
        (
            "Tahrir software izi tekshirildi: EXIF ichida editor nomi topildi."
            if metadata.editor_software_score > 0
            else "Tahrir software izi tekshirildi: EXIF ichida editor nomi topilmadi."
        ),
    ]
    if signals is not None:
        checks.extend(
            [
                f"ELA signali avtomatik hisoblandi: {round(float(getattr(signals, 'ela_anomaly_score', 0.0)) * 100)}%.",
                f"Shovqin nomuvofiqligi avtomatik hisoblandi: {round(float(getattr(signals, 'noise_inconsistency_score', 0.0)) * 100)}%.",
                f"JPEG bloklanish signali avtomatik hisoblandi: {round(float(getattr(signals, 'jpeg_blocking_score', 0.0)) * 100)}%.",
                f"Chastota anomaliyasi avtomatik hisoblandi: {round(float(getattr(signals, 'frequency_anomaly_score', 0.0)) * 100)}%.",
            ]
        )
    checks.append("Reverse-image qidiruv uchun TinEye, Google Images va Yandex havolalari tayyorlandi; maxfiylik uchun rasm tashqi servisga avtomatik yuborilmadi.")
    checks.append("Source verification bo'limi tayyorlandi: URL, screenshot va vaqt dalillari reportga qo'shish uchun alohida saqlanishi mumkin.")
    return checks


def _purpose(name: str, category: str, description: str) -> str:
    lower = f"{name} {category} {description}".lower()
    if any(token in lower for token in ("reverse image", "yandex images", "tineye", "google reverse", "oosint")):
        return "reverse_image"
    if any(token in lower for token in ("metadata", "exif", "exiftool")):
        return "metadata"
    if any(token in lower for token in ("fotoforensics", "ela", "invid", "verification")):
        return "forensics"
    if "geo" in lower or "map" in lower:
        return "geolocation"
    return "reference"


def _purpose_order(purpose: str) -> int:
    return {"reverse_image": 0, "metadata": 1, "forensics": 2, "geolocation": 3}.get(purpose, 9)


def _install_text(value: Any) -> str:
    if not isinstance(value, dict):
        return ""
    return str(value.get("raw") or value.get("kali") or value.get("method") or "")


def _fallback_tools() -> list[dict[str, str]]:
    return [
        {"name": "TinEye", "purpose": "reverse_image", "description": "Reverse image search", "url": "https://tineye.com/", "install": "web", "source": "curated"},
        {"name": "Google Reverse Image", "purpose": "reverse_image", "description": "Google image search", "url": "https://images.google.com/", "install": "web", "source": "curated"},
        {"name": "Yandex Images", "purpose": "reverse_image", "description": "Strong reverse image search for faces and places", "url": "https://yandex.com/images", "install": "web", "source": "curated"},
        {"name": "OOSINT Reverse Image", "purpose": "reverse_image", "description": "Combined reverse-image search", "url": "https://oosint.com", "install": "web", "source": "curated"},
        {"name": "ExifTool", "purpose": "metadata", "description": "Complete metadata extraction", "url": "https://exiftool.org/", "install": "apt install libimage-exiftool-perl", "source": "curated"},
        {"name": "Metadata2Go", "purpose": "metadata", "description": "Online metadata extractor", "url": "https://www.metadata2go.com", "install": "web", "source": "curated"},
        {"name": "FotoForensics", "purpose": "forensics", "description": "Image forensic ELA review", "url": "https://fotoforensics.com/", "install": "web", "source": "curated"},
        {"name": "InVID", "purpose": "forensics", "description": "Image/video verification toolkit", "url": "https://www.invid-project.eu/", "install": "browser extension", "source": "curated"},
    ]





