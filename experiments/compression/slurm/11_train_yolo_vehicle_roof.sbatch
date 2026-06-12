#!/bin/bash
#SBATCH --job-name=sc26_cdc_yolo
#SBATCH --account=bfod-dtai-gh
#SBATCH --partition=ghx4
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --time=12:00:00
#SBATCH --output=experiments/compression/slurm/logs/yolo_train_%j.log
#SBATCH --error=experiments/compression/slurm/logs/yolo_train_%j.log

set -euo pipefail

if [[ -n "${REPO_DIR:-}" && -f "${REPO_DIR}/experiments/compression/slurm/common_deltaai.sh" ]]; then
  SCRIPT_DIR="${REPO_DIR}/experiments/compression/slurm"
elif [[ -n "${SLURM_SUBMIT_DIR:-}" && -f "${SLURM_SUBMIT_DIR}/experiments/compression/slurm/common_deltaai.sh" ]]; then
  SCRIPT_DIR="${SLURM_SUBMIT_DIR}/experiments/compression/slurm"
else
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi
source "${SCRIPT_DIR}/common_deltaai.sh"

SOURCE_ROOT="${YOLO_SOURCE_ROOT:-${BASE}/data/VehicleAndBuilding_labels}"
DATASET_DIR="${YOLO_DATASET_DIR:-${BASE}/data/yolo_vehicle_roof_20260612}"
RUN_ROOT="${OUT_BASE}/11_train_yolo_vehicle_roof"
MODEL="${YOLO_MODEL:-yolov8s.pt}"
EPOCHS="${YOLO_EPOCHS:-50}"
IMGSZ="${YOLO_IMGSZ:-1280}"
BATCH="${YOLO_BATCH:-4}"
RUN_NAME="${YOLO_RUN_NAME:-vehicle_roof}"
mkdir -p "${RUN_ROOT}"

python -m pip install --user ultralytics --quiet

if [[ "${YOLO_PREPARE_DATASET:-1}" == "1" ]]; then
  PREP_ARGS=(--source_root "${SOURCE_ROOT}" --output_dir "${DATASET_DIR}" --overwrite)
  if [[ "${YOLO_COPY_DATA:-0}" == "1" ]]; then
    PREP_ARGS+=(--copy)
  fi
  if [[ -n "${YOLO_TRAIN_RANGE:-}" ]]; then
    PREP_ARGS+=(--train_range "${YOLO_TRAIN_RANGE}")
  fi
  if [[ -n "${YOLO_VAL_RANGE:-}" ]]; then
    PREP_ARGS+=(--val_range "${YOLO_VAL_RANGE}")
  fi
  if [[ -n "${YOLO_TEST_RANGE:-}" ]]; then
    PREP_ARGS+=(--test_range "${YOLO_TEST_RANGE}")
  fi
  python experiments/compression/prepare_yolo_vehicle_roof_dataset.py "${PREP_ARGS[@]}"
fi

export YOLO_MODEL_PATH="${MODEL}"
export YOLO_DATA_YAML="${DATASET_DIR}/data.yaml"
export YOLO_PROJECT="${RUN_ROOT}/ultralytics_train"
export YOLO_RUN_NAME_EFFECTIVE="${RUN_NAME}"
export YOLO_EPOCHS_EFFECTIVE="${EPOCHS}"
export YOLO_IMGSZ_EFFECTIVE="${IMGSZ}"
export YOLO_BATCH_EFFECTIVE="${BATCH}"

python - <<'PY'
import os
from ultralytics import YOLO

kwargs = {
    "data": os.environ["YOLO_DATA_YAML"],
    "epochs": int(os.environ["YOLO_EPOCHS_EFFECTIVE"]),
    "imgsz": int(os.environ["YOLO_IMGSZ_EFFECTIVE"]),
    "batch": int(os.environ["YOLO_BATCH_EFFECTIVE"]),
    "project": os.environ["YOLO_PROJECT"],
    "name": os.environ["YOLO_RUN_NAME_EFFECTIVE"],
    "exist_ok": True,
}
device = os.environ.get("YOLO_DEVICE", "")
if device:
    kwargs["device"] = device
model = YOLO(os.environ["YOLO_MODEL_PATH"])
model.train(**kwargs)
PY

echo "Done. Training output: ${YOLO_PROJECT}/${YOLO_RUN_NAME_EFFECTIVE}"
