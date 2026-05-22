# 2026-05-22 Yifan Poster Visual QA Panels

This folder records lightweight poster-ready visual QA panels for the SC26 CDC tiling comparison. The panels respond to Jooho's request to show original image, reconstructed image, and a hot difference map, with supporting pixel-difference histogram and quality metrics.

## Scope

- Source run: `20260515_yifan_selected_256_512_n50`
- System: DeltaAI GH200, partition `ghx4`
- Input: representative image `100_0005_0001`
- Cases: no tiling reference, `256 x 256` tiling, and `512 x 512` tiling
- Source artifacts: lightweight `*_comparison.jpg` panels already committed under `results/2026-05-15-yifan-selected-256-512-n50/visual_examples_small/`

The full raw visual archive remains on DeltaAI:

```text
/projects/bfod/$USER/cdc-deltaai/output/sc26_compression/20260515_yifan_selected_256_512_n50/03_tiling_sweep/
```

## Files

| File | Use |
| --- | --- |
| `visual_examples_small/100_0005_0001_no_tiling_poster_panel.jpg` | No-tiling reference poster panel |
| `visual_examples_small/100_0005_0001_tile256_poster_panel.jpg` | `256 x 256` tiling poster panel |
| `visual_examples_small/100_0005_0001_tile512_poster_panel.jpg` | `512 x 512` tiling poster panel |

## Note

These committed panels are lightweight previews generated from the existing GitHub-ready comparison images. For print-quality export, regenerate panels on DeltaAI from the raw `visuals/` folders:

```bash
python experiments/compression/make_poster_panels.py \
  --root /projects/bfod/$USER/cdc-deltaai/output/sc26_compression/20260515_yifan_selected_256_512_n50/03_tiling_sweep \
  --max_panels 4 \
  --max_edge 1200 \
  --overwrite
```
