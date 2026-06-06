# COCO Vehicle Detection Pilot, N8, 2026-06-06

This package records the first downstream object-detection pilot for Experiment 4.

Purpose:

- Run a fixed detector on original and reconstructed image sets.
- Compare detector predictions against the N8 draft YOLO vehicle labels.
- Validate the end-to-end object-detection impact workflow before formal labels or a project-specific detector are available.

This is a pilot result, not a publication-grade detection result. The detector is a COCO-pretrained Ultralytics YOLOv8x model. Predictions for COCO classes `2` car, `5` bus, and `7` truck were mapped to the pilot class `0 vehicle`.

## DeltaAI Job

| Item | Value |
|------|-------|
| Job ID | `2425670` |
| Run stamp | `20260606_detection_coco_vehicle_n8` |
| System | DeltaAI GH200 |
| Detector | `yolov8x.pt` |
| Detector source | COCO-pretrained Ultralytics YOLOv8x |
| Ground truth | `/projects/bfod/yyang48/cdc-deltaai/data/labels_yolo_vehicle_n8` |
| Image set root | `/projects/bfod/yyang48/cdc-deltaai/output/detection_image_sets/20260606_vehicle_n8_tradeoff` |
| Output root | `/projects/bfod/yyang48/cdc-deltaai/output/sc26_compression/20260606_detection_coco_vehicle_n8/08_object_detection_impact` |

## Inputs

The evaluation used `8` pilot-labeled images and `234` draft ground-truth vehicle boxes.

Image sets:

| Configuration | Image source |
|---------------|--------------|
| `original` | Original DJI images subset |
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

| configuration | mAP@0.5 | mAP@0.5:0.95 | Precision@0.5 | Recall@0.5 | F1@0.5 | GT boxes | Prediction boxes |
|---------------|---------|--------------|----------------|------------|--------|----------|------------------|
| `original` | `0.193320` | `0.045668` | `0.069799` | `0.444444` | `0.120650` | `234` | `1490` |
| `balanced_256` | `0.214162` | `0.051601` | `0.074948` | `0.461538` | `0.128955` | `234` | `1441` |
| `balanced_512` | `0.212877` | `0.052333` | `0.070903` | `0.452991` | `0.122614` | `234` | `1495` |
| `max_compression_256` | `0.159048` | `0.038141` | `0.069286` | `0.414530` | `0.118727` | `234` | `1400` |

## Interpretation

The pipeline now runs end to end on original and reconstructed image sets. In this pilot, the balanced reconstructions are close to or slightly above the original baseline, while the maximum-compression row is lower on mAP and recall.

The detector produces far more prediction boxes than the draft ground truth contains, so precision is low across all rows. Treat this as evidence that the downstream-evaluation machinery works and as a rough vehicle-detection sensitivity check. For formal paper claims, use reviewed labels and preferably a project-specific detector.
