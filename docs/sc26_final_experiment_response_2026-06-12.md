# SC26 CDC Final Experiment Response, 2026-06-12

This note consolidates the final June 2 experiment-response state after the human-label
vehicle and roof runs. It is the GitHub-side companion to the local Word deliverables:

- `/Users/yifn/Desktop/26 SC/SC26_CDC_June2_Experiment_Setup_Response.docx`
- `/Users/yifn/Desktop/26 SC/SC26_CDC_June2_Experiment_Setup_Response_EN.docx`
- `/Users/yifn/Desktop/26 SC/SC26_CDC_June2_Experiment_Setup_Response_ZH.docx`

## Final Answer

The requested experiment-response scope is complete. The repository now contains
GitHub-safe result packages for compression and reconstruction tradeoffs, YOLO-World
prompt gating, vehicle-only detection, supervised vehicle+roof detection, and SAM
vehicle/roof mask stability.

The recommended operating setting remains:

- Primary: `balanced_checkpoint_b00064` with `256 x 256` tiling.
- Quality backup: `balanced_checkpoint_b00064` with `512 x 512` tiling.
- Stress test: `checkpoint_b00128` with `256 x 256` tiling.

The final downstream model choice is:

- Use supervised `YOLOv8s` for class-aware vehicle+roof object detection.
- Use SAM only for prompt-based mask-stability analysis.
- Use YOLO-World only as a diagnostic baseline that was rejected for roof detection after
  the open-vocabulary prompt gate.

## Final Detection Table

The supervised YOLOv8s detector uses class `0=vehicle` and class `1=roof`. The final
reporting threshold is `conf=0.50`, selected from the threshold sweep because it gives the
highest overall F1 and balanced precision/recall.

| Configuration | mAP@0.5 | mAP@0.5:0.95 | Precision | Recall | F1 | GT | Predictions |
|---------------|--------:|-------------:|----------:|-------:|---:|---:|------------:|
| original | 0.863715 | 0.607265 | 0.884058 | 0.881662 | 0.882858 | 2214 | 2208 |
| high_quality_512 | 0.845486 | 0.488057 | 0.892758 | 0.868564 | 0.880495 | 2214 | 2154 |
| balanced_256 | 0.839016 | 0.481047 | 0.877467 | 0.863595 | 0.870476 | 2214 | 2179 |
| max_compression_256 | 0.833041 | 0.474657 | 0.878704 | 0.857272 | 0.867856 | 2214 | 2160 |

Compared with original images, `balanced_256` reduces overall F1 by about `1.4%`, while
`max_compression_256` reduces F1 by about `1.7%`. The stricter `mAP@0.5:0.95` metric is
more sensitive to reconstruction, dropping by about `20.8%` for `balanced_256` and
`21.8%` for `max_compression_256`.

## Final SAM Table

SAM is not a class-aware detector. It uses human boxes as prompts and measures mask
stability across original and reconstructed image sets.

| Prompt class | Configuration | Prompts | Mean mask IoU | Mean Dice | Abs. area change | Failed prompt rate |
|--------------|---------------|--------:|--------------:|----------:|-----------------:|-------------------:|
| vehicle | high_quality_512 | 1013 | 0.735026 | 0.838327 | 0.041569 | 0.000000 |
| vehicle | balanced_256 | 1013 | 0.734634 | 0.838039 | 0.039600 | 0.000000 |
| vehicle | max_compression_256 | 1013 | 0.733121 | 0.837160 | 0.043506 | 0.000000 |
| roof | high_quality_512 | 1201 | 0.900123 | 0.945443 | 0.025937 | 0.000000 |
| roof | balanced_256 | 1201 | 0.898891 | 0.944659 | 0.027758 | 0.000000 |
| roof | max_compression_256 | 1201 | 0.895618 | 0.942522 | 0.029802 | 0.000000 |

## Evidence Packages

| Evidence | Repository folder |
|----------|-------------------|
| Compression x tile matrix | `results/2026-06-05-tradeoff-n50-lpips/` |
| YOLO-World prompt gate | `results/2026-06-12-openvocab-prompt-sweep/` |
| Vehicle-only detection | `results/2026-06-12-yolo-vehicle-human-n50/` |
| Vehicle+roof detection | `results/2026-06-12-yolo-vehicle-roof-human-n50/` |
| SAM vehicle/roof mask stability | `results/2026-06-12-sam-vehicle-roof-human-n50/` |
| Final runbook | `docs/sc26_vehicle_roof_yolo_sam_plan_2026-06-12.md` |

## Publication Boundary

Keep the repository GitHub-safe. Commit only lightweight Markdown, CSV, manifests, and
documentation. Keep raw images, full-resolution reconstructed outputs, masks, logs, model
weights, and checkpoints on DeltaAI under `/projects/bfod/$USER/cdc-deltaai/`.

## Long-Paper Next Steps

- Write the methods section around the locked N50 evaluation protocol.
- Use supervised YOLOv8s vehicle+roof as the main object-detection downstream task.
- Use SAM vehicle/roof mask stability as a complementary segmentation-boundary analysis.
- Include qualitative panels for original images, reconstructions, detections, and masks.
- If time allows, expand the human-labeled validation set beyond N50 before making stronger
  manuscript-level generalization claims.
