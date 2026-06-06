# 2026-06-05 Compression x Tile-Size Tradeoff N50 LPIPS

This folder records the formal DeltaAI GH200 compression-setting x tile-size tradeoff run after the `N_IMAGES=8` smoke test.

## Scope

- System: DeltaAI GH200, partition `ghx4`
- DeltaAI code checkout: `/projects/bfod/yyang48/cdc-deltaai/code_main_641d86c`
- SLURM job: `2422336`
- Run stamp: `20260605_tradeoff_n50_lpips`
- Runtime: `13:15:48`
- MaxRSS: `23838464K`
- Allocation: 1 GPU, 4 CPU cores, `96G` memory
- Input: `N_IMAGES=50`, full-resolution `5440 x 3648` drone images
- Checkpoint roles: high quality, balanced, high compression
- Tile sizes: no tiling reference, `256 x 256`, and `512 x 512`
- LPIPS: enabled with `LPIPS_MAX_EDGE=512`

The full raw run remains on DeltaAI:

```text
/projects/bfod/yyang48/cdc-deltaai/output/sc26_compression/20260605_tradeoff_n50_lpips/07_compression_tile_tradeoff/
```

## Files

| File | Use |
| --- | --- |
| `tables/combined_summary.csv` | Machine-readable summary copied from the DeltaAI run |
| `tables/combined_summary.md` | Markdown summary table copied from the DeltaAI run |

## Key Readout

The formal run completed all nine planned rows. `256 x 256` tiling remains the fastest and lowest-memory option across all checkpoint roles, at about `79` seconds per image and about `1.6 GB` peak GPU memory. `512 x 512` tiling costs about `6` to `9` more seconds per image and about `3.0 GB` peak GPU memory, but gives slightly better PSNR, SSIM, LPIPS, and seam metrics than `256 x 256` in the balanced and high-compression rows.

For the likely deployment recommendation, `balanced_checkpoint_b00064` is still the most useful tradeoff. The `256 x 256` balanced row gives `79.98x` compression, `33.14 dB` PSNR, `0.8768` SSIM, and `0.001826` LPIPS. The `512 x 512` balanced row gives `78.48x` compression, `33.23 dB` PSNR, `0.8782` SSIM, and `0.001792` LPIPS.

Interpretation: use `balanced_checkpoint_b00064` plus `256 x 256` tiling when speed and memory are the priority. Use `balanced_checkpoint_b00064` plus `512 x 512` tiling when the poster or downstream task favors the slightly safer quality row. The high-compression checkpoint should wait for object-detection validation before becoming a recommendation.

## Next Step

Run object-detection impact only after YOLO-format ground-truth labels and either prediction folders or an Ultralytics detector model are ready. Package only the detection summary CSV, per-class CSV, Markdown summary, and manifest into GitHub after that run succeeds.
