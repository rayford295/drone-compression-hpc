#!/bin/bash
#SBATCH --job-name=sc26_cdc_sam
#SBATCH --account=bfod-dtai-gh
#SBATCH --partition=ghx4
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=96G
#SBATCH --time=08:00:00
#SBATCH --output=experiments/compression/slurm/logs/sam_%j.log
#SBATCH --error=experiments/compression/slurm/logs/sam_%j.log

set -euo pipefail

if [[ -n "${REPO_DIR:-}" && -f "${REPO_DIR}/experiments/compression/slurm/common_deltaai.sh" ]]; then
  SCRIPT_DIR="${REPO_DIR}/experiments/compression/slurm"
elif [[ -n "${SLURM_SUBMIT_DIR:-}" && -f "${SLURM_SUBMIT_DIR}/experiments/compression/slurm/common_deltaai.sh" ]]; then
  SCRIPT_DIR="${SLURM_SUBMIT_DIR}/experiments/compression/slurm"
else
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi
source "${SCRIPT_DIR}/common_deltaai.sh"

: "${SAM_CHECKPOINT:?Set SAM_CHECKPOINT to a Meta Segment Anything checkpoint.}"
: "${SAM_PROMPT_LABEL_DIR:?Set SAM_PROMPT_LABEL_DIR to a YOLO-format prompt label directory.}"
: "${SAM_IMAGE_SETS:?Set SAM_IMAGE_SETS as label=/path label=/path.}"

RUN_ROOT="${OUT_BASE}/09_sam_mask_impact"
mkdir -p "${RUN_ROOT}"

if [[ "${SAM_INSTALL_SEGMENT_ANYTHING:-0}" == "1" ]]; then
  python -m pip install --user git+https://github.com/facebookresearch/segment-anything.git --quiet
fi

SAM_ARGS=()
if [[ -n "${SAM_DEVICE:-}" ]]; then
  SAM_ARGS+=(--device "${SAM_DEVICE}")
fi
if [[ -n "${SAM_PROMPT_CLASSES:-}" ]]; then
  SAM_ARGS+=(--prompt_classes ${SAM_PROMPT_CLASSES})
fi
if [[ -n "${SAM_LIMIT_IMAGES:-}" ]]; then
  SAM_ARGS+=(--limit_images "${SAM_LIMIT_IMAGES}")
fi
if [[ "${SAM_RECURSIVE:-0}" == "1" ]]; then
  SAM_ARGS+=(--recursive)
fi
if [[ "${SAM_MULTIMASK_OUTPUT:-0}" == "1" ]]; then
  SAM_ARGS+=(--multimask_output)
fi
if [[ "${SAM_COMPUTE_BOUNDARY:-0}" == "1" ]]; then
  SAM_ARGS+=(--compute_boundary)
fi

python experiments/compression/evaluate_sam_mask_impact.py \
  --sam_checkpoint "${SAM_CHECKPOINT}" \
  --model_type "${SAM_MODEL_TYPE:-vit_h}" \
  --prompt_label_dir "${SAM_PROMPT_LABEL_DIR}" \
  --image_sets ${SAM_IMAGE_SETS} \
  --baseline_config "${SAM_BASELINE_CONFIG:-original}" \
  --prompt_batch_size "${SAM_PROMPT_BATCH_SIZE:-8}" \
  --box_expansion "${SAM_BOX_EXPANSION:-0.0}" \
  --min_mask_area "${SAM_MIN_MASK_AREA:-1}" \
  --boundary_dilation "${SAM_BOUNDARY_DILATION:-2}" \
  "${SAM_ARGS[@]}" \
  --output_dir "${RUN_ROOT}"
