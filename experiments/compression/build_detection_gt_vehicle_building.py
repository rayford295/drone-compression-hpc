#!/usr/bin/env python3
"""Assemble a 2-class YOLO ground-truth folder from the human vehicle/building labels.

Inputs are the two single-class Roboflow exports in ``data/detection_labels/``:
  - ``vehicle/labels/*.txt``  (class 0 = vehicle in the source files)
  - ``building/labels/*.txt`` (class 0 = building in the source files)

Output is one merged label file per source image, with:
  - class 0 = vehicle
  - class 1 = building

Roboflow label filenames carry a hash suffix (``100_0005_0001_JPG.rf.<hash>.txt``).
By default the output filename is normalized back to the source-image stem
(``100_0005_0001.txt``) so it matches the reconstructed/original image stems used
in the detection image sets. Use ``--keep-hashed-names`` to keep the original names.

Coordinates are passed through unchanged (normalized YOLO ``cx cy w h``).
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

HASH_SUFFIX = re.compile(r"_JPG\.rf\.[0-9a-fA-F]+$")


def normalize_stem(stem: str, keep_hashed: bool) -> str:
    if keep_hashed:
        return stem
    return HASH_SUFFIX.sub("", stem)


def read_label(path: pathlib.Path, target_class: int) -> list[str]:
    """Return YOLO lines with the class id replaced by ``target_class``."""
    out: list[str] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 5:
            continue
        out.append(" ".join([str(target_class), *parts[1:5]]))
    return out


def collect(label_dir: pathlib.Path, target_class: int, keep_hashed: bool) -> dict[str, list[str]]:
    merged: dict[str, list[str]] = {}
    for f in sorted(label_dir.glob("*.txt")):
        stem = normalize_stem(f.stem, keep_hashed)
        merged.setdefault(stem, []).extend(read_label(f, target_class))
    return merged


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vehicle_dir", required=True, help="vehicle/labels directory (class 0 -> vehicle)")
    parser.add_argument("--building_dir", required=True, help="building/labels directory (class 0 -> building, remapped to 1)")
    parser.add_argument("--output_dir", required=True, help="Merged 2-class GT output directory")
    parser.add_argument("--vehicle_class", type=int, default=0)
    parser.add_argument("--building_class", type=int, default=1)
    parser.add_argument("--keep-hashed-names", action="store_true",
                        help="Keep the Roboflow hashed filenames instead of normalizing to the source-image stem.")
    args = parser.parse_args()

    veh = collect(pathlib.Path(args.vehicle_dir).expanduser(), args.vehicle_class, args.keep_hashed_names)
    bld = collect(pathlib.Path(args.building_dir).expanduser(), args.building_class, args.keep_hashed_names)

    out = pathlib.Path(args.output_dir).expanduser()
    out.mkdir(parents=True, exist_ok=True)

    stems = sorted(set(veh) | set(bld))
    if not stems:
        sys.exit("No labels found in either input directory.")

    veh_boxes = bld_boxes = images_with_both = 0
    for stem in stems:
        lines = veh.get(stem, []) + bld.get(stem, [])
        (out / f"{stem}.txt").write_text("\n".join(lines) + ("\n" if lines else ""))
        veh_boxes += len(veh.get(stem, []))
        bld_boxes += len(bld.get(stem, []))
        if veh.get(stem) and bld.get(stem):
            images_with_both += 1

    print(f"Wrote {len(stems)} merged GT files to {out}")
    print(f"  vehicle (class {args.vehicle_class}) boxes : {veh_boxes}")
    print(f"  building (class {args.building_class}) boxes: {bld_boxes}")
    print(f"  images with both classes               : {images_with_both}")
    print(f"  images vehicle-only / building-only     : "
          f"{sum(1 for s in stems if veh.get(s) and not bld.get(s))} / "
          f"{sum(1 for s in stems if bld.get(s) and not veh.get(s))}")


if __name__ == "__main__":
    main()
