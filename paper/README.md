# SC26 CDC DeltaAI Paper Draft

This directory contains an IEEE conference-mode LaTeX draft for the SC26 CDC DeltaAI paper.

## Files

| File | Use |
| --- | --- |
| `main.tex` | Main IEEEtran paper draft |
| `references.bib` | Minimal verified bibliography for the current draft |
| `figures/` | Lightweight figures copied from committed result folders |

## Compile

This machine does not currently have `pdflatex` or `latexmk`, but it does have `tectonic`:

```bash
cd /Users/yifn/Documents/sc26-cdc-deltaai/paper
tectonic main.tex
```

The current draft intentionally leaves the full related-work section for a later pass. The core narrative, methods, results, discussion, and conclusion are filled in from the repository's committed experiment artifacts.
