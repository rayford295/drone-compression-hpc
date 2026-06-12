#!/usr/bin/env python3
"""Prepare a supervised YOLO dataset for vehicle + roof detection.

The source is the human-labeled Roboflow export:

    VehicleAndBuilding_labels/
    ├── vehicle/{images,labels}
    └── building/{images,labels}

The output follows the Ultralytics YOLO layout:

    output/
    ├── images/{train,val,test}
    ├── labels/{train,val,test}
    ├── data.yaml
    └── manifest.json

Class IDs in the output are:

    0 = vehicle
    1 = roof

The building labels are treated as roof/roof-footprint labels because the images
are top-down drone views and the open-vocabulary "building" gate failed.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import shutil


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
HASH_SUFFIX = re.compile(r"_JPG\.rf\.[0-9a-fA-F]+$", re.IGNORECASE)


def normalize_stem(stem: str) -> str:
    return HASH_SUFFIX.sub("", stem)


def parse_range(value: str) -> list[int]:
    if ":" not in value:
        return [int(value)]
    start, end = value.split(":", 1)
    start_i = int(start)
    end_i = int(end)
    if start_i > end_i:
        raise argparse.ArgumentTypeError(f"Invalid range {value}: start > end")
    return list(range(start_i, end_i + 1))


def image_id(prefix: str, index: int) -> str:
    return f"{prefix}_{index:04d}"


def index_files(path: pathlib.Path, suffixes: set[str]) -> dict[str, pathlib.Path]:
    files: dict[str, pathlib.Path] = {}
    for item in sorted(path.iterdir()):
        if item.is_file() and item.suffix.lower() in suffixes:
            files.setdefault(normalize_stem(item.stem), item)
    return files


def read_label(path: pathlib.Path | None, class_id: int) -> list[str]:
    if path is None or not path.exists():
        return []
    rows: list[str] = []
    for line in path.read_text().splitlines():
        parts = line.strip().split()
        if len(parts) < 5:
            continue
        rows.append(" ".join([str(class_id), *parts[1:5]]))
    return rows


def link_or_copy(src: pathlib.Path, dst: pathlib.Path, copy_files: bool, overwrite: bool) -> None:
    if dst.exists() or dst.is_symlink():
        if not overwrite:
            return
        dst.unlink()
    if copy_files:
        shutil.copy2(src, dst)
    else:
        os.symlink(src.resolve(), dst)


def prepare_split(
    split: str,
    indices: list[int],
    prefix: str,
    image_index: dict[str, pathlib.Path],
    vehicle_label_index: dict[str, pathlib.Path],
    roof_label_index: dict[str, pathlib.Path],
    output_dir: pathlib.Path,
    copy_files: bool,
    overwrite: bool,
) -> dict[str, object]:
    image_out = output_dir / "images" / split
    label_out = output_dir / "labels" / split
    image_out.mkdir(parents=True, exist_ok=True)
    label_out.mkdir(parents=True, exist_ok=True)

    missing_images: list[str] = []
    image_count = vehicle_boxes = roof_boxes = 0
    for index in indices:
        stem = image_id(prefix, index)
        src = image_index.get(stem)
        if src is None:
            missing_images.append(stem)
            continue
        dst_image = image_out / f"{stem}{src.suffix.lower()}"
        link_or_copy(src, dst_image, copy_files, overwrite)

        vehicle_rows = read_label(vehicle_label_index.get(stem), 0)
        roof_rows = read_label(roof_label_index.get(stem), 1)
        (label_out / f"{stem}.txt").write_text(
            "\n".join(vehicle_rows + roof_rows) + ("\n" if vehicle_rows or roof_rows else "")
        )
        image_count += 1
        vehicle_boxes += len(vehicle_rows)
        roof_boxes += len(roof_rows)

    return {
        "split": split,
        "requested_images": len(indices),
        "written_images": image_count,
        "vehicle_boxes": vehicle_boxes,
        "roof_boxes": roof_boxes,
        "missing_images": missing_images,
    }


def write_data_yaml(output_dir: pathlib.Path) -> None:
    (output_dir / "data.yaml").write_text(
        "\n".join(
            [
                f"path: {output_dir.resolve()}",
                "train: images/train",
                "val: images/val",
                "test: images/test",
                "names:",
                "  0: vehicle",
                "  1: roof",
                "",
            ]
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source_root", required=True, help="Root containing vehicle/ and building/ Roboflow folders")
    parser.add_argument("--output_dir", required=True, help="Output YOLO dataset root")
    parser.add_argument("--image_prefix", default="100_0005")
    parser.add_argument("--train_range", default="51:90", help="Inclusive image-index range, default 51:90")
    parser.add_argument("--val_range", default="91:100", help="Inclusive image-index range, default 91:100")
    parser.add_argument("--test_range", default="1:50", help="Inclusive image-index range, default 1:50")
    parser.add_argument("--copy", action="store_true", help="Copy images instead of symlinking")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    source_root = pathlib.Path(args.source_root).expanduser()
    output_dir = pathlib.Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    vehicle_images = index_files(source_root / "vehicle" / "images", IMAGE_SUFFIXES)
    building_images = index_files(source_root / "building" / "images", IMAGE_SUFFIXES)
    image_index = {**building_images, **vehicle_images}
    vehicle_labels = index_files(source_root / "vehicle" / "labels", {".txt"})
    roof_labels = index_files(source_root / "building" / "labels", {".txt"})

    splits = {
        "train": parse_range(args.train_range),
        "val": parse_range(args.val_range),
        "test": parse_range(args.test_range),
    }
    summaries = [
        prepare_split(
            split,
            indices,
            args.image_prefix,
            image_index,
            vehicle_labels,
            roof_labels,
            output_dir,
            args.copy,
            args.overwrite,
        )
        for split, indices in splits.items()
    ]
    write_data_yaml(output_dir)

    manifest = {
        "source_root": str(source_root),
        "output_dir": str(output_dir),
        "copy": args.copy,
        "class_names": {"0": "vehicle", "1": "roof"},
        "splits": summaries,
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    for summary in summaries:
        print(
            f"{summary['split']}: images={summary['written_images']}/{summary['requested_images']} "
            f"vehicle_boxes={summary['vehicle_boxes']} roof_boxes={summary['roof_boxes']} "
            f"missing={len(summary['missing_images'])}"
        )
    print(f"Wrote {output_dir / 'data.yaml'}")
    print(f"Wrote {output_dir / 'manifest.json'}")


if __name__ == "__main__":
    main()
