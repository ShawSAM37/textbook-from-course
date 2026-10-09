# Pipeline runbook

Contents: 1 Project layout - 2 book.json - 3 Phase commands - 4 Planning chapters and page ceilings - 5 Gap analysis and the no-syllabus case -
6 Coverage ledger - 7 Staging, time and cost - 8 Extending a released book - 9 Editions and archives

## 1. Project layout (created by `tb.py init` in a NEW, empty folder)
```
<project>/
  book.json            configuration (section 2); book.json.bak is written before every `scan` merge
  textbook.sty         the shared style (copy of assets/textbook.sty; nobody edits it during authoring)
  <bookid>.tex         book main file (front matter + \InputIfFileExists of chapters and appendices)
  <bookid>/chNN.tex    chapter files; a two-author chapter also has chNN_part.tex (sections only, input by the owner before the Summary)
  <bookid>/appA.tex    appendix files (restated papers etc.)
  figures/pool/        normalised figures + index.json   (pool/<slug>_pNNN_kK.png; trimmed copies end in _c.png, masked copies _m.png)
  _src/                text/, ocr/, render/, sheets/, contact/, raw_figs/, manifest.json, briefs/   (derived; safe to regenerate)
  coverage.md          the coverage ledger (section 6)
  build/               LaTeX output, _chk_*.tex drivers, PDFs
  Final/               released PDFs (only written by `tb.py release` when clean)
```
`init` stops if `book.json` already exists: that folder is another project (`--material` would be ignored and its style file overwritten).
If the project folder sits inside the material folder, `scan` ignores it (`build/`, `Final/`, `_chk_*`).

## 2. book.json
```json
{ "material_dir": "C:/path/to/uploads",
  "sources": { "slug": {"file": "relative/to/material_dir.pdf", "role": "material|syllabus|reference", "priority": 1, "duplicate_of": "slug2"} },
  "identity": { "terms": ["COURSE-CODE", "Full Course Name", "Institution", "Lecturer Name"], "patterns": ["\\bABC\\b"], "allow": [] },
  "layout": { "paper": "a4paper", "font_pt": 11, "margin_pt": 72, "binding_pt": 18, "gap_limit_pct": 35, "typeface": "Times", "style": "classic" },
  "ingest": { "render_width": 1600, "crop_width": 2400, "pdf_crop_dpi": 220 },
  "books": [ { "id": "b1", "title": "...", "title_lines": ["..",".."], "subtitle": "...", "subtitle_lines": [".."],
               "author": "...", "year": 2026, "month_year": "October 2026", "page_cap": 120, "index": true,
               "preface": ["paragraph", "paragraph"],
               "chapters": [ {"file": "ch01", "number": 1, "title": "...", "short": "...", "budget": 34,
                              "sources": ["slug"], "partner": {"file": "ch01_part", "budget": 9} } ],
               "appendices": [ {"file": "appA", "title": "Examination Papers with Solutions", "budget": 30} ] } ] }
```
* `identity.terms` are forbidden strings, matched **as whole words** (case-insensitive): course code, course name, institution, lecturer, exam name,
  semester tag. Never put the book's own subject words in `terms` (it makes the chapter unscrubbable). Abbreviations of 2-4 letters go in `patterns` as
  `\bXXX\b` (word boundaries are already added to alphanumeric terms, but a pattern lets you control case and shape, e.g. a registration-number shape).
  Seed the lists from the first page of every source, file names, footers, Office document properties (author/title) and supplementary files from other
  lecturers or courses; add exam-name variants ("TEST-2", "TEST 2", "Test2") and "Module N" spellings. `allow` regexes are case-insensitive and can silently reopen a
  real leak: use sparingly and prefer a longer term. A technical phrase caught by a generic pattern ("cross slide", "in the course of") is already allowed.
