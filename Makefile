MAIN := what-is-ai-for-courts
BUILD := build
OUTPUT := output/pdf
DOCX_OUTPUT := output/docx
DOCX_LAYOUT := scripts/apply_harvardjolt_docx_layout.py
DOCX_FILES := $(DOCX_OUTPUT)/before-the-merits.docx $(DOCX_OUTPUT)/实体审理前.docx
PYTHON ?= python3

.PHONY: all pdf docx test-docx-layout test-docx-converter clean clean-docx

all: pdf

pdf:
	mkdir -p $(BUILD) $(OUTPUT)
	TEXINPUTS=".:americanlawreview:" BIBINPUTS=".:" latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=$(BUILD) $(MAIN).tex
	cp $(BUILD)/$(MAIN).pdf $(OUTPUT)/$(MAIN).pdf

docx:
	$(PYTHON) $(DOCX_LAYOUT) $(DOCX_FILES)

test-docx-layout:
	$(PYTHON) $(DOCX_LAYOUT) --check $(DOCX_FILES)

test-docx-converter:
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py'

clean:
	$(RM) -r $(BUILD)

clean-docx:
	@echo "DOCX source artifacts are retained; rerun 'make docx' to apply the layout."
