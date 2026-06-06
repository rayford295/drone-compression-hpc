# SC26 Detection Impact Input Plan, 2026-06-06

This page records the current blocker for the downstream object-detection impact experiment.

## Current Status

The formal compression x tile-size tradeoff runs are complete and packaged:

- Smoke run: `results/2026-06-05-tradeoff-smoke/`
- Formal N50 LPIPS run: `results/2026-06-05-tradeoff-n50-lpips/`

The next planned experiment is object-detection impact, using `experiments/compression/slurm/08_object_detection_impact.sbatch`. That job cannot run yet because the required detection inputs are missing on DeltaAI.

## DeltaAI Input Audit

These checks were run on `gh-login03` from:

```text
/projects/bfod/yyang48/cdc-deltaai/code_main_641d86c
```

Ground-truth label search:

```bash
find /projects/bfod/yyang48/cdc-deltaai/data -maxdepth 5 -type d \
  \( -iname "*label*" -o -iname "*yolo*" -o -iname "*annotation*" \) -print
```

Result: no matching label, YOLO, or annotation directory was found.

Detector-weight search:

```bash
find /projects/bfod/yyang48 -maxdepth 7 -type f \
  \( -iname "*.pt" -o -iname "*.engine" -o -iname "*.onnx" \) \
  | grep -Ei "yolo|detect|detector|best|damage|debris" || true
```

Result: no matching detector model was found.

## Required Inputs

To run object-detection impact, provide one of these two input sets.

### Option A: Existing Prediction Labels

Use this if detections have already been generated elsewhere.

Required:

- YOLO-format ground-truth labels for the raw images.
- YOLO-format prediction label folders for each condition.

Expected layout:

```text
/projects/bfod/yyang48/cdc-deltaai/data/labels_yolo/
/projects/bfod/yyang48/cdc-deltaai/output/detection_predictions/original/
/projects/bfod/yyang48/cdc-deltaai/output/detection_predictions/best_quality/
/projects/bfod/yyang48/cdc-deltaai/output/detection_predictions/balanced/
/projects/bfod/yyang48/cdc-deltaai/output/detection_predictions/max_compression/
```

Run command after those folders exist:

```bash
RUN_STAMP=20260606_detection_impact \
DETECTION_GT_DIR=/projects/bfod/yyang48/cdc-deltaai/data/labels_yolo \
DETECTION_PREDICTION_DIRS="original=/projects/bfod/yyang48/cdc-deltaai/output/detection_predictions/original best_quality=/projects/bfod/yyang48/cdc-deltaai/output/detection_predictions/best_quality balanced=/projects/bfod/yyang48/cdc-deltaai/output/detection_predictions/balanced max_compression=/projects/bfod/yyang48/cdc-deltaai/output/detection_predictions/max_compression" \
sbatch --export=ALL,REPO_DIR=/projects/bfod/yyang48/cdc-deltaai/code_main_641d86c \
  experiments/compression/slurm/08_object_detection_impact.sbatch
```

### Option B: Detector Model plus Image Sets

Use this if predictions need to be generated inside the SLURM job.

Required:

- YOLO-format ground-truth labels.
- An Ultralytics-compatible detector model, such as `best.pt`.
- Image folders for original and reconstructed images.

Expected layout:

```text
/projects/bfod/yyang48/cdc-deltaai/data/labels_yolo/
/projects/bfod/yyang48/models/detector.pt
/projects/bfod/yyang48/cdc-deltaai/data/imgs/
/projects/bfod/yyang48/cdc-deltaai/output/detection_image_sets/balanced/
/projects/bfod/yyang48/cdc-deltaai/output/detection_image_sets/max_compression/
```

Run command after those folders exist:

```bash
RUN_STAMP=20260606_detection_impact \
DETECTION_GT_DIR=/projects/bfod/yyang48/cdc-deltaai/data/labels_yolo \
DETECTION_MODEL=/projects/bfod/yyang48/models/detector.pt \
DETECTION_IMAGE_SETS="original=/projects/bfod/yyang48/cdc-deltaai/data/imgs balanced=/projects/bfod/yyang48/cdc-deltaai/output/detection_image_sets/balanced max_compression=/projects/bfod/yyang48/cdc-deltaai/output/detection_image_sets/max_compression" \
sbatch --export=ALL,REPO_DIR=/projects/bfod/yyang48/cdc-deltaai/code_main_641d86c \
  experiments/compression/slurm/08_object_detection_impact.sbatch
```

## Immediate Next Task

Ask the group or data owner for:

1. YOLO-format labels for the drone image subset used in this repo.
2. The detector checkpoint used for debris or damage detection, if one exists.
3. Confirmation of which configurations should be evaluated:
   - original
   - balanced `checkpoint_b00064` plus `256 x 256`
   - balanced `checkpoint_b00064` plus `512 x 512`
   - high-compression `checkpoint_b00128` plus the selected tile size

If labels and detector weights do not exist yet, object-detection impact should be marked as pending rather than run as a failed SLURM job.

## GitHub-Safe Output Package

After the detection job succeeds, commit only:

```text
results/YYYY-MM-DD-detection-impact/
├── README.md
└── tables/
    ├── detection_summary.csv
    ├── detection_per_class.csv
    ├── detection_summary.md
    └── manifest.json
```

Do not commit model weights, raw images, generated prediction images, or large detector output folders.
