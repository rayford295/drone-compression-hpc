# Detection Labels — Vehicle & Building (Human-Labeled)

Human-annotated YOLO-format object detection labels for the `100_0005` DJI image set,
covering two object classes in separate packages. This is the **official human-labeled
dataset** for the object-detection-impact task, and supersedes the auto-assisted draft in
`data/detection_pilot/` (n8 manual / n50 YOLOv8x auto) for formal evaluation.

## Contents

| Class | Images | Boxes | Avg boxes/img | Class id |
|-------|-------:|------:|--------------:|:--------:|
| `vehicle`  | 100 | 2,065 | 20.6 | 0 |
| `building` | 100 | 2,422 | 24.2 | 0 |

Each class is a self-contained YOLO package:

```
detection_labels/
├── vehicle/
│   ├── labels/          # 100 YOLO .txt files (class 0 = vehicle)
│   ├── image_list.txt   # source image filenames
│   └── data.yaml        # metadata-only descriptor
└── building/
    ├── labels/          # 100 YOLO .txt files (class 0 = building)
    ├── image_list.txt   # source image filenames
    └── data.yaml        # metadata-only descriptor
```

## Notes

- **Source:** Roboflow export (`Vehicle&Building_labels`). Filenames carry a Roboflow
  hash suffix (`..._JPG.rf.<hash>.txt`); the label stem matches its image stem.
- **Format:** normalized YOLO (`class cx cy w h`), resolution-independent.
- **Each class uses its own `0` index** (vehicle and building are exported as separate
  single-class sets). If you train a single 2-class detector, remap building to class `1`
  and merge the two label sets accordingly.
- **Raw images are intentionally not tracked in git** (consistent with the repo
  convention). See `image_list.txt` in each class folder for the source filenames; the
  images live in the local Roboflow export.

## Relationship to `data/detection_pilot/`

`data/detection_pilot/` holds the earlier *pilot* labels — `labels_yolo_vehicle_n8`
(8 manual draft images) and `labels_yolo_vehicle_n50_draft` (8 manual + 42 YOLOv8x
auto-assisted). Those remain in place for reference. For formal mAP reporting, use the
human-labeled sets here instead.
