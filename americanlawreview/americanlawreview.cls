\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{americanlawreview}
  [2026/07/03 v0.1 American law review article class]

\RequirePackage{kvoptions}
\RequirePackage{etoolbox}

\SetupKeyvalOptions{family=alrcls,prefix=alrcls@}
\DeclareStringOption[generic]{review}
\DeclareStringOption[submission]{mode}
\def\alrcls@ptsize{12pt}
\DeclareVoidOption{10pt}{\def\alrcls@ptsize{10pt}}
\DeclareVoidOption{11pt}{\def\alrcls@ptsize{11pt}}
\DeclareVoidOption{12pt}{\def\alrcls@ptsize{12pt}}
\DeclareVoidOption{submission}{\def\alrcls@mode{submission}}
\DeclareVoidOption{final}{\def\alrcls@mode{final}}
\DeclareDefaultOption{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessKeyvalOptions*

\LoadClass[\alrcls@ptsize]{article}

\edef\alrcls@pkgopts{review=\alrcls@review,mode=\alrcls@mode,bluebook}
\expandafter\RequirePackage\expandafter[\alrcls@pkgopts]{americanlawreview}
\providecommand*\alrgeometryoptions{margin=1in}
\providecommand*\alrfontsetup{}
\providecommand*\alrprofilelayout{}
\RequirePackage[letterpaper]{geometry}
\expandafter\geometry\expandafter{\alrgeometryoptions}
\RequirePackage{setspace}
\RequirePackage{fancyhdr}
\alrfontsetup

\ifdefstring{\alrcls@mode}{submission}
  {\doublespacing}
  {\ifdefstring{\alrcls@mode}{final}
     {\singlespacing}
     {\ClassError{americanlawreview}
        {Mode '\alrcls@mode' is not implemented}
        {Use mode=submission or mode=final.}}}

\setlength{\parindent}{0.5in}
\setlength{\parskip}{0pt}
\setlength{\headheight}{14pt}
\setlength{\footnotesep}{0.8\baselineskip}
\setlength{\skip\footins}{1.2\baselineskip}
\interfootnotelinepenalty=10000

\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\alrjournalname}
\fancyhead[R]{\small\thepage}
\renewcommand{\headrulewidth}{0pt}

\makeatletter
\renewcommand\section{%
  \@startsection{section}{1}{\z@}
    {-2.5ex \@plus -1ex \@minus -.2ex}
    {1.3ex \@plus .2ex}
    {\alrsectionfont\centering}}

\renewcommand\subsection{%
  \@startsection{subsection}{2}{\z@}
    {-2.0ex \@plus -1ex \@minus -.2ex}
    {1.0ex \@plus .2ex}
    {\normalfont\normalsize\bfseries}}

\renewenvironment{abstract}
  {\begin{center}\bfseries Abstract\end{center}%
   \begin{quote}\small}
  {\end{quote}}

\renewcommand{\maketitle}{%
  \thispagestyle{plain}%
  \begin{center}
    {\alrtitlefont \@title\par}
    \vskip 1.2\baselineskip
    {\alrauthorfont \@author\alrauthornotemark\par}
    \alrprintaffiliation
    \vskip .75\baselineskip
    {\small
      \ifdefstring{\alrcls@mode}{submission}
        {\alrsubmissionlabel}
        {\alrfinallabel}%
      \par}
    \vskip 1.5\baselineskip
  \end{center}
  \alrprintauthornotes}
\alrprofilelayout
\makeatother
