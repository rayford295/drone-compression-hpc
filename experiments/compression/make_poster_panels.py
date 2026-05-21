#!/usr/bin/env python3
"""Generate poster QA panels from saved SC26 visual outputs."""

from __future__ import annotations

import argparse
import pathlib

from poster_panels import build_panels_for_visuals_dir


def iter_visual_dirs(root: pathlib.Path) -> list[pathlib.Path]:
    direct = root / "visuals"
    if direct.is_dir():
        return [direct]
    return sorted(path for path in root.rglob("visuals") if path.is_dir())


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Create original/reconstruction/difference-map poster panels from "
            "existing SC26 compression visuals."
        )
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--visuals_dir", help="One visuals directory from a run")
    group.add_argument("--root", help="Run root to scan recursively for visuals directories")
    parser.add_argument("--results_csv", default=None, help="Optional results.csv for exact metrics")
    parser.add_argument("--out_dir", default=None, help="Output directory for one --visuals_dir run")
    parser.add_argument("--max_edge", type=int, default=1200, help="Longest image edge in the panel")
    parser.add_argument("--max_panels", type=int, default=8, help="Maximum panels per visuals directory; 0 saves all")
    parser.add_argument("--overwrite", action="store_true", help="Regenerate panels that already exist")
    args = parser.parse_args()

    if args.visuals_dir:
        written = build_panels_for_visuals_dir(
            args.visuals_dir,
            results_csv=args.results_csv,
            out_dir=args.out_dir,
            max_edge=args.max_edge,
            max_panels=args.max_panels,
            overwrite=args.overwrite,
        )
        for path in written:
            print(path)
        print(f"Wrote or found {len(written)} poster panel(s)")
        return

    root = pathlib.Path(args.root)
    total = 0
    for visuals_dir in iter_visual_dirs(root):
        written = build_panels_for_visuals_dir(
            visuals_dir,
            max_edge=args.max_edge,
            max_panels=args.max_panels,
            overwrite=args.overwrite,
        )
        total += len(written)
        for path in written:
            print(path)
    print(f"Wrote or found {total} poster panel(s)")


if __name__ == "__main__":
    main()
