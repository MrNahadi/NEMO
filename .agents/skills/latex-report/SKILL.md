---
name: latex-report
description: >
  Convert markdown content into a professionally formatted LaTeX academic report following
  the JKUAT UPRO template style. Use this skill whenever the user wants to generate a LaTeX
  report, write a project report in LaTeX, convert markdown notes or drafts into a formatted
  .tex document, create an academic report with a title page and chapters, or produce any
  LaTeX-based academic deliverable. Trigger whenever the user mentions "report", "LaTeX",
  "tex file", "academic report", "project report", "write up", "format my notes into a report",
  or provides markdown content that should become a structured LaTeX document — even if they
  don't explicitly say "LaTeX".
---

# LaTeX Report Generator

This skill transforms markdown content into a complete, compilable LaTeX academic report that follows the JKUAT UPRO (University Project Report) template. The output is a professional report suitable for academic submission, with a branded title page, proper front matter, numbered chapters, IEEE-style references, and appendices.

## Why this structure matters

Academic reports at JKUAT follow a specific institutional template. Deviating from this structure — wrong margins, missing declaration pages, incorrect numbering schemes — causes reports to be sent back for reformatting. This skill encodes those conventions so the user can focus on content rather than wrestling with LaTeX formatting.

## Quick overview of the workflow

1. Read the user's markdown input and identify the content sections
2. Read the preamble template from `assets/template_preamble.tex`
3. Map markdown headings to LaTeX chapters and sections
4. Generate the complete `.tex` file set (main file + chapter files in `structure/`)
5. Ensure the HDlogo and media directory are referenced correctly
6. Provide compilation instructions

---

## Step 1: Understand the input

The user will provide markdown content. This could be:
- A single markdown file with headings and body text
- Multiple markdown sections or bullet points
- Rough notes that need to be organized into report structure
- A polished draft that just needs LaTeX formatting

Examine the markdown and identify:
- **Title / project name** — becomes the report title on the title page
- **Authors and registration numbers** — if provided
- **Supervisor** — if provided
- **Abstract** — look for a section labeled "Abstract" or a summary paragraph
- **Main content sections** — map `# Heading` → chapters, `## Heading` → sections, `### Heading` → subsections
- **References / bibliography** — any citations or reference list
- **Figures / images** — any image references
- **Tables** — any tabular data
- **Code snippets** — any code blocks
- **Appendices** — any supplementary material

If key metadata is missing (authors, supervisor, project code), use placeholder values and flag them for the user to fill in.

---

## Step 2: Load the template

Read the LaTeX preamble template from the skill's assets:

```
<skill-path>/assets/template_preamble.tex
```

This template contains:
- All required `\usepackage` declarations
- Page geometry settings (top=2cm, bottom=2.5cm, left=1in, right=1in)
- One-and-a-half line spacing
- Hyperlink configuration (all links in black)
- Code listing styles
- TikZ flowchart styles
- The complete title page layout with HDlogo

Use this template **exactly as provided** for the document preamble and title page. The only parts you modify are the metadata placeholders (title, authors, registration numbers, supervisor, project code).

---

## Step 3: Generate the document structure

The report follows this exact file organization:

```
<output-directory>/
├── main.tex              # Master file with preamble, title page, front matter, \input{} calls
├── references.bib        # BibTeX bibliography file (IEEEtran style)
├── media/
│   └── HDlogo.png        # University logo (must exist — copy from source project if needed)
├── images/               # For any figures referenced in chapters
│   └── (figure files)
└── structure/
    ├── 01-introduction.tex
    ├── 02-literature-review.tex
    ├── 03-methodology.tex
    ├── 04-results.tex
    ├── 05-budget.tex         # (if applicable)
    ├── 05-workplan.tex       # (if applicable)
    ├── 05-conclusion.tex
    └── 06-appendix.tex       # (if applicable)
```

### File naming conventions

Chapter files are numbered with a two-digit prefix followed by a descriptive kebab-case name. The numbering reflects reading order, not strict chapter numbering (e.g., budget, workplan, and conclusion all use `05-` prefix because they follow results).

### The main.tex structure

The `main.tex` file has three major regions:

1. **Preamble** (before `\begin{document}`) — packages, styles, page layout. Use the template exactly.
2. **Front matter** (roman numeral pages):
   - Title page (with HDlogo)
   - Declaration page
   - Dedication
   - Acknowledgements
   - Abstract
   - Table of contents, list of figures, list of tables
   - List of abbreviations and symbols
3. **Main content** (arabic numeral pages):
   - `\input{structure/01-introduction}`
   - `\input{structure/02-literature-review}`
   - ... etc.
4. **Back matter**:
   - `\bibliographystyle{IEEEtran}` + `\bibliography{references}`
   - `\appendix` + `\input{structure/06-appendix}`

---

## Step 4: Convert markdown content to LaTeX

For the detailed conversion rules and the exact structure of each section, read:

```
<skill-path>/references/structure-guide.md
```

### Key conversion rules (summary)

