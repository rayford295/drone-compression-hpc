# SC26 SAM Zero-Shot Segmentation Impact Plan, 2026-06-06

This page records a complementary downstream experiment idea for the compression and reconstruction study: use Meta Segment Anything (SAM) to compare zero-shot segmentation behavior on original and reconstructed drone images.

## Motivation

The current Experiment 4 measures object-detection impact:

```text
Original image -> compression -> reconstruction -> fixed detector -> mAP / precision / recall / F1
```

SAM can add a second downstream signal:

```text
Original image -> compression -> reconstruction -> same SAM prompts -> mask stability metrics
```

This is useful because SAM does not need task-specific training. It supports a zero-shot computer-vision claim, while the detector route still measures class-aware object-detection performance.

## Important Boundary

SAM is a segmentation model, not a class-aware object detector. It should not replace the YOLO-style mAP experiment.

Use SAM as a complementary mask-stability experiment:

- Detection route: asks whether vehicle detections change after reconstruction.
- SAM route: asks whether zero-shot object masks from the same prompts change after reconstruction.

For a clean comparison, use fixed prompts rather than fully automatic masks. Automatic mask generation can produce a different number of masks per image, which makes matching original and reconstructed outputs harder.

## Recommended Inputs

Use the same N50 image set as the formal compression x tile-size tradeoff.

Required:

- Original images: `100_0005_0001.JPG` through `100_0005_0050.JPG`
- Reconstructed images for selected configurations
- Prompt boxes from `data/detection_pilot/labels_yolo_vehicle_n50_draft/labels/`
- A SAM-family checkpoint stored outside git on DeltaAI

Recommended configurations:

| Configuration | Purpose |
|---------------|---------|
| `original` | Zero-shot mask baseline |
| `balanced_256` | Current speed and memory candidate |
| `balanced_512` | Quality-safe backup |
| `max_compression_256` | Stress test for downstream degradation |

## Proposed Method

1. Prepare matched image folders for original and reconstructed images.
2. Convert YOLO prompt boxes from normalized `x_center y_center width height` into pixel `x1 y1 x2 y2` boxes.
3. Run SAM with the same prompt boxes on each configuration.
4. For each object prompt, compare the reconstructed-image mask with the original-image mask.
5. Aggregate per-object metrics into per-configuration summaries.

Suggested metrics:

| Metric | Meaning |
|--------|---------|
| `mean_mask_iou` | Intersection-over-union between original and reconstructed SAM masks |
| `mean_dice` | Dice similarity between original and reconstructed SAM masks |
| `mean_area_ratio` | Reconstructed mask area divided by original mask area |
| `mean_abs_area_change` | Absolute fractional area change |
| `mean_centroid_shift_px` | Pixel distance between mask centroids |
| `boundary_f1` | Boundary stability, if boundary extraction is added |
| `failed_prompt_rate` | Fraction of prompts that fail to return a usable mask |

## DeltaAI Workflow

Code added:

```text
experiments/compression/evaluate_sam_mask_impact.py
experiments/compression/slurm/09_sam_mask_impact.sbatch
```

Stage a SAM checkpoint outside git, for example:

```bash
mkdir -p /projects/bfod/yyang48/cdc-deltaai/weights/sam
# Place Meta SAM ViT-H at:
# /projects/bfod/yyang48/cdc-deltaai/weights/sam/sam_vit_h_4b8939.pth
```

Smoke test first:

```bash
RUN_STAMP=20260606_sam_vehicle_n50_smoke \
SAM_INSTALL_SEGMENT_ANYTHING=1 \
SAM_CHECKPOINT=/projects/bfod/yyang48/cdc-deltaai/weights/sam/sam_vit_h_4b8939.pth \
SAM_MODEL_TYPE=vit_h \
SAM_PROMPT_LABEL_DIR=/projects/bfod/yyang48/cdc-deltaai/data/labels_yolo_vehicle_n50_draft \
SAM_IMAGE_SETS="original=/projects/bfod/yyang48/cdc-deltaai/output/detection_image_sets/20260606_vehicle_n50_tradeoff/original balanced_256=/projects/bfod/yyang48/cdc-deltaai/output/detection_image_sets/20260606_vehicle_n50_tradeoff/balanced_256 balanced_512=/projects/bfod/yyang48/cdc-deltaai/output/detection_image_sets/20260606_vehicle_n50_tradeoff/balanced_512 max_compression_256=/projects/bfod/yyang48/cdc-deltaai/output/detection_image_sets/20260606_vehicle_n50_tradeoff/max_compression_256" \
SAM_PROMPT_BATCH_SIZE=4 \
SAM_LIMIT_IMAGES=2 \
sbatch --export=ALL,REPO_DIR=/projects/bfod/yyang48/cdc-deltaai/code_main_641d86c \
  experiments/compression/slurm/09_sam_mask_impact.sbatch
```

Then remove `SAM_LIMIT_IMAGES=2` for the full N50 run:

```bash
RUN_STAMP=20260606_sam_vehicle_n50 \
SAM_INSTALL_SEGMENT_ANYTHING=0 \
SAM_CHECKPOINT=/projects/bfod/yyang48/cdc-deltaai/weights/sam/sam_vit_h_4b8939.pth \
SAM_MODEL_TYPE=vit_h \
SAM_PROMPT_LABEL_DIR=/projects/bfod/yyang48/cdc-deltaai/data/labels_yolo_vehicle_n50_draft \
SAM_IMAGE_SETS="original=/projects/bfod/yyang48/cdc-deltaai/output/detection_image_sets/20260606_vehicle_n50_tradeoff/original balanced_256=/projects/bfod/yyang48/cdc-deltaai/output/detection_image_sets/20260606_vehicle_n50_tradeoff/balanced_256 balanced_512=/projects/bfod/yyang48/cdc-deltaai/output/detection_image_sets/20260606_vehicle_n50_tradeoff/balanced_512 max_compression_256=/projects/bfod/yyang48/cdc-deltaai/output/detection_image_sets/20260606_vehicle_n50_tradeoff/max_compression_256" \
SAM_PROMPT_BATCH_SIZE=4 \
sbatch --mem=96G --time=08:00:00 --export=ALL,REPO_DIR=/projects/bfod/yyang48/cdc-deltaai/code_main_641d86c \
  experiments/compression/slurm/09_sam_mask_impact.sbatch
```

Use the exact checkpoint name and model type in the output manifest. Do not commit SAM checkpoints, raw images, full-resolution masks, or large visual folders.

## GitHub-Safe Output Package

After a SAM job succeeds, commit only lightweight summaries:

```text
results/YYYY-MM-DD-sam-mask-impact/
├── README.md
└── tables/
    ├── sam_mask_summary.csv
    ├── sam_mask_per_image.csv
    ├── sam_mask_per_prompt.csv
    └── manifest.json
```

Optional small QA figures can be included only if they are downsampled and useful for the paper or poster.

## Paper Wording

Use careful wording:

> We additionally evaluate zero-shot segmentation stability with Meta SAM using fixed object-box prompts. This experiment measures whether compression and reconstruction change the masks produced by a promptable foundation model, complementing the detector-based mAP analysis.

Do not claim SAM measures detection accuracy unless a separate class-aware detector or text-grounded detection stage is added.
