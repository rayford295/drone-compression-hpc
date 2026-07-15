#!/bin/bash
#SBATCH --job-name=sc26_cdc_tradeoff
#SBATCH --account=YOUR_ALLOCATION
#SBATCH --partition=ghx4
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=18:00:00
#SBATCH --output=experiments/compression/slurm/logs/tradeoff_%j.log
#SBATCH --error=experiments/compression/slurm/logs/tradeoff_%j.log

set -euo pipefail

if [[ -n "${REPO_DIR:-}" && -f "${REPO_DIR}/experiments/compression/slurm/common_deltaai.sh" ]]; then
  SCRIPT_DIR="${REPO_DIR}/experiments/compression/slurm"
elif [[ -n "${SLURM_SUBMIT_DIR:-}" && -f "${SLURM_SUBMIT_DIR}/experiments/compression/slurm/common_deltaai.sh" ]]; then
  SCRIPT_DIR="${SLURM_SUBMIT_DIR}/experiments/compression/slurm"
else
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi
source "${SCRIPT_DIR}/common_deltaai.sh"

RUN_ROOT="${OUT_BASE}/07_compression_tile_tradeoff"
mkdir -p "${RUN_ROOT}"

role_spec() {
  case "$1" in
    high_quality)
      echo "high_quality checkpoint_b00512 ${CKPT_B00512} ${LPIPS_B00512}"
      ;;
    balanced)
      echo "balanced checkpoint_b00064 ${CKPT_B00064} ${LPIPS_B00064}"
      ;;
    high_compression)
      echo "high_compression checkpoint_b00128 ${CKPT_B00128} ${LPIPS_B00128}"
      ;;
    baseline)
      echo "baseline checkpoint_b02048 ${CKPT_B02048} ${LPIPS_B02048}"
      ;;
    *)
      echo "Unknown TRADEOFF_COMPRESSION_ROLES entry: $1" >&2
      exit 2
      ;;
  esac
}

echo ">>> Compression x tile-size practical tradeoff subset"
echo "Roles     : ${TRADEOFF_COMPRESSION_ROLES}"
echo "Tile sizes: ${TRADEOFF_TILE_SIZES}"
echo "N_IMAGES  : ${N_IMAGES}"
echo "LPIPS     : ${COMPUTE_LPIPS:-0}"

for ROLE in ${TRADEOFF_COMPRESSION_ROLES}; do
  read -r ROLE_LABEL CKPT_LABEL CKPT_PATH LPIPS_VALUE <<< "$(role_spec "${ROLE}")"

  if [[ "${TRADEOFF_INCLUDE_NO_TILE}" == "1" ]]; then
    run_sc26_compression \
      --ckpt "${CKPT_PATH}" \
      --img_dir "${IMG_DIR}" \
      --out_dir "${RUN_ROOT}/${ROLE_LABEL}_tile_none" \
      --lpips_weight "${LPIPS_VALUE}" \
      --experiment_name "tradeoff_${ROLE_LABEL}_tile_none" \
      --compression_setting "${ROLE_LABEL}_${CKPT_LABEL}" \
      --resolution_label "native_full_resolution" \
      --max_edge 0 \
      --batch_size 1 \
      --n_images "${N_IMAGES}" \
      --start_index "${START_INDEX}" \
      --n_denoise_step "${N_DENOISE_STEP}" \
      --gamma "${GAMMA}" \
      --save_visual_limit "${SAVE_VISUAL_LIMIT}" \
      --comparison_max_edge "${COMPARISON_MAX_EDGE}" \
      --storage_label "shared" \
      --notes "Compression x tile tradeoff: no-tiling reference for ${ROLE_LABEL}."
  fi

  for TILE_SIZE in ${TRADEOFF_TILE_SIZES}; do
    CURRENT_TILE_BATCH_SIZE="${TILE_BATCH_SIZE}"
    if [[ "${TILE_SIZE}" == "256" ]]; then
      CURRENT_TILE_BATCH_SIZE="${TILE_BATCH_SIZE_256}"
    fi

    run_sc26_compression \
      --ckpt "${CKPT_PATH}" \
      --img_dir "${IMG_DIR}" \
      --out_dir "${RUN_ROOT}/${ROLE_LABEL}_tile_${TILE_SIZE}" \
      --lpips_weight "${LPIPS_VALUE}" \
      --experiment_name "tradeoff_${ROLE_LABEL}_tile_${TILE_SIZE}" \
      --compression_setting "${ROLE_LABEL}_${CKPT_LABEL}" \
      --resolution_label "native_full_resolution" \
      --max_edge 0 \
      --batch_size "${CURRENT_TILE_BATCH_SIZE}" \
      --tile_size "${TILE_SIZE}" \
      --tile_batch_size "${CURRENT_TILE_BATCH_SIZE}" \
      --n_images "${N_IMAGES}" \
      --start_index "${START_INDEX}" \
      --n_denoise_step "${N_DENOISE_STEP}" \
      --gamma "${GAMMA}" \
      --save_visual_limit "${SAVE_VISUAL_LIMIT}" \
      --comparison_max_edge "${COMPARISON_MAX_EDGE}" \
      --storage_label "shared" \
      --notes "Compression x tile tradeoff: ${ROLE_LABEL} checkpoint with ${TILE_SIZE} x ${TILE_SIZE} tiling."
  done
done

summarize_sc26_compression "${RUN_ROOT}"
