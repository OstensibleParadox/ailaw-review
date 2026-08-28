# The Architecture of AI Responsibility

**Subtitle:** *Deployment Control, Enterprise-Facing Recourse, and the Anti-Substitution Principle*

This directory contains the reconstructed submission package. The canonical manuscript is [`what-is-ai-for-courts.tex`](what-is-ai-for-courts.tex); section files are in [`article/`](article/), authorities are in [`what-is-ai-for-courts.bib`](what-is-ai-for-courts.bib), and source-verification notes are in [`citation-ledger.md`](citation-ledger.md).

## Core claim

AI liability has an identification-and-production ordering problem: a claimant may need to name the enterprise that controlled a deployment before obtaining the records that reveal who controlled what. The Article responds with a deployment-control cascade and a two-layer responsibility architecture. A companion anti-substitution principle prevents the availability of automation from being treated as performance of an independently imposed duty. Neither rule requires artificial personhood.

## Current structure

1. **The Deployment-Control Cascade** — maps objectives, resources, configuration, feedback, and stopping power into legally usable evidence.
2. **Responsibility Without Artificial Persons** — supplies the compact status invariant and the automatic-instrumentality account.
3. **Why Classification Matters** — shows how relational harm, copyright, and anthropomorphic marketing expose deployment facts.
4. **A Responsibility Architecture for AI Deployment** — creates the enterprise-facing front door, answers the strongest objections, works the rule through *Garcia*, and specifies the charter and production rule.
5. **The Anti-Substitution Principle** — gives courts a four-question rule for automated care, process, accommodation, professional judgment, and public service.
6. **Capability Boundaries and State Power** — distinguishes legitimate capability stratification from coercive procurement or retaliation.

The Introduction and Conclusion are unnumbered. An unnumbered source note identifies the public record and author translations used for the Hangzhou Internet Court comparison.

## Build and verification

```sh
make pdf
```

The final PDF is written to `output/pdf/what-is-ai-for-courts.pdf`.

To generate a DOCX with real Word footnotes:

```sh
python3 -m pip install -r scripts/requirements-footnote-to-docx.txt
make docx PYTHON=python3
make clean-docx
```

The generated English DOCX is written to
`output/docx/Who-Controls-Who-Answers-Liability-in-the-AI-Control-Stack-English.docx`.

See [`scripts/README-footnote-to-docx.md`](scripts/README-footnote-to-docx.md) for PDF input, strict recovery, custom LaTeX macros, and validation options.

The package keeps the source record separate from the Article's claims:

- `citation-ledger.md` records authority, proposition, treatment, and freshness concerns.
- `what-is-ai-for-courts.bib` contains the citation data used by the compiled manuscript.
- `article/08-hangzhou-source-note.tex` identifies the reported case number, the public court account, and the status of the translations.
