from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


_SIGNATURES: tuple[tuple[bytes, str, str], ...] = (
    (b"\xff\xd8\xff", "image/jpeg", "JPEG"),
    (b"\x89PNG\r\n\x1a\n", "image/png", "PNG"),
    (b"GIF87a", "image/gif", "GIF87a"),
    (b"GIF89a", "image/gif", "GIF89a"),
    (b"BM", "image/bmp", "BMP"),
    (b"II*\x00", "image/tiff", "TIFF little-endian"),
    (b"MM\x00*", "image/tiff", "TIFF big-endian"),
)

_EXTENSION_MIME = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".tif": "image/tiff",
    ".tiff": "image/tiff",
    ".webp": "image/webp",
}


@dataclass(frozen=True)
class EvidenceIntake:
    original_filename: str
    stored_filename: str
    file_size: int
    sha256: str
    md5: str
    declared_mime_type: str | None
    detected_mime_type: str
    file_signature: str
    extension_matches_signature: bool
    received_at: str
    analysis_version: str
    original_bytes_preserved: bool
    content_credentials_status: str
    provenance_note: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def inspect_evidence(
    path: Path,
    *,
    original_filename: str,
    declared_mime_type: str | None,
    analysis_version: str,
) -> EvidenceIntake:
    sha256 = hashlib.sha256()
    md5 = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as source:
        header = source.read(64)
        source.seek(0)
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            sha256.update(chunk)
            md5.update(chunk)

    detected_mime, signature = _detect_image_signature(header)
    expected_mime = _EXTENSION_MIME.get(Path(original_filename).suffix.lower())
    extension_matches = expected_mime == detected_mime if expected_mime else False
    c2pa_hint = _has_c2pa_container_hint(path)

    return EvidenceIntake(
        original_filename=original_filename,
        stored_filename=path.name,
        file_size=path.stat().st_size,
        sha256=sha256.hexdigest(),
        md5=md5.hexdigest(),
        declared_mime_type=declared_mime_type,
        detected_mime_type=detected_mime,
        file_signature=signature,
        extension_matches_signature=extension_matches,
        received_at=datetime.now(timezone.utc).isoformat(),
        analysis_version=analysis_version,
        original_bytes_preserved=True,
        content_credentials_status=(
            "manifest_hint_detected_not_cryptographically_verified"
            if c2pa_hint
            else "not_detected"
        ),
        provenance_note=(
            "A possible C2PA/JUMBF container marker was found; cryptographic verification is still required."
            if c2pa_hint
            else "No Content Credentials marker was detected. Absence is not evidence of manipulation or AI generation."
        ),
    )


def _detect_image_signature(header: bytes) -> tuple[str, str]:
    if header.startswith(b"RIFF") and header[8:12] == b"WEBP":
        return "image/webp", "RIFF/WEBP"
    for marker, mime_type, label in _SIGNATURES:
        if header.startswith(marker):
            return mime_type, label
    return "application/octet-stream", "unknown"


def _has_c2pa_container_hint(path: Path) -> bool:
    # This is discovery only, never signature validation. A dedicated C2PA verifier
    # must validate the manifest, claim, assertions, certificate chain and signature.
    markers = (b"c2pa", b"jumb", b"jumd")
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            lowered = chunk.lower()
            if any(marker in lowered for marker in markers):
                return True
    return False
