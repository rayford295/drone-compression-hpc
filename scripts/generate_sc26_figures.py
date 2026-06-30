#!/usr/bin/env python3
"""Generate GitHub-ready SC26 CDC figure panels from committed result tables."""

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "imgs"

TRADEOFF = REPO / "results/2026-06-05-tradeoff-n50-lpips/tables/combined_summary.csv"
GH200_SWEEP = REPO / "results/2026-04-26-reconstruction/tables/sweep_summary.csv"
H200_SWEEP = REPO / "results/2026-04-28-h200-reconstruction/tables/sweep_summary.csv"
DETECTION = (
    REPO
    / "results/2026-06-12-yolo-vehicle-roof-human-n50/tables/"
    / "yolo_vehicle_roof_threshold_sweep_summary.csv"
)
SAM_VEHICLE = REPO / "results/2026-06-12-sam-vehicle-roof-human-n50/tables/sam_vehicle_summary.csv"
SAM_ROOF = REPO / "results/2026-06-12-sam-vehicle-roof-human-n50/tables/sam_roof_summary.csv"


COLORS = {
    "bg": "#EAF7FA",
    "panel": "#F8FBFD",
    "ink": "#172033",
    "muted": "#5B667A",
    "grid": "#CFD9E6",
    "navy": "#0B1B32",
    "teal": "#63C7C3",
    "teal_dark": "#168B87",
    "coral": "#FA7A7D",
    "coral_dark": "#C54247",
    "blue": "#4C78A8",
    "green": "#59A96A",
    "yellow": "#F4D35E",
    "orange": "#F58518",
    "white": "#FFFFFF",
}


def color(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = []
    if bold:
        candidates.extend(
            [
                "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf",
                "/Library/Fonts/Arial Bold.ttf",
            ]
        )
    candidates.extend(
        [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Helvetica.ttf",
            "/Library/Fonts/Arial.ttf",
        ]
    )
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


FONTS = {
    "title": font(54, True),
    "h1": font(34, True),
    "h2": font(25, True),
    "body": font(22),
    "body_bold": font(22, True),
    "small": font(18),
    "small_bold": font(18, True),
    "tiny": font(15),
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def fnum(value: str | float | int) -> float:
    if value == "":
        return math.nan
    return float(value)


def image(width: int, height: int, title: str, subtitle: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (width, height), color(COLORS["bg"]))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, width, 12), fill=color("#63D3DD"))
    draw.text((55, 55), title, font=FONTS["title"], fill=color(COLORS["ink"]))
    draw.text((58, 126), subtitle, font=FONTS["body"], fill=color(COLORS["muted"]))
    return img, draw


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=fnt)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def center_text(
    draw: ImageDraw.ImageDraw,
    box: tuple[float, float, float, float],
    text: str,
    fnt: ImageFont.ImageFont,
    fill: str = COLORS["ink"],
) -> None:
    x1, y1, x2, y2 = box
    tw, th = text_size(draw, text, fnt)
    draw.text((x1 + (x2 - x1 - tw) / 2, y1 + (y2 - y1 - th) / 2), text, font=fnt, fill=color(fill))


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        test = word if not current else f"{current} {word}"
        if text_size(draw, test, fnt)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def multiline(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    fnt: ImageFont.ImageFont,
    fill: str,
    max_width: int,
    line_gap: int = 7,
) -> None:
    x, y = xy
    for line in wrap_text(draw, text, fnt, max_width):
        draw.text((x, y), line, font=fnt, fill=color(fill))
        y += text_size(draw, line, fnt)[1] + line_gap


def panel(draw: ImageDraw.ImageDraw, xywh: tuple[int, int, int, int], title: str) -> tuple[int, int, int, int]:
    x, y, w, h = xywh
    draw.rounded_rectangle((x, y, x + w, y + h), radius=12, fill=color(COLORS["panel"]), outline=color("#D9E2ED"), width=2)
    draw.text((x + 24, y + 18), title, font=FONTS["h2"], fill=color(COLORS["ink"]))
    return x + 28, y + 70, w - 56, h - 98


