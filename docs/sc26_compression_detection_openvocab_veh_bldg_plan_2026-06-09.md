# SC26 Plan — Compression Impact on Open-Vocabulary Detection (Vehicle & Building)

Date: 2026-06-09
Status: Proposed (design agreed; experiment details to be confirmed before the HPC run)
Owner: Yifan

## Goal

Produce a **complete and detailed evaluation report** of how CDC diffusion compression
degrades open-vocabulary detection of **vehicles** and **buildings** in high-resolution
drone imagery. The headline questions:

1. How far can CDC compression go before detection degrades for each class?
2. Do small objects (vehicles) degrade faster than large objects (buildings)?

This extends Experiment 4 (object-detection impact) with (a) the new human-labeled
vehicle+building ground truth in `data/detection_labels/`, (b) an open-vocabulary detector
that can score both classes, and (c) a richer report (per-size breakdown, paired analysis,
dual-threshold reporting). It keeps the original Experiment 4 comparison structure
(Original / Best quality / Balanced / Max compression) for continuity with the June 2
response document.

> JPEG / traditional-codec baselines are explicitly out of scope for this report.

## Test set

- Fixed **50 images**: `100_0005_0001`–`100_0005_0050` (aligns with the existing N50
  reconstruction, detection, and SAM pipelines for cross-comparison).
- Ground truth: human labels from `data/detection_labels/`, merged into a 2-class set:
  - class `0` = vehicle (from `vehicle/labels/`)
  - class `1` = building (from `building/labels/`, remapped 0 → 1)

## Comparison matrix (4 image sets, 50 images each, 2 classes)

| Configuration | Image source | Compression | BPP |
| --- | --- | --- | --- |
| Original | Raw drone images | baseline | — |
| Best quality | CDC `b00512` + 512 tile | ~33x | 0.735 |
| Balanced | CDC `b00064` + 256 tile | ~80x | 0.258 |
| Max compression | CDC `b00128` + 256 tile | ~140x | 0.145 |

Matches Table 6 of the June 2 response. CDC compression produces a bitstream; the
viewable image used for detection is the **reconstruction**. The full-resolution
reconstructions live on DeltaAI and are reused here (reconstruction is a GPU/HPC step and
is not re-run locally).

For context, record realized **BPP, PSNR, SSIM, LPIPS** for every set so image fidelity
sits beside the detection metrics.

## Metrics (per set × class)

- Standard five: **mAP@0.5, mAP@0.5:0.95, precision, recall, F1** (matches the June 2
  reporting style).
- **Per-object-size AP**: small / medium / large by box area (COCO area bins) — quantifies
  the small-object-sensitivity question directly.
- **Degradation Δ** vs Original, per metric and per class.

## What makes the report "complete and detailed"

1. **Dual-threshold reporting**: AP metrics use a low confidence (0.001) for the full PR
   curve; also report at an operating threshold (the one that maximizes F1 on the
   originals) for a deployment view. This corrects the misleadingly low precision (~0.06)
   in the earlier pilot, which came from `DETECTION_CONF=0.001`.
2. **Paired analysis**: the same 50 images run through every configuration, so report
   per-image Δ and a paired significance check — this makes class-level claims defensible
   on a 50-image set.
3. **Small-object focus**: vehicle (small) vs building (large), layered with
   AP_small/medium/large, to locate the breakdown point.
4. **Qualitative panels**: a few Original-vs-reconstruction side-by-sides with predicted
   boxes overlaid, highlighting failure cases (missed small vehicles, merged/hallucinated
   building boxes).

## Pipeline

1. **Freeze test set** — extract images `0001`–`0050`; assemble the 2-class GT
   (vehicle = 0, building = 1).
2. **Gather image sets** — Original + the three CDC reconstruction tiers for these 50
   images from DeltaAI.
3. **Open-vocabulary detection** — run **YOLO-World** (recommended for clean integration
   with the existing Ultralytics-based evaluator; GroundingDINO is the fallback) with
   frozen text prompts for `vehicle` and `building` on all 4 sets, writing YOLO-format
   predictions.
4. **Evaluate** — reuse `experiments/compression/evaluate_object_detection_impact.py`
   (extended to two classes and per-size AP) for the metrics above.
5. **Analyze & report** — degradation curves (metric vs BPP), vehicle-vs-building
   sensitivity, per-size breakdown, paired deltas, qualitative panels.

## Reuse vs new

- **Reuse:** `evaluate_object_detection_impact.py` (metrics), `prepare_detection_image_sets.py`
  (set preparation), the `08_object_detection_impact.sbatch` SLURM pattern, existing CDC
  reconstruction outputs.
- **New:** (1) open-vocabulary detector wrapper that emits YOLO-format predictions;
  (2) 2-class GT assembly from `data/detection_labels/`; (3) per-size AP + paired analysis;
  (4) report assembly and plots.

## Dependencies and risks (with gates)

1. **Open-vocabulary accuracy on top-down small objects may be modest.** Gate: run a
   sanity check on the originals first. If YOLO-World cannot detect vehicles on the
   originals, switch to GroundingDINO; if that also fails, fall back to training a 2-class
   YOLO on the 100 labeled images.
2. **CDC reconstructions must be available on DeltaAI** for these 50 images at all three
   tiers; otherwise reconstruct on the HPC first.
3. **Label–image alignment**: the Roboflow export may have resized the source images.
   Before scoring, overlay GT on the originals to confirm normalized coordinates align.
4. **Frozen prompts**: tune the vehicle/building text prompts on the originals only, then
   freeze them for all compressed sets to avoid bias.

## Deliverables

- Scripts under `experiments/compression/`.
- Result package under `results/2026-06-09-detection-openvocab-veh-bldg/`
  (CSV/Markdown tables, degradation plots, small visual examples; no raw images).

## Next step

Experiment details (detector choice confirmation, prompt set, per-size bins, plot set)
will be reviewed together before the HPC run. This document is the agreed design;
implementation has not started.
