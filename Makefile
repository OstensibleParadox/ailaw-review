MAIN := what-is-ai-for-courts
BUILD := build
OUTPUT := output/pdf

.PHONY: all pdf clean

all: pdf

pdf:
	mkdir -p $(BUILD) $(OUTPUT)
	TEXINPUTS=".:americanlawreview:" BIBINPUTS=".:" latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=$(BUILD) $(MAIN).tex
	cp $(BUILD)/$(MAIN).pdf $(OUTPUT)/$(MAIN).pdf

clean:
	latexmk -C -outdir=$(BUILD) $(MAIN).tex
