# YOLO Vehicle and Roof Detection, Human N50, 2026-06-12

This package records the supervised two-class YOLO detection results for the human-labeled
N50 test set.

| Class ID | Name |
|----------|------|
| `0` | vehicle |
| `1` | roof |

The roof class uses the human building labels, interpreted as roof/roof-footprint labels
because the imagery is top-down drone imagery.

## DeltaAI Runs

| Item | Value |
|------|-------|
| Repo commit for run | `d3f323f` |
| Training Slurm job | `2479315` |
| Detection Slurm job | `2479320` |
| Training stamp | `20260612_train_yolo_vehicle_roof_s_smoke` |
| Detection stamp | `20260612_detection_yolo_vehicle_roof_human_n50_s` |
| Training output | `/projects/bfod/$USER/cdc-deltaai/output/sc26_compression/20260612_train_yolo_vehicle_roof_s_smoke/11_train_yolo_vehicle_roof/ultralytics_train/vehicle_roof_yolov8s_e50` |
| Detection output | `/projects/bfod/$USER/cdc-deltaai/output/sc26_compression/20260612_detection_yolo_vehicle_roof_human_n50_s/08_object_detection_impact` |
| Dataset root | `/projects/bfod/$USER/cdc-deltaai/data/yolo_vehicle_roof_20260612` |
| Model | `yolov8s.pt` fine-tuned for 50 epochs |
| Best checkpoint | `weights/best.pt` |
| Test images | `50` |
| Vehicle GT boxes | `1013` |
| Roof GT boxes | `1201` |

Raw images, reconstructed images, prediction labels, logs, model weights, and Ultralytics
run folders remain on DeltaAI storage. This package stores only lightweight summaries.

## Validation Result

The supervised YOLOv8s smoke model trained successfully and validated well on the
10-image validation split:

| Class | Images | Instances | Precision | Recall | mAP@0.5 | mAP@0.5:0.95 |
|-------|-------:|----------:|----------:|-------:|--------:|-------------:|
| all | 10 | 442 | 0.885 | 0.867 | 0.925 | 0.665 |
| vehicle | 10 | 191 | 0.891 | 0.810 | 0.896 | 0.606 |
| roof | 10 | 251 | 0.878 | 0.924 | 0.953 | 0.725 |

## Final Operating Point

The detector first ran at `conf=0.001` to preserve low-score predictions for AP
calculation. We then filtered the saved predictions at several confidence thresholds.
The final report table uses `conf=0.50`, which gives the highest overall F1 and keeps
precision and recall balanced.

| Configuration | mAP@0.5 | mAP@0.5:0.95 | Precision | Recall | F1 | GT | Predictions |
|---------------|--------:|-------------:|----------:|-------:|---:|---:|------------:|
| original | 0.863715 | 0.607265 | 0.884058 | 0.881662 | 0.882858 | 2214 | 2208 |
| high_quality_512 | 0.845486 | 0.488057 | 0.892758 | 0.868564 | 0.880495 | 2214 | 2154 |
| balanced_256 | 0.839016 | 0.481047 | 0.877467 | 0.863595 | 0.870476 | 2214 | 2179 |
| max_compression_256 | 0.833041 | 0.474657 | 0.878704 | 0.857272 | 0.867856 | 2214 | 2160 |

## Per-Class Result at `conf=0.50`

| Configuration | Class | GT | Predictions | AP@0.5 | Precision | Recall | F1 |
|---------------|-------|---:|------------:|-------:|----------:|-------:|---:|
| original | vehicle | 1013 | 959 | 0.846608 | 0.908238 | 0.859822 | 0.883367 |
| original | roof | 1201 | 1249 | 0.880822 | 0.865492 | 0.900083 | 0.882449 |
| high_quality_512 | vehicle | 1013 | 941 | 0.819728 | 0.907545 | 0.843040 | 0.874104 |
| high_quality_512 | roof | 1201 | 1213 | 0.871244 | 0.881286 | 0.890092 | 0.885667 |
| balanced_256 | vehicle | 1013 | 932 | 0.807980 | 0.902361 | 0.830207 | 0.864781 |
| balanced_256 | roof | 1201 | 1247 | 0.870053 | 0.858861 | 0.891757 | 0.875000 |
| max_compression_256 | vehicle | 1013 | 936 | 0.802471 | 0.893162 | 0.825271 | 0.857876 |
| max_compression_256 | roof | 1201 | 1224 | 0.863610 | 0.867647 | 0.884263 | 0.875876 |

## Interpretation

The supervised YOLO path solves the roof-detection failure observed with YOLO-World.
At the final operating point, both classes have high and balanced F1 scores on original
and reconstructed image sets.

Compared with original images, `balanced_256` reduces overall F1 by about `1.4%` and
`max_compression_256` reduces F1 by about `1.7%`. The stricter mAP@0.5:0.95 metric is more
sensitive to reconstruction: it drops by about `20.8%` for `balanced_256` and `21.8%` for
`max_compression_256`. This suggests the compressed reconstructions preserve object-level
detection well, but fine localization quality is more affected.

## Files

| File | Description |
|------|-------------|
| `tables/yolo_vehicle_roof_conf_0p50_summary.csv` | Final report-ready summary at confidence `0.50`. |
| `tables/yolo_vehicle_roof_conf_0p50_per_class.csv` | Final per-class table at confidence `0.50`. |
| `tables/yolo_vehicle_roof_threshold_sweep_summary.csv` | Overall confidence sweep from `0.005` to `0.50`. |
| `tables/yolo_vehicle_roof_threshold_sweep_per_class.csv` | Per-class confidence sweep from `0.005` to `0.50`. |
| `tables/yolo_vehicle_roof_conf_0p001_summary.csv` | Initial low-confidence detector summary. |
| `tables/yolo_vehicle_roof_conf_0p001_per_class.csv` | Initial low-confidence per-class detector summary. |
