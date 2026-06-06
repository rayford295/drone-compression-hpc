#!/usr/bin/env python3
"""Evaluate zero-shot SAM mask stability on original and reconstructed images.

The evaluator uses YOLO-format boxes as fixed SAM box prompts. It runs the same
prompts on a baseline image set, normally ``original``, and on each reconstructed
image set. It then compares each reconstructed mask against the baseline mask for
the same image and prompt.

This measures promptable segmentation stability. It does not measure detection
accuracy, because SAM does not assign semantic classes by itself.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import pathlib
import re
from dataclasses import dataclass
from typing import Iterable

import numpy as np
import torch
from PIL import Image


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}


@dataclass(frozen=True)
class PromptBox:
    image_id: str
    prompt_index: int
    class_id: int
    x1: float
    y1: float
    x2: float
    y2: float


@dataclass(frozen=True)
class MaskResult:
    mask: np.ndarray
    score: float


def parse_label_mapping(value: str) -> tuple[str, pathlib.Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError(f"Expected label=path, got: {value}")
    label, path = value.split("=", 1)
    label = label.strip()
    if not label:
        raise argparse.ArgumentTypeError(f"Empty label in: {value}")
    return label, pathlib.Path(path).expanduser()


def normalize_image_id(stem: str) -> str:
    cleaned = stem
    patterns = [
        r"_tile\d+_stitched$",
        r"_tile\d+_recon$",
        r"_tile\d+$",
        r"_stitched$",
        r"_recon$",
    ]
    changed = True
    while changed:
        changed = False
        for pattern in patterns:
            updated = re.sub(pattern, "", cleaned)
            if updated != cleaned:
                cleaned = updated
                changed = True
    return cleaned


def yolo_to_xyxy(xc: float, yc: float, width: float, height: float) -> tuple[float, float, float, float]:
    half_w = width / 2.0
    half_h = height / 2.0
    return (
        max(0.0, xc - half_w),
        max(0.0, yc - half_h),
        min(1.0, xc + half_w),
        min(1.0, yc + half_h),
    )


def resolve_label_dir(path: pathlib.Path) -> pathlib.Path:
    if list(path.glob("*.txt")):
        return path
    nested = path / "labels"
    if nested.exists() and list(nested.glob("*.txt")):
        return nested
    return path


def read_prompt_file(path: pathlib.Path, image_id: str, allowed_classes: set[int] | None) -> list[PromptBox]:
    prompts: list[PromptBox] = []
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        parts = stripped.split()
        if len(parts) < 5:
            raise ValueError(f"{path}:{line_number} has fewer than 5 YOLO columns")
        class_id = int(float(parts[0]))
        if allowed_classes is not None and class_id not in allowed_classes:
            continue
        x1, y1, x2, y2 = yolo_to_xyxy(*(float(value) for value in parts[1:5]))
        prompts.append(PromptBox(image_id, len(prompts), class_id, x1, y1, x2, y2))
    return prompts


def load_prompts(label_dir: pathlib.Path, allowed_classes: set[int] | None) -> dict[str, list[PromptBox]]:
    resolved = resolve_label_dir(label_dir)
    prompts_by_image: dict[str, list[PromptBox]] = {}
    for label_file in sorted(resolved.glob("*.txt")):
        image_id = normalize_image_id(label_file.stem)
        prompts = read_prompt_file(label_file, image_id, allowed_classes)
        if prompts:
            prompts_by_image[image_id] = prompts
    if not prompts_by_image:
        raise ValueError(f"No prompt boxes found in {label_dir}")
    return prompts_by_image


def iter_images(source_dir: pathlib.Path, recursive: bool) -> list[pathlib.Path]:
    iterator = source_dir.rglob("*") if recursive else source_dir.iterdir()
    return [
        path
        for path in iterator
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    ]


def candidate_priority(path: pathlib.Path, image_id: str) -> tuple[int, str]:
    stem = path.stem
    if stem == image_id:
        return (0, path.name)
    if stem == f"{image_id}_recon":
        return (1, path.name)
    if re.fullmatch(rf"{re.escape(image_id)}_tile\d+_stitched", stem):
        return (2, path.name)
    if stem == f"{image_id}_stitched":
        return (3, path.name)
    return (9, path.name)


def build_image_index(source_dir: pathlib.Path, recursive: bool) -> dict[str, pathlib.Path]:
    grouped: dict[str, list[pathlib.Path]] = {}
    for path in iter_images(source_dir, recursive):
        grouped.setdefault(normalize_image_id(path.stem), []).append(path)
    return {
        image_id: sorted(paths, key=lambda item: candidate_priority(item, image_id))[0]
        for image_id, paths in grouped.items()
    }


def load_rgb(path: pathlib.Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB"))


def resize_mask_to_shape(mask: np.ndarray, target_shape: tuple[int, int]) -> np.ndarray:
    if mask.shape == target_shape:
        return mask
    target_height, target_width = target_shape
    resampling = getattr(Image, "Resampling", Image).NEAREST
    image = Image.fromarray(mask.astype(np.uint8) * 255)
    resized = image.resize((target_width, target_height), resampling)
    return np.asarray(resized) > 0


def pixel_boxes(prompts: list[PromptBox], width: int, height: int, box_expansion: float) -> np.ndarray:
    boxes = []
    for prompt in prompts:
        x1 = prompt.x1 * width
        y1 = prompt.y1 * height
        x2 = prompt.x2 * width
        y2 = prompt.y2 * height
        if box_expansion:
            cx = (x1 + x2) / 2.0
            cy = (y1 + y2) / 2.0
            half_w = (x2 - x1) * (1.0 + box_expansion) / 2.0
            half_h = (y2 - y1) * (1.0 + box_expansion) / 2.0
            x1, x2 = cx - half_w, cx + half_w
            y1, y2 = cy - half_h, cy + half_h
        boxes.append(
            [
                max(0.0, min(float(width - 1), x1)),
                max(0.0, min(float(height - 1), y1)),
                max(0.0, min(float(width - 1), x2)),
                max(0.0, min(float(height - 1), y2)),
            ]
        )
    return np.asarray(boxes, dtype=np.float32)


def batched(items: list[PromptBox], batch_size: int) -> Iterable[tuple[int, list[PromptBox]]]:
    for start in range(0, len(items), batch_size):
        yield start, items[start : start + batch_size]


def select_best_masks(masks: torch.Tensor, scores: torch.Tensor) -> tuple[np.ndarray, np.ndarray]:
    # SAM returns [B, C, H, W] masks and [B, C] scores. With multimask disabled,
    # C is 1. With multimask enabled, choose the highest-scoring candidate.
    best_indices = scores.argmax(dim=1)
    batch_indices = torch.arange(masks.shape[0], device=masks.device)
    selected_masks = masks[batch_indices, best_indices].detach().cpu().numpy().astype(bool)
    selected_scores = scores[batch_indices, best_indices].detach().cpu().numpy().astype(float)
    return selected_masks, selected_scores


def predict_masks_for_image(
    predictor: object,
    image: np.ndarray,
    prompts: list[PromptBox],
    device: torch.device,
    prompt_batch_size: int,
    multimask_output: bool,
    box_expansion: float,
) -> list[MaskResult]:
    height, width = image.shape[:2]
    predictor.set_image(image)
    results: list[MaskResult] = []
    for _, prompt_batch in batched(prompts, prompt_batch_size):
        boxes_np = pixel_boxes(prompt_batch, width, height, box_expansion)
        boxes_torch = torch.as_tensor(boxes_np, dtype=torch.float32, device=device)
        transformed_boxes = predictor.transform.apply_boxes_torch(boxes_torch, image.shape[:2])
        with torch.no_grad():
            masks, scores, _ = predictor.predict_torch(
                point_coords=None,
                point_labels=None,
                boxes=transformed_boxes,
                multimask_output=multimask_output,
            )
        selected_masks, selected_scores = select_best_masks(masks, scores)
        for mask, score in zip(selected_masks, selected_scores):
            results.append(MaskResult(mask=mask, score=float(score)))
        del masks, scores
        if device.type == "cuda":
            torch.cuda.empty_cache()
    return results


def mask_iou(a: np.ndarray, b: np.ndarray) -> float:
    intersection = np.logical_and(a, b).sum()
    union = np.logical_or(a, b).sum()
    return float(intersection / union) if union else math.nan


def dice(a: np.ndarray, b: np.ndarray) -> float:
    area_a = a.sum()
    area_b = b.sum()
    denom = area_a + area_b
    return float(2.0 * np.logical_and(a, b).sum() / denom) if denom else math.nan


def centroid(mask: np.ndarray) -> tuple[float, float] | None:
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return None
    return float(xs.mean()), float(ys.mean())


def centroid_shift(a: np.ndarray, b: np.ndarray) -> float:
    ca = centroid(a)
    cb = centroid(b)
    if ca is None or cb is None:
        return math.nan
    return float(math.hypot(ca[0] - cb[0], ca[1] - cb[1]))


def boundary(mask: np.ndarray) -> np.ndarray:
    edges = np.zeros_like(mask, dtype=bool)
    edges[:-1, :] |= mask[:-1, :] != mask[1:, :]
    edges[1:, :] |= mask[1:, :] != mask[:-1, :]
    edges[:, :-1] |= mask[:, :-1] != mask[:, 1:]
    edges[:, 1:] |= mask[:, 1:] != mask[:, :-1]
    return edges


def dilate_binary(mask: np.ndarray, radius: int) -> np.ndarray:
    if radius <= 0:
        return mask
    height, width = mask.shape
    padded = np.pad(mask, radius, mode="constant", constant_values=False)
    output = np.zeros_like(mask, dtype=bool)
    for dy in range(2 * radius + 1):
        for dx in range(2 * radius + 1):
            output |= padded[dy : dy + height, dx : dx + width]
    return output


def boundary_f1(a: np.ndarray, b: np.ndarray, dilation_radius: int) -> float:
    boundary_a = boundary(a)
    boundary_b = boundary(b)
    count_a = boundary_a.sum()
    count_b = boundary_b.sum()
    if count_a == 0 or count_b == 0:
        return math.nan
    boundary_a_dilated = dilate_binary(boundary_a, dilation_radius)
    boundary_b_dilated = dilate_binary(boundary_b, dilation_radius)
    precision = np.logical_and(boundary_b, boundary_a_dilated).sum() / count_b
    recall = np.logical_and(boundary_a, boundary_b_dilated).sum() / count_a
    return float(2.0 * precision * recall / (precision + recall)) if precision + recall else 0.0


def compare_masks(
    baseline: MaskResult,
    candidate: MaskResult,
    min_mask_area: int,
    compute_boundary: bool,
    boundary_dilation: int,
) -> dict[str, object]:
    original_area = int(baseline.mask.sum())
    candidate_area = int(candidate.mask.sum())
    failed_original = original_area < min_mask_area
    failed_candidate = candidate_area < min_mask_area
    area_ratio = candidate_area / original_area if original_area else math.nan
    abs_area_change = abs(candidate_area - original_area) / original_area if original_area else math.nan
    row = {
        "original_area_px": original_area,
        "candidate_area_px": candidate_area,
        "mask_iou": mask_iou(baseline.mask, candidate.mask),
        "dice": dice(baseline.mask, candidate.mask),
        "area_ratio": area_ratio,
        "abs_area_change": abs_area_change,
        "centroid_shift_px": centroid_shift(baseline.mask, candidate.mask),
        "score_original": baseline.score,
        "score_candidate": candidate.score,
        "failed_original": failed_original,
        "failed_candidate": failed_candidate,
    }
    if compute_boundary:
        row["boundary_f1"] = boundary_f1(baseline.mask, candidate.mask, boundary_dilation)
    return row


def finite_values(rows: list[dict[str, object]], key: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        value = row.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)):
            values.append(float(value))
    return values


def mean_value(rows: list[dict[str, object]], key: str) -> float:
    values = finite_values(rows, key)
    return sum(values) / len(values) if values else math.nan


def format_value(value: object) -> object:
    if isinstance(value, float):
        if not math.isfinite(value):
            return ""
        return round(value, 6)
    return value


def write_csv(path: pathlib.Path, rows: list[dict[str, object]]) -> None:
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: format_value(row.get(key, "")) for key in fieldnames})


def summarize_group(rows: list[dict[str, object]], configuration: str, image_id: str | None = None) -> dict[str, object]:
    failed_original = sum(1 for row in rows if row.get("failed_original"))
    failed_candidate = sum(1 for row in rows if row.get("failed_candidate"))
    summary: dict[str, object] = {
        "configuration": configuration,
        "num_prompts": len(rows),
        "failed_original": failed_original,
        "failed_candidate": failed_candidate,
        "failed_prompt_rate": failed_candidate / len(rows) if rows else math.nan,
        "mean_mask_iou": mean_value(rows, "mask_iou"),
        "mean_dice": mean_value(rows, "dice"),
        "mean_area_ratio": mean_value(rows, "area_ratio"),
        "mean_abs_area_change": mean_value(rows, "abs_area_change"),
        "mean_centroid_shift_px": mean_value(rows, "centroid_shift_px"),
        "mean_score_original": mean_value(rows, "score_original"),
        "mean_score_candidate": mean_value(rows, "score_candidate"),
    }
    if image_id is not None:
        summary["image_id"] = image_id
    if any("boundary_f1" in row for row in rows):
        summary["mean_boundary_f1"] = mean_value(rows, "boundary_f1")
    return summary


def write_markdown(path: pathlib.Path, rows: list[dict[str, object]]) -> None:
    columns = [
        "configuration",
        "num_images",
        "num_prompts",
        "mean_mask_iou",
        "mean_dice",
        "mean_area_ratio",
        "mean_abs_area_change",
        "mean_centroid_shift_px",
        "failed_prompt_rate",
    ]
    if any("mean_boundary_f1" in row for row in rows):
        columns.insert(-1, "mean_boundary_f1")
    lines = ["# SAM Mask Stability Summary", ""]
    if not rows:
        lines.append("No rows were evaluated.")
    else:
        lines.append("| " + " | ".join(columns) + " |")
        lines.append("| " + " | ".join(["---"] * len(columns)) + " |")
        for row in rows:
            lines.append("| " + " | ".join(str(format_value(row.get(column, ""))) for column in columns) + " |")
    path.write_text("\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sam_checkpoint", required=True, help="Path to a Segment Anything checkpoint")
    parser.add_argument("--model_type", default="vit_h", help="SAM model type, e.g. vit_h, vit_l, vit_b")
    parser.add_argument("--prompt_label_dir", required=True, help="YOLO-format box prompt label directory")
    parser.add_argument(
        "--image_sets",
        nargs="+",
        type=parse_label_mapping,
        metavar="LABEL=PATH",
        help="Image folders to compare, e.g. original=/path balanced=/path",
    )
    parser.add_argument("--baseline_config", default="original", help="Image-set label used as mask baseline")
    parser.add_argument("--recursive", action="store_true", help="Search image-set folders recursively")
    parser.add_argument("--prompt_classes", nargs="*", type=int, default=[], help="Optional YOLO class IDs to use")
    parser.add_argument("--prompt_batch_size", type=int, default=8)
    parser.add_argument("--limit_images", type=int, default=0, help="Optional smoke-test limit")
    parser.add_argument("--device", default="", help="Torch device. Defaults to cuda if available, else cpu")
    parser.add_argument("--multimask_output", action="store_true", help="Ask SAM for multiple masks and choose best score")
    parser.add_argument("--box_expansion", type=float, default=0.0, help="Fractional box expansion before prompting SAM")
    parser.add_argument("--min_mask_area", type=int, default=1)
    parser.add_argument("--compute_boundary", action="store_true", help="Compute boundary F1. This can be slow.")
    parser.add_argument("--boundary_dilation", type=int, default=2)
    parser.add_argument("--output_dir", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.prompt_batch_size <= 0:
        raise ValueError("--prompt_batch_size must be positive")
    output_dir = pathlib.Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        from segment_anything import SamPredictor, sam_model_registry
    except ImportError as exc:
        raise RuntimeError(
            "segment_anything is not installed. Install Meta Segment Anything or set "
            "SAM_INSTALL_SEGMENT_ANYTHING=1 in the SLURM wrapper."
        ) from exc

    device = torch.device(args.device or ("cuda" if torch.cuda.is_available() else "cpu"))
    allowed_classes = set(args.prompt_classes) if args.prompt_classes else None
    prompts_by_image = load_prompts(pathlib.Path(args.prompt_label_dir).expanduser(), allowed_classes)
    image_ids = sorted(prompts_by_image)
    if args.limit_images:
        image_ids = image_ids[: args.limit_images]

    image_sets = list(args.image_sets or [])
    if args.baseline_config not in {label for label, _ in image_sets}:
        raise ValueError(f"baseline_config {args.baseline_config!r} is not present in --image_sets")
    image_indices = {
        label: build_image_index(path.expanduser(), args.recursive)
        for label, path in image_sets
    }

    sam_model = sam_model_registry[args.model_type](checkpoint=str(pathlib.Path(args.sam_checkpoint).expanduser()))
    sam_model.to(device=device)
    predictor = SamPredictor(sam_model)

    per_prompt_rows: list[dict[str, object]] = []
    per_image_rows: list[dict[str, object]] = []
    missing_images: dict[str, list[str]] = {label: [] for label, _ in image_sets}
    evaluated_images: dict[str, set[str]] = {label: set() for label, _ in image_sets}

    baseline_index = image_indices[args.baseline_config]
    comparison_labels = [label for label, _ in image_sets]
    for image_number, image_id in enumerate(image_ids, start=1):
        prompts = prompts_by_image[image_id]
        baseline_path = baseline_index.get(image_id)
        if baseline_path is None:
            raise FileNotFoundError(f"Missing baseline image for {image_id} in {args.baseline_config}")
        baseline_image = load_rgb(baseline_path)
        baseline_masks = predict_masks_for_image(
            predictor,
            baseline_image,
            prompts,
            device,
            args.prompt_batch_size,
            args.multimask_output,
            args.box_expansion,
        )
        height, width = baseline_image.shape[:2]

        for label in comparison_labels:
            image_path = image_indices[label].get(image_id)
            if image_path is None:
                missing_images[label].append(image_id)
                continue
            if label == args.baseline_config:
                candidate_masks = baseline_masks
                candidate_height, candidate_width = height, width
                resized_candidate_masks = False
            else:
                candidate_image = load_rgb(image_path)
                candidate_height, candidate_width = candidate_image.shape[:2]
                candidate_masks = predict_masks_for_image(
                    predictor,
                    candidate_image,
                    prompts,
                    device,
                    args.prompt_batch_size,
                    args.multimask_output,
                    args.box_expansion,
                )
                resized_candidate_masks = candidate_image.shape[:2] != (height, width)
                if resized_candidate_masks:
                    candidate_masks = [
                        MaskResult(
                            mask=resize_mask_to_shape(mask_result.mask, (height, width)),
                            score=mask_result.score,
                        )
                        for mask_result in candidate_masks
                    ]
            evaluated_images[label].add(image_id)
            image_rows: list[dict[str, object]] = []
            for prompt, baseline_mask, candidate_mask in zip(prompts, baseline_masks, candidate_masks):
                metrics = compare_masks(
                    baseline_mask,
                    candidate_mask,
                    args.min_mask_area,
                    args.compute_boundary,
                    args.boundary_dilation,
                )
                row = {
                    "configuration": label,
                    "image_id": image_id,
                    "prompt_index": prompt.prompt_index,
                    "class_id": prompt.class_id,
                    "image_width": width,
                    "image_height": height,
                    "baseline_image_width": width,
                    "baseline_image_height": height,
                    "candidate_image_width": candidate_width,
                    "candidate_image_height": candidate_height,
                    "candidate_mask_resized_to_baseline": resized_candidate_masks,
                    "box_x1": prompt.x1,
                    "box_y1": prompt.y1,
                    "box_x2": prompt.x2,
                    "box_y2": prompt.y2,
                    **metrics,
                }
                per_prompt_rows.append(row)
                image_rows.append(row)
            per_image_rows.append(summarize_group(image_rows, label, image_id))
        print(f"{image_number}/{len(image_ids)} {image_id}: prompts={len(prompts)}")

    summary_rows: list[dict[str, object]] = []
    for label in comparison_labels:
        rows = [row for row in per_prompt_rows if row["configuration"] == label]
        summary = summarize_group(rows, label)
        summary["num_images"] = len(evaluated_images[label])
        summary["missing_images"] = len(missing_images[label])
        summary_rows.append(summary)

    write_csv(output_dir / "sam_mask_per_prompt.csv", per_prompt_rows)
    write_csv(output_dir / "sam_mask_per_image.csv", per_image_rows)
    write_csv(output_dir / "sam_mask_summary.csv", summary_rows)
    write_markdown(output_dir / "sam_mask_summary.md", summary_rows)

    manifest = {
        "sam_checkpoint": str(pathlib.Path(args.sam_checkpoint).expanduser()),
        "model_type": args.model_type,
        "device": str(device),
        "prompt_label_dir": str(pathlib.Path(args.prompt_label_dir).expanduser()),
        "baseline_config": args.baseline_config,
        "image_sets": {label: str(path) for label, path in image_sets},
        "prompt_classes": args.prompt_classes,
        "prompt_batch_size": args.prompt_batch_size,
        "limit_images": args.limit_images,
        "multimask_output": args.multimask_output,
        "box_expansion": args.box_expansion,
        "min_mask_area": args.min_mask_area,
        "compute_boundary": args.compute_boundary,
        "boundary_dilation": args.boundary_dilation,
        "num_prompt_images": len(image_ids),
        "num_prompts": sum(len(prompts_by_image[image_id]) for image_id in image_ids),
        "missing_images": missing_images,
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    print(f"Wrote {output_dir / 'sam_mask_summary.csv'}")
    print(f"Wrote {output_dir / 'sam_mask_per_image.csv'}")
    print(f"Wrote {output_dir / 'sam_mask_per_prompt.csv'}")
    print(f"Wrote {output_dir / 'sam_mask_summary.md'}")


if __name__ == "__main__":
    main()
