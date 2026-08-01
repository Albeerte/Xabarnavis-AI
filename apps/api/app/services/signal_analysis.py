from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps, UnidentifiedImageError


@dataclass(frozen=True)
class ImageSignalScores:
    frequency_anomaly_score: float
    texture_uniformity_score: float
    noise_inconsistency_score: float
    edge_inconsistency_score: float
    jpeg_blocking_score: float
    ela_anomaly_score: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


def extract_signal_scores(image_path: Path) -> ImageSignalScores:
    try:
        with Image.open(image_path) as image:
            rgb = image.convert("RGB").resize((512, 512))
    except (UnidentifiedImageError, OSError):
        return ImageSignalScores(1.0, 1.0, 1.0, 1.0, 1.0, 1.0)

    gray = np.asarray(rgb.convert("L"), dtype=np.float32) / 255.0
    rgb_array = np.asarray(rgb, dtype=np.float32) / 255.0

    frequency = _frequency_anomaly(gray)
    texture = _texture_uniformity(rgb_array)
    noise = _noise_inconsistency(gray)
    edge = _edge_inconsistency(gray)
    blocking = _jpeg_blocking_score(gray)
    ela = _ela_anomaly_score(rgb)

    return ImageSignalScores(frequency, texture, noise, edge, blocking, ela)


def create_forensic_artifacts(image_path: Path, artifact_dir: Path, case_id: int) -> dict[str, str]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    ela_path = artifact_dir / f"case-{case_id}-ela.jpg"
    heatmap_path = artifact_dir / f"case-{case_id}-heatmap.jpg"
    anomaly_path = artifact_dir / f"case-{case_id}-anomaly-overlay.jpg"

    try:
        with Image.open(image_path) as image:
            rgb = image.convert("RGB")
    except (UnidentifiedImageError, OSError):
        return {}

    recompressed_path = artifact_dir / f"case-{case_id}-recompressed.tmp.jpg"
    rgb.save(recompressed_path, "JPEG", quality=90)
    with Image.open(recompressed_path) as recompressed:
        diff = ImageChops.difference(rgb, recompressed.convert("RGB"))
    recompressed_path.unlink(missing_ok=True)

    extrema = diff.getextrema()
    max_diff = max(channel[1] for channel in extrema) or 1
    ela = ImageEnhance.Brightness(diff).enhance(255.0 / max_diff)
    ela.save(ela_path, "JPEG", quality=95)

    gray = ImageOps.grayscale(ela)
    heatmap = ImageOps.colorize(
        ImageOps.autocontrast(gray),
        black="#0b1020",
        mid="#f5c542",
        white="#ff3b30",
    )
    heatmap.save(heatmap_path, "JPEG", quality=95)
    anomaly_regions = _detect_anomaly_regions(gray)
    overlay = _draw_anomaly_overlay(rgb, anomaly_regions)
    overlay.save(anomaly_path, "JPEG", quality=95)

    return {
        "ela_image_path": str(ela_path),
        "heatmap_path": str(heatmap_path),
        "anomaly_overlay_path": str(anomaly_path),
        "anomaly_regions": anomaly_regions,
    }


def _detect_anomaly_regions(gray: Image.Image) -> list[dict[str, float | int]]:
    small = gray.resize((64, 64))
    data = np.asarray(small, dtype=np.float32)
    threshold = max(float(np.percentile(data, 93)), float(data.mean() + data.std()))
    mask = data >= threshold
    visited = np.zeros(mask.shape, dtype=bool)
    regions: list[dict[str, float | int]] = []
    height, width = mask.shape

    for y in range(height):
        for x in range(width):
            if not mask[y, x] or visited[y, x]:
                continue
            stack = [(x, y)]
            visited[y, x] = True
            xs: list[int] = []
            ys: list[int] = []
            values: list[float] = []
            while stack:
                cx, cy = stack.pop()
                xs.append(cx)
                ys.append(cy)
                values.append(float(data[cy, cx]))
                for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
                    if 0 <= nx < width and 0 <= ny < height and mask[ny, nx] and not visited[ny, nx]:
                        visited[ny, nx] = True
                        stack.append((nx, ny))

            if len(xs) < 10:
                continue
            regions.append(
                {
                    "x": round(min(xs) / width, 4),
                    "y": round(min(ys) / height, 4),
                    "width": round((max(xs) - min(xs) + 1) / width, 4),
                    "height": round((max(ys) - min(ys) + 1) / height, 4),
                    "score": round(float(np.mean(values)) / 255.0, 4),
                    "area_pixels": int(len(xs)),
                }
            )

    regions.sort(key=lambda item: float(item["score"]) * int(item["area_pixels"]), reverse=True)
    return regions[:8]


