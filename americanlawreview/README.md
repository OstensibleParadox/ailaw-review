# americanlawreview

`americanlawreview` is a v1 LaTeX/biblatex package skeleton for American
law-review articles and footnote-first legal citation.

The package intentionally ships only a `generic` review profile. Journal-specific
profiles such as Harvard, Yale, or Stanford are reserved extension points and
will raise a clear error until implemented.

## Class Mode

```tex
\documentclass[review=generic,mode=submission]{americanlawreview}
\addbibresource{demo.bib}

\title{Example}
\author{A. Student}
\institutionalaffiliation{Generic Law Review Project}
\authornote{Thanks to the editors.}

\begin{document}
\maketitle
\begin{abstract}
This is an abstract.
\end{abstract}

Text.\lrfootnote{\See \casecite[347]{brown}; \artcite[45]{coase}.}
\printbibliography
\end{document}
```

## Package Mode

```tex
\documentclass{article}
\usepackage[bluebook,review=generic]{americanlawreview}
\addbibresource{demo.bib}
```

## v1 Citation Coverage

- `@case`, `@statute`, `@constitution`, `@regulation`, `@lawreview`
- normal `@article` and `@book`
- full first citation
- immediate `Id.` citation with pin cite support
- `supra note` for later article/book citations
- legal short form for later case/statute citations
- `shorthand` and `shorttitle`
