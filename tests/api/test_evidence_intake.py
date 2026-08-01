from pathlib import Path

from app.services.evidence_intake import inspect_evidence


def test_inspect_evidence_records_hashes_and_signature(tmp_path: Path) -> None:
    path = tmp_path / "evidence.png"
    payload = b"\x89PNG\r\n\x1a\n" + b"forensic-test-payload"
    path.write_bytes(payload)

    result = inspect_evidence(
        path,
        original_filename="evidence.png",
        declared_mime_type="image/png",
        analysis_version="test-1",
    )

    assert result.detected_mime_type == "image/png"
    assert result.extension_matches_signature is True
    assert result.file_size == len(payload)
    assert len(result.sha256) == 64
    assert len(result.md5) == 32
    assert result.original_bytes_preserved is True
    assert result.content_credentials_status == "not_detected"


def test_extension_mismatch_is_explicit(tmp_path: Path) -> None:
    path = tmp_path / "renamed.jpg"
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + b"payload")

    result = inspect_evidence(
        path,
        original_filename="renamed.jpg",
        declared_mime_type="image/jpeg",
        analysis_version="test-1",
    )

    assert result.detected_mime_type == "image/png"
    assert result.extension_matches_signature is False