def _draw_anomaly_overlay(rgb: Image.Image, regions: list[dict[str, float | int]]) -> Image.Image:
    overlay = rgb.convert("RGB").copy()
    draw = ImageDraw.Draw(overlay, "RGBA")
    width, height = overlay.size
    for index, region in enumerate(regions, start=1):
        x1 = int(float(region["x"]) * width)
        y1 = int(float(region["y"]) * height)
        x2 = int((float(region["x"]) + float(region["width"])) * width)
        y2 = int((float(region["y"]) + float(region["height"])) * height)
        draw.rectangle((x1, y1, x2, y2), outline=(255, 59, 48, 235), width=max(2, width // 220))
        draw.rectangle((x1, max(0, y1 - 20), min(width, x1 + 110), y1), fill=(255, 59, 48, 210))
        draw.text((x1 + 5, max(0, y1 - 17)), f"ANOMALY {index}", fill=(255, 255, 255, 255))
    return overlay


def _frequency_anomaly(gray: np.ndarray) -> float:
    spectrum = np.fft.fftshift(np.fft.fft2(gray))
    magnitude = np.log1p(np.abs(spectrum))
    h, w = magnitude.shape
    center = magnitude[h // 4 : 3 * h // 4, w // 4 : 3 * w // 4]
    outer = magnitude.copy()
    outer[h // 4 : 3 * h // 4, w // 4 : 3 * w // 4] = 0
    outer_mean = float(outer[outer > 0].mean()) if np.any(outer > 0) else 0.0
    center_mean = float(center.mean()) + 1e-6
    ratio = outer_mean / center_mean
    return _scale(ratio, low=0.45, high=0.85)


def _texture_uniformity(rgb: np.ndarray) -> float:
    patch_size = 32
    variances = []
    for y in range(0, rgb.shape[0], patch_size):
        for x in range(0, rgb.shape[1], patch_size):
            patch = rgb[y : y + patch_size, x : x + patch_size]
            variances.append(float(np.var(patch)))
    variance_std = float(np.std(variances))
    return 1.0 - _scale(variance_std, low=0.005, high=0.04)


def _noise_inconsistency(gray: np.ndarray) -> float:
    pil = Image.fromarray(np.uint8(gray * 255))
    blurred = np.asarray(pil.filter(ImageFilter.GaussianBlur(radius=1.2)), dtype=np.float32) / 255.0
    residual = np.abs(gray - blurred)
    patch_size = 64
    patch_means = []
    for y in range(0, residual.shape[0], patch_size):
        for x in range(0, residual.shape[1], patch_size):
            patch_means.append(float(residual[y : y + patch_size, x : x + patch_size].mean()))
    return _scale(float(np.std(patch_means)), low=0.003, high=0.025)


def _edge_inconsistency(gray: np.ndarray) -> float:
    grad_y, grad_x = np.gradient(gray)
    gradient = np.sqrt(grad_x**2 + grad_y**2)
    strong_edges = gradient > np.percentile(gradient, 85)
    edge_density = float(strong_edges.mean())
    return _scale(edge_density, low=0.08, high=0.22)


def _jpeg_blocking_score(gray: np.ndarray) -> float:
    vertical_boundaries = np.abs(gray[:, 8::8] - gray[:, 7:-1:8])
    horizontal_boundaries = np.abs(gray[8::8, :] - gray[7:-1:8, :])
    boundary_strength = float((vertical_boundaries.mean() + horizontal_boundaries.mean()) / 2)
    return _scale(boundary_strength, low=0.012, high=0.055)


def _ela_anomaly_score(rgb: Image.Image) -> float:
    recompressed = rgb.copy()
    from io import BytesIO

    buffer = BytesIO()
    recompressed.save(buffer, format="JPEG", quality=90)
    buffer.seek(0)
    with Image.open(buffer) as jpeg_image:
        diff = ImageChops.difference(rgb, jpeg_image.convert("RGB"))
    diff_array = np.asarray(diff, dtype=np.float32) / 255.0
    return _scale(float(diff_array.mean()), low=0.004, high=0.030)


def _scale(value: float, low: float, high: float) -> float:
    if high <= low:
        return 0.0
    return round(max(0.0, min(1.0, (value - low) / (high - low))), 4)





