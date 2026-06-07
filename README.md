# CDC Image Compression and Reconstruction on DeltaAI

This repository contains the SC26 experiment package for evaluating Conditional Diffusion Model based lossy compression and reconstruction on high-resolution drone imagery. The work adapts the CDC image-compression code path for GPU HPC systems and studies the full systems question: how much storage can be saved before reconstruction quality and downstream computer-vision behavior degrade.

The core narrative handoff is the June 6 experiment-response document. This README mirrors that document and uses the poster draft as the project framing source.

Based on: [Lossy Image Compression with Conditional Diffusion Models](https://arxiv.org/pdf/2209.06950.pdf)

## Current Answer

For the June 2 experiment-response scope, the implementation and main DeltaAI runs are complete.

Recommended setting:

- Use `balanced_checkpoint_b00064` with `256 x 256` tiling as the primary deployment setting.
- Keep `balanced_checkpoint_b00064` with `512 x 512` tiling as the quality-safe backup.
- Keep `high_compression_checkpoint_b00128` as a stress-test setting only.

The detection and SAM downstream experiments are complete as pilots. The N50 vehicle labels are draft labels, so these results support sensitivity analysis and workflow validation. They should not be presented as final paper-grade detection benchmarks until the labels are manually reviewed and, ideally, a project-specific detector is available.

## Poster Storyline

Drone surveys can generate hundreds of gigabytes of ultra-high-resolution imagery. The poster question is whether a CDC compression and reconstruction workflow can reduce storage and transfer pressure on HPC systems while preserving enough image quality for inspection and downstream computer vision.

Current poster framing:

- Study area: Galveston, Texas.
- Data: 100 RGB drone images, approximately `5472 x 3648` pixels, 24-bit color, average original size about `8.34 MB`, collected from about `47 m` altitude.
- Baseline: native full-resolution reconstruction, fp32, 65 denoising steps, batch size 1.
- Controlled settings: checkpoint, tile size, tile batch size, denoising steps, precision, resolution, and storage placement.
- Metrics: wall time, peak GPU memory, BPP, compression ratio, PSNR, SSIM, LPIPS, high-percentile error, seam metrics, visual heatmaps, detection metrics, and SAM mask-stability metrics.
- Systems scope: DeltaAI GH200 is the main experiment platform. Delta H200 is a quick hardware comparison target.

## Experiment Status

| Item | Question | Status | Evidence |
| --- | --- | --- | --- |
| Experiment 1 | Compression optimization | Complete | Checkpoint-controlled compression settings are selected. `b00064` is the main balanced setting; `b00128` is the high-compression stress test. |
| Experiment 2 | Reconstruction optimization | Complete | 256 and 512 tiling were validated. 256 tiles are fastest and lowest memory; 512 tiles are the quality backup. |
| Experiment 3 | Compression x tile-size tradeoff | Complete | The N50 LPIPS matrix finished all 9 rows on DeltaAI GH200 under Slurm job `2422336`. |
| Experiment 4 | Object-detection impact | Complete as pilot | The N50 COCO YOLOv8x vehicle workflow finished under Slurm job `2426722`; labels remain draft. |
| Add-on | SAM zero-shot mask stability | Complete as pilot | Meta SAM ViT-H finished on 50 images and 829 prompts under Slurm job `2426827`; failed prompt rate was 0. |
| Add-on | GH200 vs H200 comparison | Complete | H200 is runnable and is about 3.6% faster than the prior GH200 fp32 sweep at matched step counts. |

## Final Recommendation

| Configuration | Setting | Sec/img | Peak GPU | Compression | PSNR | SSIM | LPIPS | Interpretation |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| High quality 512 | `b00512 + 512 tile` | 88.51 | 2.96 GB | 29.73x | 34.19 | 0.9376 | 0.002591 | Quality reference for tiled reconstruction. |
| Balanced 256 | `b00064 + 256 tile` | 79.34 | 1.57 GB | 79.98x | 33.14 | 0.8768 | 0.001826 | Recommended speed and memory setting. |
| Balanced 512 | `b00064 + 512 tile` | 86.00 | 2.90 GB | 78.48x | 33.23 | 0.8782 | 0.001792 | Quality-safe backup. |
| Max compression 256 | `b00128 + 256 tile` | 78.91 | 1.57 GB | 139.89x | 30.89 | 0.8193 | 0.005676 | Stress-test setting only. |

Source: `results/2026-06-05-tradeoff-n50-lpips/`.

System readout: 256 tiling reduces peak GPU memory from roughly 52 GB in full-image mode to roughly 1.6 GB while cutting runtime from about 143 seconds per image to about 79 seconds per image. The 512 setting is slower and uses more memory, but it is slightly safer on image-quality metrics.

## Compression Settings

The current x-param CDC path does not expose a continuous runtime compression-ratio knob. Compression is controlled by checkpoint choice and reported using measured BPP and compression ratio.

| Role | Checkpoint | Sec/img | Peak GPU | BPP | Compression | PSNR | SSIM | Use |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| High quality | `b00512` | 143.73 | 50.8 GB | 0.7345 | 32.67x | 34.84 | 0.9423 | Highest fidelity reference. |
| Balanced | `b00064` | 143.66 | 50.7 GB | 0.2578 | 93.11x | 33.73 | 0.8803 | Main compression setting. |
| High compression | `b00128` | 143.70 | 50.7 GB | 0.1448 | 165.73x | 31.52 | 0.8281 | Maximum-compression stress test. |
| Baseline | `b02048` | 143.70 | 50.8 GB | 0.3371 | 71.20x | 29.45 | 0.8727 | Earlier reference setting. |

Source: `results/2026-05-22-jacob-compression-n20/`.

## Downstream Impact

### Object Detection

Experiment 4 runs a fixed detector on original and reconstructed image sets, then compares predictions against the same YOLO-format vehicle labels.

N50 pilot setup:

- Detector: COCO-pretrained Ultralytics YOLOv8x.
- Class mapping: COCO `car`, `bus`, and `truck` mapped to one pilot class, `0 vehicle`.
- Ground truth: 50 draft-labeled images, 829 vehicle boxes.
- Caveat: the first 8 images use manual draft labels; images 9 to 50 use auto-assisted COCO YOLOv8x vehicle candidates at confidence `0.40`.

| Configuration | mAP@0.5 | mAP@0.5:0.95 | Precision@0.5 | Recall@0.5 | F1@0.5 | GT boxes | Predictions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Original | 0.6902 | 0.5711 | 0.0635 | 0.8432 | 0.1182 | 829 | 11002 |
| High quality 512 | 0.6329 | 0.2706 | 0.0625 | 0.8094 | 0.1160 | 829 | 10742 |
| Balanced 256 | 0.6280 | 0.2712 | 0.0601 | 0.8070 | 0.1118 | 829 | 11137 |
| Balanced 512 | 0.6225 | 0.2703 | 0.0592 | 0.8070 | 0.1102 | 829 | 11310 |
| Max compression 256 | 0.5889 | 0.2603 | 0.0568 | 0.7720 | 0.1059 | 829 | 11260 |

Source: `results/2026-06-06-detection-coco-vehicle-n50/`.

Interpretation: balanced reconstructions remain closer to the original baseline than maximum compression. Precision is low because `DETECTION_CONF=0.001` intentionally keeps many low-confidence predictions for AP and recall analysis.

### SAM Zero-Shot Mask Stability

The SAM add-on uses the same N50 vehicle boxes as prompts and compares the reconstructed-image mask with the original-image mask for the same image and prompt. This is not class-aware detection accuracy. It is a zero-shot segmentation boundary-stability check.

| Configuration | Images | Prompts | Mean mask IoU | Mean Dice | Area ratio | Abs. area change | Centroid shift | Failed prompt rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Original | 50 | 829 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.00 px | 0.0000 |
| Balanced 256 | 50 | 829 | 0.7056 | 0.8110 | 1.0193 | 0.0754 | 16.76 px | 0.0000 |
| Balanced 512 | 50 | 829 | 0.7061 | 0.8116 | 1.0133 | 0.0698 | 16.81 px | 0.0000 |
| Max compression 256 | 50 | 829 | 0.7048 | 0.8107 | 1.0229 | 0.0785 | 16.67 px | 0.0000 |

Source: `results/2026-06-06-sam-mask-impact-n50/`.

Interpretation: all prompts returned usable masks. Balanced 512 is slightly best on mask IoU, Dice, and area stability; Balanced 256 is nearly tied and remains the speed-memory recommendation.

## Hardware Comparison

| Steps | GH200 sec/img | H200 sec/img | H200 speedup | Note |
| ---: | ---: | ---: | ---: | --- |
| 5 | 11.27 | 10.87 | 3.6% | Same fp32 reconstruction comparison. |
| 20 | 44.37 | 42.74 | 3.7% | Same fp32 reconstruction comparison. |
| 65 | 143.67 | 138.48 | 3.6% | Same fp32 reconstruction comparison. |

Source: `results/2026-04-28-h200-reconstruction/`.

The H200 comparison confirms that the workflow runs on H200. The speed difference is modest, so the main experiment selection should be based on checkpoint and tile behavior before broad H200 reruns.

## Repository Map

| Path | Use |
| --- | --- |
| `paper/submission/` | SC26 poster draft, IEEE-format summary draft, optional artifact appendix, and poster figures. |
| `paper/` | Longer paper-style LaTeX draft and compiled PDF. |
| `results/` | GitHub-safe result summaries, CSVs, Markdown tables, and small visual examples. |
| `experiments/compression/` | DeltaAI experiment runners, SLURM scripts, detection evaluator, SAM evaluator, summarizers, and poster-panel helpers. |
| `docs/` | Dated runbooks, experiment plans, and progress notes. |
| `data/detection_pilot/` | Draft YOLO vehicle labels for N8 and N50 detection-pipeline validation. |
| `slides/` | Editable progress decks and rebuild scripts from earlier SC26 update cycles. |
| `xparam/`, `epsilonparam/` | Model code adapted from the CDC implementation. |

## Result Archive

Most readers should start from these result packages:

| Folder | Purpose |
| --- | --- |
| `results/2026-06-05-tradeoff-n50-lpips/` | Formal N50 compression-setting x tile-size matrix with LPIPS. |
| `results/2026-06-06-detection-coco-vehicle-n50/` | N50 COCO YOLOv8x vehicle detection pilot. |
| `results/2026-06-06-sam-mask-impact-n50/` | N50 Meta SAM zero-shot mask-stability pilot. |
| `results/2026-05-22-jacob-compression-n20/` | Compression-side checkpoint and storage validation. |
| `results/2026-05-15-yifan-selected-256-512-n50/` | Earlier selected 256 vs 512 tiling validation with visual examples. |
| `results/2026-04-28-h200-reconstruction/` | Delta H200 quick reconstruction comparison. |
| `results/2026-04-26-reconstruction/` | Initial DeltaAI GH200 reconstruction profiling. |

See `results/README.md` for the full archive index.

## Data and Privacy Boundary

This repository is intended as a private research and experiment package.

Tracked:

- Source code, SLURM scripts, runbooks, and result summaries.
- Small GitHub-safe visual examples and poster figures.
- Draft N8 and N50 YOLO vehicle labels used to validate the detection pipeline.

Not tracked:

- Raw drone image folders such as `100_0005/`.
- Full-resolution reconstructed outputs.
- DeltaAI logs and full output folders.
- CDC checkpoints, SAM checkpoints, detector weights, and local caches.

The expected DeltaAI storage root is:

```text
/projects/bfod/$USER/cdc-deltaai/
```

The default experiment output root is:

```text
/projects/bfod/$USER/cdc-deltaai/output/sc26_compression/$RUN_STAMP/
```

## Run the Current Workflows on DeltaAI

Use a clean checkout on DeltaAI. If an old checkout has diverged, clone a fresh `code_main_<sha>` tree rather than trying to repair the old working copy mid-run.

```bash
cd /projects/bfod/$USER/cdc-deltaai
git clone https://github.com/rayford295/sc26-cdc-deltaai.git code_main
cd code_main
git rev-parse --short HEAD
```

Stage draft N50 labels:

```bash
mkdir -p /projects/bfod/$USER/cdc-deltaai/data/labels_yolo_vehicle_n50_draft
rsync -av data/detection_pilot/labels_yolo_vehicle_n50_draft/labels/ \
  /projects/bfod/$USER/cdc-deltaai/data/labels_yolo_vehicle_n50_draft/
```

Run the formal compression x tile-size matrix:

```bash
RUN_STAMP=YYYYMMDD_tradeoff_n50_lpips \
N_IMAGES=50 \
SAVE_VISUAL_LIMIT=8 \
COMPUTE_LPIPS=1 \
LPIPS_MAX_EDGE=512 \
TRADEOFF_COMPRESSION_ROLES="high_quality balanced high_compression" \
TRADEOFF_TILE_SIZES="256 512" \
sbatch --mem=96G --time=18:00:00 \
  --export=ALL,REPO_DIR=$PWD \
  experiments/compression/slurm/07_compression_tile_tradeoff.sbatch
```

Prepare image sets for downstream detection or SAM evaluation:

```bash
python experiments/compression/prepare_detection_image_sets.py \
  --ground_truth_dir /projects/bfod/$USER/cdc-deltaai/data/labels_yolo_vehicle_n50_draft \
  --image_sets \
    original=/projects/bfod/$USER/cdc-deltaai/data/imgs \
    balanced_256=/path/to/balanced_tile_256/visuals \
    balanced_512=/path/to/balanced_tile_512/visuals \
    max_compression_256=/path/to/high_compression_tile_256/visuals \
  --output_dir /projects/bfod/$USER/cdc-deltaai/output/detection_image_sets/vehicle_n50_tradeoff \
  --overwrite
```

Run the COCO vehicle detection pilot:

```bash
RUN_STAMP=YYYYMMDD_detection_coco_vehicle_n50 \
DETECTION_INSTALL_ULTRALYTICS=1 \
DETECTION_GT_DIR=/projects/bfod/$USER/cdc-deltaai/data/labels_yolo_vehicle_n50_draft \
DETECTION_MODEL=/projects/bfod/$USER/cdc-deltaai/weights/detectors/yolov8x.pt \
DETECTION_IMAGE_SETS="original=/path/to/original balanced_256=/path/to/balanced_256 balanced_512=/path/to/balanced_512 max_compression_256=/path/to/max_compression_256" \
DETECTION_CLASSES="2 5 7" \
DETECTION_CLASS_MAP="2=0 5=0 7=0" \
DETECTION_DROP_UNMAPPED=1 \
DETECTION_RESTRICT_TO_GT=1 \
DETECTION_IMGSZ=1280 \
DETECTION_CONF=0.001 \
sbatch --mem=64G --time=04:00:00 \
  --export=ALL,REPO_DIR=$PWD \
  experiments/compression/slurm/08_object_detection_impact.sbatch
```

Run the SAM mask-stability pilot:

```bash
RUN_STAMP=YYYYMMDD_sam_vehicle_n50 \
SAM_CHECKPOINT=/projects/bfod/$USER/cdc-deltaai/weights/sam/sam_vit_h_4b8939.pth \
SAM_MODEL_TYPE=vit_h \
SAM_PROMPT_LABEL_DIR=/projects/bfod/$USER/cdc-deltaai/data/labels_yolo_vehicle_n50_draft \
SAM_IMAGE_SETS="original=/path/to/original balanced_256=/path/to/balanced_256 balanced_512=/path/to/balanced_512 max_compression_256=/path/to/max_compression_256" \
SAM_PROMPT_BATCH_SIZE=4 \
sbatch --mem=96G --time=08:00:00 \
  --export=ALL,REPO_DIR=$PWD \
  experiments/compression/slurm/09_sam_mask_impact.sbatch
```

## Remaining Quality Steps

These items are not blockers for the June 2 response package. They are the next gates before stronger manuscript claims:

- Manually review and correct the N50 draft vehicle labels.
- Expand the reviewed label set if time allows.
- Rerun Experiment 4 with a project-specific detector if one becomes available.
- Keep the repository private unless large local artifacts are removed and the label/data-sharing boundary is rechecked.

## Citation and Acknowledgment Notes

The poster draft acknowledges GH200 and H200 GPU resources through ACCESS allocation `CIV250023`. Keep that acknowledgment in poster and manuscript materials when using these results.
