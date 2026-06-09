/*
 * SC26 CDC — June 2 Experiment-Response Complete deck.
 * Built with pptxgenjs, styled to match the repo's prior SC26 CDC decks
 * (navy/blue palette, Aptos fonts, metric cards, navy-header tables).
 * Content source: SC26_CDC_June2_Experiment_Setup_Response_EN.docx + README.
 */
const path = require("node:path");
const fs = require("node:fs");
const pptxgen = require("pptxgenjs");

const HERE = __dirname;
const FOLDER = path.resolve(HERE, "..");
const REPO = path.resolve(HERE, "..", "..", "..");
const DESKTOP = "/Users/yifn/Desktop/26 SC";
const FINAL_NAME = "SC26_CDC_Experiment_Response_Complete_2026-06-07.pptx";

const C = {
  bg: "F7F9FC", ink: "172033", muted: "5B667A", faint: "E4E9F2", white: "FFFFFF",
  navy: "0B1B32", blue: "2563EB", teal: "0F766E", green: "15803D", orange: "D97706",
  red: "B91C1C", lavender: "EEF2FF", tealSoft: "E7F6F2", orangeSoft: "FFF7ED",
  blueSoft: "EAF1FF", greenSoft: "ECFDF5", graySoft: "F1F5F9",
};
const DISPLAY = "Aptos Display";
const BODY = "Aptos";
const MX = 0.55, CW = 13.333 - 2 * MX, FOOT_Y = 7.05;

const img = (rel) => path.join(REPO, rel);
const HERO = img("results/2026-04-26-reconstruction/visual_examples_small/original_100_0005_0001_small.jpg");
const PANEL = img("results/2026-05-22-yifan-poster-visual-qa/visual_examples_small/100_0005_0001_tile256_poster_panel.jpg");

const pres = new pptxgen();
pres.defineLayout({ name: "W", width: 13.333, height: 7.5 });
pres.layout = "W";
pres.author = "Yifan Yang";
pres.title = "SC26 CDC Experiment Response Complete";

