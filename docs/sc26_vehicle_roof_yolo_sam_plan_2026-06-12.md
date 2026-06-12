# SC26 Plan — Vehicle and Roof Analysis with YOLO and SAM

Date: 2026-06-12
Status: Next runnable plan after the YOLO-World prompt gate
Owner: Yifan

## Decision

We will analyze both **vehicle** and **roof** effects, but we will not use YOLO-World as
the final detector. The prompt gate showed that YOLO-World detects vehicles well but fails
on top-down building/roof labels. The next plan uses two complementary methods:

1. **YOLO detection metrics** for class-aware object detection.
2. **SAM mask-stability metrics** for promptable segmentation boundary stability.

For wording, use **roof** rather than building when discussing the human building labels,
because the drone-view annotations mostly correspond to visible roof/roof-footprint regions.

## Data Split

Human-labeled source on DeltaAI:

```text
/projects/bfod/$USER/cdc-deltaai/data/VehicleAndBuilding_labels/
```

Class mapping:

| Class ID | Name |
|----------|------|
| `0` | vehicle |
| `1` | roof |

Split:

| Split | Image IDs | Use |
|-------|-----------|-----|
| test | `100_0005_0001` to `100_0005_0050` | Fixed compression-impact evaluation |
| train | `100_0005_0051` to `100_0005_0090` | Supervised YOLO training |
| val | `100_0005_0091` to `100_0005_0100` | Supervised YOLO validation |

## Track A — Vehicle YOLO Now

For vehicle-only detection, the COCO YOLOv8x detector is already viable because COCO has
vehicle classes. Use the human vehicle labels, not the earlier draft labels.

Build vehicle-only GT:

```bash
GT_ROOT=/projects/bfod/$USER/cdc-deltaai/data/gt_human_n50
VEHICLE_LABEL_DIR=/projects/bfod/$USER/cdc-deltaai/data/VehicleAndBuilding_labels/vehicle/labels
BUILDING_LABEL_DIR=/projects/bfod/$USER/cdc-deltaai/data/VehicleAndBuilding_labels/building/labels

python experiments/compression/build_detection_gt_vehicle_building.py \
  --vehicle_dir ${VEHICLE_LABEL_DIR} \
  --building_dir ${BUILDING_LABEL_DIR} \
  --classes vehicle \
  --max_images 50 \
  --output_dir ${GT_ROOT}/vehicle
```

Prepare matched image sets:

```bash
ORIG_SRC=/projects/bfod/$USER/cdc-deltaai/data/VehicleAndBuilding_labels/vehicle/images
RECON_ROOT=/projects/bfod/$USER/cdc-deltaai/output/detection_image_sets/20260606_vehicle_n50_tradeoff
IMGSET_ROOT=/projects/bfod/$USER/cdc-deltaai/output/detection_image_sets/20260612_vehicle_human_n50

python experiments/compression/prepare_detection_image_sets.py \
  --ground_truth_dir ${GT_ROOT}/vehicle \
  --image_sets \
    original=${ORIG_SRC} \
    high_quality_512=${RECON_ROOT}/high_quality_512 \
    balanced_256=${RECON_ROOT}/balanced_256 \
    max_compression_256=${RECON_ROOT}/max_compression_256 \
  --output_dir ${IMGSET_ROOT} \
  --overwrite
```

Run vehicle detection:

```bash
RUN_STAMP=20260612_detection_yolo_vehicle_human_n50 \
DETECTION_INSTALL_ULTRALYTICS=1 \
DETECTION_GT_DIR=${GT_ROOT}/vehicle \
DETECTION_MODEL=yolov8x.pt \
DETECTION_IMAGE_SETS="original=${IMGSET_ROOT}/original high_quality_512=${IMGSET_ROOT}/high_quality_512 balanced_256=${IMGSET_ROOT}/balanced_256 max_compression_256=${IMGSET_ROOT}/max_compression_256" \
DETECTION_CLASSES="2 5 7" \
DETECTION_CLASS_MAP="2=0 5=0 7=0" \
DETECTION_DROP_UNMAPPED=1 \
DETECTION_RESTRICT_TO_GT=1 \
DETECTION_IMGSZ=1280 \
DETECTION_CONF=0.001 \
sbatch --export=ALL,REPO_DIR=$PWD \
  experiments/compression/slurm/08_object_detection_impact.sbatch
```

This gives the vehicle table:

| Configuration | mAP@0.5 | mAP@0.5:0.95 | Precision | Recall | F1 | GT | Predictions |
|---------------|--------:|-------------:|----------:|-------:|---:|---:|------------:|

## Track B — Vehicle + Roof Supervised YOLO

For roof detection, train a project-specific two-class YOLO detector.

Prepare the dataset and run a smoke training job:

```bash
RUN_STAMP=20260612_train_yolo_vehicle_roof_s_smoke \
YOLO_SOURCE_ROOT=/projects/bfod/$USER/cdc-deltaai/data/VehicleAndBuilding_labels \
YOLO_DATASET_DIR=/projects/bfod/$USER/cdc-deltaai/data/yolo_vehicle_roof_20260612 \
YOLO_MODEL=yolov8s.pt \
YOLO_EPOCHS=50 \
YOLO_IMGSZ=1280 \
YOLO_BATCH=4 \
YOLO_RUN_NAME=vehicle_roof_yolov8s_e50 \
sbatch --export=ALL,REPO_DIR=$PWD \
  experiments/compression/slurm/11_train_yolo_vehicle_roof.sbatch
```

If the smoke run trains cleanly, repeat with a larger model or more epochs:

