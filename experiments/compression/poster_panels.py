#!/usr/bin/env python3
"""Create poster-ready original/reconstruction/difference panels."""

from __future__ import annotations

import csv
import math
import pathlib
from typing import Any

import numpy as np
from PIL import Image


def _to_float_rgb(image: Any) -> np.ndarray:
    """Return an RGB float array in [0, 1] from a path, NumPy array, or tensor."""
    if isinstance(image, (str, pathlib.Path)):
        with Image.open(image) as handle:
            return np.asarray(handle.convert("RGB"), dtype=np.float32) / 255.0

    if hasattr(image, "detach"):
        tensor = image.detach().clamp(0, 1).cpu().float()
        if tensor.ndim == 4:
            tensor = tensor[0]
        if tensor.shape[0] in (1, 3):
            tensor = tensor.permute(1, 2, 0)
        array = tensor.numpy()
    else:
        array = np.asarray(image)

    if array.ndim == 2:
        array = np.repeat(array[:, :, None], 3, axis=2)
    if array.ndim == 3 and array.shape[0] in (1, 3) and array.shape[2] not in (1, 3):
        array = np.transpose(array, (1, 2, 0))
    if array.shape[2] == 1:
        array = np.repeat(array, 3, axis=2)
    if array.dtype.kind in {"u", "i"} or float(np.nanmax(array)) > 1.0:
        array = array.astype(np.float32) / 255.0
    return np.clip(array.astype(np.float32), 0.0, 1.0)


def _resize_rgb(array: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    image = Image.fromarray((np.clip(array, 0, 1) * 255).astype(np.uint8), mode="RGB")
    resized = image.resize(size, Image.Resampling.LANCZOS)
    return np.asarray(resized, dtype=np.float32) / 255.0


def _resize_to_max_edge(array: np.ndarray, max_edge: int) -> np.ndarray:
    if max_edge <= 0:
        return array
    height, width = array.shape[:2]
    current_max = max(height, width)
    if current_max <= max_edge:
        return array
    scale = max_edge / float(current_max)
    new_size = (max(1, round(width * scale)), max(1, round(height * scale)))
    return _resize_rgb(array, new_size)


def _format_metric(value: Any, digits: int) -> str:
    try:
        value_float = float(value)
    except (TypeError, ValueError):
        return "n/a"
    if not math.isfinite(value_float):
        return "n/a"
    return f"{value_float:.{digits}f}"


def _derived_metrics(original: np.ndarray, reconstructed: np.ndarray) -> dict[str, float]:
    diff = reconstructed - original
    abs_diff = np.abs(diff)
    mse = float(np.mean(diff**2))
    rmse = math.sqrt(mse)
    psnr = float("inf") if mse <= 0 else 20.0 * math.log10(1.0 / rmse)
    return {
        "psnr_db": psnr,
        "mse": mse,
        "rmse": rmse,
        "mae": float(np.mean(abs_diff)),
        "max_abs_error": float(np.max(abs_diff)),
        "bias_mean": float(np.mean(diff)),
        "error_std": float(np.std(abs_diff)),
    }


def _metrics_text(metrics: dict[str, Any], original: np.ndarray, reconstructed: np.ndarray) -> str:
    combined = _derived_metrics(original, reconstructed)
    combined.update({key: value for key, value in metrics.items() if value not in ("", None)})
    return "\n".join(
        [
            "Quality Metrics:",
            f"PSNR: {_format_metric(combined.get('psnr_db'), 2)} dB",
            f"SSIM: {_format_metric(combined.get('ssim'), 4)}",
            f"MAE: {_format_metric(combined.get('mae'), 4)}",
            f"MSE: {_format_metric(combined.get('mse'), 4)}",
            f"RMSE: {_format_metric(combined.get('rmse'), 4)}",
            f"Max Diff: {_format_metric(combined.get('max_abs_error'), 4)}",
            f"Mean Diff: {_format_metric(combined.get('mae'), 4)}",
            f"Std Diff: {_format_metric(combined.get('error_std'), 4)}",
        ]
    )


def save_poster_panel(
    original: Any,
    reconstructed: Any,
    out_path: str | pathlib.Path,
    *,
    metrics: dict[str, Any] | None = None,
    max_edge: int = 1200,
    title: str | None = None,
    dpi: int = 160,
) -> pathlib.Path:
    """Save a six-panel poster QA figure and return its path."""
    try:
        import matplotlib
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "matplotlib is required for poster panels. Install the DeltaAI "
            "plotting dependencies with: python -m pip install --user matplotlib pillow"
        ) from exc

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    original_rgb = _resize_to_max_edge(_to_float_rgb(original), max_edge)
    reconstructed_rgb = _resize_to_max_edge(_to_float_rgb(reconstructed), max_edge)
    if reconstructed_rgb.shape[:2] != original_rgb.shape[:2]:
        width = original_rgb.shape[1]
        height = original_rgb.shape[0]
        reconstructed_rgb = _resize_rgb(reconstructed_rgb, (width, height))

    abs_diff_rgb = np.abs(reconstructed_rgb - original_rgb)
    mean_diff = np.mean(abs_diff_rgb, axis=2)
    robust_max = float(np.quantile(mean_diff, 0.995))
    if robust_max <= 1e-8 or not math.isfinite(robust_max):
        robust_max = 1.0

    flat_abs = abs_diff_rgb.reshape(-1)
    flat_value = np.clip(mean_diff.reshape(-1) * 255.0, 0, 255)
    hist_counts, hist_edges = np.histogram(flat_value, bins=np.linspace(0, 255, 80))
    hist_centers = (hist_edges[:-1] + hist_edges[1:]) / 2.0

    out_path = pathlib.Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 3, figsize=(16, 9), dpi=dpi)
    fig.patch.set_facecolor("white")
    if title:
        fig.suptitle(title, fontsize=12, y=0.98)

    axes[0, 0].imshow(original_rgb)
    axes[0, 0].set_title("Original Image", fontsize=12)
    axes[0, 1].imshow(reconstructed_rgb)
    axes[0, 1].set_title("Reconstructed Image", fontsize=12)
    axes[0, 2].imshow(mean_diff, cmap="hot", vmin=0, vmax=robust_max)
    axes[0, 2].set_title("Difference Map (Hot)", fontsize=12)

    axes[1, 0].hist(flat_abs, bins=40, color="#4f46e5", alpha=0.9)
    axes[1, 0].set_title("Histogram of Pixel Differences", fontsize=12)
    axes[1, 0].set_xlabel("Absolute Difference")
    axes[1, 0].set_ylabel("Frequency")

    axes[1, 1].axis("off")
    axes[1, 1].text(
        0.16,
        0.48,
        _metrics_text(metrics or {}, original_rgb, reconstructed_rgb),
        family="monospace",
        fontsize=10,
        va="center",
    )

    axes[1, 2].plot(hist_centers, hist_counts, color="#2563eb", linewidth=1.5)
    axes[1, 2].set_title("Difference Distribution", fontsize=12)
    axes[1, 2].set_xlabel("Difference Value")
    axes[1, 2].set_ylabel("Count")
    axes[1, 2].set_xlim(0, 255)

    for axis in axes[0, :]:
        axis.set_xticks([])
        axis.set_yticks([])
    fig.tight_layout(rect=(0, 0, 1, 0.96 if title else 1))
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