/* ---------- helpers ---------- */
function title(slide, t, sub) {
  slide.addText(t, { x: MX, y: 0.4, w: CW, h: 0.6, fontSize: 27, bold: true, color: C.ink, fontFace: DISPLAY, valign: "middle", margin: 0 });
  if (sub) slide.addText(sub, { x: MX, y: 1.02, w: CW, h: 0.5, fontSize: 13.5, color: C.muted, fontFace: BODY, valign: "top", margin: 0 });
  slide.addShape("rect", { x: MX, y: sub ? 1.55 : 1.12, w: 1.3, h: 0.055, fill: { color: C.blue }, line: { color: C.blue } });
  return sub ? 1.8 : 1.35;
}
function footer(slide, source) {
  slide.addText(source, { x: MX, y: FOOT_Y, w: 9, h: 0.3, fontSize: 9, color: "6B7280", align: "left", valign: "middle", fontFace: BODY, margin: 0 });
  slide.addText("SC26 CDC · DeltaAI experiment response · June 7, 2026", { x: MX + 9, y: FOOT_Y, w: CW - 9, h: 0.3, fontSize: 9, color: "6B7280", align: "right", valign: "middle", fontFace: BODY, margin: 0 });
}
function card(slide, x, y, w, h, label, value, detail, accent, fill = C.white, dark = false) {
  slide.addShape("roundRect", { x, y, w, h, rectRadius: 0.06, fill: { color: fill }, line: { color: fill === C.white ? C.faint : fill, width: 1 } });
  const lc = dark ? "C7D2E5" : C.muted, dc = dark ? "AEB9CC" : C.muted;
  slide.addText(label, { x: x + 0.18, y: y + 0.12, w: w - 0.36, h: 0.3, fontSize: 11, bold: true, color: lc, fontFace: BODY, valign: "top", margin: 0 });
  slide.addText(value, { x: x + 0.18, y: y + 0.4, w: w - 0.36, h: h - 0.78, fontSize: 23, bold: true, color: accent, fontFace: DISPLAY, valign: "middle", margin: 0 });
  if (detail) slide.addText(detail, { x: x + 0.18, y: y + h - 0.42, w: w - 0.36, h: 0.36, fontSize: 10, color: dc, fontFace: BODY, valign: "middle", margin: 0 });
}
function bullet(slide, x, y, w, label, detail, color, h = 0.66) {
  slide.addShape("rect", { x, y: y + 0.06, w: 0.12, h: 0.12, fill: { color }, line: { color } });
  slide.addText([
    { text: label, options: { bold: true, color: C.ink, fontSize: 13, breakLine: true } },
    { text: detail || "", options: { color: C.muted, fontSize: 11 } },
  ], { x: x + 0.26, y, w: w - 0.26, h, valign: "top", fontFace: BODY, margin: 0, lineSpacingMultiple: 1.0 });
}
function badge(slide, x, y, w, text, fill, color) {
  slide.addShape("roundRect", { x, y, w, h: 0.34, rectRadius: 0.08, fill: { color: fill }, line: { color: fill } });
  slide.addText(text, { x, y, w, h: 0.34, fontSize: 11, bold: true, color, align: "center", valign: "middle", fontFace: BODY, margin: 0 });
}
function panelBox(slide, x, y, w, h, fill = C.white) {
  slide.addShape("roundRect", { x, y, w, h, rectRadius: 0.05, fill: { color: fill }, line: { color: C.faint, width: 1 } });
}
function table(slide, x, y, w, headers, rows, colW, aligns, opt = {}) {
  const hs = opt.headerSize || 10.5, bs = opt.bodySize || 11, rh = opt.rowH || 0.34, hh = opt.headerH || 0.36;
  const head = headers.map((c, i) => ({ text: c, options: { fill: { color: C.navy }, color: C.white, bold: true, fontSize: hs, align: aligns[i], valign: "middle", fontFace: BODY } }));
  const body = rows.map((r, ri) => r.map((c, i) => ({ text: String(c), options: { fill: { color: ri % 2 ? C.graySoft : C.white }, color: opt.rowColors && opt.rowColors[ri] ? opt.rowColors[ri] : C.ink, bold: !!(opt.boldFirst && i === 0), fontSize: bs, align: aligns[i], valign: "middle", fontFace: BODY } })));
  slide.addTable([head, ...body], {
    x, y, w, colW, rowH: [hh, ...rows.map(() => rh)],
    border: { type: "solid", pt: 0.75, color: C.faint }, margin: [2, 4, 2, 4], valign: "middle", autoPage: false,
  });
}

/* ---------- 1. Cover ---------- */
{
  const s = pres.addSlide(); s.background = { color: C.navy };
  s.addShape("rect", { x: 0, y: 0, w: 7.6, h: 7.5, fill: { color: C.navy }, line: { color: C.navy } });
  badge(s, MX, 0.6, 1.7, "SC26 CDC", "12345C", "BFE8FF");
  badge(s, MX + 1.85, 0.6, 2.2, "DeltaAI GH200", "163B32", "C9F4E8");
  s.addText("Compression Experiment Response Is Complete", { x: MX, y: 1.25, w: 6.7, h: 2.0, fontSize: 42, bold: true, color: C.white, fontFace: DISPLAY, valign: "top", margin: 0, lineSpacingMultiple: 0.98 });
  s.addText("CDC conditional-diffusion lossy compression and reconstruction of high-resolution drone imagery on DeltaAI. All June 2 workflows — compression, reconstruction, the tradeoff matrix, detection, and SAM — are done.", { x: MX, y: 3.35, w: 6.7, h: 1.2, fontSize: 15, color: "D7E3F5", fontFace: BODY, valign: "top", margin: 0 });
  card(s, MX, 4.75, 2.13, 1.3, "Compression", "79.98×", "balanced · 256 tile", "86EFAC", "102848", true);
  card(s, MX + 2.28, 4.75, 2.13, 1.3, "GPU peak", "≈1.6 GB", "from ~52 GB full-image", "7DD3FC", "102848", true);
  card(s, MX + 4.56, 4.75, 2.14, 1.3, "Workflows", "6 / 6", "complete (2 as pilots)", "FDBA74", "102848", true);
  s.addText("Prepared by Yifan Yang · Updated June 7, 2026 · rayford295/sc26-cdc-deltaai @ d87a8a9", { x: MX, y: 6.35, w: 6.7, h: 0.4, fontSize: 11, color: "9FB0C9", fontFace: BODY, valign: "middle", margin: 0 });
  // right: hero drone image
  panelBox(s, 8.0, 0.6, 4.78, 6.3, "12345C");
  s.addImage({ path: HERO, x: 8.18, y: 0.78, w: 4.42, h: 5.4, sizing: { type: "contain", w: 4.42, h: 5.4 } });
  s.addText("Galveston, TX — 100 RGB drone images, ≈5472×3648 px, ≈8.34 MB each, ~47 m altitude.", { x: 8.18, y: 6.22, w: 4.42, h: 0.6, fontSize: 11, color: "C7D2E5", fontFace: BODY, valign: "top", margin: 0 });
}

