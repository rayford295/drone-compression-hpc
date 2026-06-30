# SC26 CDC Figure Panels

This folder contains GitHub-ready visual summaries generated from committed
result tables in `results/`.

| File | Use |
| --- | --- |
| `sc26_compute_platform_evidence_scope.png` | Platform/evidence table showing what is measured in the repository and what still needs hardware telemetry. |
| `sc26_cdc_performance_dashboard.png` | Four-panel dashboard for runtime, peak GPU memory, compression-quality tradeoff, and human-label detection. |
| `sc26_gh200_h200_hardware_comparison.png` | GH200 vs H200 reconstruction comparison from matched step sweeps. |
| `sc26_bottleneck_proxy_heatmap.png` | Bottleneck proxy heatmap from available metrics. This is not a hardware telemetry plot. |

Regenerate:

```bash
python3 scripts/generate_sc26_figures.py
```
