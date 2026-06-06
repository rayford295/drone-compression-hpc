# Detection Label Self-Test, 2026-06-06

This package records the DeltaAI sanity check for the object-detection impact evaluator.

Purpose:

- Confirm that `experiments/compression/slurm/08_object_detection_impact.sbatch` runs on DeltaAI.
- Confirm that the N8 draft YOLO vehicle labels can be loaded as ground truth.
- Confirm that the evaluator writes summary CSV, per-class CSV, Markdown, and manifest outputs.

This is not a formal object-detection impact result. The test uses the ground-truth label folder as both ground truth and prediction input, so the expected metrics are all `1.0`.

## DeltaAI Job

| Item | Value |
|------|-------|
| Job ID | `2425654` |
| Run stamp | `20260606_detection_label_selftest` |
| State | `COMPLETED` |
| Elapsed | `00:00:06` |
| Batch MaxRSS | `51904K` |
| GPU | `1 x NVIDIA GH200` |
| Memory request | `64G` |
| Output root | `/projects/bfod/yyang48/cdc-deltaai/output/sc26_compression/20260606_detection_label_selftest/08_object_detection_impact` |

## Inputs

```text
DETECTION_GT_DIR=/projects/bfod/yyang48/cdc-deltaai/data/labels_yolo_vehicle_n8
DETECTION_PREDICTION_DIRS="self=/projects/bfod/yyang48/cdc-deltaai/data/labels_yolo_vehicle_n8"
```

The input label folder contains `8` image label files and `234` total draft vehicle boxes.

## Result

| configuration | mAP@0.5 | mAP@0.5:0.95 | Precision@0.5 | Recall@0.5 | F1@0.5 | GT boxes | Prediction boxes |
|---------------|---------|--------------|----------------|------------|--------|----------|------------------|
| `self` | `1.0` | `1.0` | `1.0` | `1.0` | `1.0` | `234` | `234` |

Interpretation: the detection-impact evaluator and SLURM wrapper are working. The next real experiment needs a detector checkpoint, such as an Ultralytics-compatible `best.pt`, or existing YOLO prediction folders for original and reconstructed images.
