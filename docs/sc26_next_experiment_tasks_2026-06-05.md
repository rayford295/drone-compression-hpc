# SC26 Next Experiment Tasks, 2026-06-05

This page records the current SC26 CDC experiment work that still needs action after the `N_IMAGES=8` compression x tile-size smoke run.

## Current Source of Truth

- Local and GitHub repository commit after the smoke-result package: `0c58272`
- DeltaAI code checkout for the active run: `/projects/bfod/yyang48/cdc-deltaai/code_main_641d86c`
- Smoke result package in GitHub: `results/2026-06-05-tradeoff-smoke/`
- Full raw smoke output on DeltaAI:

```text
/projects/bfod/yyang48/cdc-deltaai/output/sc26_compression/20260605_tradeoff_smoke/07_compression_tile_tradeoff/
```

## Completed Today

- Ran `07_compression_tile_tradeoff.sbatch` as a smoke test.
- SLURM job: `2422067`
- Run stamp: `20260605_tradeoff_smoke`
- Status: completed in `02:11:03`
- Result rows: 9
- Matrix: high-quality, balanced, and high-compression checkpoints crossed with no tiling, `256 x 256`, and `512 x 512`.
- GitHub record: committed as `0c58272` with lightweight CSV and Markdown summaries.

## Active Run to Monitor

The formal `N_IMAGES=50` tradeoff run with LPIPS was submitted after the smoke test.

```bash
RUN_STAMP=20260605_tradeoff_n50_lpips \
N_IMAGES=50 \
SAVE_VISUAL_LIMIT=8 \
COMPUTE_LPIPS=1 \
LPIPS_MAX_EDGE=512 \
TRADEOFF_COMPRESSION_ROLES="high_quality balanced high_compression" \
TRADEOFF_TILE_SIZES="256 512" \
sbatch --mem=96G --time=18:00:00 --export=ALL,REPO_DIR=/projects/bfod/yyang48/cdc-deltaai/code_main_641d86c \
  experiments/compression/slurm/07_compression_tile_tradeoff.sbatch
```

- SLURM job: `2422336`
- Run stamp: `20260605_tradeoff_n50_lpips`
- Purpose: produce the main poster/manuscript table for compression setting x tile size.
- Expected output:

```text
/projects/bfod/yyang48/cdc-deltaai/output/sc26_compression/20260605_tradeoff_n50_lpips/07_compression_tile_tradeoff/
```

Monitor it with:

```bash
squeue -j 2422336
tail -f experiments/compression/slurm/logs/tradeoff_2422336.log
sacct -j 2422336 --format=JobID,JobName,State,Elapsed,MaxRSS,AllocTRES%40
```

Read the final table with:

```bash
cat /projects/bfod/yyang48/cdc-deltaai/output/sc26_compression/20260605_tradeoff_n50_lpips/07_compression_tile_tradeoff/combined_summary.md
```

## What to Do When Job 2422336 Finishes

1. Confirm the job completed.

```bash
sacct -j 2422336 --format=JobID,JobName,State,Elapsed,MaxRSS,AllocTRES%40
```

2. Inspect the Markdown table and check that it has 9 rows.

```bash
cat /projects/bfod/yyang48/cdc-deltaai/output/sc26_compression/20260605_tradeoff_n50_lpips/07_compression_tile_tradeoff/combined_summary.md
```

3. Copy only lightweight outputs into GitHub.

Target package:

```text
results/2026-06-05-tradeoff-n50-lpips/
├── README.md
└── tables/
    ├── combined_summary.csv
    └── combined_summary.md
```

Do not commit raw full-resolution reconstructions, SLURM logs, checkpoints, raw drone images, or full `visuals/` folders.

4. Update the result index.

- `README.md`
- `results/README.md`

5. Push the package to GitHub.

Use a commit message like:

```text
Add SC26 N50 LPIPS tradeoff results
```

## How to Interpret the N=50 Result

Use the N=50 table to decide whether the poster recommendation should be:

- `balanced_checkpoint_b00064` plus `256 x 256` tiling, if the speed and memory gains hold and LPIPS/seam metrics remain acceptable.
- `balanced_checkpoint_b00064` plus `512 x 512` tiling, if `512 x 512` gives meaningfully better SSIM, LPIPS, or visible quality for a modest runtime cost.
- `high_quality_checkpoint_b00512` plus `512 x 512` or no tiling, only if the downstream task needs the highest fidelity more than compression ratio or runtime.
- `high_compression_checkpoint_b00128`, only if detection and visual QA show that the quality loss is acceptable.

Main columns to compare:

- `avg_wall_sec`
- `avg_peak_gpu_mem_mb`
- `avg_bpp`
- `avg_compression_ratio`
- `avg_psnr_db`
- `avg_ssim`
- `avg_lpips`
- `avg_error_p99`
- `avg_seam_error_mean`

## Next Experiment After N=50

Run object-detection impact only after the needed inputs exist.

Required inputs:

- YOLO-format ground-truth labels:

```text
/projects/bfod/yyang48/cdc-deltaai/data/labels_yolo
```

- Either existing prediction label folders for original and reconstructed images, or an Ultralytics detector model that can generate those predictions.

If prediction folders already exist:

```bash
RUN_STAMP=20260605_detection_impact \
DETECTION_GT_DIR=/projects/bfod/yyang48/cdc-deltaai/data/labels_yolo \
DETECTION_PREDICTION_DIRS="original=/path/to/original/pred_labels best_quality=/path/to/best/pred_labels balanced=/path/to/balanced/pred_labels max_compression=/path/to/max/pred_labels" \
sbatch --export=ALL,REPO_DIR=/projects/bfod/yyang48/cdc-deltaai/code_main_641d86c \
  experiments/compression/slurm/08_object_detection_impact.sbatch
```

If the detector should run inside the job:

```bash
RUN_STAMP=20260605_detection_impact \
DETECTION_GT_DIR=/projects/bfod/yyang48/cdc-deltaai/data/labels_yolo \
DETECTION_MODEL=/projects/bfod/yyang48/models/detector.pt \
DETECTION_IMAGE_SETS="original=/projects/bfod/yyang48/cdc-deltaai/data/imgs balanced=/path/to/balanced/recon_images max_compression=/path/to/max/recon_images" \
sbatch --export=ALL,REPO_DIR=/projects/bfod/yyang48/cdc-deltaai/code_main_641d86c \
  experiments/compression/slurm/08_object_detection_impact.sbatch
```

Expected detection outputs:

- `detection_summary.csv`
- `detection_per_class.csv`
- `detection_summary.md`
- `manifest.json`

Package only those lightweight outputs into GitHub after the detection run succeeds.
