# textbook-from-course

An agent skill (SKILL.md format) that turns a course's study material into a print-ready, old-school textbook PDF.

Give it lecture slides, PDFs, scanned pages, notes, Word or PowerPoint files and previous question papers (a syllabus and a reference
textbook help but are optional). It produces a typeset A4 LaTeX book in a standardised classic layout: Times, black ink, ruled boxes,
brief and detailed contents, running heads, index, appendices. The book reads like an ordinary published textbook.

## Defaults

1. The course identity is always removed: invented title and author, no course code, lecturer or institution.
2. Everything supplied is included, proven by a coverage ledger; page budgets are ceilings, not targets.
3. Previous question papers are requested if none are supplied, then restated and fully solved in appendices.
4. Every chapter ends with a summary, key terms, review questions, predicted practice questions and complete answers.
5. Classic layout and one authorial voice, checked by an advisory voice lint. A coloured "modern" style is available on request.

## Install

Copy this folder to your agent's skills directory, for example `~/.claude/skills/textbook-from-course`. Then check the machine:

```
python scripts/tb.py doctor --smoke
```

`doctor` reports what is present and what is missing, with the exact fix. Requirements: Python 3.9+, PyMuPDF, Pillow, numpy; a LaTeX
engine with `pdflatex` (MiKTeX or TeX Live); optional: python-pptx, python-docx, pywin32 with PowerPoint/Word for the best Office fidelity,
and `rapidocr-onnxruntime` for image-only slides and scans (`doctor --setup-ocr` installs it into a private folder).

## Use

```
python scripts/tb.py init <new-empty-folder> --material <folder with the material>
python scripts/tb.py --project <folder> scan
python scripts/tb.py --project <folder> ingest ; figures ; ocr ; sheets
python scripts/tb.py --project <folder> new-book b1
python scripts/tb.py --project <folder> check b1 ch01 --budget 20
python scripts/tb.py --project <folder> release b1
```

`SKILL.md` is the entry point (decisions, steps, non-negotiables); the `references/` folder holds the pipeline runbook, the chapter
specification, the past-paper rules, the book design rationale, the delegation templates, the pitfalls and a catalogue of real runs.

## Layout

| Path | Contents |
|---|---|
| `SKILL.md` | entry point and house defaults |
| `references/` | pipeline, chapter-spec, exam-material, agent-briefs, book-design, pitfalls, use-cases |
| `assets/` | `textbook.sty` (classic) and `textbook-modern.sty`, book/chapter/appendix templates, index styles, example `book.json`, optional workflow script |
| `scripts/` | `tb.py` and `tb_lib/` (ingest, OCR, figures, scaffold, build, audit, identity scrub, voice lint, release) |
| `evals/` | example prompts with assertions |

## Status

Developed and tested on Windows 11 with MiKTeX pdflatex and PowerPoint/Word COM. Untested: LibreOffice conversion, macOS and Linux TeX Live paths.
