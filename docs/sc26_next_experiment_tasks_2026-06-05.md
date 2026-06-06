# SC26 Next Experiment Tasks, 2026-06-05

This page records the current SC26 CDC experiment work after the `N_IMAGES=8` smoke run and formal `N_IMAGES=50` LPIPS validation.

## Current Source of Truth

- GitHub commit after the smoke-result package: `0c58272`
- GitHub commit that added this task checklist: `ab95276`
- DeltaAI code checkout used for the tradeoff runs: `/projects/bfod/yyang48/cdc-deltaai/code_main_641d86c`
- Smoke result package in GitHub: `results/2026-06-05-tradeoff-smoke/`
- Formal N50 LPIPS result package in GitHub: `results/2026-06-05-tradeoff-n50-lpips/`
- Full raw smoke output on DeltaAI:

```text
/projects/bfod/yyang48/cdc-deltaai/output/sc26_compression/20260605_tradeoff_smoke/07_compression_tile_tradeoff/
```

Full raw N50 LPIPS output on DeltaAI:

```text
/projects/bfod/yyang48/cdc-deltaai/output/sc26_compression/20260605_tradeoff_n50_lpips/07_compression_tile_tradeoff/
```

## Completed Tradeoff Runs

- Ran `07_compression_tile_tradeoff.sbatch` as a smoke test.
- SLURM job: `2422067`
- Run stamp: `20260605_tradeoff_smoke`
- Status: completed in `02:11:03`
- Result rows: 9
- Matrix: high-quality, balanced, and high-compression checkpoints crossed with no tiling, `256 x 256`, and `512 x 512`.
- GitHub record: committed as `0c58272` with lightweight CSV and Markdown summaries.

- Ran the formal `N_IMAGES=50` LPIPS tradeoff matrix.
- SLURM job: `2422336`
- Run stamp: `20260605_tradeoff_n50_lpips`
- Status: completed in `13:15:48`
- MaxRSS: `23838464K`
- Result rows: 9
- Matrix: same three checkpoint roles crossed with no tiling, `256 x 256`, and `512 x 512`.
- GitHub record: packaged under `results/2026-06-05-tradeoff-n50-lpips/`.

## Formal N50 Command

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

The output is:

```text
/projects/bfod/yyang48/cdc-deltaai/output/sc26_compression/20260605_tradeoff_n50_lpips/07_compression_tile_tradeoff/
```

The completion check was:

```bash
sacct -j 2422336 --format=JobID,JobName,State,Elapsed,MaxRSS,AllocTRES%40
```

The final table can be read on DeltaAI with:

```bash
cat /projects/bfod/yyang48/cdc-deltaai/output/sc26_compression/20260605_tradeoff_n50_lpips/07_compression_tile_tradeoff/combined_summary.md
```

## GitHub Packaging Status

The N50 LPIPS run is packaged as:

```text
results/2026-06-05-tradeoff-n50-lpips/
├── README.md
└── tables/
    ├── combined_summary.csv
    └── combined_summary.md
```

The package intentionally excludes raw full-resolution reconstructions, SLURM logs, checkpoints, raw drone images, and full `visuals/` folders.

The result index entries updated for this run are:

- `README.md`
- `results/README.md`

## How to Interpret the N=50 Result

The N50 table supports these working interpretations:

- `balanced_checkpoint_b00064` plus `256 x 256` tiling is the speed-memory recommendation: `79.34` seconds per image, about `1.6 GB` peak GPU memory, `79.98x` compression, PSNR `33.14`, SSIM `0.8768`, and LPIPS `0.001826`.
- `balanced_checkpoint_b00064` plus `512 x 512` tiling is the quality-safe backup: `86.00` seconds per image, about `3.0 GB` peak GPU memory, `78.48x` compression, PSNR `33.23`, SSIM `0.8782`, and LPIPS `0.001792`.
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
