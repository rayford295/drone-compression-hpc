# SC26 Compression Experiment Suite

This folder contains the runnable experiment scaffold for the next compression meeting task.

## What It Covers

| Task | Script |
| --- | --- |
| Baseline full-resolution run | `slurm/01_baseline_resolution_batch.sbatch` |
| Native batch-size test, default 1 only | `slurm/01_baseline_resolution_batch.sbatch` |
| Controlled-resolution batch-size test, 1, 2, 4 | `slurm/01_baseline_resolution_batch.sbatch` |
| Resolution sweep, 4K, 2K, 1K | `slurm/01_baseline_resolution_batch.sbatch` |
| Compression-level check | `inspect_compression_controls.py` |
| Checkpoint-based compression sweep | `slurm/02_checkpoint_level_sweep.sbatch` |
| Tiling, 256, 512, 1024, 2048 | `slurm/03_tiling_sweep.sbatch` |
| Multiple parallel jobs | `slurm/04_hpc_scaling_array.sbatch` |
| Shared vs local storage | `slurm/05_storage_compare.sbatch` |
| Final all-run summary | `slurm/06_summarize_all.sbatch` |
| Practical compression x tile-size tradeoff | `slurm/07_compression_tile_tradeoff.sbatch` |
| Downstream object-detection impact | `evaluate_object_detection_impact.py`, `slurm/08_object_detection_impact.sbatch` |
| Jacob compression-side suite, no tiling | `slurm/run_jacob_compression_suite.sh` |
| Combined tables | `summarize_results.py` |
| Poster-ready visual panels | `make_poster_panels.py` |

## Important Compression-Level Finding

The x-param path used by the current SC26 workflow does not expose a direct runtime parameter called `compression_level`, `quality`, `bitrate`, or `quantization`.

For this workflow, run the checkpoint sweep and assign practical low, medium, and high compression from the measured BPP and compression ratio. The epsilon-param code has a `bitrate_scale` argument, but that belongs to a different path and should not be mixed into the x-param results unless the experiment changes.

Generate the inspection report with:

```bash
python experiments/compression/inspect_compression_controls.py
```

It writes:

```text
experiments/compression/compression_controls_report.md
```

## Output Layout

On DeltaAI the default output root is:

```text
/projects/bfod/$USER/cdc-deltaai/output/sc26_compression/$RUN_STAMP/
```

`RUN_STAMP` defaults to `YYYYMMDD_HHMMSS`. The full suite uses one shared
timestamp for all submitted jobs, so baseline, checkpoint, tiling, scaling, and
storage results stay together.

Each run writes:

```text
experiment_name/
├── results.csv       # per-image metrics
├── summary.csv       # one-row aggregate
├── manifest.json     # full config and summary
├── report.md         # compact Markdown summary
└── visuals/          # saved reconstructions, previews, heatmaps, comparison panels
```

After each SLURM script finishes, it also writes:

```text
combined_summary.csv
combined_summary.md
```

## Metrics

The core table columns are:

| Column | Meaning |
| --- | --- |
| `run_start_utc` | experiment start timestamp in UTC |
| `run_end_utc` | experiment end timestamp in UTC |
| `run_stamp` | suite timestamp used in the output folder |
| `slurm_job_id` | SLURM job ID, if available |
| `resolution_label` | native, 4k, 2k, or 1k |
| `tile_size` | `0` for no tiling, otherwise tile edge length |
| `tile_batch_size` | number of tiles compressed in one model call for tiled runs |
| `batch_size` | full-image batch size, or default tile batch size for tiled runs |
| `avg_wall_sec` | average wall time per image |
| `avg_data_prepare_sec` | average image read / resize / crop preparation time |
| `avg_pipeline_sec` | average end-to-end per-image time including preparation |
| `avg_non_gpu_sec` | average non-inference time, useful as a lightweight I/O / CPU overhead estimate |
| `avg_process_cpu_util_pct` | process CPU time divided by wall time, reported as a percent |
| `avg_inference_sec` | GPU-timed inference time |
| `avg_peak_gpu_mem_mb` | peak allocated GPU memory |
| `avg_bpp` | estimated model bitrate |
| `avg_compression_ratio` | `24 / avg_bpp` vs uncompressed RGB |
| `avg_psnr_db` | PSNR in decibels; higher means lower pixel-level reconstruction error |
| `avg_ssim` | SSIM in `[0, 1]`; higher means better structural similarity |
| `avg_lpips` | optional LPIPS perceptual distance when `COMPUTE_LPIPS=1`; lower is better |
| `avg_mse` | mean squared pixel error on clamped `[0, 1]` RGB values |
| `avg_rmse` | square root of MSE, in `[0, 1]` pixel-value units |
| `avg_mae` | mean absolute pixel error, easier to read than MSE |
| `avg_error_p95` | 95th percentile absolute pixel error |
| `avg_error_p99` | 99th percentile absolute pixel error |
| `avg_max_abs_error` | maximum absolute pixel error in the image |
| `avg_bias_mean` | signed mean reconstruction bias; positive means brighter on average |
| `avg_error_std` | standard deviation of absolute pixel error |
| `avg_seam_error_mean` | tiled-only seam artifact metric |

