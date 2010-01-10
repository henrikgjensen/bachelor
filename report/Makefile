all: pdf

pdf: report.tex referencelist.bib sections/*
	pdflatex report.tex
	bibtex report
	pdflatex report.tex
	pdflatex report.tex

test: test.tex litteraturliste.bib afsnit/*
	pdflatex test.tex
	bibtex test
	pdflatex test.tex
	pdflatex test.tex
	mv -f test.pdf rapport.pdf
