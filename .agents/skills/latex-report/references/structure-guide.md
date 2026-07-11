# LaTeX Report Structure Guide

This reference details the exact structure, formatting conventions, and content expectations for each section of the JKUAT UPRO project report.

## Table of Contents

1. [Title Page](#title-page)
2. [Front Matter](#front-matter)
3. [Chapter Structure](#chapter-structure)
4. [Standard Chapter Templates](#standard-chapter-templates)
5. [LaTeX Formatting Patterns](#latex-formatting-patterns)
6. [Cross-Referencing](#cross-referencing)
7. [Bibliography](#bibliography)

---

## Title Page

The title page is the institutional branding page. It follows a rigid layout that should not be modified structurally.

### Required elements (top to bottom)

1. **University logo** — `\includegraphics[width=0.22\textwidth]{./media/HDlogo.png}` with 0.6cm spacing below
2. **University name** — "JOMO KENYATTA UNIVERSITY OF AGRICULTURE AND TECHNOLOGY" split across 3 lines
3. **College** — "COLLEGE OF ENGINEERING AND TECHNOLOGY"
4. **School** — "SCHOOL OF MECHANICAL, MANUFACTURING AND MATERIALS ENGINEERING"
5. **Department** — Variable (e.g., "DEPARTMENT OF MARINE ENGINEERING AND MARITIME OPERATIONS")
6. **Degree** — Variable (e.g., "BACHELOR OF SCIENCE IN MARINE ENGINEERING")
7. **Horizontal rule**
8. **Project title** — Bold, centered, may span multiple lines using `\\[0.08cm]` between lines
9. **Horizontal rule**
10. **Project code** — e.g., "MR-PRO-25-02"
11. **Authors** — Each author on their own lines: name in `\large \textbf{}`, reg number in `\normalsize` below
12. **Supervisor** — "Supervised by" label, then name in `\large \textbf{}`
13. **Submission statement** — Three lines of italic footnotesize text about partial fulfilment

### Author entry format

For each author, generate:
```latex
{\large \textbf{LASTNAME FIRSTNAME MIDDLENAME}}\\[0.1cm]
{\normalsize REG-NUMBER}\\[0.25cm]
```

### Declaration author entry format

For each author in the declaration section:
```latex
\vspace{1cm}
\noindent
\textbf{Name:} LASTNAME Firstname Middlename \hfill \textbf{REG NUMBER:} REG-NUMBER\\
\vspace{0.5cm}

\noindent
\textbf{Signature:} \underline{\hspace{5cm}} \hfill \textbf{Date:} \underline{\hspace{4cm}}
```

---

## Front Matter

All front matter pages use **roman numeral** page numbering (`\pagenumbering{roman}`).

### Sections in order

1. **Declaration** — `\section*{DECLARATION}` with `\addcontentsline{toc}{section}{Declaration}`
2. **Dedication** — `\chapter*{Dedication}` with `\addcontentsline{toc}{section}{Dedication}`
3. **Acknowledgements** — `\chapter*{Acknowledgements}` with `\addcontentsline{toc}{section}{Acknowledgements}`
4. **Abstract** — `\chapter*{Abstract}` with `\addcontentsline{toc}{section}{Abstract}`
5. **Table of Contents** — `\tableofcontents`
6. **List of Figures** — `\listoffigures`
7. **List of Tables** — `\listoftables`
8. **Abbreviations and Symbols** — `\section*{LIST OF ABBREVIATIONS AND SYMBOLS}` with `\addcontentsline`

### Default text patterns

If the user doesn't provide dedication or acknowledgement text, use these templates:

**Dedication:**
> We dedicate this Project Report to our parents, guardians, lecturers, and mentors whose encouragement, sacrifice, and guidance have supported our academic journey.

**Acknowledgements:**
> We would like to express our sincere gratitude to all those who contributed to the successful completion of this Project Report.
> 
> First and foremost, we extend our deepest appreciation to our supervisor, [Supervisor Name], for [his/her] invaluable guidance, constructive feedback, and unwavering support throughout this research project.
>
> [Additional acknowledgements as appropriate]

### Abbreviations table format

```latex
\textbf{ABBR} & Full Expansion \\
```

Extract abbreviations from the markdown content automatically. Look for:
- Parenthetical definitions: "Explainable AI (XAI)"
- Glossary sections
- Technical terms that appear repeatedly in abbreviated form

### Symbols table format

```latex
$symbol$ & Description (units) \\
```

---

## Chapter Structure

### Every chapter file follows this pattern:

```latex
\chapter{Chapter Title}
\label{chap:chapter-label}

\section{First Section}
Content...

\section{Second Section}
Content...
```

### Labels

- Chapters: `\label{chap:kebab-case-name}`
- Sections: `\label{sec:kebab-case-name}`
- Figures: `\label{fig:kebab-case-name}`
- Tables: `\label{tab:kebab-case-name}`
- Equations: `\label{eq:kebab-case-name}`

### Each chapter begins with a `\chapter{}` command

Do NOT use `\chapter*{}` for main content chapters (that's only for front matter). Numbered chapters ensure proper table of contents generation.

---

## Standard Chapter Templates

The standard report structure maps to these chapters. Not all are required — adapt based on the user's content.

### 01-introduction.tex

Typical sections:
- `\section{Background}` — Context and motivation
- `\section{Problem Statement}` — The gap or problem being addressed
- `\section{Objectives}` — Primary and specific objectives (enumerated list)
- `\section{Significance}` — Why this work matters
- `\section{Scope}` — Boundaries and limitations of the study

### 02-literature-review.tex

Typical sections:
- `\section{Introduction}` — Brief chapter overview
- `\section{Topic Area 1}` — Thematic grouping of literature
- `\section{Topic Area 2}` — Another thematic grouping
- `\section{Research Gap}` or `\section{Summary}` — What's missing / what this project addresses

Literature review sections should be citation-heavy. Each paragraph should reference at least one source.

### 03-methodology.tex

Typical sections:
- `\section{Introduction}` — Chapter overview
- `\section{Research Design}` — Overall approach
- `\section{Data Collection}` or `\section{Dataset}` — Data sources and characteristics
- `\section{Implementation}` — Tools, algorithms, frameworks
- `\section{Validation}` or `\section{Testing}` — How results are verified

This chapter often contains:
- Flowcharts (TikZ diagrams)
- Algorithm descriptions
- Code snippets (`lstlisting` environment)
- Mathematical formulations
- System architecture diagrams

### 04-results.tex

Typical sections:
- `\section{Introduction}` — Chapter overview
- `\section{Result Category 1}` — Group of results with figures/tables
- `\section{Discussion}` — Interpretation of results

This chapter is figure-heavy and table-heavy. Every figure and table must have:
- A descriptive caption
- A label for cross-referencing
- Discussion in the surrounding text

### 05-budget.tex (if applicable)

Contains project budget breakdown in tabular format.

### 05-workplan.tex (if applicable)

Contains Gantt chart or timeline table for project milestones.

### 05-conclusion.tex

Typical sections:
- `\section{Introduction}` — Brief chapter overview
- `\section{Conclusion}` — Summary of findings
- `\section{Achievement of Objectives}` — How each objective was met (enumerated)
- `\section{Recommendations}` — Actionable recommendations (enumerated)
- `\section{Limitations of the Study}` — Honest limitations (enumerated)
- `\section{Future Work}` — Directions for future research (subsections)

### 06-appendix.tex (if applicable)

```latex
\chapter{Appendices}
\label{chap:appendix}

\section{Appendix Item Title}
Content...
```

---

## LaTeX Formatting Patterns

### Enumerated lists (for objectives, recommendations, etc.)

```latex
\begin{enumerate}
    \item \textbf{First item title:} Description text that follows.
    \item \textbf{Second item title:} Description text that follows.
\end{enumerate}
```

Use bold lead-in text when list items have distinct titles or categories.

### Bullet lists

```latex
\begin{itemize}
    \item First item
    \item Second item
\end{itemize}
```

### Equations

Display equations:
```latex
\begin{equation}
    F_m(x) = F_{m-1}(x) + \eta \cdot h_m(x)
    \label{eq:gradient-boosting}
\end{equation}
```

Inline math: `$variable$` or `$expression$`

### Code listings

```latex
\begin{lstlisting}[language=Python, caption={Description of the code}, label={lst:code-label}]
def function_name():
    return result
\end{lstlisting}
```

### Landscape pages (for wide tables or figures)

```latex
\begin{landscape}
    % Wide content here
\end{landscape}
```

### TikZ flowcharts

Use the predefined styles from the preamble:

```latex
\begin{figure}[H]
\centering
\begin{tikzpicture}[node distance=2cm]
    \node (start) [startstop] {Start};
    \node (process1) [process, below of=start] {Process Step};
    \node (decision1) [decision, below of=process1, yshift=-0.5cm] {Decision?};
    
    \draw [arrow] (start) -- (process1);
    \draw [arrow] (process1) -- (decision1);
\end{tikzpicture}
\caption{Flowchart description}
\label{fig:flowchart-name}
\end{figure}
```

---

## Cross-Referencing

Always use LaTeX cross-referencing rather than hardcoded numbers:

- "as shown in Figure \ref{fig:name}"
- "Table \ref{tab:name} presents..."
- "discussed in Chapter \ref{chap:name}"
- "according to Equation \ref{eq:name}"
- "see Section \ref{sec:name}"

---

## Bibliography

### BibTeX format

Use `IEEEtran` bibliography style. Create entries in `references.bib`:

```bibtex
@article{key2024,
    author  = {Lastname, Firstname and Lastname2, Firstname2},
    title   = {Article Title},
    journal = {Journal Name},
    year    = {2024},
    volume  = {1},
    number  = {1},
    pages   = {1--10},
    doi     = {10.xxxx/xxxxx}
}

@inproceedings{key2024conf,
    author    = {Lastname, Firstname},
    title     = {Paper Title},
    booktitle = {Conference Name},
    year      = {2024},
    pages     = {1--5}
}

@book{key2024book,
    author    = {Lastname, Firstname},
    title     = {Book Title},
    publisher = {Publisher Name},
    year      = {2024},
    edition   = {2nd}
}

@misc{key2024web,
    author       = {Organization Name},
    title        = {Web Page Title},
    howpublished = {\url{https://example.com}},
    year         = {2024},
    note         = {Accessed: 2024-01-15}
}
```

### Citation commands

- Single citation: `\cite{key}`
- Multiple citations: `\cite{key1,key2,key3}`
- Citation in sentence: "Smith \cite{smith2024} demonstrated..."

### Extracting references from markdown

If the markdown contains:
- Numbered references like `[1]` → convert to `\cite{}`
- Author-year like `(Smith et al., 2024)` → convert to `\cite{}`
- URLs to papers → create `@misc` entries
- A references section → parse into BibTeX entries
