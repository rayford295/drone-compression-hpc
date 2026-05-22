import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { Canvas } = require("../../2026-05-12-yifan-tiling-progress/node_modules/@oai/artifact-tool/node_modules/skia-canvas");

const {
  Presentation,
  PresentationFile,
  row,
  column,
  grid,
  layers,
  panel: rawPanel,
  text,
  image: rawImage,
  shape: rawShape,
  rule,
  fill,
  hug,
  fixed,
  wrap,
  grow,
  fr,
  drawSlideToCtx,
} = await import("../../2026-05-12-yifan-tiling-progress/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs");
const { paint, stroke } = await import("../../2026-05-12-yifan-tiling-progress/node_modules/@oai/artifact-tool/dist/presentation-jsx/index.mjs");

const WORKSPACE = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const REPO = path.resolve(WORKSPACE, "..", "..");
const OUTPUT_DIR = path.join(WORKSPACE, "output");
const FINAL_NAME = "SC26_CDC_Yifan_Jacob_Poster_Update_2026-05-22.pptx";
const OUTPUT = path.join(OUTPUT_DIR, FINAL_NAME);
const ROOT_COPY = path.join(WORKSPACE, FINAL_NAME);
const PREVIEW_DIR = path.join(WORKSPACE, "scratch", "previews");

const COLORS = {
  bg: "#F7F9FC",
  ink: "#172033",
  muted: "#5B667A",
  faint: "#E4E9F2",
  white: "#FFFFFF",
  navy: "#0B1B32",
  blue: "#2563EB",
  teal: "#0F766E",
  green: "#15803D",
  orange: "#D97706",
  red: "#B91C1C",
  lavender: "#EEF2FF",
  tealSoft: "#E7F6F2",
  orangeSoft: "#FFF7ED",
  blueSoft: "#EAF1FF",
  greenSoft: "#ECFDF5",
  graySoft: "#F1F5F9",
};

const SLIDE = { width: 1920, height: 1080 };
const BODY_FONT = "Aptos";
const DISPLAY_FONT = "Aptos Display";

const tileRows = [
  { setup: "No tiling", time: 144.35, memory: 52.01, ratio: 70.11, psnr: 28.96, ssim: 0.8616, mae: 0.027016, p99: 0.117676, seam: "n/a" },
  { setup: "256 tile", time: 79.84, memory: 1.66, ratio: 68.24, psnr: 28.78, ssim: 0.8552, mae: 0.027463, p99: 0.120211, seam: "0.032556" },
  { setup: "512 tile", time: 87.71, memory: 3.02, ratio: 66.31, psnr: 28.86, ssim: 0.8583, mae: 0.027246, p99: 0.118897, seam: "0.032224" },
];

const checkpointRows = [
  { role: "High quality", checkpoint: "b00512", ratio: 32.67, psnr: 34.84, ssim: 0.942 },
  { role: "Balanced", checkpoint: "b00064", ratio: 93.11, psnr: 33.73, ssim: 0.880 },
  { role: "High compression", checkpoint: "b00128", ratio: 165.73, psnr: 31.52, ssim: 0.828 },
];

function asFill(value) {
  return typeof value === "string" ? paint(value) : value;
}

function asLine(value) {
  return typeof value === "string" ? stroke(value) : value;
}

function panel(options = {}, child) {
  return rawPanel({ ...options, fill: asFill(options.fill), line: asLine(options.line) }, child);
}

function shape(options = {}) {
  return rawShape({ ...options, fill: asFill(options.fill), line: asLine(options.line) });
}

function image(options = {}) {
  if (options.path) {
    const ext = path.extname(options.path).toLowerCase();
    const mime = ext === ".jpg" || ext === ".jpeg" ? "image/jpeg" : "image/png";
    const dataUrl = `data:${mime};base64,${fs.readFileSync(options.path).toString("base64")}`;
    const { path: _path, ...rest } = options;
    return rawImage({ ...rest, dataUrl, contentType: mime });
  }
  return rawImage(options);
}

function pathTo(relativePath) {
  return path.join(REPO, relativePath);
}

function t(value, options = {}) {
  return text(value, {
    width: options.width ?? fill,
    height: options.height ?? hug,
    name: options.name,
    style: {
      fontFamily: options.fontFamily ?? BODY_FONT,
      fontSize: options.size ?? 28,
      color: options.color ?? COLORS.ink,
      bold: options.bold ?? false,
      italic: options.italic ?? false,
    },
    columnSpan: options.columnSpan,
    rowSpan: options.rowSpan,
  });
}

