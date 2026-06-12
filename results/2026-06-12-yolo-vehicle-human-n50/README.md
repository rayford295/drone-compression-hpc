# YOLO Vehicle Detection, Human N50, 2026-06-12

This package records the vehicle-only object-detection results from the human-labeled
N50 test set. It uses COCO-pretrained YOLOv8x as the detector and maps COCO vehicle
classes to the single project class `vehicle`.

This is the class-aware object-detection result for vehicles. It is separate from the
SAM vehicle and roof package, which measures prompt-based mask stability rather than
detection accuracy.

## DeltaAI Run

| Item | Value |
|------|-------|
| Repo commit | `539d9b0` |
| Slurm job | `2479273` |
| Run stamp | `20260612_detection_yolo_vehicle_human_n50` |
| Result root | `/projects/bfod/$USER/cdc-deltaai/output/sc26_compression/20260612_detection_yolo_vehicle_human_n50/08_object_detection_impact` |
| Ground truth | `/projects/bfod/$USER/cdc-deltaai/data/gt_human_n50/vehicle` |
| Detector | `yolov8x.pt` |
| Detector classes | COCO `2 car`, `5 bus`, `7 truck` |
| Class map | `2=0 5=0 7=0` |
| Test images | `50` |
| Vehicle GT boxes | `1013` |
| Image sets | `original`, `high_quality_512`, `balanced_256`, `max_compression_256` |

Raw images, reconstructed images, raw YOLO prediction labels, logs, model weights, and
Ultralytics output folders remain on DeltaAI storage. This package stores only lightweight
summary tables.

## Final Operating Point

The detector first ran at low confidence (`conf=0.001`) to preserve the full score range.
A threshold sweep then filtered the saved predictions without rerunning YOLO. We use
`conf=0.25` as the report-ready operating point because it is the YOLO default confidence
threshold and it gives the best F1 among the tested thresholds.

| Configuration | mAP@0.5 | mAP@0.5:0.95 | Precision | Recall | F1 | GT | Predictions |
|---------------|--------:|-------------:|----------:|-------:|---:|---:|------------:|
| original | 0.697209 | 0.366182 | 0.682184 | 0.752221 | 0.715493 | 1013 | 1117 |
| high_quality_512 | 0.622906 | 0.208523 | 0.637184 | 0.696940 | 0.665724 | 1013 | 1108 |
| balanced_256 | 0.605004 | 0.201938 | 0.654545 | 0.675222 | 0.664723 | 1013 | 1045 |
| max_compression_256 | 0.531950 | 0.175555 | 0.639035 | 0.601185 | 0.619532 | 1013 | 953 |

## Interpretation

The vehicle detector shows a clear compression effect. Compared with original images,
`high_quality_512` reduces mAP@0.5 by about `10.7%`, while `balanced_256` reduces it by
about `13.2%`. The two settings are close in F1: `0.665724` for `high_quality_512` and
`0.664723` for `balanced_256`.

`max_compression_256` causes the largest degradation, with mAP@0.5 dropping by about
`23.7%` and recall dropping by about `20.1%` relative to original images. The main
failure mode is missed vehicles rather than a collapse in precision.

## Files

| File | Description |
|------|-------------|
| `tables/vehicle_detection_conf_0p25_summary.csv` | Final report-ready summary at confidence `0.25`. |
| `tables/vehicle_detection_conf_0p25_per_class.csv` | Final per-class table. This run has only class `0 vehicle`. |
| `tables/vehicle_detection_threshold_sweep_summary.csv` | Confidence sweep from `0.005` to `0.25`. |
| `tables/vehicle_detection_conf_0p001_summary.csv` | Initial low-confidence detector summary. |
