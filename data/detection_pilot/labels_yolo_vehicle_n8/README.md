# Vehicle Detection Pilot Labels, N8

This directory contains draft YOLO-format vehicle labels for the first 8 sorted DJI images from the local `100_0005` image folder.

Scope:
- Class `0 vehicle` covers clearly visible cars, vans, trucks, and RV-like vehicles.
- Pedestrians, bicycles, motorcycles, and very small or ambiguous objects are not labeled.
- Heavily truncated edge objects are usually excluded unless most of the vehicle is visible.

Important status:
- These labels are a pilot input for validating the object-detection-impact pipeline.
- Review and correction are required before using them as publication-grade ground truth for formal mAP claims.
- Raw images are intentionally not committed to GitHub.

Source images:
- Local folder: `/Users/yifn/Desktop/26 SC/OneDrive_1_2026-4-11/100_0005/`
- Image size: `5472 x 3648`
- Annotation reference grid: `1368 x 912`, same aspect ratio as the source images

Files:
- `labels/`: YOLO-format label files
- `pilot_images.txt`: source image filenames
- `data.yaml`: metadata-only review descriptor
- `manifest.json`: image counts, class mapping, and draft status

Use on DeltaAI:

```bash
mkdir -p /projects/bfod/$USER/cdc-deltaai/data/labels_yolo_vehicle_n8
rsync -av data/detection_pilot/labels_yolo_vehicle_n8/labels/   /projects/bfod/$USER/cdc-deltaai/data/labels_yolo_vehicle_n8/
```

Then set:

```bash
DETECTION_GT_DIR=/projects/bfod/$USER/cdc-deltaai/data/labels_yolo_vehicle_n8
```