/* ---------- 2. Question & Setup ---------- */
{
  const s = pres.addSlide(); s.background = { color: C.bg };
  const by = title(s, "The Systems Question Behind the Poster", "Can a CDC compression and reconstruction workflow cut HPC storage and transfer pressure while preserving enough quality for inspection and downstream computer vision?");
  // left cards (setup), right image
  const lw = 7.4;
  card(s, MX, by + 0.05, lw / 2 - 0.12, 1.35, "Data", "100 images", "≈5472×3648 px · ≈8.34 MB · ~47 m", C.blue);
  card(s, MX + lw / 2 + 0.12, by + 0.05, lw / 2 - 0.12, 1.35, "Baseline", "fp32 · 65 steps", "native full-res · batch size 1", C.teal);
  card(s, MX, by + 1.55, lw / 2 - 0.12, 1.35, "Platform", "GH200", "DeltaAI main · H200 compare", C.orange);
  card(s, MX + lw / 2 + 0.12, by + 1.55, lw / 2 - 0.12, 1.35, "Metrics", "11 families", "time · GPU · BPP · PSNR/SSIM/LPIPS · CV", C.green);
  s.addText("Controlled settings: checkpoint, tile size, tile batch, denoising steps, precision, resolution, and storage placement.", { x: MX, y: by + 3.05, w: lw, h: 0.6, fontSize: 12, italic: true, color: C.muted, fontFace: BODY, valign: "top", margin: 0 });
  panelBox(s, MX + lw + 0.25, by + 0.05, CW - lw - 0.25, 3.6);
  s.addImage({ path: HERO, x: MX + lw + 0.42, y: by + 0.22, w: CW - lw - 0.59, h: 2.85, sizing: { type: "contain", w: CW - lw - 0.59, h: 2.85 } });
  s.addText("Representative drone survey scene: vehicles, roads, and buildings drive the downstream-CV tests.", { x: MX + lw + 0.42, y: by + 3.12, w: CW - lw - 0.59, h: 0.5, fontSize: 10.5, color: C.muted, fontFace: BODY, valign: "top", margin: 0 });
  footer(s, "Source: poster storyline and run setup in README + experiment-response document.");
}

/* ---------- 3. Completion status ---------- */
{
  const s = pres.addSlide(); s.background = { color: C.bg };
  const by = title(s, "Every Requested Workflow Is Complete", "Implementation and the main DeltaAI runs are done; the only open items are quality upgrades before paper-grade detection claims.");
  table(s, MX, by + 0.05, CW,
    ["Item", "Question", "Status", "Evidence"],
    [
      ["Experiment 1", "Compression optimization", "Complete", "Checkpoint-controlled settings selected; b00064 balanced, b00128 stress test."],
      ["Experiment 2", "Reconstruction optimization", "Complete", "256 and 512 tiling validated; 256 fastest/lowest memory, 512 quality backup."],
      ["Experiment 3", "Compression × tile-size tradeoff", "Complete", "N50 LPIPS matrix finished all 9 rows on GH200 (Slurm 2422336)."],
      ["Experiment 4", "Object-detection impact", "Complete (pilot)", "N50 COCO YOLOv8x vehicle workflow finished (2426722); labels are draft."],
      ["Add-on", "SAM zero-shot mask stability", "Complete (pilot)", "SAM ViT-H on 50 images, 829 prompts (2426827); 0 failed prompts."],
      ["Add-on", "GH200 vs H200 comparison", "Complete", "H200 runs the workflow and is ~3.6% faster at matched step counts."],
    ],
    [1.5, 3.0, 1.5, 6.23], ["left", "left", "left", "left"],
    { rowH: 0.66, bodySize: 11, boldFirst: true,
      rowColors: [C.green, C.green, C.green, C.orange, C.orange, C.green] });
  footer(s, "Source: experiment-response completion table; Slurm job IDs as cited.");
}

