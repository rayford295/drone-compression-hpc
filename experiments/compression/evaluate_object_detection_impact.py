#!/usr/bin/env python3
"""Evaluate downstream object detection on original and reconstructed images.

The script accepts either existing YOLO-format prediction folders or an
Ultralytics YOLO model plus image-set folders. It writes configuration-level
precision, recall, F1, mAP@0.5, and mAP@0.5:0.95 summaries.

Label format:
  class_id x_center y_center width height [confidence]

Coordinates are normalized YOLO coordinates. Ground-truth files omit
confidence. Prediction files should include confidence; if absent, confidence
defaults to 1.0.
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


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
DEFAULT_IOU_THRESHOLDS = [round(0.5 + 0.05 * i, 2) for i in range(10)]
ROBOFLOW_SUFFIX = re.compile(r"_JPG\.rf\.[0-9a-fA-F]+$", re.IGNORECASE)


@dataclass(frozen=True)
class Detection:
    image_id: str
    class_id: int
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float = 1.0


def parse_label_mapping(value: str) -> tuple[str, pathlib.Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError(f"Expected label=path, got: {value}")
    label, path = value.split("=", 1)
    label = label.strip()
    if not label:
        raise argparse.ArgumentTypeError(f"Empty label in: {value}")
    return label, pathlib.Path(path).expanduser()


def parse_class_mapping(value: str) -> tuple[int, int]:
    if "=" not in value:
        raise argparse.ArgumentTypeError(f"Expected source=target class mapping, got: {value}")
    source, target = value.split("=", 1)
    try:
        return int(source), int(target)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Class mapping must use integer IDs, got: {value}") from exc


def normalize_image_id(stem: str) -> str:
    cleaned = ROBOFLOW_SUFFIX.sub("", stem)
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


def read_yolo_file(path: pathlib.Path, image_id: str, is_prediction: bool) -> list[Detection]:
    detections: list[Detection] = []
    if not path.exists():
        return detections
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        parts = stripped.split()
        if len(parts) < 5:
            raise ValueError(f"{path}:{line_number} has fewer than 5 YOLO columns")
        class_id = int(float(parts[0]))
        x1, y1, x2, y2 = yolo_to_xyxy(*(float(value) for value in parts[1:5]))
        confidence = float(parts[5]) if is_prediction and len(parts) >= 6 else 1.0
        detections.append(Detection(image_id, class_id, x1, y1, x2, y2, confidence))
    return detections


def load_yolo_dir(path: pathlib.Path, is_prediction: bool) -> dict[str, list[Detection]]:
    by_image: dict[str, list[Detection]] = {}
    for label_file in sorted(path.glob("*.txt")):
        image_id = normalize_image_id(label_file.stem)
        by_image.setdefault(image_id, []).extend(read_yolo_file(label_file, image_id, is_prediction))
    return by_image


def remap_predictions(
    by_image: dict[str, list[Detection]],
    class_map: dict[int, int],
    drop_unmapped: bool,
) -> dict[str, list[Detection]]:
    if not class_map and not drop_unmapped:
        return by_image

    remapped: dict[str, list[Detection]] = {}
    for image_id, detections in by_image.items():
        for detection in detections:
            if detection.class_id in class_map:
                mapped = Detection(
                    detection.image_id,
                    class_map[detection.class_id],
                    detection.x1,
                    detection.y1,
                    detection.x2,
                    detection.y2,
                    detection.confidence,
                )
            elif drop_unmapped:
                continue
            else:
                mapped = detection
            remapped.setdefault(image_id, []).append(mapped)
    return remapped


def restrict_to_image_ids(
    by_image: dict[str, list[Detection]],
    allowed_image_ids: set[str],
) -> dict[str, list[Detection]]:
    return {image_id: detections for image_id, detections in by_image.items() if image_id in allowed_image_ids}


def list_image_ids(image_dir: pathlib.Path) -> set[str]:
    if not image_dir.exists():
        return set()
    return {
        normalize_image_id(path.stem)
        for path in image_dir.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    }


def box_iou(a: Detection, b: Detection) -> float:
    ix1 = max(a.x1, b.x1)
    iy1 = max(a.y1, b.y1)
    ix2 = min(a.x2, b.x2)
    iy2 = min(a.y2, b.y2)
    iw = max(0.0, ix2 - ix1)
    ih = max(0.0, iy2 - iy1)
    intersection = iw * ih
    area_a = max(0.0, a.x2 - a.x1) * max(0.0, a.y2 - a.y1)
    area_b = max(0.0, b.x2 - b.x1) * max(0.0, b.y2 - b.y1)
    union = area_a + area_b - intersection
    return intersection / union if union > 0 else 0.0


def class_ids(*collections: dict[str, list[Detection]]) -> list[int]:
    ids: set[int] = set()
    for collection in collections:
        for detections in collection.values():
            ids.update(det.class_id for det in detections)
    return sorted(ids)


def flatten(collection: dict[str, list[Detection]], class_id: int | None = None) -> list[Detection]:
    detections: list[Detection] = []
    for image_detections in collection.values():
        for detection in image_detections:
            if class_id is None or detection.class_id == class_id:
                detections.append(detection)
    return detections


def match_predictions(
    gt_by_image: dict[str, list[Detection]],
    pred_by_image: dict[str, list[Detection]],
    class_id: int,
    iou_threshold: float,
) -> tuple[list[int], list[int], int]:
    predictions = sorted(flatten(pred_by_image, class_id), key=lambda item: item.confidence, reverse=True)
    gt_for_class = {
        image_id: [gt for gt in detections if gt.class_id == class_id]
        for image_id, detections in gt_by_image.items()
    }
    num_gt = sum(len(items) for items in gt_for_class.values())
    matched: dict[str, set[int]] = {image_id: set() for image_id in gt_for_class}
    tp: list[int] = []
    fp: list[int] = []

    for pred in predictions:
        candidates = gt_for_class.get(pred.image_id, [])
        best_iou = 0.0
        best_index = -1
        for index, gt in enumerate(candidates):
            if index in matched.setdefault(pred.image_id, set()):
                continue
            current_iou = box_iou(pred, gt)
            if current_iou > best_iou:
                best_iou = current_iou
                best_index = index
        if best_index >= 0 and best_iou >= iou_threshold:
            matched[pred.image_id].add(best_index)
            tp.append(1)
            fp.append(0)
        else:
            tp.append(0)
            fp.append(1)

    return tp, fp, num_gt


def cumulative(values: Iterable[int]) -> list[int]:
    total = 0
    output = []
    for value in values:
        total += value
        output.append(total)
    return output


def average_precision(tp: list[int], fp: list[int], num_gt: int) -> float:
    if num_gt == 0:
        return math.nan
    if not tp:
        return 0.0
    cum_tp = cumulative(tp)
    cum_fp = cumulative(fp)
    recalls = [value / num_gt for value in cum_tp]
    precisions = [
        cum_tp[index] / max(cum_tp[index] + cum_fp[index], 1)
        for index in range(len(cum_tp))
    ]
    mrec = [0.0] + recalls + [1.0]
    mpre = [0.0] + precisions + [0.0]
    for index in range(len(mpre) - 2, -1, -1):
        mpre[index] = max(mpre[index], mpre[index + 1])
    ap = 0.0
    for index in range(1, len(mrec)):
        if mrec[index] != mrec[index - 1]:
            ap += (mrec[index] - mrec[index - 1]) * mpre[index]
    return ap


def precision_recall_f1(tp: list[int], fp: list[int], num_gt: int) -> tuple[float, float, float]:
    total_tp = sum(tp)
    total_fp = sum(fp)
    false_negative = max(0, num_gt - total_tp)
    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) else 0.0
    recall = total_tp / (total_tp + false_negative) if (total_tp + false_negative) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return precision, recall, f1


def evaluate_config(
    config_label: str,
    gt_by_image: dict[str, list[Detection]],
    pred_by_image: dict[str, list[Detection]],
    thresholds: list[float],
) -> tuple[dict[str, object], list[dict[str, object]]]:
    ids = class_ids(gt_by_image, pred_by_image)
    class_rows: list[dict[str, object]] = []
    ap_by_threshold: dict[float, list[float]] = {threshold: [] for threshold in thresholds}
    p50_values: list[float] = []
    r50_values: list[float] = []
    f50_values: list[float] = []

    for class_id in ids:
        for threshold in thresholds:
            tp, fp, num_gt = match_predictions(gt_by_image, pred_by_image, class_id, threshold)
            ap = average_precision(tp, fp, num_gt)
            if not math.isnan(ap):
                ap_by_threshold[threshold].append(ap)
            if abs(threshold - 0.5) < 1e-9:
                precision, recall, f1 = precision_recall_f1(tp, fp, num_gt)
                p50_values.append(precision)
                r50_values.append(recall)
                f50_values.append(f1)
                class_rows.append(
                    {
                        "configuration": config_label,
                        "class_id": class_id,
                        "num_gt": num_gt,
                        "num_predictions": len(flatten(pred_by_image, class_id)),
                        "ap50": round(ap, 6) if not math.isnan(ap) else "",
                        "precision50": round(precision, 6),
                        "recall50": round(recall, 6),
                        "f1_50": round(f1, 6),
                    }
                )

    map50 = mean_or_nan(ap_by_threshold.get(0.5, []))
    map_all = mean_or_nan([mean_or_nan(values) for values in ap_by_threshold.values()])
    all_tp, all_fp, all_gt = [], [], 0
    for class_id in ids:
        tp, fp, num_gt = match_predictions(gt_by_image, pred_by_image, class_id, 0.5)
        all_tp.extend(tp)
        all_fp.extend(fp)
        all_gt += num_gt
    precision, recall, f1 = precision_recall_f1(all_tp, all_fp, all_gt)
    summary = {
        "configuration": config_label,
        "num_images_with_gt": len(gt_by_image),
        "num_images_with_predictions": len(pred_by_image),
        "num_gt": sum(len(items) for items in gt_by_image.values()),
        "num_predictions": sum(len(items) for items in pred_by_image.values()),
        "map50": round(map50, 6) if not math.isnan(map50) else "",
        "map50_95": round(map_all, 6) if not math.isnan(map_all) else "",
        "precision50": round(precision, 6),
        "recall50": round(recall, 6),
        "f1_50": round(f1, 6),
        "macro_precision50": round(mean_or_nan(p50_values), 6) if p50_values else "",
        "macro_recall50": round(mean_or_nan(r50_values), 6) if r50_values else "",
        "macro_f1_50": round(mean_or_nan(f50_values), 6) if f50_values else "",
    }
    return summary, class_rows


def mean_or_nan(values: Iterable[float]) -> float:
    clean = [value for value in values if not math.isnan(value)]
    return sum(clean) / len(clean) if clean else math.nan


def write_csv(path: pathlib.Path, rows: list[dict[str, object]]) -> None:
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_ultralytics_predictions(
    model_path: str,
    image_sets: list[tuple[str, pathlib.Path]],
    output_dir: pathlib.Path,
    imgsz: int,
    conf: float,
    detector_classes: list[int] | None,
    device: str,
) -> list[tuple[str, pathlib.Path]]:
    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise RuntimeError(
            "Ultralytics prediction requested, but ultralytics is not installed. "
            "Install ultralytics or pass --prediction_dirs instead."
        ) from exc

    model = YOLO(model_path)
    prediction_dirs: list[tuple[str, pathlib.Path]] = []
    for label, image_dir in image_sets:
        predict_kwargs: dict[str, object] = {}
        if detector_classes:
            predict_kwargs["classes"] = detector_classes
        if device:
            predict_kwargs["device"] = device
        model.predict(
            source=str(image_dir),
            project=str(output_dir / "ultralytics_runs"),
            name=label,
            imgsz=imgsz,
            conf=conf,
            save_txt=True,
            save_conf=True,
            exist_ok=True,
            **predict_kwargs,
        )
        prediction_dirs.append((label, output_dir / "ultralytics_runs" / label / "labels"))
    return prediction_dirs


def write_markdown(path: pathlib.Path, rows: list[dict[str, object]]) -> None:
    columns = [
        "configuration",
        "map50",
        "map50_95",
        "precision50",
        "recall50",
        "f1_50",
        "num_gt",
        "num_predictions",
    ]
    lines = ["# Object Detection Impact Summary", ""]
    if not rows:
        lines.append("No rows were evaluated.")
    else:
        lines.append("| " + " | ".join(columns) + " |")
        lines.append("| " + " | ".join(["---"] * len(columns)) + " |")
        for row in rows:
            lines.append("| " + " | ".join(str(row.get(column, "")) for column in columns) + " |")
    path.write_text("\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ground_truth_dir", required=True, help="YOLO-format ground-truth label directory")
    parser.add_argument(
        "--prediction_dirs",
        nargs="*",
        type=parse_label_mapping,
        default=[],
        metavar="LABEL=PATH",
        help="Existing YOLO-format prediction label directories",
    )
    parser.add_argument(
        "--image_sets",
        nargs="*",
        type=parse_label_mapping,
        default=[],
        metavar="LABEL=PATH",
        help="Image folders to run through --detector_model",
    )
    parser.add_argument("--detector_model", default="", help="Optional Ultralytics YOLO model path/name")
    parser.add_argument("--imgsz", type=int, default=1280)
    parser.add_argument("--conf", type=float, default=0.001)
    parser.add_argument(
        "--detector_classes",
        nargs="*",
        type=int,
        default=[],
        help="Optional detector class IDs to pass to Ultralytics, e.g. COCO vehicle IDs 2 5 7.",
    )
    parser.add_argument("--device", default="", help="Optional Ultralytics device, e.g. 0 or cpu")
    parser.add_argument(
        "--prediction_class_map",
        nargs="*",
        type=parse_class_mapping,
        default=[],
        metavar="SOURCE=TARGET",
        help="Map prediction class IDs before evaluation, e.g. 2=0 5=0 7=0 for COCO vehicles.",
    )
    parser.add_argument(
        "--drop_unmapped_prediction_classes",
        action="store_true",
        help="Drop prediction classes not listed in --prediction_class_map.",
    )
    parser.add_argument(
        "--restrict_predictions_to_gt",
        action="store_true",
        help="Ignore predictions for image IDs that are not present in the ground-truth label folder.",
    )
    parser.add_argument(
        "--iou_thresholds",
        nargs="*",
        type=float,
        default=DEFAULT_IOU_THRESHOLDS,
        help="IoU thresholds used for AP. Default is 0.50:0.05:0.95.",
    )
    parser.add_argument("--output_dir", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = pathlib.Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    gt_dir = pathlib.Path(args.ground_truth_dir).expanduser()
    gt_by_image = load_yolo_dir(gt_dir, is_prediction=False)
    if not gt_by_image:
        raise ValueError(f"No ground-truth YOLO labels found in {gt_dir}")

    prediction_dirs = list(args.prediction_dirs)
    if args.detector_model:
        if not args.image_sets:
            raise ValueError("--image_sets is required when --detector_model is used")
        prediction_dirs.extend(
            run_ultralytics_predictions(
                args.detector_model,
                args.image_sets,
                output_dir,
                args.imgsz,
                args.conf,
                args.detector_classes or None,
                args.device,
            )
        )
    if not prediction_dirs:
        raise ValueError("Provide --prediction_dirs or --detector_model with --image_sets")

    summary_rows: list[dict[str, object]] = []
    class_rows: list[dict[str, object]] = []
    manifest = {
        "ground_truth_dir": str(gt_dir),
        "iou_thresholds": args.iou_thresholds,
        "detector_model": args.detector_model,
        "detector_classes": args.detector_classes,
        "prediction_class_map": {str(source): target for source, target in args.prediction_class_map},
        "drop_unmapped_prediction_classes": args.drop_unmapped_prediction_classes,
        "restrict_predictions_to_gt": args.restrict_predictions_to_gt,
        "prediction_dirs": {},
    }
    prediction_class_map = dict(args.prediction_class_map)
    gt_image_ids = set(gt_by_image)
    for label, pred_dir in prediction_dirs:
        pred_by_image = load_yolo_dir(pred_dir.expanduser(), is_prediction=True)
        pred_by_image = remap_predictions(
            pred_by_image,
            prediction_class_map,
            args.drop_unmapped_prediction_classes,
        )
        if args.restrict_predictions_to_gt:
            pred_by_image = restrict_to_image_ids(pred_by_image, gt_image_ids)
        summary, per_class = evaluate_config(label, gt_by_image, pred_by_image, args.iou_thresholds)
        summary["prediction_dir"] = str(pred_dir)
        summary_rows.append(summary)
        class_rows.extend(per_class)
        manifest["prediction_dirs"][label] = str(pred_dir)

    write_csv(output_dir / "detection_summary.csv", summary_rows)
    write_csv(output_dir / "detection_per_class.csv", class_rows)
    write_markdown(output_dir / "detection_summary.md", summary_rows)
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    print(f"Wrote {output_dir / 'detection_summary.csv'}")
    print(f"Wrote {output_dir / 'detection_per_class.csv'}")
    print(f"Wrote {output_dir / 'detection_summary.md'}")


if __name__ == "__main__":
    main()
