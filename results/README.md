# Results Archive

This folder stores lightweight, report-ready experiment outputs that can be committed to GitHub.

Large raw outputs, full-resolution reconstructed PNGs, logs, model weights, and full datasets should stay on DeltaAI under `/projects/bfod/$USER/cdc-deltaai/`.

## Index

| Folder | Cycle | Owner | Purpose |
|--------|-------|-------|---------|
| `2026-04-26-reconstruction/` | 2026-04-25 to 2026-05-01 meeting cycle | Yifan | Reconstruction profiling, step sweep, batch-size decision, plots, reports, and visual examples |
| `2026-04-28-h200-reconstruction/` | 2026-04-28 hardware comparison extension | Yifan | Delta H200 batch pilot and quick reconstruction step sweep |
| `2026-05-12-yifan-tiling-smoke/` | 2026-05-12 weekly update | Yifan | DeltaAI GH200 tiling smoke test for 512, 1024, and 2048 patch sizes |
| `2026-05-12-yifan-tiling-pilot/` | 2026-05-12 weekly update | Yifan | DeltaAI GH200 `N_IMAGES=8` tiling pilot for 512, 1024, and 2048 patch sizes |
| `2026-05-15-yifan-selected-256-512-n50/` | 2026-05-15 selected comparison | Yifan | DeltaAI GH200 `N_IMAGES=50` comparison of 256 and 512 tiling with heatmap-ready metrics |
| `2026-05-22-yifan-poster-visual-qa/` | 2026-05-22 poster visual QA | Yifan | Poster-ready original/reconstruction/hot-difference panels for no tiling, 256 tiling, and 512 tiling |
| `2026-05-22-jacob-compression-n20/` | 2026-05-22 compression-side validation | Jacob / Yifan | DeltaAI GH200 `N_IMAGES=20` compression baseline, resolution, batch, checkpoint, scaling, and storage comparison |
| `2026-06-05-tradeoff-smoke/` | 2026-06-05 tradeoff smoke | Yifan | DeltaAI GH200 `N_IMAGES=8` compression-setting x tile-size matrix for high-quality, balanced, and high-compression checkpoints |
| `2026-06-05-tradeoff-n50-lpips/` | 2026-06-05 formal tradeoff validation | Yifan | DeltaAI GH200 `N_IMAGES=50` compression-setting x tile-size matrix with LPIPS for poster/manuscript tradeoff selection |
| `2026-06-06-detection-label-selftest/` | 2026-06-06 detection pipeline sanity check | Yifan | DeltaAI GH200 self-test confirming the N8 draft YOLO labels and detection evaluator run end to end |
| `2026-06-06-detection-coco-vehicle-n8/` | 2026-06-06 detection pilot | Yifan | DeltaAI GH200 COCO YOLOv8x vehicle-detection pilot comparing original, balanced, and maximum-compression reconstructions |
| `2026-06-06-detection-coco-vehicle-n50/` | 2026-06-06 detection pilot | Yifan | DeltaAI GH200 N50 COCO YOLOv8x vehicle-detection pilot comparing original, high-quality, balanced, and maximum-compression reconstructions |
| `2026-06-06-sam-mask-impact-n50/` | 2026-06-06 zero-shot segmentation pilot | Yifan | DeltaAI GH200 N50 Meta SAM mask-stability pilot comparing original, balanced, and maximum-compression reconstructions |
| `2026-06-12-openvocab-prompt-sweep/` | 2026-06-12 Experiment 4b model gate | Yifan | DeltaAI GH200 YOLO-World prompt sweep showing vehicle detection works but open-vocabulary building detection is not suitable for the final compression-impact table |
| `2026-06-12-sam-vehicle-roof-human-n50/` | 2026-06-12 SAM human-label add-on | Yifan | DeltaAI GH200 N50 SAM mask-stability comparison for human vehicle and roof prompts across original and reconstructed image sets |

## Hardware Scope

The first committed reconstruction result set is DeltaAI GH200. Delta is a separate NCSA system and has visible H200 partitions under the `bfod-delta-gpu` account:

- `gpuH200x8`
- `gpuH200x8-interactive`

Delta H200 results are stored separately under `2026-04-28-h200-reconstruction/` so they are not mixed with the 2026-04-26 DeltaAI GH200 result set.

## Convention for Future Results

Use one dated folder per experiment cycle:

```text
results/YYYY-MM-DD-short-description/
├── plots/
├── reports/
├── tables/
└── visual_examples_small/
```

Commit small summaries, CSVs, and slide-ready compressed images. Keep full-resolution generated outputs on DeltaAI unless they are specifically needed in the repository.
