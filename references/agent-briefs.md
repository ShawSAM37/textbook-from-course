# Delegating chapters: briefs and prompt templates

Contents: 1 Rules for every agent - 2 Chapter brief file - 3 Author - 4 Partner - 5 Past-paper author - 6 Survey agent - 7 Common brief pattern -
8 Opt-in higher-assurance pass (reviewers and fixer) - 9 Resuming interrupted agents

## 1. Rules for every delegated agent
* **Model tier**: spawn at the session's tier or below (obey the user's CLAUDE.md routing rules). Omit the `model` option to inherit the session model.
* **Files**: each agent owns named files only. Nobody edits `textbook.sty`, the book main file, `book.json` or another chapter; needed changes are reported.
* **Tools**: read and write with the Write/Edit tools (shell heredocs halve backslashes on Windows), run `tb.py` with the interpreter `doctor` reports, view images with the Read tool.
* **Evidence (default)**: the report contains the pasted output of `tb.py check` (`PROBLEMS: 0`), `tb.py scrub` (0 findings) and `tb.py voice` (answered), plus the
  recompute log for numerical answers. Full recomputation of every number in the *notes* and a page-by-page review belong to the opt-in pass (section 8).
* **Look at pages once**: render your compiled PDF and look at it while writing, mainly to read image-only slides correctly and to catch layout breakage.
* Files are written early (skeleton first, then deepen) so an interruption never loses a chapter.
* Several authors never run a full-book `build`; each compiles only its own `check` driver.

## 2. Chapter brief file (`_src/briefs/<book>_<file>.md`, written by the orchestrator)
```
# Brief: <book title> - Chapter <N> "<title>"   (file <book>/<file>.tex; short header title "<short>")
## Scope text for this chapter (verbatim syllabus lines, or "no syllabus: the decks' own headings are the scope")
## Slide-to-section table (REQUIRED, first table)
<for each source: slide/page ranges -> intended section; image-only slides flagged; duplicates and animation builds noted>
## Sources
<slugs with contents and counts; priority and duplicate_of from book.json; text-light pages; reference-book page ranges for back-fill; relevant figure ids>
## Past papers and routing
<the routing rows (tag, marks, topic) that land in this chapter's practice questions or its appendix; exam format and mark structure>
## Known gaps and traps
<topics missing/thin (confirmed by search AND by looking), formulas the text layer garbles, slides that are wrong, overlapping decks, publisher captions found by the provenance gate>
## Structure and ceiling
<owner/partner split, page ceilings (total, own, partner), shared labels (chapter-prefixed), ordering constraints, the other chapters' numbers and titles for plain-text cross-references>
## Voice and identity
<invented book title and author, chapters' titles, identity terms in force, "published-book voice", forbidden words>
```
Keep briefs factual. **Never declare content "out of scope" or tell the author to "keep it proportionately shorter" unless the user or syllabus said so**: briefs written from the
text layer alone omit image-only content, and "keep it short" produced a 73-page book against a 120-150 page target and a user complaint. In the no-syllabus case every deck topic
goes in. Do not claim something is absent from the slides unless you searched and looked.

## 3. Author (owner of a chapter)
Parameters: project folder, book id, chapter file, number, title, short title, page ceilings, partner file, brief path, skill path.
Instructions to include verbatim in the prompt:
1. Read `<skill>/references/chapter-spec.md` completely (and `exam-material.md` if the chapter has practice questions), then the brief. Run `tb.py --project <p> check <book> <file> --budget N` early on the skeleton.
2. Read the sources: `_src/text/<slug>.txt`, OCR, **the renders in `_src/render/<slug>/`** (skim a deck with the 2x2 `_src/sheets/` first), the figure index and contact sheets. Look at every slide that carries a diagram, formula, code or worked example. Never write code or formulas from OCR alone.
3. Write the chapter in the shape of chapter-spec section 1 and in the published-book voice of section 7: introduction, objectives, sections of connected prose, summary, key terms, review questions, practice questions, complete answers. The page figure is a ceiling; **do not drop content to stay short**; log anything you omit (slide number, reason). If the book has an index, call `\index{term}` as you write.
4. Recompute every number you print in an answer in a scratch script and keep the log; follow the notes' conventions; fix only self-contradictions and report them.
5. Verify (`check` to `PROBLEMS: 0`, `scrub` to 0, `voice` answered, a look at the rendered pages) and report: files, pages vs ceiling, counts (sections, examples, figures used/excluded, supplements, questions), the slide-to-section table with omissions, recomputed numbers, corrections, additions beyond the source (one line each), pasted outputs, open problems, "macro feedback". When the chapter lists a reference or attributed quotation, list every author-year you cite.
Partner present: read the partner file (its topics need summary entries, questions and answers) but never edit it.