/* ---------- 4. Executive recommendation ---------- */
{
  const s = pres.addSlide(); s.background = { color: C.bg };
  const by = title(s, "Recommended Setting: Balanced b00064 + 256 Tile", "Best speed and memory profile in the formal N50 tradeoff run, with a quality-safe backup and a stress-test ceiling.");
  card(s, MX, by + 0.05, 3.85, 1.5, "Primary (deploy)", "b00064 · 256", "79.34 s/img · 1.57 GB · 79.98×", C.green, C.greenSoft);
  card(s, MX + 4.05, by + 0.05, 3.85, 1.5, "Quality-safe backup", "b00064 · 512", "86.0 s/img · 2.90 GB · 78.48×", C.orange, C.orangeSoft);
  card(s, MX + 8.1, by + 0.05, CW - 8.1, 1.5, "Stress test only", "b00128 · 256", "139.89× · PSNR 30.89", C.red, C.lavender);
  panelBox(s, MX, by + 1.75, CW, 3.05);
  s.addText("Why 256 tiling wins operationally", { x: MX + 0.3, y: by + 1.92, w: CW - 0.6, h: 0.4, fontSize: 17, bold: true, color: C.ink, fontFace: DISPLAY, margin: 0 });
  bullet(s, MX + 0.3, by + 2.45, 5.9, "Peak GPU memory: ~52 GB → ~1.6 GB.", "256 tiling makes full-resolution reconstruction practical on shared GPUs.", C.green);
  bullet(s, MX + 0.3, by + 3.25, 5.9, "Runtime: ~143 s → ~79 s per image.", "Fastest and lowest-memory setting in the N50 matrix.", C.green);
  bullet(s, MX + 6.4, by + 2.45, 6.0, "Quality at 256: PSNR 33.14 · SSIM 0.877 · LPIPS 0.00183.", "Only marginally below 512; 512 is slightly better on PSNR/SSIM/LPIPS and seams.", C.orange);
  bullet(s, MX + 6.4, by + 3.25, 6.0, "b00128 saves the most storage (139.9×).", "But shows the largest quality and detection drop — keep as a ceiling only.", C.red);
  footer(s, "Source: results/2026-06-05-tradeoff-n50-lpips/ (combined_summary).");
}

/* ---------- 5. Experiment 1: compression ---------- */
{
  const s = pres.addSlide(); s.background = { color: C.bg };
  const by = title(s, "Experiment 1 — Compression Is Controlled by Checkpoint", "The x-parameterization CDC path has no continuous runtime ratio knob; compression is set by checkpoint and reported via measured BPP and ratio.");
  table(s, MX, by + 0.05, 8.4,
    ["Role", "Ckpt", "Sec/img", "GPU GB", "BPP", "Ratio", "PSNR", "SSIM"],
    [
      ["High quality", "b00512", "143.73", "50.8", "0.7345", "32.67×", "34.84", "0.9423"],
      ["Balanced", "b00064", "143.66", "50.7", "0.2578", "93.11×", "33.73", "0.8803"],
      ["High compression", "b00128", "143.70", "50.7", "0.1448", "165.73×", "31.52", "0.8281"],
      ["Baseline", "b02048", "143.70", "50.8", "0.3371", "71.20×", "29.45", "0.8727"],
    ],
    [1.7, 0.95, 1.0, 0.95, 0.95, 0.95, 0.95, 0.95],
    ["left", "left", "right", "right", "right", "right", "right", "right"],
    { rowH: 0.5, bodySize: 11.5, boldFirst: true });
  s.addText("N=20 checkpoint sweep (full-image). These settings feed the formal N50 tradeoff run.", { x: MX, y: by + 2.9, w: 8.4, h: 0.4, fontSize: 11, italic: true, color: C.muted, fontFace: BODY, margin: 0 });
  const rx = MX + 8.65, rw = CW - 8.65;
  card(s, rx, by + 0.05, rw, 1.05, "Main candidate", "b00064", "93.11× · PSNR 33.73", C.blue);
  card(s, rx, by + 1.25, rw, 1.05, "Ratio ceiling", "165.7×", "b00128 stress test", C.red);
  card(s, rx, by + 2.45, rw, 1.05, "Fidelity ref.", "34.84 dB", "b00512 high quality", C.teal);
  footer(s, "Source: results/2026-05-22-jacob-compression-n20/.");
}

