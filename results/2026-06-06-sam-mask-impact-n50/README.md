# SAM Zero-Shot Mask-Stability Pilot, N50, 2026-06-06

This package records the N50 downstream zero-shot segmentation pilot for Experiment 4.

Purpose:

- Run Meta Segment Anything (SAM) on original and reconstructed image sets.
- Use the same YOLO vehicle boxes as fixed SAM prompts.
- Compare each reconstructed-image mask with the original-image baseline mask for the same image and prompt.

This is a promptable segmentation-stability result, not a class-aware detection-accuracy result. It complements the COCO YOLOv8x detector pilot.

## DeltaAI Job

| Item | Value |
|------|-------|
| Job ID | `2426827` |
| Run stamp | `20260606_sam_vehicle_n50` |
| State | `COMPLETED` |
| Elapsed | `00:12:18` |
| System | DeltaAI GH200 |
| SAM model | Meta SAM ViT-H |
| SAM checkpoint | `/projects/bfod/yyang48/cdc-deltaai/weights/sam/sam_vit_h_4b8939.pth` |
| Prompt labels | `/projects/bfod/yyang48/cdc-deltaai/data/labels_yolo_vehicle_n50_draft` |
| Image set root | `/projects/bfod/yyang48/cdc-deltaai/output/detection_image_sets/20260606_vehicle_n50_tradeoff` |
| Output root | `/projects/bfod/yyang48/cdc-deltaai/output/sc26_compression/20260606_sam_vehicle_n50/09_sam_mask_impact` |

## Inputs

The evaluation used `50` images and `829` draft vehicle-box prompts. The labels are not publication-grade ground truth yet. The first `8` images use manual draft labels; images `9-50` use auto-assisted COCO YOLOv8x vehicle candidates at confidence `0.40`.

Image sets:

| Configuration | Image source |
|---------------|--------------|
| `original` | Original DJI images subset and mask baseline |
| `balanced_256` | `balanced_checkpoint_b00064`, `256 x 256` tiled reconstruction |
| `balanced_512` | `balanced_checkpoint_b00064`, `512 x 512` tiled reconstruction |
| `max_compression_256` | `high_compression_checkpoint_b00128`, `256 x 256` tiled reconstruction |

## Result

| Configuration | Mean mask IoU | Mean Dice | Mean area ratio | Mean abs. area change | Mean centroid shift | Failed prompt rate |
|---------------|---------------|-----------|-----------------|-----------------------|---------------------|--------------------|
| `original` | `1.000000` | `1.000000` | `1.000000` | `0.000000` | `0.000000 px` | `0.000000` |
| `balanced_256` | `0.705602` | `0.811042` | `1.019321` | `0.075364` | `16.763959 px` | `0.000000` |
| `balanced_512` | `0.706134` | `0.811647` | `1.013330` | `0.069779` | `16.809197 px` | `0.000000` |
| `max_compression_256` | `0.704829` | `0.810710` | `1.022910` | `0.078523` | `16.672371 px` | `0.000000` |

## Interpretation

The SAM zero-shot workflow runs end to end on the full N50 prompt set. All prompts returned usable masks, with `failed_prompt_rate = 0.0` for every configuration.

The three reconstructed configurations are very close on mask stability. `balanced_512` is slightly highest on mean mask IoU and Dice and has the smallest mean absolute area change, while `balanced_256` is nearly tied. `max_compression_256` remains close on IoU and Dice but shows the largest area-ratio drift.

Use this as a zero-shot segmentation sensitivity result: compression and reconstruction change mask boundaries and areas, but the promptable segmentation pipeline does not fail. The result supports the broader downstream-impact story alongside the N50 COCO vehicle detection pilot.
