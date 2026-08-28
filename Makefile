MAIN := what-is-ai-for-courts
BUILD := build
OUTPUT := output/pdf
DOCX_OUTPUT := output/docx
DOCX_FILE := $(DOCX_OUTPUT)/$(MAIN).docx
DOCX_REVIEW := $(DOCX_OUTPUT)/$(MAIN).review.json
PYTHON ?= python3

.PHONY: all pdf docx test-docx-converter clean clean-docx

all: pdf

pdf:
	mkdir -p $(BUILD) $(OUTPUT)
	TEXINPUTS=".:americanlawreview:" BIBINPUTS=".:" latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=$(BUILD) $(MAIN).tex
	cp $(BUILD)/$(MAIN).pdf $(OUTPUT)/$(MAIN).pdf

docx:
	mkdir -p $(DOCX_OUTPUT)
	$(PYTHON) scripts/footnote_to_docx.py $(MAIN).tex --output $(DOCX_FILE) --force

test-docx-converter:
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py'

clean:
	latexmk -C -outdir=$(BUILD) $(MAIN).tex

clean-docx:
	$(RM) $(DOCX_FILE) $(DOCX_REVIEW)
	@rmdir $(DOCX_OUTPUT) 2>/dev/null || true