function badge(label, fillColor = COLORS.blueSoft, color = COLORS.blue) {
  return panel(
    { width: hug, height: hug, padding: { x: 18, y: 8 }, fill: fillColor, borderRadius: 8, line: fillColor },
    t(label, { width: hug, size: 19, bold: true, color }),
  );
}

function titleBlock(title, subtitle) {
  return column({ width: fill, height: hug, gap: 12 }, [
    t(title, { name: "slide-title", size: 48, bold: true, fontFamily: DISPLAY_FONT }),
    subtitle ? t(subtitle, { name: "slide-subtitle", size: 23, color: COLORS.muted, width: wrap(1370) }) : null,
  ].filter(Boolean));
}

function footer(source) {
  return row({ width: fill, height: hug, align: "center", justify: "between" }, [
    t(source, { size: 14, color: "#6B7280", width: wrap(1330) }),
    t("SC26 CDC update | May 22, 2026", { size: 14, color: "#6B7280", width: hug }),
  ]);
}

function metricCard(label, value, detail, accent = COLORS.blue, fillColor = COLORS.white) {
  return panel(
    { width: fill, height: fill, fill: fillColor, line: COLORS.faint, borderRadius: 8, padding: { x: 22, y: 18 } },
    column({ width: fill, height: fill, gap: 8, justify: "between" }, [
      t(label, { size: 17, bold: true, color: COLORS.muted }),
      t(value, { size: 33, bold: true, color: accent, fontFamily: DISPLAY_FONT }),
      t(detail, { size: 17, color: COLORS.muted }),
    ]),
  );
}

function evidencePanel(children, fillColor = COLORS.white) {
  return panel(
    { width: fill, height: fill, fill: fillColor, line: COLORS.faint, borderRadius: 8, padding: { x: 26, y: 24 } },
    column({ width: fill, height: fill, gap: 16 }, children),
  );
}

function slideShell(presentation, title, subtitle, body, source) {
  const slide = presentation.slides.add();
  slide.compose(
    layers({ width: fill, height: fill }, [
      shape({ width: fill, height: fill, fill: COLORS.bg, line: COLORS.bg }),
      column({ width: fill, height: fill, padding: { x: 72, y: 54 }, gap: 26 }, [
        titleBlock(title, subtitle),
        rule({ width: fixed(180), stroke: COLORS.blue, weight: 4 }),
        ...body,
        footer(source),
      ]),
    ]),
    { frame: { left: 0, top: 0, width: SLIDE.width, height: SLIDE.height }, baseUnit: 8 },
  );
}

function fmt(value, digits = 1) {
  return Number(value).toFixed(digits);
}

function pct(value, digits = 0) {
  return `${Number(value).toFixed(digits)}%`;
}

function reduction(baseline, candidate) {
  return ((baseline - candidate) / baseline) * 100;
}

function tableRows(headers, rowsData, widths, options = {}) {
  const cols = widths.map((width) => fr(width));
  const makeCell = (cell, fillColor, size, bold = false, color = COLORS.ink) =>
    panel({ width: fill, height: fill, fill: fillColor, line: COLORS.faint, padding: { x: 10, y: 7 } },
      t(String(cell), { size, bold, color, width: fill }));
  return column({ width: fill, height: hug, gap: 2 }, [
    grid({ width: fill, height: fixed(options.headerHeight ?? 42), columns: cols }, headers.map((cell) => makeCell(cell, COLORS.navy, options.headerSize ?? 15, true, COLORS.white))),
    ...rowsData.map((cells, rowIndex) =>
      grid({ width: fill, height: fixed(options.rowHeight ?? 48), columns: cols },
        cells.map((cell) => makeCell(cell, rowIndex % 2 === 0 ? COLORS.white : COLORS.graySoft, options.bodySize ?? 16))),
    ),
  ]);
}

function bullet(label, detail, color = COLORS.blue) {
  return row({ width: fill, height: hug, gap: 14, align: "start" }, [
    shape({ width: fixed(12), height: fixed(12), fill: color, line: color, borderRadius: 6 }),
    column({ width: fill, height: hug, gap: 3 }, [
      t(label, { size: 22, bold: true }),
      detail ? t(detail, { size: 18, color: COLORS.muted }) : null,
    ].filter(Boolean)),
  ]);
}

