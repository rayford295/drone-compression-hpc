# SC26 Plan — Compression Impact on Open-Vocabulary Detection (Vehicle & Building)

Date: 2026-06-09
Status: Proposed (design agreed; implementation plan to follow)
Owner: Yifan

## Goal

Quantify how lossy compression degrades open-vocabulary detection of **vehicles**
and **buildings** in high-resolution drone imagery, and compare **traditional JPEG**
against **CDC diffusion reconstruction at matched compression ratios**. The headline
question is whether small objects (vehicles) degrade faster than large objects
(buildings), and whether CDC preserves downstream detectability better than JPEG at the
same storage budget.

This extends Experiment 4 (object-detection impact) with (a) the new human-labeled
vehicle+building ground truth in `data/detection_labels/`, (b) an open-vocabulary
detector that can score both classes, and (c) a JPEG baseline alongside CDC.

## Test set

- Fixed **50 images**: `100_0005_0001`–`100_0005_0050` (aligns with the existing N50
  reconstruction, detection, and SAM pipelines for cross-comparison).
- Ground truth: human labels from `data/detection_labels/`, merged into a 2-class set:
  - class `0` = vehicle (from `vehicle/labels/`)
  - class `1` = building (from `building/labels/`, remapped 0 → 1)

## Image families (7 sets, 50 images each, paired by compression ratio)

| Ratio tier | Traditional compression | CDC reconstruction |
| --- | --- | --- |
| ~30x  | JPEG @ ~30x  | CDC `b00512` + 512 tile (High quality 512) |
| ~80x  | JPEG @ ~80x  | CDC `b00064` + 256 tile (Balanced 256) |
| ~140x | JPEG @ ~140x | CDC `b00128` + 256 tile (Max compression 256) |
| baseline | — | **Original** (uncompressed reference) |

Conceptually three families (original / compressed / reconstructed); compressed and
reconstructed are each split into three fidelity tiers and matched pairwise so we can
compare JPEG vs CDC at equal storage and also plot degradation curves.

## Pipeline

1. **Freeze test set** — extract images `0001`–`0050` and assemble the 2-class GT
   (vehicle = 0, building = 1).
2. **Build compressed sets**
   - JPEG (local, PIL): tune per-image quality to hit each target compression ratio;
     record realized BPP / ratio per image and per tier.
   - CDC (DeltaAI): reuse the existing three-tier reconstruction outputs for these 50
     images. Reconstruction is a GPU/HPC step and is not re-run locally.
3. **Open-vocabulary detection** — run **YOLO-World** (recommended for clean integration
   with the existing Ultralytics-based evaluator; GroundingDINO is the alternative) with
   text prompts `vehicle` and `building` on all 7 sets, writing YOLO-format predictions.
4. **Evaluate** — reuse `experiments/compression/evaluate_object_detection_impact.py`
   (extended to two classes) to produce per-class and overall **mAP@0.5, mAP@0.5:0.95,
   precision, recall, F1** for each set.
5. **Analyze** — degradation curves (metric vs compression ratio), JPEG-vs-CDC at matched
   ratio, vehicle-vs-building sensitivity, and a small-object size breakdown.

## Reuse vs new

- **Reuse:** `evaluate_object_detection_impact.py` (metrics), `prepare_detection_image_sets.py`
  (set preparation), the `08_object_detection_impact.sbatch` SLURM pattern, existing CDC
  reconstruction outputs.
- **New:** (1) JPEG matched-ratio compressor; (2) open-vocabulary detector wrapper that
  emits YOLO-format predictions; (3) 2-class GT assembly from `data/detection_labels/`;
  (4) analysis and plotting.

## Dependencies and risks

1. **CDC reconstructions must be available on DeltaAI** for these 50 images at all three
   tiers; otherwise reconstruct on the HPC first.
2. **Label–image alignment**: the Roboflow export may have resized the source images.
   Before scoring, overlay GT on the originals to confirm normalized coordinates align.
3. **Open-vocabulary accuracy on top-down small objects may be modest** — run a sanity
   check on the originals first to establish a baseline before comparing compressed sets.

## Deliverables

- Scripts under `experiments/compression/`.
- Result package under `results/2026-06-09-detection-openvocab-veh-bldg/`
  (CSV/Markdown tables, degradation plots, small visual examples; no raw images).