/* ---------- 6. Experiments 2 & 3: tradeoff matrix ---------- */
{
  const s = pres.addSlide(); s.background = { color: C.bg };
  const by = title(s, "Experiments 2 & 3 — Reconstruction × Tile-Size Tradeoff", "Formal N50 run (LPIPS on) across checkpoint roles and tile sizes. Rows most relevant to the recommendation and downstream tests.");
  table(s, MX, by + 0.05, CW,
    ["Configuration", "Setting", "Sec/img", "GPU GB", "Ratio", "Storage saved", "PSNR", "SSIM", "LPIPS"],
    [
      ["High quality 512", "b00512 + 512", "88.51", "2.96", "29.73×", "96.64%", "34.19", "0.9376", "0.002591"],
      ["Balanced 256  ◀ recommended", "b00064 + 256", "79.34", "1.57", "79.98×", "98.75%", "33.14", "0.8768", "0.001826"],
      ["Balanced 512  (backup)", "b00064 + 512", "86.00", "2.90", "78.48×", "98.73%", "33.23", "0.8782", "0.001792"],
      ["Max compression 256", "b00128 + 256", "78.91", "1.57", "139.89×", "99.29%", "30.89", "0.8193", "0.005676"],
    ],
    [3.0, 1.7, 1.0, 1.0, 1.0, 1.4, 0.94, 0.94, 1.25],
    ["left", "left", "right", "right", "right", "right", "right", "right", "right"],
    { rowH: 0.52, bodySize: 11, boldFirst: true,
      rowColors: [C.ink, C.green, C.orange, C.red] });
  s.addText("System readout: 256 tiling cuts peak GPU memory from ~52 GB (full-image) to ~1.6 GB and runtime from ~143 s to ~79 s per image. 512 is slower and heavier, but slightly safer on image-quality metrics.", { x: MX, y: by + 3.0, w: CW, h: 0.8, fontSize: 12.5, color: C.ink, fontFace: BODY, valign: "top", margin: 0 });
  footer(s, "Source: results/2026-06-05-tradeoff-n50-lpips/. Storage saved vs native full-resolution.");
}

/* ---------- 7. Tile-size screening ---------- */
{
  const s = pres.addSlide(); s.background = { color: C.bg };
  const by = title(s, "Why 256 — Early Tile-Size Screening (512 / 1024 / 2048)", "Before the N50 matrix, a baseline_b02048 pilot on 8 full-resolution images explained why larger tiles were dropped.");
  table(s, MX, by + 0.05, 8.4,
    ["Tile", "Time/img", "GPU memory", "PSNR", "SSIM", "Conclusion"],
    [
      ["No tiling", "143.55 s", "52.0 GB", "29.88", "0.8847", "Reference; too slow & memory-heavy"],
      ["512 × 512", "86.01 s", "3.0 GB", "29.73", "0.8822", "Best speed/memory at that stage"],
      ["1024 × 1024", "88.35 s", "11.2 GB", "29.82", "0.8835", "Slightly better quality, far more memory"],
      ["2048 × 2048", "95.39 s", "43.8 GB", "29.90", "0.8841", "Near no-tiling; loses tiling benefit"],
    ],
    [1.3, 1.1, 1.2, 0.85, 0.85, 3.1],
    ["left", "right", "right", "right", "right", "left"],
    { rowH: 0.56, bodySize: 11, boldFirst: true });
  const rx = MX + 8.65, rw = CW - 8.65;
  panelBox(s, rx, by + 0.05, rw, 2.66, C.blueSoft);
  s.addText("Takeaway", { x: rx + 0.22, y: by + 0.22, w: rw - 0.44, h: 0.35, fontSize: 15, bold: true, color: C.blue, fontFace: DISPLAY, margin: 0 });
  s.addText("512 was best at the screening stage. Larger tiles kept quality marginally closer to no-tiling but cost far more memory. Once 256 was added it beat 512 on speed and memory, so the formal matrix focused on 256 and 512.", { x: rx + 0.22, y: by + 0.68, w: rw - 0.44, h: 1.85, fontSize: 12.5, color: C.ink, fontFace: BODY, valign: "top", margin: 0 });
  footer(s, "Source: baseline_b02048 tile-size pilot (8 full-resolution images).");
}