def source(draw: ImageDraw.ImageDraw, text: str, width: int, height: int) -> None:
    draw.text((55, height - 44), text, font=FONTS["tiny"], fill=color(COLORS["muted"]))


def draw_bar_chart(
    draw: ImageDraw.ImageDraw,
    rect: tuple[int, int, int, int],
    labels: list[str],
    values: list[float],
    *,
    bar_colors: list[str],
    ymax: float | None = None,
    unit: str = "",
    fmt: str = "{:.1f}",
    lower_is_better: bool = True,
) -> None:
    x, y, w, h = rect
    plot_left, plot_top = x + 70, y + 16
    plot_right, plot_bottom = x + w - 20, y + h - 86
    ymax = ymax or max(values) * 1.18
    if ymax <= 1.2:
        tick_fmt = "{:.2f}"
    elif ymax <= 10:
        tick_fmt = "{:.1f}"
    else:
        tick_fmt = "{:.0f}"
    for i in range(5):
        gy = plot_bottom - (plot_bottom - plot_top) * i / 4
        draw.line((plot_left, gy, plot_right, gy), fill=color(COLORS["grid"]), width=1)
        tick = ymax * i / 4
        draw.text((x + 8, gy - 10), tick_fmt.format(tick), font=FONTS["tiny"], fill=color(COLORS["muted"]))
    draw.line((plot_left, plot_bottom, plot_right, plot_bottom), fill=color(COLORS["muted"]), width=2)
    n = len(values)
    slot = (plot_right - plot_left) / n
    for i, (label, value) in enumerate(zip(labels, values)):
        bw = slot * 0.58
        bx = plot_left + i * slot + (slot - bw) / 2
        by = plot_bottom - (plot_bottom - plot_top) * value / ymax
        draw.rounded_rectangle((bx, by, bx + bw, plot_bottom), radius=5, fill=color(bar_colors[i]), outline=color("#314155"), width=2)
        value_text = f"{fmt.format(value)}{unit}"
        tw, _ = text_size(draw, value_text, FONTS["small_bold"])
        draw.text((bx + bw / 2 - tw / 2, by - 28), value_text, font=FONTS["small_bold"], fill=color(COLORS["ink"]))
        for li, line in enumerate(label.split("\n")):
            lw, _ = text_size(draw, line, FONTS["tiny"])
            draw.text((bx + bw / 2 - lw / 2, plot_bottom + 14 + li * 20), line, font=FONTS["tiny"], fill=color(COLORS["muted"]))
    note = "lower is better" if lower_is_better else "higher is better"
    draw.text((plot_right - 145, plot_top - 8), note, font=FONTS["tiny"], fill=color(COLORS["muted"]))


def draw_grouped_bars(
    draw: ImageDraw.ImageDraw,
    rect: tuple[int, int, int, int],
    labels: list[str],
    series: list[tuple[str, list[float], str]],
    *,
    ymax: float | None = None,
    unit: str = "",
    fmt: str = "{:.1f}",
) -> None:
    x, y, w, h = rect
    plot_left, plot_top = x + 72, y + 20
    plot_right, plot_bottom = x + w - 28, y + h - 82
    ymax = ymax or max(max(vals) for _, vals, _ in series) * 1.18
    for i in range(5):
        gy = plot_bottom - (plot_bottom - plot_top) * i / 4
        draw.line((plot_left, gy, plot_right, gy), fill=color(COLORS["grid"]), width=1)
        tick = ymax * i / 4
        draw.text((x + 8, gy - 10), f"{tick:.0f}", font=FONTS["tiny"], fill=color(COLORS["muted"]))
    draw.line((plot_left, plot_bottom, plot_right, plot_bottom), fill=color(COLORS["muted"]), width=2)
    n = len(labels)
    slot = (plot_right - plot_left) / n
    bar_w = slot * 0.58 / len(series)
    for i, label in enumerate(labels):
        group_x = plot_left + i * slot + slot * 0.21
        for si, (_, vals, c) in enumerate(series):
            value = vals[i]
            bx = group_x + si * bar_w
            by = plot_bottom - (plot_bottom - plot_top) * value / ymax
            draw.rectangle((bx, by, bx + bar_w * 0.86, plot_bottom), fill=color(c), outline=color("#314155"), width=1)
            if i == n - 1 or len(labels) <= 4:
                txt = f"{fmt.format(value)}{unit}"
                tw, _ = text_size(draw, txt, FONTS["tiny"])
                draw.text((bx + bar_w * 0.43 - tw / 2, by - 21), txt, font=FONTS["tiny"], fill=color(COLORS["ink"]))
        for li, line in enumerate(label.split("\n")):
            lw, _ = text_size(draw, line, FONTS["tiny"])
            draw.text((plot_left + i * slot + slot / 2 - lw / 2, plot_bottom + 14 + li * 20), line, font=FONTS["tiny"], fill=color(COLORS["muted"]))
    lx = plot_left
    for name, _, c in series:
        draw.rectangle((lx, plot_top - 10, lx + 20, plot_top + 10), fill=color(c), outline=color("#314155"))
        draw.text((lx + 28, plot_top - 14), name, font=FONTS["tiny"], fill=color(COLORS["muted"]))
        lx += 148