def read_metrics_by_preview(results_csv: str | pathlib.Path | None) -> dict[str, dict[str, str]]:
    if not results_csv:
        return {}
    path = pathlib.Path(results_csv)
    if not path.exists():
        return {}
    metrics: dict[str, dict[str, str]] = {}
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            preview_path = row.get("original_preview_path", "")
            if preview_path:
                metrics[pathlib.Path(preview_path).name] = row
            recon_path = row.get("recon_path", "")
            if recon_path:
                metrics[pathlib.Path(recon_path).name] = row
    return metrics


def find_reconstruction_for_preview(original_preview: pathlib.Path) -> pathlib.Path | None:
    stem = original_preview.name.removesuffix("_original_preview.png")
    for suffix in ("_recon.png", "_stitched.png"):
        candidate = original_preview.with_name(f"{stem}{suffix}")
        if candidate.exists():
            return candidate
    return None


def build_panels_for_visuals_dir(
    visuals_dir: str | pathlib.Path,
    *,
    results_csv: str | pathlib.Path | None = None,
    out_dir: str | pathlib.Path | None = None,
    max_edge: int = 1200,
    max_panels: int = 8,
    overwrite: bool = False,
) -> list[pathlib.Path]:
    visuals_path = pathlib.Path(visuals_dir)
    output_path = pathlib.Path(out_dir) if out_dir else visuals_path
    if results_csv is None:
        sibling_results = visuals_path.parent / "results.csv"
        results_csv = sibling_results if sibling_results.exists() else None
    metrics_by_preview = read_metrics_by_preview(results_csv)
    written: list[pathlib.Path] = []

    previews = sorted(visuals_path.glob("*_original_preview.png"))
    if max_panels > 0:
        previews = previews[:max_panels]
    for preview in previews:
        reconstructed = find_reconstruction_for_preview(preview)
        if reconstructed is None:
            continue
        stem = preview.name.removesuffix("_original_preview.png")
        panel_path = output_path / f"{stem}_poster_panel.png"
        if panel_path.exists() and not overwrite:
            written.append(panel_path)
            continue
        metrics = metrics_by_preview.get(preview.name) or metrics_by_preview.get(reconstructed.name) or {}
        save_poster_panel(
            preview,
            reconstructed,
            panel_path,
            metrics=metrics,
            max_edge=max_edge,
            title=stem,
        )
        written.append(panel_path)
    return written