/* ---------- 8. Reconstruction quality is inspectable (poster panel) ---------- */
{
  const s = pres.addSlide(); s.background = { color: C.bg };
  const by = title(s, "Reconstruction Quality Is Visually Inspectable", "Difference maps put small reconstruction errors next to scalar metrics — the poster's quality-evidence visual for the 256 setting.");
  panelBox(s, MX, by + 0.05, 8.6, 4.55);
  s.addImage({ path: PANEL, x: MX + 0.2, y: by + 0.2, w: 8.2, h: 4.25, sizing: { type: "contain", w: 8.2, h: 4.25 } });
  const rx = MX + 8.85, rw = CW - 8.85;
  card(s, rx, by + 0.05, rw, 1.05, "PSNR", "28.78 dB", "256 tile, this scene", C.teal);
  card(s, rx, by + 1.25, rw, 1.05, "SSIM", "0.8552", "structural similarity", C.blue);
  card(s, rx, by + 2.45, rw, 1.05, "Mean diff", "0.0275", "max diff 0.687", C.orange);
  bullet(s, rx, by + 3.7, rw, "Errors concentrate on edges.", "Hot map highlights roof lines, road markings, and vehicles.", C.red, 0.8);
  footer(s, "Source: results/2026-05-22-yifan-poster-visual-qa/ (256 tiling poster panel).");
}

/* ---------- 9. Experiment 4: detection ---------- */
{
  const s = pres.addSlide(); s.background = { color: C.bg };
  const by = title(s, "Experiment 4 — Object-Detection Impact (Pilot)", "Fixed COCO YOLOv8x detector; COCO car/bus/truck → one pilot vehicle class; compared on 50 draft-labeled images (829 boxes).");
  table(s, MX, by + 0.05, 8.7,
    ["Configuration", "mAP@.5", "mAP@.5:.95", "Precision", "Recall", "F1", "Pred"],
    [
      ["Original", "0.6902", "0.5711", "0.0635", "0.8432", "0.1182", "11002"],
      ["High quality 512", "0.6329", "0.2706", "0.0625", "0.8094", "0.1160", "10742"],
      ["Balanced 256", "0.6280", "0.2712", "0.0601", "0.8070", "0.1118", "11137"],
      ["Balanced 512", "0.6225", "0.2703", "0.0592", "0.8070", "0.1102", "11310"],
      ["Max compression 256", "0.5889", "0.2603", "0.0568", "0.7720", "0.1059", "11260"],
    ],
    [2.5, 1.05, 1.2, 1.05, 0.95, 0.9, 1.05],
    ["left", "right", "right", "right", "right", "right", "right"],
    { rowH: 0.48, bodySize: 11, boldFirst: true,
      rowColors: [C.ink, C.ink, C.green, C.orange, C.red] });
  const rx = MX + 8.95, rw = CW - 8.95;
  bullet(s, rx, by + 0.1, rw, "Balanced stays close to original.", "mAP@.5 0.690 → 0.628; max-compression drops to 0.589.", C.green, 0.85);
  bullet(s, rx, by + 1.05, rw, "Low precision is intentional.", "conf=0.001 keeps many low-confidence boxes for AP/recall.", C.muted, 0.85);
  bullet(s, rx, by + 2.0, rw, "Pilot, not a benchmark.", "Draft labels → sensitivity evidence; review labels before paper claims.", C.red, 0.95);
  footer(s, "Source: results/2026-06-06-detection-coco-vehicle-n50/. Labels are draft.");
}

