.PHONY: all clean

all: sc26_summary.pdf poster_draft.pdf artifact_description_appendix.pdf

sc26_summary.pdf: sc26_summary.tex references.bib
	tectonic sc26_summary.tex

poster_draft.pdf: poster_draft.tex
	tectonic poster_draft.tex

artifact_description_appendix.pdf: artifact_description_appendix.tex
	tectonic artifact_description_appendix.tex

clean:
	rm -f *.aux *.bbl *.blg *.log *.out *.xdv *.toc *.snm *.nav *.vrb