def blend(c1: str, c2: str, t: float) -> tuple[int, int, int]:
    a, b = color(c1), color(c2)
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def heat_color(value: float, high_good: bool) -> tuple[int, int, int]:
    v = max(0.0, min(1.0, value))
    if high_good:
        return blend("#FBEA8A", COLORS["green"], v)
    return blend(COLORS["green"], COLORS["coral"], v)


def draw_heatmap(
    draw: ImageDraw.ImageDraw,
    rect: tuple[int, int, int, int],
    rows: list[tuple[str, list[float], bool]],
    col_labels: list[str],
    value_text: list[list[str]],
) -> None:
    x, y, w, h = rect
    label_w = 250
    top_h = 70
    cell_w = (w - label_w) / len(col_labels)
    cell_h = (h - top_h) / len(rows)
    for ci, label in enumerate(col_labels):
        cx = x + label_w + ci * cell_w
        multiline(draw, (cx + 8, y + 7), label, FONTS["tiny"], COLORS["muted"], int(cell_w - 16), 3)
    for ri, (row_label, values, high_good) in enumerate(rows):
        ry = y + top_h + ri * cell_h
        draw.text((x + 6, ry + cell_h / 2 - 11), row_label, font=FONTS["small_bold"], fill=color(COLORS["ink"]))
        for ci, value in enumerate(values):
            cx = x + label_w + ci * cell_w
            draw.rectangle(
                (cx, ry, cx + cell_w - 2, ry + cell_h - 2),
                fill=heat_color(value / 100.0, high_good),
                outline=color("#E8EEF6"),
            )
            center_text(
                draw,
                (cx, ry, cx + cell_w - 2, ry + cell_h - 2),
                value_text[ri][ci],
                FONTS["small_bold"],
                COLORS["ink"],
            )


def find_row(rows: Iterable[dict[str, str]], **kwargs: str) -> dict[str, str]:
    for row in rows:
        if all(row.get(key) == value for key, value in kwargs.items()):
            return row
    raise KeyError(kwargs)


def tradeoff_rows() -> dict[str, dict[str, str]]:
    rows = read_csv(TRADEOFF)
    return {
        "Full balanced": find_row(rows, experiment_name="tradeoff_balanced_tile_none"),
        "Balanced 256": find_row(rows, experiment_name="tradeoff_balanced_tile_256"),
        "Balanced 512": find_row(rows, experiment_name="tradeoff_balanced_tile_512"),
        "Max 256": find_row(rows, experiment_name="tradeoff_high_compression_tile_256"),
        "High quality 512": find_row(rows, experiment_name="tradeoff_high_quality_tile_512"),
    }


def detection_conf(confidence: str = "0.250") -> dict[str, dict[str, str]]:
    rows = [r for r in read_csv(DETECTION) if r["confidence"] == confidence]
    return {r["configuration"]: r for r in rows}


