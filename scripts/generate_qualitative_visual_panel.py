#!/usr/bin/env python3
"""Build a poster-ready 256-vs-512 qualitative visual comparison panel."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


REPO = Path(__file__).resolve().parents[1]
SRC_DIR = REPO / "results/2026-05-15-yifan-selected-256-512-n50/visual_examples_small"
OUT_DIR = REPO / "imgs"

TILE256_COMPARISON = SRC_DIR / "100_0005_0001_tile256_comparison.jpg"
TILE512_COMPARISON = SRC_DIR / "100_0005_0001_tile512_comparison.jpg"
TILE256_HEATMAP = SRC_DIR / "100_0005_0001_tile256_error_heatmap.jpg"
TILE512_HEATMAP = SRC_DIR / "100_0005_0001_tile512_error_heatmap.jpg"

PANEL_PNG = OUT_DIR / "sc26_qualitative_256_512_visual_comparison.png"
PANEL_JPG = OUT_DIR / "sc26_qualitative_256_512_visual_comparison.jpg"

WIDTH, HEIGHT = 2541, 1419
MAROON = "#500000"
MAROON_DARK = "#360000"
MUTED = "#51433F"
CREAM = "#FFF9F1"
PANEL_BG = "#FFFFFF"
BORDER = "#CBB8A5"
TAN = "#F2E3D0"


def color(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    names = []
    if bold:
        names.extend(
            [
                "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf",
            ]
        )
    names.extend(
        [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Helvetica.ttf",
        ]
    )
    for name in names:
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            pass
    return ImageFont.load_default()


F_TITLE = font(58, True)
F_SUB = font(28)
F_HEAD = font(34, True)
F_ROW = font(34, True)
F_SMALL = font(23)


def crop_comparison(path: Path) -> tuple[Image.Image, Image.Image]:
    with Image.open(path) as img:
        rgb = img.convert("RGB")
    w, h = rgb.size
    third = w // 3
    original = rgb.crop((0, 0, third, h))
    reconstruction = rgb.crop((third, 0, third * 2, h))
    return original, reconstruction


def cover(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    target_w, target_h = size
    src_w, src_h = img.size
    scale = max(target_w / src_w, target_h / src_h)
    resized = img.resize((round(src_w * scale), round(src_h * scale)), Image.Resampling.LANCZOS)
    left = max(0, (resized.width - target_w) // 2)
    top = max(0, (resized.height - target_h) // 2)
    return resized.crop((left, top, left + target_w, top + target_h))


def fit(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    target_w, target_h = size
    src_w, src_h = img.size
    scale = min(target_w / src_w, target_h / src_h)
    resized = img.resize((round(src_w * scale), round(src_h * scale)), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, color(PANEL_BG))
    canvas.paste(resized, ((target_w - resized.width) // 2, (target_h - resized.height) // 2))
    return canvas


def draw_centered(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, fnt: ImageFont.ImageFont, fill: str) -> None:
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x1, y1, x2, y2 = box
    draw.text((x1 + (x2 - x1 - tw) / 2, y1 + (y2 - y1 - th) / 2), text, font=fnt, fill=color(fill))


def add_image_frame(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    img: Image.Image,
    box: tuple[int, int, int, int],
    *,
    mode: str = "cover",
) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle((x1 - 4, y1 - 4, x2 + 4, y2 + 4), radius=10, fill=color("#F4EEE8"), outline=color(BORDER), width=3)
    prepared = cover(img, (x2 - x1, y2 - y1)) if mode == "cover" else fit(img, (x2 - x1, y2 - y1))
    canvas.paste(prepared, (x1, y1))


def build_panel() -> Image.Image:
    original_256, recon_256 = crop_comparison(TILE256_COMPARISON)
    _, recon_512 = crop_comparison(TILE512_COMPARISON)
    heat_256 = Image.open(TILE256_HEATMAP).convert("RGB")
    heat_512 = Image.open(TILE512_HEATMAP).convert("RGB")

    canvas = Image.new("RGB", (WIDTH, HEIGHT), color(CREAM))
    draw = ImageDraw.Draw(canvas)

    draw.rectangle((0, 0, WIDTH, 18), fill=color(MAROON))
    draw.text((70, 55), "Visual Reconstruction Check: 256 vs 512 Tiling", font=F_TITLE, fill=color(MAROON_DARK))
    draw.text(
        (74, 130),
        "Representative Galveston drone scene; only image-level comparison panels are shown for poster readability.",
        font=F_SUB,
        fill=color(MUTED),
    )

    left, top = 70, 215
    row_label_w = 250
    gap = 34
    col_w = 690
    img_h = 455
    header_h = 58
    row_gap = 58
    cols = [
        ("Original", original_256, "cover"),
        ("Reconstruction", recon_256, "cover"),
        ("Difference map", heat_256, "cover"),
    ]
    headers_y = top
    for ci, (label, _, _) in enumerate(cols):
        x = left + row_label_w + ci * (col_w + gap)
        draw_centered(draw, (x, headers_y, x + col_w, headers_y + header_h), label, F_HEAD, MAROON_DARK)

    def row(y: int, label: str, recon: Image.Image, heatmap: Image.Image) -> None:
        draw.rounded_rectangle((left, y, left + row_label_w - 24, y + img_h), radius=16, fill=color(MAROON), outline=color(MAROON))
        draw_centered(draw, (left, y, left + row_label_w - 24, y + img_h), label, F_ROW, "#FFFFFF")
        imgs = [original_256, recon, heatmap]
        for ci, img in enumerate(imgs):
            x = left + row_label_w + ci * (col_w + gap)
            add_image_frame(canvas, draw, img, (x, y, x + col_w, y + img_h), mode="cover")

    first_y = top + header_h + 15
    second_y = first_y + img_h + row_gap
    row(first_y, "256 x 256", recon_256, heat_256)
    row(second_y, "512 x 512", recon_512, heat_512)

    draw.text(
        (74, HEIGHT - 70),
        "Columns compare the same scene: original image, reconstructed image, and absolute reconstruction-error map.",
        font=F_SMALL,
        fill=color(MUTED),
    )
    return canvas


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    panel = build_panel()
    panel.save(PANEL_PNG)
    panel.save(PANEL_JPG, quality=95, subsampling=0)
    print(PANEL_PNG.relative_to(REPO))
    print(PANEL_JPG.relative_to(REPO))


if __name__ == "__main__":
    main()