function addCover(presentation) {
  const slide = presentation.slides.add();
  slide.compose(
    layers({ width: fill, height: fill }, [
      shape({ width: fill, height: fill, fill: COLORS.navy, line: COLORS.navy }),
      grid({ width: fill, height: fill, columns: [fr(1), fr(1)], columnGap: 54, padding: { x: 76, y: 70 } }, [
        column({ width: fill, height: fill, gap: 26, justify: "center" }, [
          row({ width: fill, height: hug, gap: 12 }, [
            badge("SC26 CDC", "#12345C", "#BFE8FF"),
            badge("DeltaAI results", "#163B32", "#C9F4E8"),
          ]),
          t("Compression Results Are Ready for the Poster Story", { width: wrap(850), size: 68, bold: true, color: COLORS.white, fontFamily: DISPLAY_FONT }),
          t("Three linked deliverables now support the update: 256 tiling, Jacob's compression-side experiment, and poster-ready difference-map panels.", { width: wrap(840), size: 28, color: "#D7E3F5" }),
          grid({ width: fill, height: fixed(170), columns: [fr(1), fr(1), fr(1)], columnGap: 16 }, [
            metricCard("Tiling", "256 wins", "79.84s and 1.66 GB", "#86EFAC", "#102848"),
            metricCard("Compression", "N=20", "checkpoint sweep complete", "#7DD3FC", "#102848"),
            metricCard("Poster", "3 panels", "difference maps ready", "#FDBA74", "#102848"),
          ]),
        ]),
        panel({ width: fill, height: fill, fill: COLORS.white, line: "#223B5C", borderRadius: 8, padding: { x: 18, y: 18 } },
          column({ width: fill, height: fill, gap: 12 }, [
            image({ path: pathTo("results/2026-05-22-yifan-poster-visual-qa/visual_examples_small/100_0005_0001_tile256_poster_panel.jpg"), width: fill, height: grow(1), fit: "contain", alt: "Poster panel for 256 tiling" }),
            t("Poster visual QA: original, reconstructed, hot difference map, histogram, metrics, and distribution.", { size: 17, color: COLORS.muted }),
          ])),
      ]),
    ]),
    { frame: { left: 0, top: 0, width: SLIDE.width, height: SLIDE.height }, baseUnit: 8 },
  );
}

function addAgenda(presentation) {
  slideShell(
    presentation,
    "Three Pieces Are Complete",
    "The update can now move from experiment setup to poster assembly.",
    [
      grid({ width: fill, height: grow(1), columns: [fr(1), fr(1), fr(1)], columnGap: 22 }, [
        evidencePanel([badge("1", COLORS.greenSoft, COLORS.green), t("Yifan tiling", { size: 31, bold: true }), t("Selected `256 x 256` against no tiling and `512 x 512` on 50 full-resolution images.", { size: 21, color: COLORS.muted }), metricCard("Result", "256 x 256", "speed and memory candidate", COLORS.green)]),
        evidencePanel([badge("2", COLORS.blueSoft, COLORS.blue), t("Jacob compression", { size: 31, bold: true }), t("Baseline, resolution, batch, checkpoint, scaling, and storage tests on 20 images.", { size: 21, color: COLORS.muted }), metricCard("Result", "N=20", "table is on GitHub", COLORS.blue)]),
        evidencePanel([badge("3", COLORS.orangeSoft, COLORS.orange), t("Poster visuals", { size: 31, bold: true }), t("Difference-map panels now match the visual format requested in chat.", { size: 21, color: COLORS.muted }), metricCard("Result", "3 panels", "no tiling / 256 / 512", COLORS.orange)]),
      ]),
    ],
    "Source: committed result folders under results/2026-05-15, results/2026-05-22.",
  );
}

function addTilingSlide(presentation) {
  const baseline = tileRows[0];
  const tile256 = tileRows[1];
  slideShell(
    presentation,
    "256 x 256 Is the New Speed and Memory Candidate",
    "The larger N=50 selected run confirms smaller tiles cut memory below 2 GB and improve wall time compared with 512 tiles.",
    [
      grid({ width: fill, height: grow(1), columns: [fr(1.12), fr(0.88)], columnGap: 26 }, [
        evidencePanel([
          t("Selected N=50 Tiling Results", { size: 30, bold: true }),
          tableRows(
            ["Setup", "Time", "Memory", "Ratio", "PSNR", "SSIM", "p99"],
            tileRows.map((item) => [item.setup, `${fmt(item.time, 2)}s`, `${fmt(item.memory, 2)} GB`, `${fmt(item.ratio, 2)}x`, fmt(item.psnr, 2), fmt(item.ssim, 4), fmt(item.p99, 3)]),
            [1.2, 0.68, 0.76, 0.68, 0.58, 0.62, 0.56],
            { rowHeight: 52, bodySize: 15 },
          ),
        ]),
        evidencePanel([
          t("Decision Point", { size: 30, bold: true }),
          metricCard("Runtime gain", pct(reduction(baseline.time, tile256.time), 1), "144.35s to 79.84s", COLORS.teal),
          metricCard("Memory gain", "31.3x", "52.01 GB to 1.66 GB", COLORS.green),
          bullet("Use 256 x 256 as the speed/memory recommendation.", "Quality is slightly lower than 512, but the operational savings are large.", COLORS.green),
          bullet("Keep 512 x 512 as the quality-safe backup.", "It has slightly better PSNR, SSIM, MAE, and high-percentile error.", COLORS.orange),
        ]),
      ]),
    ],
    "Source: results/2026-05-15-yifan-selected-256-512-n50/.",
  );
}