def sam_summary(path: Path) -> dict[str, dict[str, str]]:
    return {r["configuration"]: r for r in read_csv(path)}


def render_platform_table() -> Path:
    width, height = 1800, 1000
    img, draw = image(
        width,
        height,
        "Compute Platforms and Evidence Scope",
        "What can be drawn from rayford295/sc26-cdc-deltaai today, using committed result summaries.",
    )
    x, y, w, h = 70, 210, 1660, 650
    draw.rounded_rectangle((x, y, x + w, y + h), radius=12, fill=color(COLORS["panel"]), outline=color("#B7C6D8"), width=3)
    headers = ["Evidence lane", "DeltaAI GH200", "Delta H200", "Not measured in repo"]
    col_w = [300, 470, 430, 460]
    rows = [
        [
            "Role",
            "Main experiment platform for N50 tradeoff, detection, SAM, and poster-ready visual QA.",
            "Quick portability comparison for the same reconstruction workflow.",
            "A100, GraphCore IPU, cost, power, temperature, and memory bandwidth telemetry.",
        ],
        [
            "Workload",
            "CDC compression and reconstruction on 5440 x 3648 drone images.",
            "Matched fp32/fp16 reconstruction step sweep.",
            "No structured external-platform runs in committed CSV files.",
        ],
        [
            "Measured fields",
            "Sec/img, peak GPU memory, BPP, compression ratio, PSNR, SSIM, LPIPS, seam metrics, detection, SAM.",
            "Sec/img, images/hour, peak GPU memory, PSNR, SSIM, BPP.",
            "GPU core utilization, memory-bandwidth utilization, power W, temperature C.",
        ],
        [
            "Key readout",
            "Balanced 256: 79.34 s/img, 1.57 GB peak GPU, 79.98x compression.",
            "At 65 fp32 steps: 138.48 s/img vs GH200 143.67 s/img, about 3.6% faster.",
            "Can be added later with nvidia-smi dmon, DCGM, or Nsight.",
        ],
    ]
    row_h = [72, 138, 138, 150, 150]
    cursor_y = y
    cursor_x = x
    for i, header in enumerate(headers):
        draw.rectangle((cursor_x, cursor_y, cursor_x + col_w[i], cursor_y + row_h[0]), fill=color(COLORS["navy"]), outline=color("#B7C6D8"))
        center_text(draw, (cursor_x, cursor_y, cursor_x + col_w[i], cursor_y + row_h[0]), header, FONTS["body_bold"], COLORS["white"])
        cursor_x += col_w[i]
    cursor_y += row_h[0]
    for ri, row in enumerate(rows):
        cursor_x = x
        fill = "#FFFFFF" if ri % 2 == 0 else "#F1F7FA"
        for ci, cell in enumerate(row):
            draw.rectangle((cursor_x, cursor_y, cursor_x + col_w[ci], cursor_y + row_h[ri + 1]), fill=color(fill), outline=color("#B7C6D8"))
            fnt = FONTS["body_bold"] if ci == 0 else FONTS["small"]
            multiline(draw, (cursor_x + 18, cursor_y + 20), cell, fnt, COLORS["ink"] if ci == 0 else COLORS["muted"], col_w[ci] - 36, 6)
            cursor_x += col_w[ci]
        cursor_y += row_h[ri + 1]
    draw.text((78, 888), "Interpretation: draw measured GH200/H200 performance figures now; label uncollected telemetry as missing or proxy.", font=FONTS["body_bold"], fill=color(COLORS["coral_dark"]))
    source(draw, "Sources: README, results/README.md, tradeoff N50 LPIPS table, H200 reconstruction table.", width, height)
    out = OUT_DIR / "sc26_compute_platform_evidence_scope.png"
    img.save(out)
    return out


