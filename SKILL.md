---
name: textbook-from-course
description: >-
  Turn a course's study material (slides, PDFs, scanned pages, notes, Word/PowerPoint files, past question papers,
  optionally a syllabus and a reference textbook) into a print-ready, old-school textbook PDF: typeset A4 LaTeX in a
  standardised classic layout (Times, black ink, ruled boxes, brief and detailed contents, index) that reads like an
  ordinary published textbook. By default the course identity is always removed (invented title and author, no course
  codes, lecturers or institution), all supplied material is included, past papers are restated and solved, and
  predicted exam questions with full answers are added to each chapter. Use whenever the user supplies a syllabus
  and/or slides, PDFs or notes and wants a textbook, study or exam-prep book, question bank with solutions, or a
  printable PDF from course material, e.g. "convert my slides into a book", "make a textbook from this", "exam
  preparation material with questions and solutions", even if LaTeX is never mentioned.
---

# Textbook from a course (material -> printed-quality textbook PDF)

The output is an A4 book that looks like a standard early-2000s university textbook: half-title, title and copyright
pages, brief and detailed contents, preface, numbered chapters that open on right-hand pages, running heads, ruled
boxes, uniformly set figures, an index, appendices. Every chapter ends with a summary, key terms, review questions,
predicted practice questions and complete model answers; restated past papers sit in appendices.

The hard parts are (1) reading every slide faithfully, including image-only ones, (2) proving that nothing the user
supplied was dropped, and (3) keeping layout and page count under control. Deterministic tools (`scripts/tb.py`) do
everything checkable: compiling, page budgets, print audit, identity scrub, voice lint. Run it with the interpreter that
`tb.py doctor` reports (a bare `python3` in Git Bash may lack PyMuPDF).

## House defaults (apply them without asking; the user's request can override any of them)
1. **Identity always removed.** Invented title and invented author (a plausible, non-famous name; never a real
   published book's title or author), no course code, course name, institution, lecturer, exam name, semester, "module N",
   "lecture", "slide". Seed `identity.terms`/`patterns` from the first page of every source, file names and Office
   document properties, including supplementary files from other lecturers or courses (`references/pitfalls.md`, identity).
   Chapters are numbered 1..n unless the user asks otherwise (`chapters[].number` may start anywhere).
2. **Everything supplied is included.** Complete mode: every slide, page, table, formula, worked example and figure
   of every file appears in the book (merged where repeated), proven by a coverage ledger (Step 2.5, Step 4).
   Page budgets are ceilings, never targets, and never a reason to drop content.
3. **Past papers.** If the user supplied none, ask once, early: "Do you have previous question papers (and answer
   keys)? They set the exam style and are printed, solved, in the book." Restate every paper question in full and solve it
   (`references/exam-material.md`). If there are none, say so and write the practice questions from the syllabus and
   the exam format.
4. **Predicted questions.** Every chapter gets practice questions in the style of the papers, with fresh scenarios and
   numbers and complete answers, introduced by one honest sentence that they are written for the book, not extracted.
5. **Classic layout and published-book voice.** `layout.style` is `classic` (default). Write one authorial voice in
   connected prose, with none of the tells of slide-derived or machine-written text (`references/chapter-spec.md`
   section 7). `layout.style: "modern"` (coloured, sans headings) is available only when the user asks for it.
6. **Lean process with a completeness audit.** One author per chapter, `tb.py check`/`scrub` clean, `tb.py voice`
   read, coverage ledger verified, every numerical answer recomputed in a scratch script, scanned past papers checked
   against their renders by an independent agent. The three-reviewers-and-fixer pass is opt-in
   (`references/agent-briefs.md` section 8) and costs several times more; offer it, never assume it.

## Read these when needed
| File | Read it when |
|---|---|
| `references/pipeline.md` | you start a project: commands, `book.json` fields, planning, ledger, staging, extending a book |
| `references/chapter-spec.md` | you write or review a chapter: structure, macros, voice, figures, questions, answers, LaTeX hygiene |
| `references/exam-material.md` | the user supplied (or should supply) past papers or a question bank; predicted questions |
| `references/agent-briefs.md` | you delegate: brief format and prompt templates |
| `references/book-design.md` | you must justify or change the look: layout, front/back matter, excerpts, density, index |
| `references/pitfalls.md` | anything fails (Windows, LaTeX, OCR, identity scrub, agents), or before installing software |
| `references/use-cases.md` | you want a precedent: the real configurations this skill has been run on and what went wrong |
| `assets/book-workflow.js` | you fan out chapter authors with the Workflow tool (only if the user opted into orchestration) |