/* ---------- 10. SAM mask stability ---------- */
{
  const s = pres.addSlide(); s.background = { color: C.bg };
  const by = title(s, "Add-On — SAM Zero-Shot Mask Stability (Pilot)", "Promptable SAM ViT-H masks from reconstructed vs original images, same box prompts — a class-agnostic boundary-stability check.");
  table(s, MX, by + 0.05, 8.7,
    ["Configuration", "Mask IoU", "Dice", "Area ratio", "Centroid shift", "Failed"],
    [
      ["Original", "1.0000", "1.0000", "1.0000", "0.00 px", "0%"],
      ["Balanced 256", "0.7056", "0.8110", "1.0193", "16.76 px", "0%"],
      ["Balanced 512", "0.7061", "0.8116", "1.0133", "16.81 px", "0%"],
      ["Max compression 256", "0.7048", "0.8107", "1.0229", "16.67 px", "0%"],
    ],
    [2.6, 1.15, 1.0, 1.15, 1.5, 0.9],
    ["left", "right", "right", "right", "right", "right"],
    { rowH: 0.52, bodySize: 11.5, boldFirst: true,
      rowColors: [C.ink, C.green, C.orange, C.red] });
  const rx = MX + 8.95, rw = CW - 8.95;
  card(s, rx, by + 0.05, rw, 1.1, "Prompts", "829 / 829", "all returned usable masks", C.green);
  card(s, rx, by + 1.3, rw, 1.1, "Failed rate", "0.0%", "every configuration", C.teal);
  bullet(s, rx, by + 2.65, rw, "Balanced 512 slightly best.", "On IoU, Dice, and area stability; 256 nearly tied → stays the pick.", C.orange, 0.9);
  footer(s, "Source: results/2026-06-06-sam-mask-impact-n50/ (50 images, 829 prompts).");
}

/* ---------- 11. Hardware + evidence ---------- */
{
  const s = pres.addSlide(); s.background = { color: C.bg };
  const by = title(s, "Hardware Check and Evidence Package", "H200 runs the same workflow and is modestly faster; all results are committed as GitHub-safe summaries.");
  // left: hardware table
  s.addText("GH200 vs H200 (fp32, matched steps)", { x: MX, y: by + 0.05, w: 5.8, h: 0.35, fontSize: 14, bold: true, color: C.ink, fontFace: DISPLAY, margin: 0 });
  table(s, MX, by + 0.45, 5.8,
    ["Steps", "GH200 s/img", "H200 s/img", "Speedup"],
    [["5", "11.27", "10.87", "3.6%"], ["20", "44.37", "42.74", "3.7%"], ["65", "143.67", "138.48", "3.6%"]],
    [1.1, 1.7, 1.7, 1.3], ["right", "right", "right", "right"],
    { rowH: 0.5, bodySize: 12 });
  s.addText("Modest gain — base experiment selection on checkpoint and tile behavior before broad H200 reruns.", { x: MX, y: by + 2.55, w: 5.8, h: 0.6, fontSize: 11, italic: true, color: C.muted, fontFace: BODY, valign: "top", margin: 0 });
  // right: evidence
  s.addText("Evidence package (committed)", { x: MX + 6.1, y: by + 0.05, w: CW - 6.1, h: 0.35, fontSize: 14, bold: true, color: C.ink, fontFace: DISPLAY, margin: 0 });
  table(s, MX + 6.1, by + 0.45, CW - 6.1,
    ["Evidence", "Repository folder"],
    [
      ["Compression × tile matrix", "results/2026-06-05-tradeoff-n50-lpips/"],
      ["Detection impact, N50", "results/2026-06-06-detection-coco-vehicle-n50/"],
      ["SAM mask stability, N50", "results/2026-06-06-sam-mask-impact-n50/"],
      ["Experiment code", "experiments/compression/"],
    ],
    [2.7, 3.53], ["left", "left"],
    { rowH: 0.5, bodySize: 10.5, boldFirst: true });
  s.addText("Publication boundary: GitHub stores lightweight tables, summaries, manifests, and docs. Full-resolution images, logs, weights, and raw outputs stay on /projects/bfod/$USER/cdc-deltaai/.", { x: MX + 6.1, y: by + 2.95, w: CW - 6.1, h: 0.65, fontSize: 10.5, color: C.muted, fontFace: BODY, valign: "top", margin: 0 });
  footer(s, "Source: results/2026-04-28-h200-reconstruction/ and committed evidence folders.");
}