The compressed size is estimated from model BPP:

```text
estimated compressed bytes = width * height * bpp / 8
```

The reconstructed PNG size is recorded only for saved visual outputs. It is not the actual compressed representation.

### How to Explain Compression Ratio, PSNR, and SSIM

Compression ratio compares uncompressed RGB storage with the model's estimated compressed bitrate. The runner uses `24 / bpp` because an uncompressed RGB image has 24 bits per pixel. A value of `68x` means the model representation is estimated to use about one sixty-eighth of the uncompressed RGB bits.

PSNR measures pixel-level fidelity in decibels. Higher is better. It is sensitive to small pixel errors, but it does not always match human perception.

SSIM measures structural similarity, including luminance, contrast, and local structure. Higher is better, and values closer to `1.0` mean the reconstruction keeps more of the original image structure.

Use the metrics together: compression ratio reports storage savings, PSNR and MAE/RMSE report pixel error, SSIM reports structural quality, and seam metrics plus heatmaps check tiling artifacts.

LPIPS is disabled by default because it adds extra model work and memory pressure. Enable it for final-quality sweeps:

```bash
COMPUTE_LPIPS=1 LPIPS_MAX_EDGE=512 N_IMAGES=8 sbatch experiments/compression/slurm/03_tiling_sweep.sbatch
```

### Visual Difference Algorithm

For each saved visual example, the runner now saves:

| File suffix | Meaning |
| --- | --- |
| `_recon.png` or `_stitched.png` | reconstructed output at native saved resolution |
| `_original_preview.png` | downsampled original image preview |
| `_error_heatmap.png` | absolute RGB error heatmap, normalized by the 99.5th percentile error |
| `_comparison.png` | left: original preview; middle: reconstruction preview; right: error heatmap |
| `_poster_panel.png` | six-panel poster figure: original, reconstruction, hot difference map, histogram, metrics, and distribution |

The heatmap computes the per-pixel mean absolute RGB difference between the original image and the reconstruction. Dark areas mean small differences. Yellow-white areas mark the largest residuals in that image. Because the heatmap uses a robust 99.5th percentile normalization, a few extreme pixels do not hide broad lower-level artifacts.

To generate the poster panels from an existing DeltaAI output folder without rerunning the model:

```bash
python experiments/compression/make_poster_panels.py \
  --root /projects/bfod/$USER/cdc-deltaai/output/sc26_compression/20260515_yifan_selected_256_512_n50/03_tiling_sweep \
  --max_panels 4 \
  --max_edge 1200 \
  --overwrite
```

## Run on DeltaAI

Clone or update the repo on DeltaAI:

```bash
cd /projects/bfod/$USER/cdc-deltaai/code
git pull
```

Run the baseline, batch, and resolution sweep:

```bash
N_IMAGES=8 sbatch experiments/compression/slurm/01_baseline_resolution_batch.sbatch
```

The native full-resolution batch test defaults to `batch_size=1` because `batch_size=2` can exceed GH200 memory for `5440 x 3648` images. The 1/2/4 batch-size sweep runs at a controlled `2K` max edge by default. Override only when you want to test the native OOM boundary:

```bash
NATIVE_BATCH_SIZES="1 2 4" N_IMAGES=4 sbatch experiments/compression/slurm/01_baseline_resolution_batch.sbatch
```

Run the checkpoint compression-level sweep:

```bash
N_IMAGES=8 sbatch experiments/compression/slurm/02_checkpoint_level_sweep.sbatch
```

Run the tiling sweep:

```bash
N_IMAGES=8 sbatch experiments/compression/slurm/03_tiling_sweep.sbatch
```

The tiling sweep now includes `256 x 256` by default:

```bash
TILING_SIZES="256 512 1024 2048" N_IMAGES=8 sbatch experiments/compression/slurm/03_tiling_sweep.sbatch
```

For a quick 256-only smoke test:

```bash
TILING_SIZES="256" N_IMAGES=2 SAVE_VISUAL_LIMIT=2 sbatch experiments/compression/slurm/03_tiling_sweep.sbatch
```

Run multiple jobs in parallel:

```bash
SHARD_IMAGES=8 sbatch experiments/compression/slurm/04_hpc_scaling_array.sbatch
```

Run shared-vs-local storage comparison:

```bash
N_IMAGES=8 sbatch experiments/compression/slurm/05_storage_compare.sbatch
```

Run the practical compression x tile-size subset requested in the June 2 setup:

```bash
TRADEOFF_COMPRESSION_ROLES="high_quality balanced high_compression" \
TRADEOFF_TILE_SIZES="256 512" \
N_IMAGES=8 \
sbatch experiments/compression/slurm/07_compression_tile_tradeoff.sbatch
```

This produces no-tiling references plus selected tiled rows for:

- high quality / low compression: `checkpoint_b00512`
- balanced: `checkpoint_b00064`
- high compression: `checkpoint_b00128`

Run downstream object-detection impact after reconstructed image folders and YOLO labels are ready:

```bash
DETECTION_GT_DIR=/projects/bfod/$USER/cdc-deltaai/data/labels_yolo \
DETECTION_PREDICTION_DIRS="original=/path/to/original/pred_labels balanced=/path/to/balanced/pred_labels max_compression=/path/to/max/pred_labels" \
sbatch experiments/compression/slurm/08_object_detection_impact.sbatch
```

Or let the script run an Ultralytics detector if that package and model are available:

```bash
DETECTION_GT_DIR=/projects/bfod/$USER/cdc-deltaai/data/labels_yolo \
DETECTION_MODEL=/projects/bfod/$USER/models/detector.pt \
DETECTION_IMAGE_SETS="original=/projects/bfod/$USER/cdc-deltaai/data/imgs tile256=/path/to/recon_tile256" \
sbatch experiments/compression/slurm/08_object_detection_impact.sbatch
```

The detection output folder contains `detection_summary.csv`, `detection_per_class.csv`, `detection_summary.md`, and `manifest.json`.

For the N8 vehicle pilot, the evaluator supports COCO detector class mapping:

```bash
python experiments/compression/prepare_detection_image_sets.py \
  --ground_truth_dir /projects/bfod/$USER/cdc-deltaai/data/labels_yolo_vehicle_n8 \
  --image_sets original=/projects/bfod/$USER/cdc-deltaai/data/imgs \
  --output_dir /projects/bfod/$USER/cdc-deltaai/output/detection_image_sets/vehicle_n8 \
  --overwrite

RUN_STAMP=20260606_detection_coco_vehicle_n8 \
DETECTION_INSTALL_ULTRALYTICS=1 \
DETECTION_GT_DIR=/projects/bfod/$USER/cdc-deltaai/data/labels_yolo_vehicle_n8 \
DETECTION_MODEL=/projects/bfod/$USER/cdc-deltaai/weights/detectors/yolov8x.pt \
DETECTION_IMAGE_SETS="original=/projects/bfod/$USER/cdc-deltaai/output/detection_image_sets/vehicle_n8/original" \
DETECTION_CLASSES="2 5 7" \
DETECTION_CLASS_MAP="2=0 5=0 7=0" \
DETECTION_DROP_UNMAPPED=1 \
DETECTION_RESTRICT_TO_GT=1 \
sbatch experiments/compression/slurm/08_object_detection_impact.sbatch
```

COCO classes `2`, `5`, and `7` are car, bus, and truck. They are mapped to the pilot `0 vehicle` class. Use this as a detector-pipeline pilot unless a project-specific detector is available.

Submit the whole suite:

```bash
N_IMAGES=8 experiments/compression/slurm/run_all_suite.sh
```

Run Jacob's compression-side suite without the tiling sweep:

```bash
RUN_STAMP=20260515_jacob_compression_smoke N_IMAGES=4 SHARD_IMAGES=4 SAVE_VISUAL_LIMIT=1 experiments/compression/slurm/run_jacob_compression_suite.sh
```

Use this Jacob launcher for the group-chat task about baseline compression, resolution sweep, compression-level candidates, batch size, HPC scaling, and storage comparison. It skips tiling because that belongs to Yifan's reconstruction/tiling workflow.

To choose a timestamp yourself:

```bash
RUN_STAMP=20260504_meeting_prep N_IMAGES=8 experiments/compression/slurm/run_all_suite.sh
```

For poster-quality numbers, raise `N_IMAGES` after the smoke run succeeds:

```bash
N_IMAGES=100 experiments/compression/slurm/run_all_suite.sh
```

## Run One Local Interactive Test

Inside a GPU allocation:

```bash
module load python/miniforge3_pytorch/2.10.0
conda activate base
export PYTHONPATH=$HOME/.local/lib/python3.12/site-packages:$PYTHONPATH
python -m pip install --user scikit-image compressai einops lpips ema-pytorch tqdm matplotlib pandas --quiet

cd /projects/bfod/$USER/cdc-deltaai/code

python experiments/compression/run_compression_experiment.py \
  --ckpt /projects/bfod/$USER/cdc-deltaai/weights/x_param/image-l2-use_weight5-vimeo-d64-t8193-b0.2048-x-cosine-01-float32-aux0.9lpips_2.pt \
  --img_dir /projects/bfod/$USER/cdc-deltaai/data/imgs \
  --out_dir /projects/bfod/$USER/cdc-deltaai/output/sc26_compression/smoke_test \
  --lpips_weight 0.9 \
  --experiment_name smoke_test \
  --compression_setting baseline_b02048 \
  --resolution_label native_full_resolution \
  --max_edge 0 \
  --batch_size 1 \
  --n_images 1 \
  --n_denoise_step 65
```

## Tiling Notes

Tiling uses independent tile compression, then stitches tiles back into one image. It records:

- total runtime
- peak GPU memory
- PSNR and SSIM
- MSE, RMSE, MAE, high-percentile absolute error, maximum absolute error, and mean bias
- estimated compressed size and compression ratio
- seam artifact metrics at tile boundaries
- original/reconstruction/error-heatmap comparison panels

The first few stitched outputs are saved under `visuals/`. Inspect the comparison panels before using tiling results in the poster.