def render_performance_dashboard() -> Path:
    data = tradeoff_rows()
    det = detection_conf("0.250")
    labels = ["Full\nbalanced", "Balanced\n256", "Balanced\n512", "Max comp.\n256"]
    keys = ["Full balanced", "Balanced 256", "Balanced 512", "Max 256"]
    width, height = 1900, 1280
    img, draw = image(
        width,
        height,
        "CDC Reconstruction Performance Dashboard",
        "Measured DeltaAI GH200 results from the formal N50 compression-setting x tile-size run.",
    )
    p1 = panel(draw, (60, 200, 860, 450), "Runtime per Image")
    draw_bar_chart(
        draw,
        p1,
        labels,
        [fnum(data[k]["avg_wall_sec"]) for k in keys],
        bar_colors=[COLORS["coral"], COLORS["teal"], COLORS["teal"], COLORS["coral"]],
        ymax=160,
        unit=" s",
        fmt="{:.1f}",
        lower_is_better=True,
    )
    p2 = panel(draw, (980, 200, 860, 450), "Peak GPU Memory")
    draw_bar_chart(
        draw,
        p2,
        labels,
        [fnum(data[k]["avg_peak_gpu_mem_mb"]) / 1024 for k in keys],
        bar_colors=[COLORS["coral"], COLORS["teal"], COLORS["teal"], COLORS["teal"]],
        ymax=56,
        unit=" GB",
        fmt="{:.2f}",
        lower_is_better=True,
    )
    p3 = panel(draw, (60, 700, 860, 450), "Compression Ratio and Fidelity")
    q_keys = ["High quality 512", "Balanced 256", "Balanced 512", "Max 256"]
    q_labels = [
        f"High qual.\n512\nPSNR {fnum(data['High quality 512']['avg_psnr_db']):.2f}",
        f"Balanced\n256\nPSNR {fnum(data['Balanced 256']['avg_psnr_db']):.2f}",
        f"Balanced\n512\nPSNR {fnum(data['Balanced 512']['avg_psnr_db']):.2f}",
        f"Max comp.\n256\nPSNR {fnum(data['Max 256']['avg_psnr_db']):.2f}",
    ]
    draw_bar_chart(
        draw,
        p3,
        q_labels,
        [fnum(data[k]["avg_compression_ratio"]) for k in q_keys],
        bar_colors=[COLORS["blue"], COLORS["teal"], COLORS["teal"], COLORS["coral"]],
        ymax=155,
        unit="x",
        fmt="{:.1f}",
        lower_is_better=False,
    )
    p4 = panel(draw, (980, 700, 860, 450), "Downstream Detection, Human Labels")
    det_labels = ["Original", "High qual.\n512", "Balanced\n256", "Max comp.\n256"]
    det_keys = ["original", "high_quality_512", "balanced_256", "max_compression_256"]
    draw_bar_chart(
        draw,
        p4,
        det_labels,
        [fnum(det[k]["map50"]) for k in det_keys],
        bar_colors=[COLORS["blue"], COLORS["teal"], COLORS["teal"], COLORS["coral"]],
        ymax=1.0,
        unit="",
        fmt="{:.3f}",
        lower_is_better=False,
    )
    draw.text((p4[0] + 502, p4[1] + 15), "YOLO vehicle+roof, conf=0.25", font=FONTS["tiny"], fill=color(COLORS["muted"]))
    source(draw, "Sources: results/2026-06-05-tradeoff-n50-lpips and results/2026-06-12-yolo-vehicle-roof-human-n50.", width, height)
    out = OUT_DIR / "sc26_cdc_performance_dashboard.png"
    img.save(out)
    return out


