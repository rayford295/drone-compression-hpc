#!/usr/bin/env python3
"""Prepare image-set folders for object-detection impact evaluation.

The detection evaluator compares predictions against YOLO label files by image
stem. This helper builds small image folders that match the ground-truth label
stems, which is useful when only a pilot subset is labeled.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import shutil


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
ROBOFLOW_SUFFIX = re.compile(r"_JPG\.rf\.[0-9a-fA-F]+$", re.IGNORECASE)


def parse_label_mapping(value: str) -> tuple[str, pathlib.Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError(f"Expected label=path, got: {value}")
    label, path = value.split("=", 1)
    label = label.strip()
    if not label:
        raise argparse.ArgumentTypeError(f"Empty label in: {value}")
    return label, pathlib.Path(path).expanduser()


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


def list_gt_image_ids(gt_dir: pathlib.Path) -> list[str]:
    image_ids = [normalize_image_id(path.stem) for path in sorted(gt_dir.glob("*.txt"))]
    if not image_ids:
        raise ValueError(f"No YOLO label files found in {gt_dir}")
    return image_ids


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


def build_source_index(source_dir: pathlib.Path, recursive: bool) -> dict[str, list[pathlib.Path]]:
    index: dict[str, list[pathlib.Path]] = {}
    for path in iter_images(source_dir, recursive):
        image_id = normalize_image_id(path.stem)
        index.setdefault(image_id, []).append(path)
    return index


def link_or_copy(src: pathlib.Path, dst: pathlib.Path, copy_files: bool, overwrite: bool) -> None:
    if dst.exists() or dst.is_symlink():
        if not overwrite:
            return
        dst.unlink()
    if copy_files:
        shutil.copy2(src, dst)
    else:
        os.symlink(src.resolve(), dst)


def prepare_set(
    label: str,
    source_dir: pathlib.Path,
    image_ids: list[str],
    output_root: pathlib.Path,
    recursive: bool,
    copy_files: bool,
    overwrite: bool,
) -> dict[str, object]:
    source_index = build_source_index(source_dir, recursive)
    out_dir = output_root / label
    out_dir.mkdir(parents=True, exist_ok=True)
    linked: list[dict[str, str]] = []
    missing: list[str] = []

    for image_id in image_ids:
        candidates = source_index.get(image_id, [])
        if not candidates:
            missing.append(image_id)
            continue
        selected = sorted(candidates, key=lambda path: candidate_priority(path, image_id))[0]
        dst = out_dir / f"{image_id}{selected.suffix.lower()}"
        link_or_copy(selected, dst, copy_files, overwrite)
        linked.append(
            {
                "image_id": image_id,
                "source": str(selected),
                "prepared": str(dst),
            }
        )

    return {
        "label": label,
        "source_dir": str(source_dir),
        "output_dir": str(out_dir),
        "linked_count": len(linked),
        "missing_count": len(missing),
        "missing": missing,
        "images": linked,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ground_truth_dir", required=True, help="YOLO label folder that defines image IDs")
    parser.add_argument(
        "--image_sets",
        nargs="+",
        type=parse_label_mapping,
        metavar="LABEL=PATH",
        help="Source image folders to subset, e.g. original=/path/to/imgs balanced=/path/to/visuals",
    )
    parser.add_argument("--output_dir", required=True, help="Prepared image-set output root")
    parser.add_argument("--recursive", action="store_true", help="Search source folders recursively")
    parser.add_argument("--copy", action="store_true", help="Copy files instead of creating symlinks")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing prepared files")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    gt_dir = pathlib.Path(args.ground_truth_dir).expanduser()
    output_dir = pathlib.Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    image_ids = list_gt_image_ids(gt_dir)

    summaries = [
        prepare_set(
            label,
            source_dir.expanduser(),
            image_ids,
            output_dir,
            args.recursive,
            args.copy,
            args.overwrite,
        )
        for label, source_dir in args.image_sets
    ]

    manifest = {
        "ground_truth_dir": str(gt_dir),
        "image_ids": image_ids,
        "copy": args.copy,
        "recursive": args.recursive,
        "sets": summaries,
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    for summary in summaries:
        print(
            f"{summary['label']}: linked {summary['linked_count']} images, "
            f"missing {summary['missing_count']} -> {summary['output_dir']}"
        )
    print(f"Wrote {output_dir / 'manifest.json'}")


if __name__ == "__main__":
    main()