## Step 0 - Decide with the user (ask only what blocks you; at most 4 questions in one round)
Read the syllabus and skim the material first. Ask, with a recommended default on each, only what you cannot infer:
1. **Scope**: which units become chapters (and one book per course if several are involved).
2. **Past papers**: supplied? If not, ask for them and for any answer keys (house default 3). Mention that a late addition
   is possible but costs a re-run of the exercises.
3. **Exam format** (only if there are no papers): number of questions x marks, descriptive / numerical / MCQ / programming.
4. **Length**: only if the user has a cap. Otherwise do not invent one; set `page_cap` generously from the material and
   say what size the book will come out at after the pilot chapter (budgets are ceilings; thin decks land at 40-70 %).
   Never present a cap above the usual 100-120 pages per three chapters as "Recommended".
State every assumption instead of asking about it (identity hidden, classic style, complete mode, A4, index on). If the
user is away or does not answer, proceed on the stated defaults; they can correct afterwards. Also ask, once, only when
relevant: standalone book or an **excerpt** (no front matter, chapters numbered from N, first page folio P:
`references/book-design.md` "Excerpts"); "extended contents" is already the default (brief + detailed contents).
If the user explicitly wants the course name kept, keep it and say so; if they ask for a real book's title on the cover,
decline (it passes the PDF off as someone else's work) and offer an invented one.

## Step 1 - Environment (a system change: survey first)
`python scripts/tb.py doctor` reports what is present and what is missing, with the exact fix. Installing LaTeX
(MiKTeX/TeX Live) or the OCR environment changes the user's machine: show the survey, record the prior state, say how to
revert, get a yes. `doctor --smoke` compiles the style once so package downloads happen up front.

## Step 2 - Ingest, look, plan
1. Create a **new, empty project folder** and run `tb.py init <folder> --material <dir>` (it refuses a folder that
   already holds a `book.json`), then `tb.py --project <folder> scan`. Fix roles in `book.json`: `syllabus`, `material`
   (anything with content to include, even a small formula sheet or a whole converted book), `reference` (a published
   textbook, text-only, used to back-fill gaps). Open the first page of every file and confirm it belongs to the course;
   leave out files from another course, name them in your first message, and do not OCR them.
2. `tb.py ingest`, `figures`, `ocr`, `sheets`: text per page, a picture of every page, OCR for image-only pages,
   uniform figures, 2x2 contact sheets. The renders are ground truth (text layers miss formulas and diagrams; OCR garbles code).
   **Figure provenance gate before any brief**: grep the OCR and text for `Figure \d+[-.]\d+`, `(c)`, `Copyright`,
   `Source:`, `Courtesy of`, publisher names; many hits mean the raster figures are publisher artwork, so briefs say
   "redraw or retypeset, never `\stdfig`" (`references/chapter-spec.md` section 4).
3. **Syllabus**: read it (render if scanned) and write `topics.json`; `tb.py gaps topics.json`; confirm gaps by `tb.py find` and
   by looking at renders before believing them. Missing topics are back-filled from the reference book or written from standard
   knowledge into clearly marked supplement boxes. **No syllabus**: the decks' own dividers and headings are the scope (every
   deck topic goes in); a photo of a past paper is an adequate proxy for exam format; say so, do not invent syllabus wording.
4. Past papers, if any: catalogue and route them (`references/exam-material.md`) before writing briefs.
5. **Coverage ledger** `coverage.md`: one row per source file -> chapter/section, marked `full`, `partial (slides x-y omitted: why)`,
   `duplicate of X`, or `omitted: reason`; for every source with numericals or code, one row per problem. Each chapter brief starts
   with its slide-to-section table. Briefs never declare content "out of scope" or "to keep shorter" unless the user said so.
6. Plan chapters (one per syllabus unit or deck group), give each a page ceiling (`references/pipeline.md` section 4), split
   any chapter above about 200 slides between an owner and a partner author. Fill `book.json` (`books`, `chapters`, `appendices`,
   `identity`), write the briefs, run `tb.py new-book <id>`.

