# 2026-06-07 Experiment Response Complete Slides

This folder contains the SC26 CDC deck that summarizes the completed June 2
experiment-response package: compression optimization, reconstruction and the
tile-size tradeoff matrix, object-detection impact, SAM mask stability, and the
GH200 vs H200 hardware add-on.

Content source: `SC26_CDC_June2_Experiment_Setup_Response_EN.docx` and the
repository `README.md` / poster storyline.

## Deck

| File | Use |
| --- | --- |
| `SC26_CDC_Experiment_Response_Complete_2026-06-07.pptx` | Standalone editable PowerPoint deck (12 slides, 16:9) |
| `src/create_experiment_response_deck.js` | Rebuild script |

Generated `output/`, `scratch/`, and `node_modules/` files are local build
artifacts and are not tracked.

## Rebuild

Run from this folder:

```bash
npm install pptxgenjs
node src/create_experiment_response_deck.js
```

Note: earlier decks in this repo used an internal layout tool that is not
publicly installable, so this deck is built with `pptxgenjs` and styled to match
the same navy/blue palette, Aptos fonts, metric cards, and navy-header tables.
Figures are pulled from committed `results/` panels and reconstruction examples.
