# CDC Drone-Imagery Compression on GPU Supercomputers

This repository supports an SC26 poster study on high-resolution drone imagery,
lossy compression, tiled diffusion reconstruction, and downstream inspection on
GPU supercomputers.

The project does not propose a new compression algorithm. It evaluates an
existing conditional diffusion compression (CDC) workflow as a data-centric HPC
workload: raw drone imagery creates storage and transfer pressure, while
diffusion reconstruction creates GPU-memory and throughput pressure. The main
question is which operating point makes full-resolution drone imagery practical
for repeated analysis on NCSA DeltaAI GH200.

## Key Finding

For the current Galveston drone-image workload, the best operating point is:

```text
balanced checkpoint b00064 + 256 x 256 tiled reconstruction
```

This setting keeps full-resolution imagery usable while reducing the cost of
reconstruction:

| Setting | Sec/img | Img/hr | Peak GPU | Compression | F1 | Roof IoU |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| High quality 512 | 88.51 | 40.7 | 2.96 GB | 29.73x | 0.8805 | 0.9001 |
| Balanced 256 | 79.34 | 45.4 | 1.57 GB | 79.98x | 0.8705 | 0.8989 |
| Max compression 256 | 78.91 | 45.6 | 1.57 GB | 139.89x | 0.8679 | 0.8956 |

Compared with full-image balanced reconstruction, balanced 256 tiling cuts peak
GPU memory from about 52 GB to about 1.6 GB and reduces runtime from about
143 seconds to about 79 seconds per image.

## What Is in This Repository

The repository contains code, runbooks, and GitHub-safe result summaries for a
measured systems study of CDC reconstruction on HPC hardware.

| Path | Purpose |
| --- | --- |
| `experiments/compression/` | Compression, reconstruction, detection, SAM, and summarization workflows. |
| `results/` | CSV tables, summaries, and small visual examples from completed runs. |
| `imgs/` | Public-facing figure panels for posters and summaries. |
| `paper/` | Manuscript and SC26 submission materials. |
| `docs/` | Internal runbooks, dated plans, and archived project notes. |
| `xparam/`, `epsilonparam/` | CDC-derived model code paths used by the experiments. |

## Public Figures

Selected figure panels are available in `imgs/`:

- `sc26_cdc_performance_dashboard.png`
- `sc26_gh200_h200_hardware_comparison.png`
- `sc26_bottleneck_proxy_heatmap.png`
- `sc26_qualitative_256_512_visual_comparison.png`
- `sc26_compute_platform_evidence_scope.png`

These figures are generated from committed result tables using:

```bash
python3 scripts/generate_sc26_figures.py
python3 scripts/generate_qualitative_visual_panel.py
```

## Main Result Packages

Most readers should start with these result folders:

| Folder | Contents |
| --- | --- |
| `results/2026-06-05-tradeoff-n50-lpips/` | Main N50 compression-setting x tile-size matrix with LPIPS. |
| `results/2026-06-12-yolo-vehicle-roof-human-n50/` | Human-label vehicle and roof detection evaluation. |
| `results/2026-06-12-sam-vehicle-roof-human-n50/` | SAM vehicle and roof mask-stability evaluation. |
| `results/2026-04-28-h200-reconstruction/` | Delta H200 quick reconstruction comparison. |
| `results/2026-04-26-reconstruction/` | Initial DeltaAI GH200 reconstruction profiling. |

See `results/README.md` for the full archive index.

## Data Boundary

This repository tracks source code, scripts, summary tables, and small
GitHub-safe visual examples. It does not track raw drone-image collections,
full-resolution reconstructed outputs, large model checkpoints, detector
weights, local caches, or full HPC output directories.

The result tables are intended to make the systems story auditable without
publishing private or oversized data artifacts.

## Citation

If you use this repository, please cite the corresponding SC26 poster or project
paper once available.