## Step 3 - Write the chapters
For one or two chapters write them directly. For three or more, write the first as a pilot, check it, look at its pages, show
the user if they are present and no style has been approved yet, then fan the rest out in parallel with the Agent tool and the
author template in `references/agent-briefs.md` (the Workflow tool only if the user opted into multi-agent orchestration).
- Each author owns only its files; nobody edits `textbook.sty` or the main file (report needed changes).
- Spawn subagents at, never above, the session model's tier (the user's CLAUDE.md routing rules win).
- Expect rate limits and connection errors on long fan-outs; files stay on disk; resume with SendMessage first
  (`references/pitfalls.md`, delegation). Stage the work and write skeletons first.
- Authors recompute every number they print in solved numerical answers, in a scratch script (`references/exam-material.md`).

## Step 4 - Release
Each author has already run `tb.py check <id> <file> --budget N` to `PROBLEMS: 0`, `tb.py scrub` to 0 findings and read
`tb.py voice`. You then: (a) check the coverage ledger against the finished chapters and open the renders of every thin-text slide
that the ledger marks `full`; (b) have scanned past papers compared with their renders by one independent agent
(`references/exam-material.md`); (c) run `tb.py release <id>`: build, print audit, identity scan of sources, PDF text, metadata and
images, advisory voice lint, and copy to `Final/` only when clean (a locked old PDF produces `... (new).pdf` and a loud message;
tell the user which file is current). Never copy to `Final/` by hand past a failed gate; if you override a block, say which check and why.
(d) Skim a handful of rendered pages yourself. In the final message state plainly what was and was not audited.
Answering "is everything in the book?" always comes from the ledger plus a slide-by-slide pass, never from spot greps.

## Step 5 - Extending a released book
Late material ("add this at the end", "everything from here must be in the book"), a prerequisite chapter the papers need, or a
changed cap: archive to `_archive_<name>/` first, then follow `references/pipeline.md` section 8 (back-matter append, expansion pass,
backfilled chapters as supplement boxes, density change instead of cuts when only the cap shrank).

## Non-negotiables (and why)
- **Faithful, with two exceptions.** Numbers, formulas and problem statements are transcribed as given; fix only what contradicts
  itself and note it neutrally. Exceptions: every number in a solved numerical or past-paper answer is recomputed (answer keys are often
  wrong), and every entry of a References list or attributed quotation is verified. Anything not in the user's material goes in a
  visibly marked supplement box.
- **Read from the pictures, not OCR** for code, formulas, diagrams, mark columns and question order.
- **Budgets are hard ceilings** checked by tools; completeness is checked by the ledger. Neither replaces the other.
- **Cheap scripted checks stay mandatory:** `check` to `PROBLEMS: 0`, `scrub` to 0 findings before a chapter counts as done.
- **Privacy in figures:** mask hostnames, user names, domains in copies; never edit originals. Publisher artwork is redrawn, not reused.
- **Past papers are labelled honestly** ("Examination Papers with Solutions"), never disguised as original exercises; they carry
  no institution, course, date or registration wording.
- **Boundaries:** work only in the project folder; delete no user files; keep archives of earlier editions; never run `init`/`scan`
  inside another project's folder.

## Tool cheat sheet (`python scripts/tb.py --project <folder> ...`)
`doctor [--smoke|--setup-ocr]` - `init <folder> [--material D] [--style classic|modern]` - `scan` - `ingest [slug] [--engine auto|com|soffice|pptx]` -
`figures` - `ocr` - `sheets` - `gaps topics.json` - `find <regex>` - `new-book <id>` - `check <id> <file> [--budget N]` - `build <id>` -
`audit <pdf> [--budget N]` - `scrub <tex...>` / `scrub --pdf <pdf>` / `scrub-images <pdf>` - `voice <tex...>` - `release <id>`.
Tested: PDF (text, scanned, image-heavy), PPTX/PPT via PowerPoint, DOCX via Word, python-pptx and python-docx fallbacks, text-only
reference books, MiKTeX pdfLaTeX on Windows. Untested: LibreOffice conversion, macOS/Linux TeX Live paths.
