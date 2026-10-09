# Book design rationale

Read this when you must justify or change the look. `assets/textbook.sty` (classic, the default) implements it; `assets/textbook-modern.sty` is the coloured alternative.

Contents: Page and typography - Running headers - Front matter - Back matter: index and appendices - Boxes - Questions and answers - Figures -
Chapter numbering and identity - Styles - Matching a reference book's look - Excerpts and front-matter options - Density - Page arithmetic

## Page and typography
A4 (US Letter, A5, B5 configurable), 11 pt Times text and maths (`mathptmx`), Bera Mono for code, `microtype`. Line spacing 1.08, paragraphs indented rather than spaced, widows and clubs
forbidden, ragged-bottom pages (consistent baselines matter more than a flush bottom when figures and boxes are present). The intent is a standardised early-2000s university
textbook that does not look generated: serif throughout, black ink only, rules instead of tints, small capitals in the running heads.
Margins 1 in plus a 0.25 in **binding offset** on the inner edge, mirrored on recto and verso (`twoside`), so a duplex printout bound on the left keeps identical margins page after page.
Header and footer sit at fixed heights; the footer carries the centred page number. Chapters open on right-hand pages (`openright`); blank pages have no header or number.

## Running headers (classic book scheme)
Verso (left) pages show `N  CHAPTER TITLE` in small capitals, recto (right) pages `N.M  SECTION TITLE`; chapter openers and blank pages show none; page number centred in the footer.
Front matter uses Roman numerals, main matter restarts at 1 on the first chapter's page. Never use the `titlepage` environment (it resets the page counter).

## Front matter (from `book.tex.tmpl`)
Half-title, blank verso, title page (rules, title, subtitle, author, edition, year), copyright page ("Typeset in <typeface> with LaTeX"; no ISBN, publisher or real institution is ever invented),
**Brief Contents** (preface, chapters, appendices, index, with dot leaders from `\pageref{tbch:N}` / `tba:<file>` / `tb:preface` / `tb:index`), **Contents in Detail** (chapters bold, sections
and subsections with dot leaders), preface (what the book covers, what each chapter does, how questions and answers are arranged; initials and month/year). A book with no subtitle or no author is
handled cleanly: no empty italic line, no stray space in the copyright line, release file name without the author. PDF metadata carries only title and author. "Extended contents" requests
are met by the default; if the user means *more chapters than exist*, decline: contents list only what the pages carry.

## Back matter: index and appendices
`books[].index: true` adds `\backmatter`, `\printindex` (bold letter groups, `assets/index.ist` copied to `<id>.ist`; edit freely) and `\label{tb:index}`; `build`, `check` and `release` run
makeidx automatically when `<id>.idx` is non-empty. While writing, call `\index{term}` for every definition and named concept (`\index{term!subterm}`, `\index{term|see{Other}}`,
`\index{term|seealso{Other}}`); index the first substantive occurrence only. `\see`/`\seealso` already exist in makeidx: restyle with `\renewcommand`, never `\newcommand`. After all chapters are
finished, one pass reading every chapter's `\index{}` calls together catches naming drift (`shard key` versus `Shard Key`) and adds hub entries for the central subject.
`books[].appendices` lists plain `\chapter` files after `\appendix` ("APPENDIX A" opener, sections A.1, questions A.1); they appear in both contents lists. Use them for restated past papers and
reference sheets. The audit treats `APPENDIX x` and any headerless opener (index, an unnumbered formula-sheet chapter) as a chapter boundary, so the page before is not flagged as a gap.

## Boxes (all ruled, nothing tinted; prints identically in greyscale)
A rule above and below, no fill, no coloured bar. Definitions, examples and key points carry a heavy rule on top; "Further Discussion" (supplement) is set smaller with hairlines. Box titles:
Definition, Example, Key Points, Points to Remember (`examfocus`; omit it in the disguised-book voice), Further Discussion, Chapter Objectives. Boxes break across pages. Use them sparingly:
a box under every heading is a tell.

## Questions and answers
Questions are numbered N.k per chapter ("Question 1.3"), marks optional at the right margin; answers repeat the number ("Answer to Question 1.3") one size smaller. A chapter ends: text, summary, key
terms, review questions, practice questions, answers. Restated past papers sit in appendices (A.1, A.2) with their answers after each paper.