function addJacobSlide(presentation) {
  slideShell(
    presentation,
    "Jacob Compression-Side Experiment Is Now a Usable Table",
    "N=20 results cover the requested baseline, batch, resolution, checkpoint, scaling, and storage questions.",
    [
      grid({ width: fill, height: grow(1), columns: [fr(0.9), fr(1.1)], columnGap: 26 }, [
        evidencePanel([
          t("Operational Baseline", { size: 30, bold: true }),
          metricCard("Native batch 1", "144.32s", "per full-resolution image", COLORS.blue),
          metricCard("Peak memory", "52.0 GB", "native full-resolution", COLORS.orange),
          metricCard("Compression", "71.20x", "baseline_b02048", COLORS.teal),
          bullet("Batching is not helpful at 2K.", "Batch 1 is 7.35s/image; batch 2 and 4 are slower and use more memory.", COLORS.red),
        ]),
        evidencePanel([
          t("Checkpoint Roles", { size: 30, bold: true }),
          tableRows(
            ["Role", "Checkpoint", "Ratio", "PSNR", "SSIM"],
            checkpointRows.map((item) => [item.role, item.checkpoint, `${fmt(item.ratio, 2)}x`, fmt(item.psnr, 2), fmt(item.ssim, 3)]),
            [1.2, 0.82, 0.6, 0.55, 0.55],
            { rowHeight: 58, bodySize: 17 },
          ),
          bullet("Storage staging did not help.", "Shared: 143.86s/image; local: 143.89s/image.", COLORS.muted),
          bullet("Recommended default remains batch size 1.", "It is the safest setting for shared CDC workflows.", COLORS.blue),
        ]),
      ]),
    ],
    "Source: results/2026-05-22-jacob-compression-n20/.",
  );
}

function addPosterSlide(presentation) {
  slideShell(
    presentation,
    "Poster Visuals Now Show the Difference Map Directly",
    "The visual package follows the requested layout: original, reconstructed, hot difference map, histogram, metrics, and distribution.",
    [
      grid({ width: fill, height: fixed(610), columns: [fr(1), fr(1)], columnGap: 24 }, [
        panel({ width: fill, height: fill, fill: COLORS.white, line: COLORS.faint, borderRadius: 8, padding: { x: 16, y: 14 } },
          column({ width: fill, height: fill, gap: 10 }, [
            t("256 x 256 tiling panel", { size: 24, bold: true }),
            image({ path: pathTo("results/2026-05-22-yifan-poster-visual-qa/visual_examples_small/100_0005_0001_tile256_poster_panel.jpg"), width: fill, height: fixed(500), fit: "contain", alt: "Poster panel for 256 tiling" }),
          ])),
        panel({ width: fill, height: fill, fill: COLORS.white, line: COLORS.faint, borderRadius: 8, padding: { x: 16, y: 14 } },
          column({ width: fill, height: fill, gap: 10 }, [
            t("512 x 512 tiling panel", { size: 24, bold: true }),
            image({ path: pathTo("results/2026-05-22-yifan-poster-visual-qa/visual_examples_small/100_0005_0001_tile512_poster_panel.jpg"), width: fill, height: fixed(500), fit: "contain", alt: "Poster panel for 512 tiling" }),
          ])),
      ]),
      grid({ width: fill, height: fixed(126), columns: [fr(1), fr(1), fr(1)], columnGap: 16 }, [
        metricCard("Visual format", "Ready", "matches group-chat example", COLORS.green),
        metricCard("Cases", "3", "no tiling, 256, 512", COLORS.blue),
        metricCard("Next", "Regenerate raw", "for print-quality panels", COLORS.orange),
      ]),
    ],
    "Source: results/2026-05-22-yifan-poster-visual-qa/.",
  );
}

