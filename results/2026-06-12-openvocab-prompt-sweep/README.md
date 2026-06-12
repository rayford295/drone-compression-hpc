# YOLO-World Open-Vocabulary Prompt Sweep, N50, 2026-06-12

This package records the sanity gate for using YOLO-World as the vehicle and building
detector in Experiment 4b.

Purpose:

- Use the human-labeled vehicle and building annotations as the official ground truth.
- Test whether YOLO-World can detect both classes on the original N50 images before
  comparing original and reconstructed images.
- Decide whether the open-vocabulary detector is suitable for the full compression-impact
  experiment.

## DeltaAI Runs

| Item | Value |
|------|-------|
| System | DeltaAI GH200 |
| Code commit | `05591bb` |
| Model | `yolov8x-worldv2.pt` |
| Test split | `100_0005_0001` to `100_0005_0050` |
| Ground truth | human labels, vehicle class `0`, building class `1` |
| GT boxes | `1013` vehicle, `1201` building |
| Original gate run | `20260612_ovdet_veh_bldg_n50_original_gate_retry1` |
| Prompt sweep runs | `20260612_ovdet_prompt_{prompt}_{conf}_n50` |

Raw images, predictions, logs, downloaded model weights, and full DeltaAI output folders
remain on DeltaAI storage. This GitHub package stores only lightweight summary tables.

## Prompt Sweep Result

The baseline prompt pair was `vehicle building`. It worked well for vehicles but failed
for buildings:

| Prompt pair | Conf | Class | AP@0.5 | Precision | Recall | F1 | Predictions |
|-------------|------|-------|-------:|----------:|-------:|---:|------------:|
| vehicle building | 0.02 | vehicle | 0.835927 | 0.770979 | 0.870681 | 0.817803 | 1144 |
| vehicle building | 0.02 | building | 0.021027 | 0.606557 | 0.030808 | 0.058637 | 61 |

The follow-up prompt sweep tested `roof`, `rooftop`, `house`, `structure`, and
`warehouse` as building substitutes at confidence thresholds `0.02` and `0.005`.
None produced usable building detection. The best building row was:

| Prompt pair | Conf | Building AP@0.5 | Building Precision | Building Recall | Building F1 | Building Predictions |
|-------------|------|----------------:|-------------------:|----------------:|------------:|---------------------:|
| vehicle rooftop | 0.005 | 0.006916 | 0.260417 | 0.020816 | 0.038551 | 96 |

For comparison, the original `building` prompt had AP@0.5 `0.021027` and recall
`0.030808`, which is still too low for a compression-impact study.

## Decision

YOLO-World should not be used as the final detector for the vehicle and building
compression-impact table. The detector recognizes vehicles well, but it does not detect
top-down drone-view buildings reliably from open-vocabulary prompts. A full comparison
with this detector would confound compression effects with detector failure.

Recommended next step:

- Train a supervised two-class YOLO detector on the human labels.
- Use images `100_0005_0051` to `100_0005_0100` for training and validation.
- Keep images `100_0005_0001` to `100_0005_0050` as the fixed test split.
- Run the trained detector on Original, High quality reconstruction, Balanced
  reconstruction, and Max compression reconstruction.

The resulting table can then support the intended columns:

| Configuration | mAP@0.5 | mAP@0.5:0.95 | Precision | Recall | F1 | GT | Predictions |
|---------------|--------:|-------------:|----------:|-------:|---:|---:|------------:|

## Files

| File | Description |
|------|-------------|
| `tables/prompt_sweep_per_class.csv` | Full per-class results for the baseline prompt and all prompt-sweep runs. |
| `tables/building_prompt_summary.csv` | Building-only comparison used for model-choice decisions. |