```bash
RUN_STAMP=20260612_train_yolo_vehicle_roof_x \
YOLO_PREPARE_DATASET=0 \
YOLO_DATASET_DIR=/projects/bfod/$USER/cdc-deltaai/data/yolo_vehicle_roof_20260612 \
YOLO_MODEL=yolov8x.pt \
YOLO_EPOCHS=150 \
YOLO_IMGSZ=1280 \
YOLO_BATCH=2 \
YOLO_RUN_NAME=vehicle_roof_yolov8x_e150 \
sbatch --export=ALL,REPO_DIR=$PWD \
  experiments/compression/slurm/11_train_yolo_vehicle_roof.sbatch
```

Use the trained `best.pt` as `DETECTION_MODEL` in `08_object_detection_impact.sbatch`
with a merged vehicle+roof N50 GT folder.

## Track C — SAM for Vehicle and Roof

SAM does not produce class-aware detection metrics. It uses the human boxes as prompts
and compares masks across original and reconstructed image sets. Run it separately for
vehicle and roof so the tables are interpretable.

Full N50 runs completed on 2026-06-12. The lightweight result package is
`results/2026-06-12-sam-vehicle-roof-human-n50/`.

Summary:

| Prompt class | Configuration | Prompts | Mean mask IoU | Mean Dice | Abs. area change | Failed prompt rate |
|--------------|---------------|--------:|--------------:|----------:|-----------------:|-------------------:|
| vehicle | high_quality_512 | 1013 | 0.735026 | 0.838327 | 0.041569 | 0.000000 |
| vehicle | balanced_256 | 1013 | 0.734634 | 0.838039 | 0.039600 | 0.000000 |
| vehicle | max_compression_256 | 1013 | 0.733121 | 0.837160 | 0.043506 | 0.000000 |
| roof | high_quality_512 | 1201 | 0.900123 | 0.945443 | 0.025937 | 0.000000 |
| roof | balanced_256 | 1201 | 0.898891 | 0.944659 | 0.027758 | 0.000000 |
| roof | max_compression_256 | 1201 | 0.895618 | 0.942522 | 0.029802 | 0.000000 |

Interpretation: all prompts returned usable masks. Roof masks are more stable than
vehicle masks under reconstruction, which is consistent with roofs being larger objects.
Balanced 256 remains close to high quality 512 for both prompt classes.

Build merged prompt labels:

```bash
GT_ROOT=/projects/bfod/$USER/cdc-deltaai/data/gt_human_n50
VEHICLE_LABEL_DIR=/projects/bfod/$USER/cdc-deltaai/data/VehicleAndBuilding_labels/vehicle/labels
BUILDING_LABEL_DIR=/projects/bfod/$USER/cdc-deltaai/data/VehicleAndBuilding_labels/building/labels

python experiments/compression/build_detection_gt_vehicle_building.py \
  --vehicle_dir ${VEHICLE_LABEL_DIR} \
  --building_dir ${BUILDING_LABEL_DIR} \
  --max_images 50 \
  --output_dir ${GT_ROOT}/vehicle_roof
```

Vehicle SAM:

```bash
RUN_STAMP=20260612_sam_vehicle_human_n50 \
SAM_INSTALL_SEGMENT_ANYTHING=1 \
SAM_CHECKPOINT=/projects/bfod/$USER/cdc-deltaai/weights/sam/sam_vit_h_4b8939.pth \
SAM_MODEL_TYPE=vit_h \
SAM_PROMPT_LABEL_DIR=${GT_ROOT}/vehicle_roof \
SAM_PROMPT_CLASSES="0" \
SAM_IMAGE_SETS="original=${IMGSET_ROOT}/original high_quality_512=${IMGSET_ROOT}/high_quality_512 balanced_256=${IMGSET_ROOT}/balanced_256 max_compression_256=${IMGSET_ROOT}/max_compression_256" \
SAM_PROMPT_BATCH_SIZE=4 \
sbatch --export=ALL,REPO_DIR=$PWD \
  experiments/compression/slurm/09_sam_mask_impact.sbatch
```

Roof SAM:

```bash
RUN_STAMP=20260612_sam_roof_human_n50 \
SAM_INSTALL_SEGMENT_ANYTHING=1 \
SAM_CHECKPOINT=/projects/bfod/$USER/cdc-deltaai/weights/sam/sam_vit_h_4b8939.pth \
SAM_MODEL_TYPE=vit_h \
SAM_PROMPT_LABEL_DIR=${GT_ROOT}/vehicle_roof \
SAM_PROMPT_CLASSES="1" \
SAM_IMAGE_SETS="original=${IMGSET_ROOT}/original high_quality_512=${IMGSET_ROOT}/high_quality_512 balanced_256=${IMGSET_ROOT}/balanced_256 max_compression_256=${IMGSET_ROOT}/max_compression_256" \
SAM_PROMPT_BATCH_SIZE=4 \
sbatch --export=ALL,REPO_DIR=$PWD \
  experiments/compression/slurm/09_sam_mask_impact.sbatch
```

Report SAM with:

| Configuration | Prompts | Mean mask IoU | Mean Dice | Area ratio | Abs. area change | Centroid shift | Failed prompt rate |
|---------------|--------:|--------------:|----------:|-----------:|-----------------:|---------------:|-------------------:|

## Optional DINO Use

DINO or GroundingDINO can still be useful for roof as a diagnostic open-vocabulary
baseline, but it should not replace the supervised YOLO path unless it passes the same
original-image N50 gate with acceptable roof AP and recall.
