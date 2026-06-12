# SAM Mask Stability Summary

| configuration | num_images | num_prompts | mean_mask_iou | mean_dice | mean_area_ratio | mean_abs_area_change | mean_centroid_shift_px | failed_prompt_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| original | 50 | 1201 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 0.0 |
| high_quality_512 | 50 | 1201 | 0.900123 | 0.945443 | 1.002042 | 0.025937 | 15.960561 | 0.0 |
| balanced_256 | 50 | 1201 | 0.898891 | 0.944659 | 1.002866 | 0.027758 | 16.096677 | 0.0 |
| max_compression_256 | 50 | 1201 | 0.895618 | 0.942522 | 1.00266 | 0.029802 | 16.634331 | 0.0 |