* `role: material` is for every source with content to include, however small (a formula sheet) or large (a converted 155-page book with figures);
  `role: reference` is read as text only and used to back-fill, so figures and practice problems of a reference are not reused; `role: syllabus`
  is excluded from coverage counts. `priority` and `duplicate_of` are notes for the briefs (copy them into every chapter brief): the higher priority
  supplies the explanation and numbers where two providers disagree. The build does not enforce `chapters[].sources`; keep it truthful anyway.
* `layout.style`: `classic` (default) or `modern` (coloured, sans headings); chosen at `init --style`. `layout.typeface` is text only (the copyright
  page's "Typeset in ..." sentence); it does not change the rendered font.
* `books[].author` may be empty (a neutral edition): the copyright line and the release file name then omit it.
* `books[].index` (default `false`): `true` adds the back-of-book index (`\printindex`, makeindex run automatically by `build`/`check`/`release`).
* `books[].appendices`: plain `\chapter` files after `\appendix`, listed in the Brief Contents; `tb.py new-book` writes the skeletons and `tb.py check <id> appA` works.
* Chapter `file` names are arbitrary; the printed number is `number` (equal to the `\tbchapter` argument).
* Write JSON with the Write tool (Windows PowerShell's `Set-Content -Encoding utf8` adds a BOM; the tools tolerate it, other programs may not).

## 3. Phase commands (run from anywhere with `--project <folder>`)
| Phase | Command | Output / notes |
|---|---|---|
| environment | `tb.py doctor [--smoke] [--setup-ocr]` | present/missing + fix; never installs LaTeX itself |
| init | `tb.py init <folder> --material <dir> [--style classic|modern]` | book.json, style, folders; refuses an existing project |
| register | `tb.py scan` | adds every pdf/pptx/ppt/docx/doc/txt/md under material_dir with a readable slug and a guessed role; saves `book.json.bak` first; re-run after adding files late |
| ingest | `tb.py ingest [slug] [--engine auto|com|soffice|pptx] [--force]` | text + renders + raw figures; PowerPoint COM first, then LibreOffice, then python-pptx (no renders) |
| figures | `tb.py figures` | autocropped, white-background, width-normalised PNGs in `figures/pool`, duplicates and logos dropped, contact sheets |
| OCR | `tb.py ocr [slug]` | `_src/ocr/<slug>.txt` for pages with < 60 characters of text; private OCR venv |
| sheets | `tb.py sheets` | `_src/sheets/<slug>_NN.png` = 4 pages per image, page number in a red tag |
| gaps | `tb.py gaps topics.json` / `tb.py find <regex>` | coverage table per syllabus topic / page-numbered search |
| scaffold | `tb.py new-book <id>` | `<id>.tex` + chapter, partner and appendix skeletons; `<id>.ist` if `index: true`; existing files are kept (`--overwrite` regenerates the front matter) |
| chapter | `tb.py check <id> <file> --budget N` | stand-alone compile of one chapter, partner or appendix + print audit; exit 0 only if clean |
| book | `tb.py build <id>`; `tb.py audit <pdf> --budget N` | 3-pass compile with log summary (makeindex between passes 1 and 2 when `<id>.idx` is non-empty); audit of any PDF |
| identity | `tb.py scrub <tex...>` / `scrub --pdf <pdf>` / `scrub-images <pdf>` | sources / PDF text+metadata / text inside images; paths relative to the cwd or the project |
| voice | `tb.py voice <tex...>` | advisory lint for machine-written / slide-derived tells |
| release | `tb.py release <id>` | build + audit + all scrubs + voice lint; writes `Final/<title> - <author>.pdf` only when clean; locked target -> `... (new).pdf` |
Ingest time: PDF seconds; PowerPoint COM 0.5-1 s per slide; OCR about 3 s per text-light page; a 700-page reference book as text in ~1 s; a full release
(build, audit, OCR of 63 images) about 2 minutes (`--no-images` while iterating).

## 4. Planning chapters and page ceilings
Mapping: one chapter per syllabus unit or deck group (merge tiny units, split huge ones), in syllabus order. **Budgets are ceilings, not targets.**
Measured across ten books: faithful chapters from text-heavy slide decks land at 40-70 % of the ceiling (15-24 pages for 50-100 slides including the
questions and answers); image-heavy decks with solved questions fill it. Say so in the brief so authors do not pad, and tell the user the expected final
size after the pilot. Arithmetic (11 pt Times, 1.08 spacing, calibrated on slide-derived books):
* Core content about **1 page per 4-6 slides** after condensing in condensing mode (complete mode is closer to 1 per 3-4); derivations written out line by
  line are about 1.7 pages per source page of notes.
* Objectives and introduction: 1 page; summary and key terms: 1 page; review and practice questions: 2-4 pages; **answers about 0.5-1.3 pages each**
  (1.1-1.2 for code or numerical, 0.5-0.7 for prose).
* Front matter 10-12 pages with brief and detailed contents; a blank verso may follow a chapter that ends on a recto.
* Past papers: about 1 page per solved question (`exam-material.md` section 10).
A chapter whose sources exceed ~200 slides or ~4 decks is split between an **owner** (head, introduction, objectives, summary, questions, answers) and a
**partner** (sections only, `file_part.tex`), each with its own ceiling and a shared label list. If a user-stated cap is tighter than the content needs,
do not cut: use the density change in book-design.md ("Density"), which bought 32 % in one book, and say what you did.

## 5. Gap analysis and the no-syllabus case
`topics.json`: `[{"topic": "Amdahl's law", "chapter": "ch02", "patterns": ["amdahl", "speed-?up limit"]}, ...]`. Verdicts: **NOT IN MATERIAL** (no hits in
the material; hits in the reference -> back-fill from it; none -> write from standard knowledge as a supplement), **thin** (< 4 hits: read the slides),
otherwise covered. Keyword hits are a search aid only: confirm a gap with `tb.py find` and by opening renders before telling the user (one reported gap
was covered on three slides). Write confirmed gaps into each chapter brief.
**No syllabus** (five of ten recent books): derive the scope from the decks' dividers and headings (every deck topic is in), skip `topics.json`/`gaps`,
state this in the first message and the final report, never invent syllabus wording inside the book, and offer to take a pasted syllabus line. With
fewer than about 60 source pages write the chapters directly, with no fan-out. A photographed past paper is a sufficient proxy for exam format.
Topics that the papers test but the notes never teach are gaps too (`exam-material.md` section 3).

## 6. Coverage ledger (mandatory in complete mode, the default)
After `scan`, write `coverage.md`: one row per source file -> chapter and sections, with `full` (every slide used), `partial (slides x-y omitted because ...)`,
`duplicate of X`, or `omitted: reason`. A deck called "background" is `partial` by definition: say so. For every source with numericals or code, one row per problem
with the worked-example or question label. Each chapter brief opens with its slide-to-section table (which slide numbers feed which section; image-only slides flagged);
that table made a 41-slide recurrent-network chapter complete at 16 pages. Show the ledger in the plan message and again at release. At release answer "is everything in
the book?" from the ledger plus a slide-by-slide pass (every slide cited in a brief appears in a section) and the renders of every thin-text slide, never from a few
spot greps. If the user later says a source was not fully covered, add a section covering it in full and update the ledger. Authors' `check` and `scrub` verify geometry
and identity only; they say nothing about coverage.

## 7. Staging, time and cost (be honest with the user)
Default process (SKILL.md house default 6): stage 1 (doctor, ingest, figures, OCR, ledger) minutes to an hour, mechanical; stage 2 (plan, routing table, briefs)
15-30 minutes; stage 3 (one author per chapter, parallel) **measured 5-24 minutes and 0.15-0.37 M tokens per author for 15-25 finished pages, 8-10 minutes and
155-313 K tokens for a 25-50 page expansion**; a first pilot takes 10-15 minutes; stage 4 (ledger check, numerical recompute, release, skim) 15-30 minutes. A
past-paper appendix author can take up to 49 minutes. A mid-size exam book (4 chapters, 6 papers) was 77-100 minutes wall-clock and 3.5-6.5 M subagent tokens in
total over 13-15 agents. A disguised book written in two passes cost about 580 K extra tokens, which is why the published-book voice is the first-draft voice.
**Opt-in higher-assurance pass** (three reviewers and a fixer per chapter, agent-briefs.md section 8): roughly doubles the cost again; offer it, get a yes.
* A first draft at full length followed by condensing was more efficient than hitting a cap in one shot, but if a cap is known write to it.
* Account limits (HTTP 429) and transient connection errors (expired certificate, "Unable to connect") can stop many authors at once. Files stay on disk:
  check state, then SendMessage each agent ("state was lost, re-check the disk, continue, verify, report"); all resumed cleanly in three sessions.
* Ask before launching more than a couple of agents at once only when the user is present; when they are away, proceed on stated defaults and say so.
* When the owner of a split chapter waits for its partner the chapter serialises (24 minutes); let the owner write its sections and question list from the
  brief outline in parallel and add the partner's suggestions afterwards.
* Concurrent authors must not run a full-book `build` (a sibling's half-edited file produces fatal errors and spurious undefined references): each compiles its own
  `check` driver; the orchestrator does the one full build.

## 8. Extending a released book
Archive the current chapters and PDFs to `_archive_<name>/` first (nothing is deleted); an expansion works from the archived copy so an interrupted pass can be restored.
* **Late small source** ("just add this at the end", a formula sheet): a back-matter append, not a rerun. Register it `role: material`, ingest text-only,
  write one unnumbered back-matter chapter (`\chapter*{Title}` + `\markboth` + `\addcontentsline{toc}{chapter}{Title}`, input after the last chapter in
  `<id>.tex`), run `build` and `release`, skip chapter reviews, ask nothing, do not also fold it into chapters unless asked. The audit recognises `APPENDIX x` openers and
  any headerless opener page, so the page before it is not flagged as a gap.
* **"Everything from here must be in the book" (page budget lifted)**: (a) register the source `role: material` and run scan/ingest/figures; add it to
  `chapters[].sources`; (b) raise `page_cap` and treat chapter budgets as soft ceilings, still `check --budget`; (c) archive; (d) one expansion author per chapter,
  given the page ranges of the new source outlined by page, building a checklist of every concept, table, figure, worked example, listing and note/tip/warning
  box and crossing it against the existing chapter, merging duplicates, keeping existing questions byte-unchanged, replacing general-knowledge supplements by the
  source's own content; (e) a source's end-of-part scenario problems become `\section{Practice Problems}` / `\section{Answers to Practice Problems}` with labels `ppN-k`;
  (f) a new topic is a new chapter: add it to `book.json`, `tb.py new-book <id>` (writes only the missing skeleton), then update the preface and subtitle in both `<id>.tex`
  and `book.json` so they agree; (g) a DOCX text layer lacks Note/Tip boxes and letter-spaces code: read those from the renders. Example: a 155-page DOCX took one book from
  115 to 225 pages across five chapters in 35 minutes.
* **Backfilling a missing prerequisite** that the papers test: its own chapter or a section of grey supplement boxes (22 supplement boxes made a 24-page chapter once), never
  blended into course-sourced boxes; say plainly that it comes from standard knowledge.
* **Appending a chapter after others that use its topic** reads oddly: offer to reorder and recompute numbering; add a cross-reference sentence in an earlier chapter that
  overlaps a new one.
* After any extension re-run the ledger, `release`, and tell the user which `Final/` PDF is current.

## 9. Editions and archives
Before any redesign, condensing or density pass copy the current chapters, style and PDFs to `_archive_<name>/`. When a later pass overwrites chapter files in place, its
authors work from the archived copy. `release` leaves older PDFs in `Final/` alone: name or move them yourself and say which is current.