def render_hardware_comparison() -> Path:
    gh_rows = read_csv(GH200_SWEEP)
    h_rows = read_csv(H200_SWEEP)

    def sweep(rows: list[dict[str, str]], precision: str, steps: list[str]) -> dict[str, dict[str, str]]:
        return {step: find_row(rows, precision=precision, n_denoise_step=step, batch_size="1") for step in steps}

    steps = ["5", "20", "65"]
    gh_fp32 = sweep(gh_rows, "fp32", steps)
    h_fp32 = sweep(h_rows, "fp32", steps)
    gh_fp16 = sweep(gh_rows, "fp16", steps)
    h_fp16 = sweep(h_rows, "fp16", steps)
    width, height = 1900, 1180
    img, draw = image(
        width,
        height,
        "GH200 vs H200 Reconstruction Check",
        "Matched CDC reconstruction sweeps show H200 portability and modest speed gains.",
    )
    labels = [f"{s}\nsteps" for s in steps]
    p1 = panel(draw, (60, 200, 860, 405), "fp32 Inference Time")
    draw_grouped_bars(
        draw,
        p1,
        labels,
        [
            ("GH200", [fnum(gh_fp32[s]["avg_inference_sec"]) for s in steps], COLORS["coral"]),
            ("H200", [fnum(h_fp32[s]["avg_inference_sec"]) for s in steps], COLORS["teal"]),
        ],
        ymax=160,
        unit=" s",
        fmt="{:.1f}",
    )
    p2 = panel(draw, (980, 200, 860, 405), "Images per Hour")
    draw_grouped_bars(
        draw,
        p2,
        labels,
        [
            ("GH200", [fnum(gh_fp32[s]["avg_images_per_hour"]) for s in steps], COLORS["coral"]),
            ("H200", [fnum(h_fp32[s]["avg_images_per_hour"]) for s in steps], COLORS["teal"]),
        ],
        ymax=370,
        unit="",
        fmt="{:.0f}",
    )
    p3 = panel(draw, (60, 655, 860, 405), "H200 Speedup over GH200")
    speedups = [(fnum(gh_fp32[s]["avg_inference_sec"]) / fnum(h_fp32[s]["avg_inference_sec"]) - 1) * 100 for s in steps]
    draw_bar_chart(
        draw,
        p3,
        labels,
        speedups,
        bar_colors=[COLORS["teal"], COLORS["teal"], COLORS["teal"]],
        ymax=5,
        unit="%",
        fmt="{:.1f}",
        lower_is_better=False,
    )
    p4 = panel(draw, (980, 655, 860, 405), "Peak GPU Memory at 65 Steps")
    draw_grouped_bars(
        draw,
        p4,
        ["GH200\nfp32", "GH200\nfp16", "H200\nfp32", "H200\nfp16"],
        [
            (
                "Peak GB",
                [
                    fnum(gh_fp32["65"]["avg_peak_gpu_mem_mb"]) / 1024,
                    fnum(gh_fp16["65"]["avg_peak_gpu_mem_mb"]) / 1024,
                    fnum(h_fp32["65"]["avg_peak_gpu_mem_mb"]) / 1024,
                    fnum(h_fp16["65"]["avg_peak_gpu_mem_mb"]) / 1024,
                ],
                COLORS["blue"],
            )
        ],
        ymax=60,
        unit=" GB",
        fmt="{:.1f}",
    )
    source(draw, "Sources: results/2026-04-26-reconstruction and results/2026-04-28-h200-reconstruction.", width, height)
    out = OUT_DIR / "sc26_gh200_h200_hardware_comparison.png"
    img.save(out)
    return out


