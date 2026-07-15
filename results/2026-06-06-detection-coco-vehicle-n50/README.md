# COCO Vehicle Detection Pilot, N50, 2026-06-06

This package records the N50 downstream object-detection pilot for Experiment 4.

Purpose:

- Run a fixed detector on original and reconstructed image sets.
- Compare detector predictions against the N50 draft YOLO vehicle labels.
- Test whether the selected compression and reconstruction settings preserve downstream vehicle-detection behavior.

This is a pilot result, not a publication-grade detection result. The detector is a COCO-pretrained Ultralytics YOLOv8x model. Predictions for COCO classes `2` car, `5` bus, and `7` truck were mapped to the pilot class `0 vehicle`.

The ground-truth labels are also draft. The first `8` images use manual draft labels; images `9-50` use auto-assisted COCO YOLOv8x vehicle candidates at confidence `0.40`. Review and correction are required before formal mAP reporting.

## DeltaAI Jobs

Reconstructed image preparation:

| Item | Value |
|------|-------|
| Job ID | `2425687` |
| Run stamp | `20260606_tradeoff_n50_visuals_for_detection` |
| Purpose | Save 50 reconstructed images for each tiled configuration |
| Result | `6` summary rows, with `50` saved reconstructed images per `visuals/` directory |
| Output root | `/projects/bfod/USERNAME/cdc-deltaai/output/sc26_compression/20260606_tradeoff_n50_visuals_for_detection/07_compression_tile_tradeoff` |

Detection evaluation:

| Item | Value |
|------|-------|
| Job ID | `2426722` |
| Run stamp | `20260606_detection_coco_vehicle_n50_retry1` |
| State | `COMPLETED` |
| Elapsed | `00:02:17` |
| Batch MaxRSS | `10494336K` |
| System | DeltaAI GH200 |
| Detector | `yolov8x.pt` |
| Detector source | COCO-pretrained Ultralytics YOLOv8x |
| Ground truth | `/projects/bfod/USERNAME/cdc-deltaai/data/labels_yolo_vehicle_n50_draft` |
| Image set root | `/projects/bfod/USERNAME/cdc-deltaai/output/detection_image_sets/20260606_vehicle_n50_tradeoff` |
| Output root | `/projects/bfod/USERNAME/cdc-deltaai/output/sc26_compression/20260606_detection_coco_vehicle_n50_retry1/08_object_detection_impact` |

## Inputs

The evaluation used `50` pilot-labeled images and `829` draft ground-truth vehicle boxes.

Image sets:

| Configuration | Image source |
|---------------|--------------|
| `original` | Original DJI images subset |
| `high_quality_512` | `high_quality_checkpoint_b00512`, `512 x 512` tiled reconstruction |
| `balanced_256` | `balanced_checkpoint_b00064`, `256 x 256` tiled reconstruction |
| `balanced_512` | `balanced_checkpoint_b00064`, `512 x 512` tiled reconstruction |
| `max_compression_256` | `high_compression_checkpoint_b00128`, `256 x 256` tiled reconstruction |

Detector settings:

```text
DETECTION_CLASSES="2 5 7"
DETECTION_CLASS_MAP="2=0 5=0 7=0"
DETECTION_DROP_UNMAPPED=1
DETECTION_RESTRICT_TO_GT=1
DETECTION_IMGSZ=1280
DETECTION_CONF=0.001
```

## Result

| Configuration | mAP@0.5 | mAP@0.5:0.95 | Precision@0.5 | Recall@0.5 | F1@0.5 | GT boxes | Prediction boxes |
|---------------|---------|--------------|----------------|------------|--------|----------|------------------|
| `original` | `0.690179` | `0.571109` | `0.063534` | `0.843185` | `0.118164` | `829` | `11002` |
| `high_quality_512` | `0.632874` | `0.270631` | `0.062465` | `0.809409` | `0.115980` | `829` | `10742` |
| `balanced_256` | `0.627999` | `0.271220` | `0.060070` | `0.806996` | `0.111817` | `829` | `11137` |
| `balanced_512` | `0.622452` | `0.270333` | `0.059151` | `0.806996` | `0.110223` | `829` | `11310` |
| `max_compression_256` | `0.588941` | `0.260333` | `0.056838` | `0.772014` | `0.105881` | `829` | `11260` |

## Interpretation

The N50 detection-impact workflow now runs end to end. The original baseline reaches mAP@0.5 `0.690179` and recall `0.843185` against the draft N50 labels.

The reconstructed image sets show a graded downstream drop. `balanced_256` has mAP@0.5 `0.627999`, about `0.062` below the original baseline, while `max_compression_256` falls farther to `0.588941`. This supports using the balanced checkpoint as the main deployment candidate and keeping maximum compression as a stress-test setting.

Precision is low across all rows because `DETECTION_CONF=0.001` intentionally keeps many low-confidence detector predictions. This helps compute recall and AP curves, but it inflates the raw prediction count. Use this result as a workflow-complete sensitivity check. For formal paper claims, review the N50 labels and preferably run a project-specific detector.