## 4. Partner (part-file author)
Owns `<book>/<file>_part.tex`: sections only, no `\tbchapter`, no questions. Does the content work for its topics, keeps labels (chapter-prefixed) and section order, stays inside its ceiling, verifies with `tb.py check <book> <file>_part --budget M` and `tb.py scrub`. Reports like an author. The owner file already inputs the partner file before its Summary; the owner does not wait for the partner to start (it writes its own sections and the question list from the brief outline).

## 5. Past-paper author (appendix)
Owns `<book>/appA.tex` (and further appendices). Input: the transcription files and routing table (`exam-material.md` sections 2-3). Writes each paper as a `\section`, restated verbatim in the original order with marks and sub-part labels as printed and identity wording removed, then the answers as a `\section`. Every answer is self-contained and every number recomputed; where the key disagrees with the maths, solve correctly. Reports: papers, questions, pages vs ceiling, recomputed numbers, keys found wrong, conventions adopted, pasted `check`/`scrub` output.

## 6. Survey agent (image-heavy decks, before authoring)
For decks with more than half low-text pages: one agent per deck views every contact sheet and writes `_src/briefs/survey_<slug>.md`: section outline with page ranges, worked examples present, duplicate slides, suspected source errors, internal inconsistencies (two pin assignments for one circuit), publisher captions. Authors are briefed from the surveys. All authors then covered all sections.

## 7. Common brief pattern (many authors)
One shared `COMMON.md` (what the book is, identity and voice rules, the macro list, label scheme, report format with counts, the numerical-recompute rule, past-paper rules) plus one short per-chapter prompt that names its files and ceiling made nine agent prompts short and consistent. Put project-specific rules there; they win over chapter-spec on conflict.
A one-pass **published-book voice** brief (chapter-spec section 7) at the first draft is cheaper than a slide-flavoured draft followed by a rewrite: it makes the author regroup freely, write subsections of 250+ words, use at most three lists, avoid exam furniture and boxes under every heading, link chapters in plain text, and keep every substantive item of the source.

## 8. Opt-in higher-assurance pass (reviewers and fixer) -- not part of the default pipeline
Run only when the user explicitly asks for thorough review or names a concern. It multiplies cost and time several-fold (three reviewers plus a fixer per chapter, each recomputing numbers and reading every page): say so and get a yes. For exam books a lighter version is the default (SKILL.md house default 6). Reviewers read only; run the three roles in parallel per chapter, then the fixer.
**Reviewer: solutions.** Try to refute the work. Recompute every number in every answer and worked example in Python; check each formula, derivation step, algorithm and program (no compiler assumed unless one exists; WSL gcc often does); check each answer covers all parts and answer k matches question k; check consistency with the chapter text and that the questions are realistic examination questions. Report real defects only: location, quoted fragment, why wrong, corrected content, severity (high = wrong/misleading/missing, medium = incomplete/inconsistent, low = polish).
**Reviewer: identity and voice.** Run `tb.py scrub` and `tb.py voice`, then read the prose for anything that reveals a course, lecturer, slides, syllabus, exam board, module numbering or source deck, hard-coded numbers, slide-note phrasing, the tells of chapter-spec section 7, inconsistent notation, typos, missing structure. Open the figures used and look for personal or institutional details.
**Reviewer: layout and completeness.** Run `check`, render contact sheets and view every page: ceiling, gaps > 35 %, overflow, unreadable figure text, boxes that split badly, running heads, tables and code legibility, equal numbers of questions and answers in the same order; then the notes-to-chapter coverage map against the ledger and, for restated papers, every question against its render.
**Fixer.** Receives the merged findings and the author's report; verifies each finding before acting (reviewers can be wrong); fixes every valid high and medium finding and the cheap lows within the ceiling; re-runs the checks, recomputes any number it changed, looks at every page it changed; reports fixed count, unfixed with reasons, pasted outputs. Findings that need a style change go back to the orchestrator.

## 9. Resuming interrupted agents
Agents that stop on an account limit or a connection error keep their files. Check the real state on disk first (modification times, `tb.py check`, whether the chapter is still the unedited skeleton). Then **resume with SendMessage** naming what to do next: "state was lost; re-check the real state on disk, continue where you stopped, finish verification, report". This worked for 7 of 7 authors after one connection error and for single agents elsewhere. Relaunch fresh only if the resume yields no progress. If a workflow was interrupted, read its journal to see which agents finished and run only the missing step.
