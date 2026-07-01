# SC26 CDC Figure Panels

This folder contains GitHub-ready visual summaries generated from committed
result tables in `results/`.

| File | Use |
| --- | --- |
| `sc26_compute_platform_evidence_scope.png` | Platform/evidence table showing what is measured in the repository and what still needs hardware telemetry. |
| `sc26_cdc_performance_dashboard.png` | Four-panel dashboard for runtime, peak GPU memory, compression-quality tradeoff, and human-label detection. |
| `sc26_gh200_h200_hardware_comparison.png` | GH200 vs H200 reconstruction comparison from matched step sweeps. |
| `sc26_bottleneck_proxy_heatmap.png` | Bottleneck proxy heatmap from available metrics. This is not a hardware telemetry plot. |
| `sc26_qualitative_256_512_visual_comparison.png` | Poster-ready qualitative image comparison for 256 x 256 and 512 x 512 tiling, without histogram or curve panels. |

Regenerate:

```bash
python3 scripts/generate_sc26_figures.py
python3 scripts/generate_qualitative_visual_panel.py
```
