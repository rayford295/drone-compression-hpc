#!/usr/bin/env python3
"""Run an open-vocabulary detector (YOLO-World) over an image folder.

Writes YOLO-format prediction files (one ``.txt`` per image) with lines:

    class_id  x_center  y_center  width  height  confidence

Coordinates are normalized (0-1). ``class_id`` is the index of the matched prompt
in ``--classes`` (so the prompt ORDER must match the ground-truth class ids:
by default ``vehicle`` -> 0 and ``building`` -> 1, matching
``build_detection_gt_vehicle_building.py``).

The prediction folders this produces are consumed directly by
``evaluate_object_detection_impact.py --prediction_dirs LABEL=PATH``.

YOLO-World is the recommended open-vocab detector here because it integrates with
the same Ultralytics stack as the COCO pilot. If it underperforms on top-down
small objects, swap in GroundingDINO behind the same output contract.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG", ".tif", ".tiff"}
ROBOFLOW_SUFFIX = re.compile(r"_JPG\.rf\.[0-9a-fA-F]+$", re.IGNORECASE)


def normalize_image_id(stem: str) -> str:
    return ROBOFLOW_SUFFIX.sub("", stem)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image_dir", required=True, help="Folder of images to run detection on")
    parser.add_argument("--output_dir", required=True, help="Folder to write YOLO-format prediction .txt files")
    parser.add_argument("--classes", nargs="+", default=["vehicle", "building"],
                        help="Open-vocab text prompts. Order defines class ids (default: vehicle=0 building=1).")
    parser.add_argument("--model", default="yolov8x-worldv2.pt",
                        help="Ultralytics YOLO-World weights (downloaded on first use if absent).")
    parser.add_argument("--conf", type=float, default=0.02,
                        help="Confidence floor. Keep low for AP/recall analysis (the evaluator sweeps thresholds).")
    parser.add_argument("--imgsz", type=int, default=1280)
    parser.add_argument("--device", default="", help="Ultralytics device, e.g. 0 or cpu")
    args = parser.parse_args()

    try:
        from ultralytics import YOLOWorld
    except Exception as exc:  # pragma: no cover - import guard
        sys.exit(f"Could not import ultralytics YOLOWorld ({exc}). Install with: pip install --user ultralytics")

    image_dir = pathlib.Path(args.image_dir).expanduser()
    images = sorted(p for p in image_dir.iterdir() if p.suffix in IMAGE_SUFFIXES)
    if not images:
        sys.exit(f"No images found in {image_dir}")

    out = pathlib.Path(args.output_dir).expanduser()
    out.mkdir(parents=True, exist_ok=True)

    model = YOLOWorld(args.model)
    model.set_classes(args.classes)
    print(f"Loaded {args.model}; prompts -> {dict(enumerate(args.classes))}")

    predict_kwargs = dict(conf=args.conf, imgsz=args.imgsz, verbose=False)
    if args.device:
        predict_kwargs["device"] = args.device

    total_boxes = 0
    per_class = {i: 0 for i in range(len(args.classes))}
    for img in images:
        results = model.predict(source=str(img), **predict_kwargs)
        lines: list[str] = []
        for r in results:
            boxes = getattr(r, "boxes", None)
            if boxes is None:
                continue
            xywhn = boxes.xywhn.cpu().numpy()
            cls = boxes.cls.cpu().numpy().astype(int)
            conf = boxes.conf.cpu().numpy()
            for (cx, cy, w, h), c, p in zip(xywhn, cls, conf):
                lines.append(f"{int(c)} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f} {p:.6f}")
                per_class[int(c)] = per_class.get(int(c), 0) + 1
                total_boxes += 1
        (out / f"{normalize_image_id(img.stem)}.txt").write_text(
            "\n".join(lines) + ("\n" if lines else "")
        )

    print(f"Wrote predictions for {len(images)} images to {out}")
    print(f"  total predicted boxes: {total_boxes}")
    for i, name in enumerate(args.classes):
        print(f"  class {i} ({name}): {per_class.get(i, 0)}")


if __name__ == "__main__":
    main()
