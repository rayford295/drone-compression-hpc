# SAM Vehicle and Roof Mask Stability, Human N50, 2026-06-12

This package records the full N50 SAM mask-stability results for the human-labeled
vehicle and roof prompts.

Purpose:

- Use the same 50 image IDs across original and CDC-reconstructed image sets.
- Use human-labeled boxes as fixed SAM prompts.
- Measure whether reconstructed images preserve promptable segmentation masks.
- Report vehicle and roof separately so the results are interpretable.

SAM is not a class-aware object detector. These results measure segmentation stability
from fixed box prompts, not detection accuracy and not image classification.

## DeltaAI Runs

| Item | Vehicle | Roof |
|------|---------|------|
| Run stamp | `20260612_sam_vehicle_human_n50` | `20260612_sam_roof_human_n50` |
| Prompt class | `0 vehicle` | `1 roof` |
| Images | `50` | `50` |
| Prompts | `1013` | `1201` |
| SAM model | Meta SAM ViT-H | Meta SAM ViT-H |
| Checkpoint | `/projects/bfod/$USER/cdc-deltaai/weights/sam/sam_vit_h_4b8939.pth` | same |
| Image-set root | `/projects/bfod/$USER/cdc-deltaai/output/detection_image_sets/20260612_vehicle_roof_human_n50` | same |

Raw images, reconstructed images, masks, logs, and checkpoints remain on DeltaAI
storage. This package stores only lightweight summaries.

## Vehicle Result

| Configuration | Images | Prompts | Mean mask IoU | Mean Dice | Area ratio | Abs. area change | Centroid shift | Failed prompt rate |
|---------------|-------:|--------:|--------------:|----------:|-----------:|-----------------:|---------------:|-------------------:|
| Original | 50 | 1013 | 1.000000 | 1.000000 | 1.000000 | 0.000000 | 0.000000 | 0.000000 |
| High quality 512 | 50 | 1013 | 0.735026 | 0.838327 | 1.006251 | 0.041569 | 16.252926 | 0.000000 |
| Balanced 256 | 50 | 1013 | 0.734634 | 0.838039 | 1.003210 | 0.039600 | 16.301191 | 0.000000 |
| Max compression 256 | 50 | 1013 | 0.733121 | 0.837160 | 1.004961 | 0.043506 | 16.389820 | 0.000000 |

## Roof Result

| Configuration | Images | Prompts | Mean mask IoU | Mean Dice | Area ratio | Abs. area change | Centroid shift | Failed prompt rate |
|---------------|-------:|--------:|--------------:|----------:|-----------:|-----------------:|---------------:|-------------------:|
| Original | 50 | 1201 | 1.000000 | 1.000000 | 1.000000 | 0.000000 | 0.000000 | 0.000000 |
| High quality 512 | 50 | 1201 | 0.900123 | 0.945443 | 1.002042 | 0.025937 | 15.960561 | 0.000000 |
| Balanced 256 | 50 | 1201 | 0.898891 | 0.944659 | 1.002866 | 0.027758 | 16.096677 | 0.000000 |
| Max compression 256 | 50 | 1201 | 0.895618 | 0.942522 | 1.002660 | 0.029802 | 16.634331 | 0.000000 |

## Interpretation

All vehicle and roof prompts returned usable masks, with failed prompt rate `0.0` across
all configurations.

Roof masks are more stable than vehicle masks. This is expected because roof objects are
larger and less sensitive to small boundary shifts than vehicles. For roof prompts, the
balanced 256 reconstruction preserves high mask agreement with mean IoU `0.898891` and
mean Dice `0.944659`. Vehicle prompts are more sensitive, but the three reconstructed
settings remain close to each other, with balanced 256 nearly matching high quality 512.

The result supports two cautious claims:

- CDC reconstructions do not cause SAM prompt failure for either vehicle or roof prompts.
- Roof segmentation masks remain more stable than vehicle masks under reconstruction.

Do not describe this as object-detection accuracy. The class-aware detection table still
comes from YOLO-style detectors.

## Files

| File | Description |
|------|-------------|
| `tables/sam_vehicle_summary.csv` | Vehicle SAM summary table. |
| `tables/sam_roof_summary.csv` | Roof SAM summary table. |
| `tables/sam_vehicle_summary.md` | Vehicle Markdown summary copied from DeltaAI. |
| `tables/sam_roof_summary.md` | Roof Markdown summary copied from DeltaAI. |