function addDecisionSlide(presentation) {
  slideShell(
    presentation,
    "Recommended Poster Story",
    "The message is now coherent: tiling makes reconstruction practical, checkpoint choice controls compression trade-off, and difference maps make quality inspectable.",
    [
      grid({ width: fill, height: grow(1), columns: [fr(1), fr(1)], columnGap: 26 }, [
        evidencePanel([
          badge("Use in poster", COLORS.greenSoft, COLORS.green),
          bullet("Main reconstruction setting: 256 x 256 tiling.", "Fastest selected run and lowest memory among tested cases.", COLORS.green),
          bullet("Quality-safe backup: 512 x 512 tiling.", "Use if visual artifacts appear in broader raw-panel review.", COLORS.orange),
          bullet("Compression setting language: checkpoint-based.", "The x-param path has no direct runtime compression-level knob.", COLORS.blue),
        ]),
        evidencePanel([
          badge("Write-up angle", COLORS.blueSoft, COLORS.blue),
          bullet("Report speed, memory, and ratio together.", "Avoid making compression ratio the only success metric.", COLORS.blue),
          bullet("Show difference maps next to scalar metrics.", "This makes small reconstruction differences visible to the poster audience.", COLORS.teal),
          bullet("Do not overclaim storage staging.", "N=20 shows no meaningful local-storage speed gain.", COLORS.muted),
        ]),
      ]),
      grid({ width: fill, height: fixed(136), columns: [fr(1), fr(1), fr(1)], columnGap: 16 }, [
        metricCard("Poster table", "Ready", "N=50 tiling + N=20 compression", COLORS.green),
        metricCard("Visual evidence", "Ready", "3 difference-map panels", COLORS.orange),
        metricCard("Remaining work", "Layout", "place tables and panels on poster", COLORS.blue),
      ]),
    ],
    "Source: committed GitHub result folders and runbooks.",
  );
}

function addNextStepsSlide(presentation) {
  slideShell(
    presentation,
    "Next Step Is Poster Assembly, Not More Setup",
    "All requested experiment lanes have a committed artifact. Further experiments should be targeted only if the poster needs one missing comparison.",
    [
      grid({ width: fill, height: grow(1), columns: [fr(1), fr(1), fr(1)], columnGap: 20 }, [
        evidencePanel([badge("1", COLORS.greenSoft, COLORS.green), t("Poster table", { size: 30, bold: true }), bullet("Use 256 vs 512 vs no tiling.", "Pull the N=50 tiling table directly from GitHub.", COLORS.green), bullet("Add checkpoint roles.", "High quality, balanced, high compression.", COLORS.green)]),
        evidencePanel([badge("2", COLORS.orangeSoft, COLORS.orange), t("Poster figures", { size: 30, bold: true }), bullet("Place one poster panel.", "Use 256 panel as primary visual evidence.", COLORS.orange), bullet("Regenerate from raw if needed.", "Use `make_poster_panels.py` on DeltaAI.", COLORS.orange)]),
        evidencePanel([badge("3", COLORS.blueSoft, COLORS.blue), t("Group update", { size: 30, bold: true }), bullet("Say what is done.", "Tiling, compression, and visual QA are all committed.", COLORS.blue), bullet("Ask for poster placement feedback.", "The next choice is layout emphasis.", COLORS.blue)]),
      ]),
    ],
    "Source: GitHub main branch after commits 47f85fb and 5fd6756.",
  );
}

function buildDeck() {
  const presentation = Presentation.create({ slideSize: { width: SLIDE.width, height: SLIDE.height } });
  addCover(presentation);
  addAgenda(presentation);
  addTilingSlide(presentation);
  addJacobSlide(presentation);
  addPosterSlide(presentation);
  addDecisionSlide(presentation);
  addNextStepsSlide(presentation);
  return presentation;
}

async function renderPreviews(presentation) {
  fs.mkdirSync(PREVIEW_DIR, { recursive: true });
  const slides = presentation.slides.items ?? presentation.slides;
  for (let index = 0; index < slides.length; index += 1) {
    const canvas = new Canvas(SLIDE.width, SLIDE.height);
    await drawSlideToCtx(slides[index], presentation, canvas.getContext("2d"));
    await canvas.toFile(path.join(PREVIEW_DIR, `slide_${String(index + 1).padStart(2, "0")}.png`));
  }
}

async function main() {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  fs.mkdirSync(PREVIEW_DIR, { recursive: true });
  const presentation = buildDeck();
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(OUTPUT);
  fs.copyFileSync(OUTPUT, ROOT_COPY);
  await renderPreviews(presentation);
  console.log(`Saved PPTX: ${OUTPUT}`);
  console.log(`Saved PPTX copy: ${ROOT_COPY}`);
  console.log(`Saved previews: ${PREVIEW_DIR}`);
}

await main();
