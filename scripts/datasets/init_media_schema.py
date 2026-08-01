from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ROOT / "data"
ARTIFACTS_ROOT = ROOT / "artifacts"

MEDIA_TYPES = ("photo", "video", "audio", "text")
ORIGINS = ("external", "milliy")
VERSION = "0.1"

DISPLAY_NAMES = {
    ("photo", "external"): "Xabarnavis External 0.1",
    ("photo", "milliy"): "Xabarnavis Image 0.1",
    ("video", "external"): "Xabarnavis Video External 0.1",
    ("video", "milliy"): "Xabarnavis Video 0.1",
    ("audio", "external"): "Xabarnavis Audio External 0.1",
    ("audio", "milliy"): "Xabarnavis Audio 0.1",
    ("text", "external"): "Xabarnavis Text External 0.1",
    ("text", "milliy"): "Xabarnavis Text 0.1",
}


def dataset_name(media_type: str, origin: str) -> str:
    if origin == "external":
        return f"xabarnavis_{media_type}_external_{VERSION}"
    if media_type == "photo":
        return f"xabarnavis_image_{VERSION}"
    return f"xabarnavis_{media_type}_{VERSION}"


def dataset_leaf_dirs(media_type: str) -> list[str]:
    if media_type == "photo":
        return ["real", "ai_generated", "manipulated", "test_holdout", "masks", "metadata"]
    if media_type == "video":
        return ["real", "ai_generated", "manipulated", "frames", "metadata"]
    if media_type == "audio":
        return ["real", "ai_generated", "manipulated", "features", "metadata"]
    return ["real", "ai_generated", "manipulated", "metadata"]


def build_schema() -> dict[str, object]:
    entries = []
    for media_type in MEDIA_TYPES:
        for origin in ORIGINS:
            name = dataset_name(media_type, origin)
            entries.append(
                {
                    "media_type": media_type,
                    "origin": origin,
                    "name": name,
                    "display_name": DISPLAY_NAMES[(media_type, origin)],
                    "version": VERSION,
                    "raw_path": _rel(DATA_ROOT / "raw" / "xabarnavis_media" / media_type / origin / name),
                    "ready_path": _rel(DATA_ROOT / "ready" / media_type / origin / name),
                    "run_path": _rel(ARTIFACTS_ROOT / "runs" / media_type / origin / name),
                    "model_path": _rel(ARTIFACTS_ROOT / "models" / media_type / origin / name),
                    "leaf_dirs": dataset_leaf_dirs(media_type),
                }
            )
    return {
        "project": "xabarnavis",
        "schema_version": VERSION,
        "description": "Unified media dataset and training artifact layout.",
        "entries": entries,
    }


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def main() -> None:
    schema = build_schema()
    for entry in schema["entries"]:
        raw_root = ROOT / str(entry["raw_path"])
        ready_root = ROOT / str(entry["ready_path"])
        run_root = ROOT / str(entry["run_path"])
        model_root = ROOT / str(entry["model_path"])

        for leaf_dir in entry["leaf_dirs"]:
            (raw_root / str(leaf_dir)).mkdir(parents=True, exist_ok=True)
        ready_root.mkdir(parents=True, exist_ok=True)
        run_root.mkdir(parents=True, exist_ok=True)
        model_root.mkdir(parents=True, exist_ok=True)
        (raw_root / "schema.json").write_text(json.dumps(entry, indent=2), encoding="utf-8")

    schema_root = DATA_ROOT / "raw" / "xabarnavis_media"
    schema_root.mkdir(parents=True, exist_ok=True)
    (schema_root / "schema.json").write_text(json.dumps(schema, indent=2), encoding="utf-8")
    print(f"Media schema initialized at: {schema_root}")


if __name__ == "__main__":
    main()
