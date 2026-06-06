# SC26 Detection Impact Input Plan, 2026-06-06

This page records the current blocker for the downstream object-detection impact experiment.

## Current Status

The formal compression x tile-size tradeoff runs are complete and packaged:

- Smoke run: `results/2026-06-05-tradeoff-smoke/`
- Formal N50 LPIPS run: `results/2026-06-05-tradeoff-n50-lpips/`
- Detection label self-test: `results/2026-06-06-detection-label-selftest/`

The next planned formal experiment is object-detection impact, using `experiments/compression/slurm/08_object_detection_impact.sbatch`. The wrapper and evaluator are working, but the formal job cannot run yet because reviewed detection labels and a detector checkpoint or prediction folders are still missing.

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

## Local Image Dataset Audit

The local image dataset is available on Yifan's Mac at:

```text
/Users/yifn/Desktop/26 SC/OneDrive_1_2026-4-11/100_0005/
```

Audit result:

- `363` image files were found.
- The images are DJI `.JPG` files with size `5472 x 3648`.
- No `.txt`, `.json`, `.xml`, `.yaml`, or `.csv` annotation files were found in the dataset folder.
- The first sorted image is `100_0005_0001.JPG`.
- The compression runner selects images by sorted filename order, so the formal `N_IMAGES=50` tradeoff run used `100_0005_0001.JPG` through `100_0005_0050.JPG` when `START_INDEX=0`.

This means the local folder can provide the original image inputs, but it is not yet a ground-truth object-detection dataset.

## Pilot Labels Added

A small GitHub-safe pilot label package has been added at:

```text
data/detection_pilot/labels_yolo_vehicle_n8/
```

Contents:

- `8` YOLO label files for `100_0005_0001.JPG` through `100_0005_0008.JPG`
- `234` total draft vehicle boxes
- One class: `0 vehicle`
- Metadata and notes in `README.md`, `data.yaml`, `manifest.json`, and `pilot_images.txt`

These labels are intended to validate the object-detection-impact pipeline on the same first `8` images that were saved as visual examples during the N50 LPIPS tradeoff run. They are not yet publication-grade ground truth. Review and correction are still required before reporting formal mAP values in the paper.

## DeltaAI Label Self-Test Completed

The N8 pilot labels were staged on DeltaAI and used in a self-test where the same label folder was passed as ground truth and predictions.

Job summary:

| Item | Value |
|------|-------|
| Job ID | `2425654` |
| Run stamp | `20260606_detection_label_selftest` |
| State | `COMPLETED` |
| Elapsed | `00:00:06` |
| Batch MaxRSS | `51904K` |
| Output root | `/projects/bfod/yyang48/cdc-deltaai/output/sc26_compression/20260606_detection_label_selftest/08_object_detection_impact` |

Result:

| configuration | mAP@0.5 | mAP@0.5:0.95 | Precision@0.5 | Recall@0.5 | F1@0.5 | GT boxes | Prediction boxes |
|---------------|---------|--------------|----------------|------------|--------|----------|------------------|
| `self` | `1.0` | `1.0` | `1.0` | `1.0` | `1.0` | `234` | `234` |

Interpretation: the SLURM wrapper, label loader, and metric writer are functional. This is a sanity check only, not a downstream detection-impact result.

## Practical Labeling Strategy

Because there are no existing formal labels, start with the small manual YOLO labeling pilot rather than trying to label all `363` images at once.

Recommended pilot:

- Label the first `8` images first, because the N50 tradeoff run saved visual/reconstruction outputs for `SAVE_VISUAL_LIMIT=8`.
- Use one conservative class for the first pilot:

```text
0 vehicle
```

Reason: vehicles are visible in the drone images and are suitable for a standard object-detection sanity check. This supports a downstream computer-vision stability claim, but it should be described as vehicle-detection impact, not debris/damage detection, unless debris/damage labels are added later.

Pilot target labels:

```text
data/detection_pilot/labels_yolo_vehicle_n8/labels/
├── 100_0005_0001.txt
├── 100_0005_0002.txt
├── 100_0005_0003.txt
├── 100_0005_0004.txt
├── 100_0005_0005.txt
├── 100_0005_0006.txt
├── 100_0005_0007.txt
└── 100_0005_0008.txt
```

If the pilot workflow succeeds, expand to the first `50` sorted images so the detection-impact set matches the formal N50 compression x tile-size table.

To stage the pilot labels on DeltaAI:

```bash
cd /projects/bfod/yyang48/cdc-deltaai/code_main_641d86c
mkdir -p /projects/bfod/yyang48/cdc-deltaai/data/labels_yolo_vehicle_n8
rsync -av data/detection_pilot/labels_yolo_vehicle_n8/labels/ \
  /projects/bfod/yyang48/cdc-deltaai/data/labels_yolo_vehicle_n8/
```

Then use:

```bash
DETECTION_GT_DIR=/projects/bfod/yyang48/cdc-deltaai/data/labels_yolo_vehicle_n8
```

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

For the pilot, the remaining requirements are:

1. Review the `N8` draft vehicle labels and correct any missed or over-broad boxes.
2. Provide a detector checkpoint, such as an Ultralytics-compatible `best.pt`, or provide existing YOLO prediction folders.
3. Confirm which configurations should be evaluated:
   - original
   - balanced `checkpoint_b00064` plus `256 x 256`
   - balanced `checkpoint_b00064` plus `512 x 512`
   - high-compression `checkpoint_b00128` plus the selected tile size

For formal paper numbers, expand and review the labels to the first `50` sorted images, or obtain the original object-detection ground truth from the data owner. If no reviewed labels and no detector weights exist yet, the formal object-detection impact experiment should remain pending rather than be reported as completed.

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
