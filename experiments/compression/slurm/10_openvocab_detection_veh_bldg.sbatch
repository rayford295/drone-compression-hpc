#!/bin/bash
#SBATCH --job-name=sc26_cdc_ovdet
#SBATCH --account=YOUR_ALLOCATION
#SBATCH --partition=ghx4
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=experiments/compression/slurm/logs/ovdet_%j.log
#SBATCH --error=experiments/compression/slurm/logs/ovdet_%j.log

# Experiment 4b: open-vocabulary (YOLO-World) detection of vehicle + building on
# Original vs CDC-reconstructed image sets, scored against the human 2-class GT.
#
# Required:
#   OPENVOCAB_IMAGE_SETS="original=/path high_quality_512=/path balanced_256=/path max_compression_256=/path"
# Common (have sensible defaults):
#   OPENVOCAB_VEHICLE_DIR   default: data/detection_labels/vehicle/labels
#   OPENVOCAB_BUILDING_DIR  default: data/detection_labels/building/labels
#   OPENVOCAB_PROMPTS       default: "vehicle building"   (order = class ids: vehicle=0 building=1)
#   OPENVOCAB_MODEL         default: yolov8x-worldv2.pt
#   OPENVOCAB_CONF          default: 0.02
#   OPENVOCAB_IMGSZ         default: 1280
#   OPENVOCAB_MAX_IMAGES    default: 50  (matches the N50 reconstructed image sets)
#   DETECTION_INSTALL_ULTRALYTICS=1  to pip install ultralytics and YOLO-World text deps on the node

set -euo pipefail

if [[ -n "${REPO_DIR:-}" && -f "${REPO_DIR}/experiments/compression/slurm/common_deltaai.sh" ]]; then
  SCRIPT_DIR="${REPO_DIR}/experiments/compression/slurm"
elif [[ -n "${SLURM_SUBMIT_DIR:-}" && -f "${SLURM_SUBMIT_DIR}/experiments/compression/slurm/common_deltaai.sh" ]]; then
  SCRIPT_DIR="${SLURM_SUBMIT_DIR}/experiments/compression/slurm"
else
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi
source "${SCRIPT_DIR}/common_deltaai.sh"

: "${OPENVOCAB_IMAGE_SETS:?Set OPENVOCAB_IMAGE_SETS as label=/path label=/path (original + reconstructed sets).}"

VEHICLE_DIR="${OPENVOCAB_VEHICLE_DIR:-data/detection_labels/vehicle/labels}"
BUILDING_DIR="${OPENVOCAB_BUILDING_DIR:-data/detection_labels/building/labels}"
PROMPTS="${OPENVOCAB_PROMPTS:-vehicle building}"
MODEL="${OPENVOCAB_MODEL:-yolov8x-worldv2.pt}"
CONF="${OPENVOCAB_CONF:-0.02}"
IMGSZ="${OPENVOCAB_IMGSZ:-1280}"
MAX_IMAGES="${OPENVOCAB_MAX_IMAGES:-50}"

RUN_ROOT="${OUT_BASE}/10_openvocab_detection_veh_bldg"
GT_DIR="${RUN_ROOT}/gt_vehicle_building"
PRED_ROOT="${RUN_ROOT}/predictions"
mkdir -p "${RUN_ROOT}" "${PRED_ROOT}"

if [[ "${DETECTION_INSTALL_ULTRALYTICS:-0}" == "1" ]]; then
  python -m pip install --user ultralytics --quiet
  python -c "import clip" >/dev/null 2>&1 || \
    python -m pip install --user ftfy regex tqdm git+https://github.com/openai/CLIP.git --quiet
fi

echo "== Step 1: build 2-class ground truth (vehicle=0, building=1) =="
GT_ARGS=()
if [[ -n "${MAX_IMAGES}" ]]; then
  GT_ARGS+=(--max_images "${MAX_IMAGES}")
fi
python experiments/compression/build_detection_gt_vehicle_building.py \
  --vehicle_dir "${VEHICLE_DIR}" \
  --building_dir "${BUILDING_DIR}" \
  --output_dir "${GT_DIR}" \
  "${GT_ARGS[@]}"

echo "== Step 2: run open-vocab detection on each image set =="
PRED_ARGS=()
for set_spec in ${OPENVOCAB_IMAGE_SETS}; do
  label="${set_spec%%=*}"
  img_dir="${set_spec#*=}"
  pred_dir="${PRED_ROOT}/${label}"
  echo "--- ${label}: ${img_dir} ---"
  python experiments/compression/run_open_vocab_detection.py \
    --image_dir "${img_dir}" \
    --output_dir "${pred_dir}" \
    --classes ${PROMPTS} \
    --model "${MODEL}" \
    --conf "${CONF}" \
    --imgsz "${IMGSZ}" \
    ${OPENVOCAB_DEVICE:+--device ${OPENVOCAB_DEVICE}}
  PRED_ARGS+=("${label}=${pred_dir}")
done

echo "== Step 3: evaluate (per-class + overall mAP@0.5, mAP@0.5:0.95, P, R, F1) =="
python experiments/compression/evaluate_object_detection_impact.py \
  --ground_truth_dir "${GT_DIR}" \
  --prediction_dirs "${PRED_ARGS[@]}" \
  --restrict_predictions_to_gt \
  --output_dir "${RUN_ROOT}"

echo "Done. Results in ${RUN_ROOT} (detection_summary.csv / detection_per_class.csv)."