## Figures
One pipeline gives every figure the same treatment: flatten to RGB on white, autocrop, uniform margin, width normalised into [720, 1800] px, one caption style, fixed height cap, placement exactly where
discussed (`[H]`). Size classes `s` 45 %, `m` 65 %, `l` 88 %, `xl` 96 % of the text width. Classic figures carry no frame (the modern style adds a hairline frame). Low-resolution or vector-only diagrams are
redrawn in TikZ; screenshots with personal details are masked in copies.
**Publisher artwork**: course slides are often built from published books, and instructor decks carry "Figure N-M ... (c) publisher" captions baked into screenshots, with or without a reference book in
the folder. Never `\stdfig` such an image: it is someone else's copyrighted figure. Redraw the concept as an original TikZ figure with the chapter's own example, or retypeset it as a table or listing. Run the
caption grep (SKILL.md Step 2) before briefing authors; if it hits, treat every polished raster of that source as publisher artwork.

## Chapter numbering and identity
Chapters are numbered 1..n by default; keeping module numbers (3, 4, 6) reveals the course structure. A user may ask for any start (3, 4); `\tbchapter{N}` and `book.json` `number` carry it. File names may keep
old numbers. Identity is removed by default (SKILL.md house default 1); the invented author is a plausible non-famous name, or a neutral edition line if the user prefers. Never print a real book's title or
author on the cover. A disguised book is a voice and structure problem as much as a wording problem (chapter-spec section 7).

## Styles
* **classic** (default): Times, black only (colour names are kept and redefined to grey levels, so old chapters and TikZ styles still compile), ruled boxes, small-caps running heads, `titletoc` contents.
* **modern**: Palatino, navy/green/maroon/amber boxes with a tinted fill and a thick left bar, sans headings, framed figures. Only on request: `tb.py init <folder> --style modern`.
Projects keep their own copy of `textbook.sty`; changing the skill's asset never alters an existing project.

## Matching a reference book's look
Rarely requested. Page geometry usually needs no change. The body typeface carries the resemblance: classic already uses Times; for the modern style swap `\RequirePackage{mathpazo}` for
`\RequirePackage{mathptmx}` in the project's own copy and set `layout.typeface` so the copyright page stays truthful. Check the reference PDF's embedded fonts and page size first (`fitz`:
`page.get_fonts()`, `page.rect`): a converted ebook can have a different trim size and substituted fonts. An epigraph (`\chapepigraph{quote}{attribution}`) only with a genuine, correctly attributed
quotation; skip it rather than fabricate one.

## Excerpts and front-matter options
For a printable add-on to existing notes the user may want no front matter, chapters numbered from N and a first page folio P (one request: no cover, no contents, no preface, chapters from 4, first page 88).
* Main file: `\documentclass ... \usepackage{textbook} \booktitle{...} \begin{document}` then `\mainmatter`, the folio line below, the chapter inputs, `\end{document}`; set `pdfauthor={}`. Chapter numbers come from `number`/`\tbchapter`.
* Folio: shift only the **displayed** number, **after `\mainmatter`** (it resets `\thepage`; before it the override is silently lost and the pages print 1, 2, ...): `\renewcommand{\thepage}{\the\numexpr\value{page}+(P-1)\relax}`. Never `\setcounter{page}{P}` with an even P: it flips the two-sided margin mirroring and the
  `openright` logic for the whole book (observed: 343 audit problems, chapter openers on versos). Choose P odd so recto pages carry odd folios; if the user asks for an even P, warn and offer P+1 or a leading blank
  verso. The audit accepts the offset; it does not check folio parity against the side.
* Name the output "excerpt" only if the user asked for it. Title-only front matter (half-title, title, copyright without contents or preface) is the same idea with the first three pages kept.
* An author-less release names the file by title alone.

## Density (when only the page cap shrank)
A tighter layout recovers pages without cutting content. Measured on a 214-page book: 145 pages (-32 %) with no content change. Archive first (`_archive_before_compact/`), try it on a scratch copy, then edit the
project's `textbook.sty` and `book.json` so the audit matches. The values used (relative to the classic style): class option 10 pt and `layout.font_pt: 10`; geometry `margin=0.7in, top=0.6in, bottom=0.62in,
bindingoffset=0.15in, headheight=11pt, headsep=11pt, footskip=22pt` (and `margin_pt` 50.4, `binding_pt` 10.8 in `book.json`); `\setstretch{1.0}`; `arraystretch` 1.05; list spacing 1 pt / 2 pt; chapter title
22/26 pt; section spacings about 13/5, 9/3, 7/3 pt; caption skip 4 pt; `intextsep` 6 pt, `textfloatsep` 8 pt; `\stdfig` and tall tables `[H]` -> `[htbp]`; box padding 8/6/3/3 pt with skips 5 pt; question and answer
spacing 6/5 pt. Afterwards re-run `check` on every chapter (budgets made at the old density are void) and expect a few margin overruns that `\allowbreak` fixes (three blocked one release).
Ask for the cap before authors start so this is a choice, not a rescue.

## Page arithmetic
See `pipeline.md` section 4: ceilings, not targets; thin slide decks finish at 40-70 % of them.
