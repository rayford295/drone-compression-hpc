# Data Setup on DeltaAI

The dataset (100_0005, ~3.18 GB) and model weights are **not** stored in this repository.
Upload them manually to DeltaAI before running jobs.

## 1. Upload data from your local machine

```bash
# From your local machine (Mac terminal)
scp -r /path/to/100_0005 yyang48@dtai-login.delta.ncsa.illinois.edu:/projects/YOUR_PROJECT/data/
```

Or use rsync (faster for large files, resumable):
```bash
rsync -avP /path/to/100_0005 yyang48@dtai-login.delta.ncsa.illinois.edu:/projects/YOUR_PROJECT/data/
```

## 2. Download model weights on DeltaAI

SSH into DeltaAI, then:
```bash
mkdir -p /projects/YOUR_PROJECT/weights
cd /projects/YOUR_PROJECT/weights

# Install huggingface_hub if needed
pip install huggingface_hub

# Download weights
python -c "
from huggingface_hub import hf_hub_download
hf_hub_download(repo_id='rhyang/CDC_params', filename='epsilon_lpips0.9.pt', local_dir='.')
hf_hub_download(repo_id='rhyang/CDC_params', filename='epsilon_lpips0.0.pt', local_dir='.')
"
```

## 3. Update paths in scripts/run_deltaai.sh

Edit the following lines with your actual paths:
- `--account=YOUR_ALLOCATION`
- `DATA_DIR=/projects/YOUR_PROJECT/data/100_0005`
- `CKPT_DIR=/projects/YOUR_PROJECT/weights`

## 4. Optional detection pilot labels

A small vehicle-detection pilot label package is tracked in:

```text
data/detection_pilot/labels_yolo_vehicle_n8/
```

It contains draft YOLO labels for `100_0005_0001.JPG` through `100_0005_0008.JPG`.
These labels are for pipeline validation and should be reviewed before formal mAP reporting.

An expanded auto-assisted draft package is tracked in:

```text
data/detection_pilot/labels_yolo_vehicle_n50_draft/
```

It contains draft YOLO labels for `100_0005_0001.JPG` through `100_0005_0050.JPG`.
The first 8 images reuse the manual draft labels. Images 9-50 use COCO YOLOv8x `car`, `bus`, and `truck` candidates mapped to `0 vehicle` at confidence `0.40`. Review is required before formal mAP reporting.

To stage them on DeltaAI:

```bash
mkdir -p /projects/bfod/$USER/cdc-deltaai/data/labels_yolo_vehicle_n8
rsync -av data/detection_pilot/labels_yolo_vehicle_n8/labels/ \
  /projects/bfod/$USER/cdc-deltaai/data/labels_yolo_vehicle_n8/

mkdir -p /projects/bfod/$USER/cdc-deltaai/data/labels_yolo_vehicle_n50_draft
rsync -av data/detection_pilot/labels_yolo_vehicle_n50_draft/labels/ \
  /projects/bfod/$USER/cdc-deltaai/data/labels_yolo_vehicle_n50_draft/
```

Use the staged folder as:

```bash
DETECTION_GT_DIR=/projects/bfod/$USER/cdc-deltaai/data/labels_yolo_vehicle_n8
# or, for the expanded draft:
DETECTION_GT_DIR=/projects/bfod/$USER/cdc-deltaai/data/labels_yolo_vehicle_n50_draft
```