/* ---------- 12. Final answer & next steps ---------- */
{
  const s = pres.addSlide(); s.background = { color: C.navy };
  s.addShape("rect", { x: 0, y: 0, w: 13.333, h: 7.5, fill: { color: C.navy }, line: { color: C.navy } });
  badge(s, MX, 0.6, 2.4, "Final answer", "12345C", "BFE8FF");
  s.addText("All Requested Workflows Are Done", { x: MX, y: 1.05, w: CW, h: 0.9, fontSize: 36, bold: true, color: C.white, fontFace: DISPLAY, valign: "top", margin: 0 });
  s.addText("Recommended setting: balanced_checkpoint_b00064 with 256 × 256 tiling, and b00064 + 512 × 512 as the quality-safe backup when fidelity is prioritized.", { x: MX, y: 1.95, w: CW, h: 0.8, fontSize: 16, color: "D7E3F5", fontFace: BODY, valign: "top", margin: 0 });
  card(s, MX, 2.95, 3.95, 1.35, "Deploy", "b00064 · 256", "79.98× · 1.6 GB · 79 s", "86EFAC", "102848", true);
  card(s, MX + 4.15, 2.95, 3.95, 1.35, "Backup", "b00064 · 512", "quality-safe", "FDBA74", "102848", true);
  card(s, MX + 8.3, 2.95, CW - 8.3, 1.35, "Ceiling", "b00128 · 256", "stress test only", "FCA5A5", "102848", true);
  s.addText("Remaining non-blocking quality steps", { x: MX, y: 4.6, w: CW, h: 0.4, fontSize: 16, bold: true, color: "BFE8FF", fontFace: DISPLAY, margin: 0 });
  bullet2(s, MX, 5.1, "Review and correct the N50 draft labels.", "First gate before stronger detection claims.");
  bullet2(s, MX, 5.6, "Expand the reviewed label set if time allows.", "Improves benchmark credibility.");
  bullet2(s, MX + 6.4, 5.1, "Rerun Experiment 4 with a project-specific detector.", "When one becomes available.");
  bullet2(s, MX + 6.4, 5.6, "Then promote pilots to paper-grade benchmarks.", "Detection + SAM are workflow-complete today.");
  s.addText("rayford295/sc26-cdc-deltaai @ d87a8a9 · Prepared by Yifan Yang · June 7, 2026", { x: MX, y: 6.7, w: CW, h: 0.4, fontSize: 11, color: "9FB0C9", fontFace: BODY, valign: "middle", margin: 0 });
}
function bullet2(s, x, y, label, detail) {
  s.addShape("rect", { x, y: y + 0.05, w: 0.12, h: 0.12, fill: { color: "7DD3FC" }, line: { color: "7DD3FC" } });
  s.addText([
    { text: label + "  ", options: { bold: true, color: C.white, fontSize: 12.5 } },
    { text: detail, options: { color: "C7D2E5", fontSize: 11 } },
  ], { x: x + 0.24, y: y - 0.02, w: 6.0, h: 0.45, valign: "top", fontFace: BODY, margin: 0 });
}

const OUT_FOLDER = path.join(FOLDER, FINAL_NAME);
pres.writeFile({ fileName: OUT_FOLDER }).then(() => {
  console.log("Saved:", OUT_FOLDER);
  // Optional local convenience copy; skipped if the directory is absent.
  try {
    if (fs.existsSync(DESKTOP)) {
      fs.copyFileSync(OUT_FOLDER, path.join(DESKTOP, FINAL_NAME));
      console.log("Saved:", path.join(DESKTOP, FINAL_NAME));
    }
  } catch (_) { /* non-fatal */ }
});
