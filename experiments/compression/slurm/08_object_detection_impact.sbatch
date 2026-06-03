#!/bin/bash
#SBATCH --job-name=sc26_cdc_detect
#SBATCH --account=bfod-dtai-gh
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

if [[ -n "${DETECTION_MODEL:-}" ]]; then
  : "${DETECTION_IMAGE_SETS:?Set DETECTION_IMAGE_SETS as label=/path label=/path when DETECTION_MODEL is used.}"
  python experiments/compression/evaluate_object_detection_impact.py \
    --ground_truth_dir "${DETECTION_GT_DIR}" \
    --detector_model "${DETECTION_MODEL}" \
    --image_sets ${DETECTION_IMAGE_SETS} \
    --imgsz "${DETECTION_IMGSZ:-1280}" \
    --conf "${DETECTION_CONF:-0.001}" \
    --output_dir "${RUN_ROOT}"
else
  : "${DETECTION_PREDICTION_DIRS:?Set DETECTION_PREDICTION_DIRS as label=/path label=/path, or set DETECTION_MODEL.}"
  python experiments/compression/evaluate_object_detection_impact.py \
    --ground_truth_dir "${DETECTION_GT_DIR}" \
    --prediction_dirs ${DETECTION_PREDICTION_DIRS} \
    --output_dir "${RUN_ROOT}"
fi
