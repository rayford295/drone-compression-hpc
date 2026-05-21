# Yifan Poster Experiment Checklist for 2026-05-24

## Purpose

Finish the SC26 poster-support experiments before Sunday, 2026-05-24. The immediate new request from Jooho is to add poster-ready visual evidence: original image, reconstructed image, hot difference map, pixel-difference histogram, quality metrics, and difference distribution.

The target is a small, defensible package for the poster, not a large raw archive.

## Code Update

The runner now saves one extra visual file for each saved example:

```text
*_poster_panel.png
```

Each panel contains:

- original image
- reconstructed image
- hot difference map
- histogram of pixel differences
- quality metric text block
- difference distribution curve

The helper script can also generate poster panels from existing DeltaAI `visuals/` folders without rerunning the model:

```bash
python experiments/compression/make_poster_panels.py \
  --root /projects/bfod/$USER/cdc-deltaai/output/sc26_compression/20260515_yifan_selected_256_512_n50/03_tiling_sweep \
  --max_panels 4 \
  --max_edge 1200 \
  --overwrite
```

## Experiments to Finish

| Priority | Experiment | Why it matters | Target output |
| --- | --- | --- | --- |
| P0 | Generate poster visual panels from the existing `20260515_yifan_selected_256_512_n50` raw run | Gives Jooho the figure type requested in chat without waiting for a new model run | `*_poster_panel.png` files for no tiling, `256 x 256`, and `512 x 512` |
| P0 | Run a final selected `256 x 256` vs `512 x 512` poster validation | Confirms that the `N=50` result still holds at a larger sample size | `combined_summary.csv`, `combined_summary.md`, and 6 to 8 poster panels |
| P1 | Keep no-tiling reference in the selected run | Gives a baseline for speed, memory, and visual difference | no-tiling row and panel in the same run folder |
| P1 | Package only lightweight outputs into the repo | Makes GitHub easy to review and keeps large raw files on DeltaAI | dated `results/2026-05-24-yifan-poster-visual-qa/` folder |
| P2 | Finish or refresh Jacob's compression-side summary if not already complete | Keeps the poster story connected to compression ratio, speed, scaling, and storage | compression table and one short README summary |

## Recommended Run Order

First update the DeltaAI checkout:

```bash
cd /projects/bfod/$USER/cdc-deltaai/code_tiling_fixed
git pull origin main
```

Generate poster panels from the existing selected run:

```bash
python experiments/compression/make_poster_panels.py \
  --root /projects/bfod/$USER/cdc-deltaai/output/sc26_compression/20260515_yifan_selected_256_512_n50/03_tiling_sweep \
  --max_panels 4 \
  --max_edge 1200 \
  --overwrite
```

Run a small smoke check for the updated panel code:

```bash
sbatch --export=ALL,REPO_DIR=/projects/bfod/$USER/cdc-deltaai/code_tiling_fixed,RUN_STAMP=20260521_yifan_poster_panel_smoke,TILING_SIZES="256",N_IMAGES=2,SAVE_VISUAL_LIMIT=2 experiments/compression/slurm/03_tiling_sweep.sbatch
```

If the smoke run succeeds, run the selected poster validation:

```bash
sbatch --export=ALL,REPO_DIR=/projects/bfod/$USER/cdc-deltaai/code_tiling_fixed,RUN_STAMP=20260522_yifan_poster_256_512_n100,TILING_SIZES="256 512",N_IMAGES=100,SAVE_VISUAL_LIMIT=8 experiments/compression/slurm/03_tiling_sweep.sbatch
```

If queue time is tight, use `N_IMAGES=50` and keep the same `RUN_STAMP` pattern:

```bash
sbatch --export=ALL,REPO_DIR=/projects/bfod/$USER/cdc-deltaai/code_tiling_fixed,RUN_STAMP=20260522_yifan_poster_256_512_n50,TILING_SIZES="256 512",N_IMAGES=50,SAVE_VISUAL_LIMIT=8 experiments/compression/slurm/03_tiling_sweep.sbatch
```

## What to Inspect

Start with:

```bash
cat /projects/bfod/$USER/cdc-deltaai/output/sc26_compression/$RUN_STAMP/03_tiling_sweep/combined_summary.md
```

Then inspect the saved visuals under each run's `visuals/` folder:

| File suffix | Use |
| --- | --- |
| `_comparison.png` | quick original, reconstruction, and heatmap check |
| `_error_heatmap.png` | focused reconstruction-error map |
| `_poster_panel.png` | poster-ready six-panel figure requested by Jooho |

Use `256 x 256` as the recommendation if it keeps the best speed and memory profile and the poster panels show no regular tile-boundary artifacts. Use `512 x 512` as the safer recommendation if `256 x 256` shows visible grid patterns or consistently worse high-error regions.

## GitHub Package to Bring Back

After the final DeltaAI run, copy only lightweight artifacts:

```text
results/2026-05-24-yifan-poster-visual-qa/
├── README.md
├── tables/
│   ├── combined_summary.csv
│   └── combined_summary.md
└── visual_examples_small/
    ├── *_comparison.jpg
    ├── *_error_heatmap.jpg
    └── *_poster_panel.jpg
```

Leave full-resolution reconstructions, full logs, checkpoints, and raw `visuals/` folders on DeltaAI.

## Sunday Deliverable

By Sunday, 2026-05-24, the minimum deliverable is:

- one selected table comparing no tiling, `256 x 256`, and `512 x 512`
- at least two poster panels for representative images
- one short recommendation: `256 x 256` for speed and memory, or `512 x 512` if visual artifacts appear
- a pushed GitHub commit with code, runbook, and lightweight result package if the final run has finished
