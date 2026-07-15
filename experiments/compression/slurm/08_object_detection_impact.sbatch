#!/bin/bash
#SBATCH --job-name=sc26_cdc_detect
#SBATCH --account=YOUR_ALLOCATION
#SBATCH --partition=ghx4
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=experiments/compression/slurm/logs/detection_%j.log
#SBATCH --error=experiments/compression/slurm/logs/detection_%j.log

set -euo pipefail

if [[ -n "${REPO_DIR:-}" && -f "${REPO_DIR}/experiments/compression/slurm/common_deltaai.sh" ]]; then
  SCRIPT_DIR="${REPO_DIR}/experiments/compression/slurm"
elif [[ -n "${SLURM_SUBMIT_DIR:-}" && -f "${SLURM_SUBMIT_DIR}/experiments/compression/slurm/common_deltaai.sh" ]]; then
  SCRIPT_DIR="${SLURM_SUBMIT_DIR}/experiments/compression/slurm"
else
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi
source "${SCRIPT_DIR}/common_deltaai.sh"

: "${DETECTION_GT_DIR:?Set DETECTION_GT_DIR to a YOLO-format ground-truth label directory.}"

RUN_ROOT="${OUT_BASE}/08_object_detection_impact"
mkdir -p "${RUN_ROOT}"

if [[ "${DETECTION_INSTALL_ULTRALYTICS:-0}" == "1" ]]; then
  python -m pip install --user ultralytics --quiet
fi

COMMON_ARGS=()
if [[ -n "${DETECTION_CLASS_MAP:-}" ]]; then
  COMMON_ARGS+=(--prediction_class_map ${DETECTION_CLASS_MAP})
fi
if [[ "${DETECTION_DROP_UNMAPPED:-0}" == "1" ]]; then
  COMMON_ARGS+=(--drop_unmapped_prediction_classes)
fi
if [[ "${DETECTION_RESTRICT_TO_GT:-0}" == "1" ]]; then
  COMMON_ARGS+=(--restrict_predictions_to_gt)
fi

if [[ -n "${DETECTION_MODEL:-}" ]]; then
  : "${DETECTION_IMAGE_SETS:?Set DETECTION_IMAGE_SETS as label=/path label=/path when DETECTION_MODEL is used.}"
  MODEL_ARGS=()
  if [[ -n "${DETECTION_CLASSES:-}" ]]; then
    MODEL_ARGS+=(--detector_classes ${DETECTION_CLASSES})
  fi
  if [[ -n "${DETECTION_DEVICE:-}" ]]; then
    MODEL_ARGS+=(--device "${DETECTION_DEVICE}")
  fi
  python experiments/compression/evaluate_object_detection_impact.py \
    --ground_truth_dir "${DETECTION_GT_DIR}" \
    --detector_model "${DETECTION_MODEL}" \
    --image_sets ${DETECTION_IMAGE_SETS} \
    --imgsz "${DETECTION_IMGSZ:-1280}" \
    --conf "${DETECTION_CONF:-0.001}" \
    "${MODEL_ARGS[@]}" \
    "${COMMON_ARGS[@]}" \
    --output_dir "${RUN_ROOT}"
else
  : "${DETECTION_PREDICTION_DIRS:?Set DETECTION_PREDICTION_DIRS as label=/path label=/path, or set DETECTION_MODEL.}"
  python experiments/compression/evaluate_object_detection_impact.py \
    --ground_truth_dir "${DETECTION_GT_DIR}" \
    --prediction_dirs ${DETECTION_PREDICTION_DIRS} \
    "${COMMON_ARGS[@]}" \
    --output_dir "${RUN_ROOT}"
fi
