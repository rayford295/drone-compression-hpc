# 2026-05-22 Jacob Compression-Side N=20 Result

This folder records the DeltaAI GH200 `N_IMAGES=20` compression-side experiment for Jacob's SC26 CDC task.

## Scope

- System: DeltaAI GH200, partition `ghx4`
- Run stamp: `20260522_jacob_compression_n20`
- Input: twenty full-resolution drone images cropped to `5440 x 3648`
- Baseline checkpoint: `baseline_b02048`
- Denoising steps: `65`
- Precision: `fp32`

The full raw output remains on DeltaAI:

```text
/projects/bfod/$USER/cdc-deltaai/output/sc26_compression/20260522_jacob_compression_n20/
```

## Key Findings

Native full-resolution compression is feasible at `batch_size=1`, but it is memory-heavy:

| Setup | Time per image | Peak GPU memory | Compression ratio | PSNR | SSIM |
| --- | ---: | ---: | ---: | ---: | ---: |
| Native, batch 1 | 144.32 s | 52.0 GB | 71.20x | 29.45 | 0.873 |

The controlled 2K batch-size sweep shows that larger batches do not improve throughput:

| Batch size | Time per image | Peak GPU memory |
| --- | ---: | ---: |
| 1 | 7.35 s | 7.47 GB |
| 2 | 11.60 s | 14.64 GB |
| 4 | 9.29 s | 28.96 GB |

Recommended default: use `batch_size=1`.

Checkpoint sweep candidates:

| Compression role | Checkpoint | Compression ratio | PSNR | SSIM |
| --- | --- | ---: | ---: | ---: |
| High quality / low compression | `checkpoint_b00512` | 32.67x | 34.84 | 0.942 |
| Balanced | `checkpoint_b00064` | 93.11x | 33.73 | 0.880 |
| High compression | `checkpoint_b00128` | 165.73x | 31.52 | 0.828 |

Storage comparison shows no useful local-staging gain in this run:

| Storage | Time per image |
| --- | ---: |
| Shared | 143.86 s |
| Local | 143.89 s |

## Files

| File | Use |
| --- | --- |
| `tables/combined_summary.csv` | Machine-readable selected-run summary |
| `tables/combined_summary.md` | Markdown summary table copied from the DeltaAI combined summary |