| Markdown | LaTeX |
|---|---|
| `# Chapter Title` | `\chapter{Chapter Title}` |
| `## Section` | `\section{Section}` |
| `### Subsection` | `\subsection{Subsection}` |
| `**bold**` | `\textbf{bold}` |
| `*italic*` | `\emph{italic}` |
| `` `code` `` | `\texttt{code}` |
| `- item` | `\begin{itemize} \item ...` |
| `1. item` | `\begin{enumerate} \item ...` |
| `![caption](path)` | `\begin{figure}[H] \includegraphics...` |
| `> quote` | `\begin{quote}...` |
| ` ```lang ... ``` ` | `\begin{lstlisting}[language=lang]...` |
| `[text](url)` | `\href{url}{text}` or `\url{url}` |
| Tables | `\begin{table}[H] \begin{tabularx}...` |

### Special characters

Escape these characters in all text content: `% & $ # _ { } ~ ^ \`

### Citations

If the markdown contains references in any format (numbered, author-year, URLs to papers):
- Create corresponding entries in `references.bib` using BibTeX format
- Replace in-text references with `\cite{key}` commands
- Use the `IEEEtran` bibliography style

### Figures

- Place figure files in the `images/` directory
- Use the `[H]` float specifier (requires `float` package) to place figures where they appear in the text
- Include `\label{fig:descriptive-name}` for cross-referencing
- Use `\centering` inside the figure environment

```latex
\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\textwidth]{./images/figure-name.png}
    \caption{Descriptive caption text}
    \label{fig:figure-name}
\end{figure}
```

### Tables

- Use `booktabs` formatting (`\toprule`, `\midrule`, `\bottomrule`)
- Center table captions with `\captionsetup[table]{justification=centering,singlelinecheck=false}`
- Use `tabularx` for tables that should span the page width

```latex
\begin{table}[H]
    \centering
    \caption{Descriptive caption}
    \label{tab:table-name}
    \begin{tabularx}{\textwidth}{lXX}
        \toprule
        \textbf{Column 1} & \textbf{Column 2} & \textbf{Column 3} \\
        \midrule
        Data & Data & Data \\
        \bottomrule
    \end{tabularx}
\end{table}
```

---

## Step 5: Title page metadata

The title page must always include the HDlogo at `./media/HDlogo.png`. If the HDlogo file does not exist in the output directory, check:
1. The source project's `media/` directory
2. Ask the user to provide it

The title page placeholders to fill from the user's input:

- **Project title** — displayed between horizontal rules, in bold, split across lines if long
- **Project code** — e.g., "MR-PRO-25-02"
- **Author name(s)** — in uppercase, with registration numbers below each
- **Supervisor** — with title (Dr., Prof., etc.)
- **Degree program** — defaults to "BACHELOR OF SCIENCE IN MARINE ENGINEERING" but should be adjusted to match the user's program if specified
- **Department** — defaults to "DEPARTMENT OF MARINE ENGINEERING AND MARITIME OPERATIONS"
- **School** — defaults to "SCHOOL OF MECHANICAL, MANUFACTURING AND MATERIALS ENGINEERING"
- **Submission statement** — the italic text at the bottom about partial fulfilment

If the user doesn't specify these, use the defaults from the template and note which values need to be updated.

---

## Step 6: Writing style and tone

The LaTeX output should reflect formal academic writing:

- **Third person or first person plural** ("This study demonstrates..." or "We demonstrate...")
- **Past tense** for describing what was done ("The model was trained...")
- **Present tense** for stating facts and conclusions ("The results indicate...")
- **Formal vocabulary** — avoid colloquialisms
- **Each chapter begins with a brief introductory paragraph** explaining what the chapter covers
- **Sections within a chapter flow logically** with transitional sentences
- **Cross-references** use `\ref{}` and `\label{}` (e.g., "as shown in Figure \ref{fig:architecture}")

If the user's markdown is informal or note-like, elevate the language to academic register while preserving the technical meaning.

---

## Step 7: Output and compilation

After generating all files, provide the user with:

1. A summary of what was generated (file list)
2. Which placeholder values need to be filled in
3. Compilation instructions:

```bash
# Compile the report (run multiple times for cross-references)
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex

# Or using latexmk (recommended)
latexmk -pdf main.tex
```

4. Any warnings about missing figures, references, or metadata

---

## Common edge cases

- **No explicit chapter structure in markdown**: If the user provides flat content without clear heading hierarchy, organize it into the standard chapter structure (Introduction → Literature Review → Methodology → Results → Conclusion) based on content analysis.

- **Very short content**: If the user provides brief notes, expand the structure but keep chapter files minimal. Don't pad with filler — just create the skeleton with the content placed appropriately.

- **Multiple markdown files**: If the user provides several markdown files, each typically maps to a chapter. Ask for clarification if the mapping isn't obvious.

- **Content that doesn't fit standard chapters**: Create additional chapter files with appropriate numbering and naming. The structure is flexible — the key constraint is the preamble, title page, and front matter format.

- **Mathematical content**: Use `amsmath` environments (`equation`, `align`, `gather`) for display math. Use `$...$` for inline math. Number equations that are referenced.

- **The HDlogo must always be present**: This is the JKUAT institutional branding. Never omit it from the title page. The logo file is located at `./media/HDlogo.png` relative to the main.tex file.
