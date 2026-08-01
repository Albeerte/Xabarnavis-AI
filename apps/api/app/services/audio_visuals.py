from __future__ import annotations

from pathlib import Path
from typing import Any


def create_audio_artifacts(audio_path: Path, artifact_dir: Path, case_id: int, model_results: list[dict[str, Any]]) -> dict[str, str]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    waveform_path = artifact_dir / f"case-{case_id}-audio-waveform.png"
    timeline_path = artifact_dir / f"case-{case_id}-audio-timeline.png"
    segments = _segments_from_results(model_results)

    try:
        _plot_waveform(audio_path, segments, waveform_path)
    except Exception as exc:
        _plot_placeholder(waveform_path, "Audio waveform unavailable", f"The stored audio could not be decoded: {exc}")
    try:
        _plot_timeline(segments, timeline_path)
    except Exception as exc:
        _plot_placeholder(timeline_path, "Audio timeline unavailable", str(exc))

    artifacts: dict[str, str] = {}
    if waveform_path.is_file():
        artifacts["audio_waveform_path"] = str(waveform_path)
    if timeline_path.is_file():
        artifacts["audio_timeline_path"] = str(timeline_path)
    return artifacts


def _plot_waveform(audio_path: Path, segments: list[dict[str, Any]], output_path: Path) -> None:
    import librosa
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    y, sr = librosa.load(str(audio_path), sr=16000, mono=True)
    if len(y) == 0:
        raise ValueError("empty audio")

    duration = len(y) / sr
    max_points = 6000
    step = max(1, len(y) // max_points)
    sampled = y[::step]
    times = np.arange(len(sampled)) * step / sr

    fig, ax = plt.subplots(figsize=(13, 5), dpi=140)
    fig.patch.set_facecolor("#101720")
    ax.set_facecolor("#101720")

    ax.fill_between(times, sampled, 0, color="#2f8cff", alpha=0.16)
    ax.plot(times, sampled, color="#75b7ff", linewidth=1.0, alpha=0.95)

    for segment in segments:
        ai_score = _number(segment.get("ai_score"))
        if ai_score is None:
            continue
        start = _number(segment.get("start_seconds")) or 0.0
        end = _number(segment.get("end_seconds")) or start
        if ai_score >= 0.55:
            color = "#ff5f56" if ai_score >= 0.70 else "#f59e0b"
            ax.axvspan(start, end, color=color, alpha=0.22)
            ax.text(
                (start + end) / 2,
                0.92,
                f"{round(ai_score * 100)}% AI",
                color=color,
                fontsize=8,
                ha="center",
                va="top",
                transform=ax.get_xaxis_transform(),
            )

    ax.axhline(0, color="#334155", linewidth=0.8)
    ax.set_xlim(0, max(duration, 1))
    ax.set_title("Xabarnavis AI + Jabberjay Audio Forensic Waveform", color="#e5eef8", fontsize=18, pad=18)
    ax.set_xlabel("Time", color="#94a3b8")
    ax.set_ylabel("Amplitude", color="#94a3b8")
    ax.tick_params(colors="#94a3b8", labelsize=9)
    for spine in ax.spines.values():
        spine.set_color("#263241")
    ax.grid(color="#263241", linewidth=0.6, alpha=0.65)
    _add_model_chips(ax)
    fig.tight_layout()
    fig.savefig(output_path, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


def _plot_timeline(segments: list[dict[str, Any]], output_path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(13, 2.8), dpi=140)
    fig.patch.set_facecolor("#101720")
    ax.set_facecolor("#101720")

    if not segments:
        ax.text(0.5, 0.5, "No segment timeline available", color="#94a3b8", ha="center", va="center", transform=ax.transAxes)
        ax.set_axis_off()
    else:
        for segment in segments:
            start = _number(segment.get("start_seconds")) or 0.0
            end = _number(segment.get("end_seconds")) or start + 1.0
            ai_score = _number(segment.get("ai_score")) or 0.0
            color = "#ff5f56" if ai_score >= 0.70 else "#f59e0b" if ai_score >= 0.55 else "#2f8cff"
            ax.barh(0, end - start, left=start, height=0.36, color=color, alpha=0.85)
            ax.text((start + end) / 2, 0, f"{round(ai_score * 100)}%", color="#f8fafc", fontsize=8, fontweight="bold", ha="center", va="center")
        max_end = max((_number(item.get("end_seconds")) or 0 for item in segments), default=1)
        ax.set_xlim(0, max(max_end, 1))
        ax.set_yticks([])
        ax.set_xlabel("Audio time segments: blue=bonafide leaning, amber/red=AI or spoof suspicious", color="#94a3b8")
        ax.tick_params(colors="#94a3b8", labelsize=9)
        for spine in ax.spines.values():
            spine.set_color("#263241")
        ax.grid(axis="x", color="#263241", linewidth=0.6, alpha=0.65)
    ax.set_title("Segment Timeline: Possible AI/Spoof Regions", color="#e5eef8", fontsize=15, pad=12)
    fig.tight_layout()
    fig.savefig(output_path, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


def _plot_placeholder(output_path: Path, title: str, message: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(13, 3.6), dpi=140)
    fig.patch.set_facecolor("#101720")
    ax.set_facecolor("#101720")
    ax.text(0.5, 0.62, title, color="#e5eef8", fontsize=18, fontweight="bold", ha="center", va="center", transform=ax.transAxes)
    ax.text(0.5, 0.42, message[:180], color="#94a3b8", fontsize=10, ha="center", va="center", transform=ax.transAxes)
    ax.text(0.5, 0.24, "New audio analyses will generate waveform and AI/Spoof segment visuals when the audio codec is readable.", color="#64748b", fontsize=9, ha="center", va="center", transform=ax.transAxes)
    ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(output_path, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


def _segments_from_results(model_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for preferred_id in ("xabarnavis_audio_0_2", "jabberjay"):
        segments = _segments_for_model(model_results, preferred_id)
        if segments:
            return segments
    return []


def _segments_for_model(model_results: list[dict[str, Any]], model_id: str) -> list[dict[str, Any]]:
    for result in model_results:
        if result.get("model_id") != model_id:
            continue
        details = result.get("details") or {}
        if not isinstance(details, dict):
            return []
        segments = details.get("segment_analysis") or []
        return [item for item in segments if isinstance(item, dict)]
    return []


def _add_model_chips(ax: Any) -> None:
    labels = ["HuBERT", "Wav2Vec2", "WavLM", "AST", "ViT", "RawNet2", "Classical"]
    for index, label in enumerate(labels):
        ax.text(
            0.10 + index * 0.13,
            1.06,
            label,
            transform=ax.transAxes,
            fontsize=8,
            color="#9ca3af",
            ha="center",
            va="center",
            bbox={"boxstyle": "round,pad=0.35,rounding_size=0.08", "facecolor": "#202832", "edgecolor": "#334155", "alpha": 0.9},
        )


def _number(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None





