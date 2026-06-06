# Vehicle Detection Draft Labels, N50

This directory contains a draft YOLO-format vehicle label package for the first 50 sorted DJI images from the local `100_0005` image folder.

Important status:
- This is an auto-assisted draft, not publication-grade ground truth.
- The first 8 images reuse the existing manual draft labels from `labels_yolo_vehicle_n8`.
- Images 9-50 use COCO-pretrained YOLOv8x `car`, `bus`, and `truck` candidates mapped to class `0 vehicle`.
- Review and correction are required before formal mAP reporting.

Scope:
- Class `0 vehicle` covers clearly visible cars, vans, trucks, and RV-like vehicles.
- Pedestrians, bicycles, motorcycles, and very small or ambiguous objects are outside the current label policy.

Source images:
- Local folder: `/Users/yifn/Desktop/26 SC/OneDrive_1_2026-4-11/100_0005/`
- Image size: `5472 x 3648`
- Image subset: `100_0005_0001.JPG` through `100_0005_0050.JPG`

Draft-generation settings for images 9-50:

```text
detector: Ultralytics YOLOv8x COCO pretrained
classes: 2 car, 5 bus, 7 truck
class map: 2=0, 5=0, 7=0
confidence threshold: 0.4
imgsz: 1280
```

Threshold note: an N8 threshold sweep against the existing manual draft labels selected `0.40` because it reduced over-prediction and gave the best F1 among the tested thresholds.

Files:
- `labels/`: YOLO-format label files
- `pilot_images.txt`: source image filenames
- `data.yaml`: metadata-only review descriptor
- `manifest.json`: image counts, class mapping, and draft status
- `threshold_sweep_n8.csv`: N8 calibration sweep used to select the auto-label confidence threshold

Use on DeltaAI:

```bash
mkdir -p /projects/bfod/$USER/cdc-deltaai/data/labels_yolo_vehicle_n50_draft
rsync -av data/detection_pilot/labels_yolo_vehicle_n50_draft/labels/ \
  /projects/bfod/$USER/cdc-deltaai/data/labels_yolo_vehicle_n50_draft/
```

Then set:

```bash
DETECTION_GT_DIR=/projects/bfod/$USER/cdc-deltaai/data/labels_yolo_vehicle_n50_draft
```