def render_bottleneck_proxy() -> Path:
    data = tradeoff_rows()
    det = detection_conf("0.250")
    sam_roof = sam_summary(SAM_ROOF)
    keys = ["Full balanced", "Balanced 256", "Balanced 512", "Max 256"]
    labels = ["Full\nbalanced", "Balanced\n256", "Balanced\n512", "Max comp.\n256"]
    runtime = [fnum(data[k]["avg_wall_sec"]) for k in keys]
    mem = [fnum(data[k]["avg_peak_gpu_mem_mb"]) / 1024 for k in keys]
    non_gpu = [fnum(data[k]["avg_non_gpu_sec"]) / fnum(data[k]["avg_wall_sec"]) * 100 for k in keys]
    psnr = [fnum(data[k]["avg_psnr_db"]) for k in keys]
    det_keys = ["original", "balanced_256", "high_quality_512", "max_compression_256"]
    det_values = [
        fnum(det["original"]["map50"]),
        fnum(det["balanced_256"]["map50"]),
        fnum(det["high_quality_512"]["map50"]),
        fnum(det["max_compression_256"]["map50"]),
    ]
    roof_values = [
        1.0,
        fnum(sam_roof["balanced_256"]["mean_mask_iou"]),
        fnum(sam_roof["high_quality_512"]["mean_mask_iou"]),
        fnum(sam_roof["max_compression_256"]["mean_mask_iou"]),
    ]
    max_runtime = max(runtime)
    max_mem = max(mem)
    best_psnr = max(psnr)
    min_psnr = min(psnr)
    psnr_pressure = [(best_psnr - v) / (best_psnr - min_psnr) * 100 if best_psnr > min_psnr else 0 for v in psnr]
    rows = [
        ("Runtime pressure", [v / max_runtime * 100 for v in runtime], False),
        ("GPU memory pressure", [v / max_mem * 100 for v in mem], False),
        ("Non-GPU overhead", [min(100, v * 10) for v in non_gpu], False),
        ("Quality-loss proxy", psnr_pressure, False),
        ("Detection retention", [v / det_values[0] * 100 for v in det_values], True),
        ("SAM roof IoU", [v * 100 for v in roof_values], True),
    ]
    texts = [
        [f"{v:.0f}%" for v in rows[0][1]],
        [f"{v:.1f} GB" for v in mem],
        [f"{v:.1f}%" for v in non_gpu],
        [f"{v:.2f} dB" for v in psnr],
        [f"{v:.3f}" for v in det_values],
        [f"{v:.3f}" for v in roof_values],
    ]
    width, height = 1900, 1180
    img, draw = image(
        width,
        height,
        "Bottleneck Analysis from Available Metrics",
        "Proxy heatmap from committed summaries. Hardware telemetry such as bandwidth, power, and temperature is not in the repo yet.",
    )
    hm = panel(draw, (60, 200, 1780, 515), "Measured Proxies, Not Hardware Telemetry")
    draw_heatmap(draw, hm, rows, labels, texts)
    p2 = panel(draw, (60, 765, 860, 305), "Wall-Time Breakdown")
    inference = [fnum(data[k]["avg_inference_sec"]) for k in keys]
    non_gpu_secs = [fnum(data[k]["avg_non_gpu_sec"]) for k in keys]
    draw_grouped_bars(
        draw,
        p2,
        labels,
        [
            ("GPU inference", inference, COLORS["teal"]),
            ("Non-GPU", non_gpu_secs, COLORS["coral"]),
        ],
        ymax=180,
        unit=" s",
        fmt="{:.1f}",
    )
    p3 = panel(draw, (980, 765, 860, 305), "Operational Reading")
    multiline(
        draw,
        (p3[0] + 10, p3[1] + 15),
        "Full-image reconstruction is the memory wall: about 52 GB peak GPU allocation. "
        "Balanced 256 tiling cuts peak memory to 1.57 GB, a 32.2x reduction, while also "
        "cutting runtime from 143.17 to 79.34 seconds per image.",
        FONTS["body"],
        COLORS["ink"],
        p3[2] - 20,
        9,
    )
    multiline(
        draw,
        (p3[0] + 10, p3[1] + 155),
        "Next instrumentation step: add nvidia-smi dmon or DCGM sampling to record gpu_util, "
        "mem_util, power_w, temp_c, and bandwidth-like counters during each SLURM run.",
        FONTS["small_bold"],
        COLORS["coral_dark"],
        p3[2] - 20,
        8,
    )
    source(draw, "Sources: tradeoff N50 LPIPS table, human-label YOLO vehicle+roof table, SAM vehicle/roof table.", width, height)
    out = OUT_DIR / "sc26_bottleneck_proxy_heatmap.png"
    img.save(out)
    return out


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = [
        render_platform_table(),
        render_performance_dashboard(),
        render_hardware_comparison(),
        render_bottleneck_proxy(),
    ]
    for output in outputs:
        print(output.relative_to(REPO))


if __name__ == "__main__":
    main()
