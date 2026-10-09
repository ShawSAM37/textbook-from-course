# Pitfalls and lessons learned

Contents: Windows and shells - LaTeX and the style - Reading the material - Identity scrub - Delegation and limits - Verification

## Windows and shells
* **Heredocs**: in Git Bash on the machine this skill came from, `cat > file <<'EOF'` halved backslashes (`\\` became `\`), corrupting `.tex`, `.py` and `.json`, and Python `-` heredocs and
  in-place `replace` splices failed repeatedly the same way. Write any file with backslashes using the Write/Edit tools (raw strings in Python); for multi-part chapters write each part to a scratch file
  and concatenate in a script. If a file was written by a shell, re-read it before trusting it.
* **PowerShell 5.1**: no `&&`/`||`; never redirect a native program's stderr (`2>&1` turns exit 0 into an error record); `Set-Content -Encoding utf8` writes a BOM (JSON readers may choke: the tools read
  `utf-8-sig`); `Remove-Item` on very long paths may be blocked; foreground `Start-Sleep` may be blocked, wait with a background command. Printing a non-ASCII character through a piped Python snippet can crash
  on cp1252: set `PYTHONIOENCODING=utf-8`.
* **Interpreter**: a bare `python3` in Git Bash may lack PyMuPDF (`No module named fitz`); use the interpreter `tb.py doctor` reports.
* **Paths with spaces** are normal for lecture folders; quote them, or use forward slashes in scripts.
* `pdftoppm` (poppler) is often missing from the PATH (sometimes present in the MiKTeX bin); the tools render PDFs with PyMuPDF instead.
* **MiKTeX**: install per-user (`winget install --id MiKTeX.MiKTeX --scope user`), enable on-the-fly package installation; the first compile downloads packages. The install directory is not on the PATH of
  shells opened before the install (the tools search it). "You have not checked for MiKTeX updates" on stderr is harmless.
* **Office automation**: PowerPoint COM gives exact renders and picture crops (about a second per slide); Word COM converts docx to PDF. Without Office, LibreOffice converts; the python fallbacks give text and
  embedded images only (no renders). A 155-page DOCX needed its Note/Tip boxes read from the renders (the text layer lacks them and letter-spaces code).
* **Locked output PDF**: a PDF already opened or sent to the user is locked on Windows, so moving or overwriting it fails. `release` then writes `... (new).pdf`; copy rather than move, build the new edition under a different
  name, and tell the user which file in `Final/` is current. Never leave two different PDFs with similar names unannounced. Never copy to `Final/` by hand past a failed gate.
* A compiler for C/POSIX listings may exist only in WSL (probe `wsl gcc --version`); use it to compile and run listings and say if none exists.
* **Project folders**: `init` and `scan` belong in a new, empty folder. Running them inside an earlier project once registered 41 unrelated files into its `book.json`; `scan` now saves `book.json.bak` first, `init` refuses.

## LaTeX and the style
* `\titlepage` resets the page counter -> wrong Roman numerals; use a group and `\clearpage`. `\makeatother` inside a `.sty` turns `@` into a non-letter for the rest of the file.
* A TikZ style named `step` clashes with a built-in key. `\stdfig` height caps shrink dense panel images: use `xl` or split the panels.
* A TikZ node's text is set in LR mode, which does not support `\\`; node styles here set `align=center`. A relative offset with a *negative* secondary component (`below left=12mm and -8mm of x`) can overlap a neighbour:
  give nodes an explicit `text width` and non-negative distances, or chain each node off the real node above or beside it.
* A stray, unescaped `_` between letters in ordinary prose fails with "Missing $ inserted", which does not point at the cause; grep the chapter for `[a-zA-Z]_[a-zA-Z]` outside code listings.
* `makeidx` already defines `\see` and `\seealso`; use `\renewcommand`. Listing frames overshoot the right margin unless `xrightmargin` >= 6 pt. `float=` on a listing can make it vanish.
* A table taller than about 40 % of a page jumps to the next page and leaves a half-empty page: compact it, or use `[htbp]` instead of `[H]`. Figures set `[H]` follow the text exactly: reorder paragraphs to avoid gaps.
* In `\texttt`, `--` turns into an en-dash unless ligatures are disabled (done in the style).
* Labels of `defn`/`worked`/`suppworked` are given bare; the box adds `def:`/`ex:`/`sex:`. Converting one environment into another silently breaks references. Prefix labels per chapter in multi-author books.
* `bashcode` treats `#SBATCH`/`#PBS` lines as code; ordinary `# text` remains a comment.
* A nested `]` inside a titlesec `\titleformat` after-code `[...]` ends the optional argument: wrap it in braces (`[{...\titlerule[0.8pt]}]`).
* `\titlecontents` needs `titletoc` (the classic style loads it). Do not redirect pdflatex stdout to `<main>.out`: it collides with hyperref's `.out` ("restricted \write18" fatal error).
* `\paragraph{...}` adds its own full stop: a title written with a trailing period prints "..". A 13-column matrix exceeds `pmatrix`: use `array` with `\left( \right)`. A `\multirow` inside `tabularx` overflows.
* An appendix needs `\section` per paper, not `\subsection` directly under `\chapter` (prints A.0.1). Two authors defining the same label in different chapters block `release`: prefix labels with the chapter.
* After a density change or any re-flow, margin overruns can appear that were not there before; `\allowbreak` fixes them.
* The shipped listing numbers are 6.5 pt, not `\tiny`, so the 7 pt label rule holds.

## Reading the material
* A quarter to a third of slides can be image-only (code screenshots, equations as pictures, scanned lectures). The text layer misses them; OCR recovers words but garbles code (`0`/`o`, `()`->`O`, dropped spaces),
  mark columns and question order. Always read the render for code, formulas, diagrams, matrices and numbers.
* Slide numbers restart oddly and slides repeat as animation builds; use the render order and merge duplicates. Near-duplicate files (`RNN`, `RNN (2)`) are common: record `duplicate_of`.
* **Never announce a gap before searching and looking**: keyword counts under-count (formulas, images). Equally, never call a deck "background" or a topic "out of scope" from the text layer: that is how a
  book came out 40 % short.
* **Source errors**: decks and keys contain errors (dropped divisions, wrong exponents, a formula belonging to another algorithm). Transcribe faithfully and fix only what contradicts itself, noting it neutrally.
  Where the book *solves* numerical questions, recompute every number in a scratch script and correct (answer keys were wrong in three books); verify every cited reference (an added list had about ten errors).
  Source data that cannot be right (a problem with no possible answer) is flagged in the answer and the final report, not silently changed.
* A published reference book in the folder is a gold mine for back-filling thin topics (text-only ingest of 700 pages takes seconds); mark what came from outside the material.
* **Publisher artwork** in slides (screenshots with "Figure 9.2" or "(c) publisher" baked in; instructor decks of a textbook; stock photos; a diagram mirroring a well-known blog illustration) must not be reused,
  with or without a reference book. Run the caption grep at ingest and brief accordingly: one book lost two author runs (about 340 K tokens) because the rule was gated on a reference book. Re-check the neighbouring
  slides of any flagged figure.
* Files from another course are sometimes mixed into an upload (an embedded-systems deck among security notes; another lecturer's phonetics notes): look at the first page of every file, leave out what does not belong,
  say so, do not OCR it.

## Identity scrub
* `identity.terms` match as whole words; short acronyms (an institution's three letters, an exam abbreviation, a word like `SCOPE`) once matched inside "activity", "Application", "scope", "cavity", "gravity", "relativity" (103 false hits in one book, authors reworded correct
  terminology to dodge them). Use patterns (`\bABC\b`) for abbreviations, long literal terms otherwise; **never list the book's own subject words** as terms.
* `allow` regexes match case-insensitively and can silently reopen the leak: prefer fixing the term. Generic patterns that trip on legitimate technical phrases ("cross slide", "in the course of an investigation") are allowed by default;
  add others rather than rewording.
* The generic lecture/slide/module/"the course" patterns always apply, so a book that deliberately keeps its course identity must add the offending phrases to `identity.allow`.
* Identity hides in: figure captions, source comments, PDF metadata and Office document properties, hostnames and viewer UI text in screenshots, box titles, "as shown earlier in the notes" phrasing, exam-content strings
  inside example programs and questions, URLs, a footer lecturer name, another lecturer's byline, the reference book's name and table numbers, and in the images themselves (OCR them). `release` can report clean while a URL
  is still in the PDF: grep the PDF text for `https?://|www\.` yourself, and read the voice lint.
* A scrub path is relative to the current directory or the project folder; a wrong path now says so.
* Build the hidden-identity edition **first** (house default): hiding it later forced a second build, 30 hand-found wording changes and a stale named PDF in `Final/`.
* The release file name is `<title> - <author>.pdf`; an invented author is fine for a private study copy, not for presenting as a published work. State that plainly.

## Delegation and limits
* Parallel authors hit account usage limits (HTTP 429) and transient connection errors (expired certificate, "Unable to connect to API") that can stop many agents at the same instant. Files stay on disk: check state
  (sizes, TODO counts), then SendMessage each agent. Resuming worked every time it was tried (7 of 7 after one outage; single agents in three other sessions); relaunch fresh only if the resume yields no progress or the file is still the
  unedited skeleton and the agent seems hung.
* The question tool accepts at most 4 questions per round. An unanswered round once stalled a session about ten hours and the lead had guessed that a topic was out of scope: ask at most four, bundle, give defaults, and
  proceed on them when the user is away.
* Two authors sharing a chapter must agree on labels (chapter-prefixed) and never edit each other's file; give the owner the questions so they are consistent.
* Authors report needed style changes rather than editing the shared style; apply them centrally after testing on a scratch copy, then tell running authors.
* A workflow interrupted by a session restart leaves a journal; read it, find the one unfinished step and run only that.
* The user's routing rules win: never spawn a subagent above the session's model tier.
* Late changes of the page cap force a whole-book re-flow; ask before fan-out, and do not mark a larger-than-usual cap as "Recommended".

## Verification
* Independent checks beat self-reports: re-run `tb.py check`/`release` yourself and read real pages. Automated checks catch geometry, not legibility, and **not coverage**: `check` and `scrub` were clean on books that were missing content.
* The audit checks: page size, embedded fonts, header/footer positions, page numbers, chapter and appendix openers on right-hand pages, text/figure/TikZ inside the margins, gaps > 35 %, page cap. It does not check coverage,
  voice, folio parity in excerpts, or that a cited figure is legible.
* Cross-chapter `\ref` and partner-only labels are undefined in a stand-alone `check`; verify with `tb.py build`. A clean `check` prints `PROBLEMS: 0` even when it lists undefined references: read the log summary.
* Say plainly what was not verified: code that was never compiled, engines never run, exercises that are educated guesses about an exam, papers not compared with their renders, a release gate that was overridden.
