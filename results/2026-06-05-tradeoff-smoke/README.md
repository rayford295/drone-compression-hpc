# 2026-06-05 Compression x Tile-Size Tradeoff Smoke

This folder records the first DeltaAI GH200 smoke run for the combined compression-setting x tile-size matrix requested in the June 2 SC26 experiment setup.

## Scope

- System: DeltaAI GH200, partition `ghx4`
- Repository commit on DeltaAI: `641d86c`
- SLURM job: `2422067`
- Run stamp: `20260605_tradeoff_smoke`
- Runtime: `02:11:03`
- Input: `N_IMAGES=8`, full-resolution `5440 x 3648` drone images
- Checkpoint roles: high quality, balanced, high compression
- Tile sizes: no tiling reference, `256 x 256`, and `512 x 512`
- LPIPS: not enabled in this smoke run

The full raw run remains on DeltaAI:

```text
/projects/bfod/USERNAME/cdc-deltaai/output/sc26_compression/20260605_tradeoff_smoke/07_compression_tile_tradeoff/
```

## Files

| File | Use |
| --- | --- |
| `tables/combined_summary.csv` | Machine-readable summary copied from the DeltaAI run |
| `tables/combined_summary.md` | Markdown summary table copied from the DeltaAI run |

## Key Readout

The smoke run completed all nine planned rows. `256 x 256` tiling was the fastest and lowest-memory option across all three checkpoint roles, with about `79` to `80` seconds per image and about `1.6 GB` peak GPU memory. `512 x 512` tiling was slower, about `86` to `90` seconds per image, and used about `3.0 GB` peak GPU memory, but it slightly improved PSNR and SSIM relative to `256 x 256`.

No-tiling references stayed near `144` seconds per image and about `52 GB` peak GPU memory. That makes the tile-size benefit clear even before the larger validation run.

For the next run, use the same matrix at `N_IMAGES=50` and enable LPIPS:

```bash
RUN_STAMP=20260605_tradeoff_n50_lpips \
N_IMAGES=50 \
SAVE_VISUAL_LIMIT=8 \
COMPUTE_LPIPS=1 \
LPIPS_MAX_EDGE=512 \
TRADEOFF_COMPRESSION_ROLES="high_quality balanced high_compression" \
TRADEOFF_TILE_SIZES="256 512" \
sbatch --mem=96G --export=ALL,REPO_DIR=/projects/bfod/USERNAME/cdc-deltaai/code_main_641d86c \
  experiments/compression/slurm/07_compression_tile_tradeoff.sbatch
```
