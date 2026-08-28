.PHONY: examples check clean

LATEXMK ?= latexmk
LATEXMK_FLAGS := -r .latexmkrc -interaction=nonstopmode -halt-on-error -pdf

EXAMPLES := \
	examples/demo.tex \
	examples/final-demo.tex \
	examples/package-demo.tex

examples:
	$(LATEXMK) $(LATEXMK_FLAGS) $(EXAMPLES)

check: examples
	sh tests/check.sh

clean:
	$(LATEXMK) -r .latexmkrc -C $(EXAMPLES) || true
	rm -rf build
