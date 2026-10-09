# Chapter specification (authors and reviewers follow this)

Contents: 1 Chapter structure - 2 Content rules - 3 Macro reference - 4 Figures - 5 Questions - 6 Answers - 7 Voice and identity -
8 LaTeX hygiene - 9 Verification of a chapter

## 1. Chapter structure (final form)
1. `\tbchapter[Short header title]{N}{Full title}` and an introduction of three or four substantial paragraphs (no heading): what the
   subject is, why it matters, how it follows from the previous chapter, what this chapter does.
2. `objectives` box ("Chapter Objectives": 4-5 one-line bullets).
3. Four to six `\section`s in syllabus (or deck) order, each with two to four `\subsection`s of real prose (see section 7). A `defn` box
   only for the few central definitions; one `worked` box for each computational topic, with every intermediate step; the key figure; the
   key formula, algorithm or short program. Ordinary, informative headings: the printed contents lists them.
4. `\section{Chapter Summary}`: one to three paragraphs of prose.
5. `\section{Key Terms}` with `\keyterms{a; b; c.}`.
6. `\section{Review Questions}` (`exq` without marks), `\section{Practice Questions}` (section 5), `\section{Answers}` (section 6).
Chapter numbers are printed 1..n unless the user asked otherwise (`\tbchapter` takes any N; keep `book.json` `number` equal to it). No
hard-coded "Chapter 3" or "Section 4.2": use `\ref` within a chapter; for another chapter write it out ("Chapter~2") because a stand-alone
`check` cannot resolve cross-chapter labels.

## 2. Content rules
* **Cover everything the chapter's sources contain, and nothing from outside them unless marked.** Every definition, formula, derivation,
  algorithm, worked example, table, code listing and figure of the sources assigned to the chapter appears, merged where slides repeat
  (animation builds) and minus decoration (footers, slide numbers). A chapter that finishes below about 60 % of its ceiling from slide
  sources is a red flag for dropped content, not a success. An author may omit something only by logging it (slide number, reason) in
  the report's "omitted" list. "Everything", "all derivations and proofs", "every step" from the user override any cutting rule below and
  the page ceiling (write each derivation line by line, answer questions the material merely poses).
* **Prose, not slide fragments.** Bullets become explanatory paragraphs; true enumerations stay lists, at most three per chapter besides the
  objectives. Formal but plain.
* **Faithful transcription.** Numbers, formulas and worked-example steps are taken from the material as given. Fix only what contradicts itself
  (its own working does not give its own answer) and note the correction neutrally. Exceptions: recompute every number in solved numerical or
  past-paper answers, and verify every cited reference or quotation (`exam-material.md`, `pitfalls.md`).
* **Back-fill and supplements.** Topics missing from the material are written from the reference book or standard knowledge inside a
  `supplement` box titled by what it contains ("Further Discussion" by default); never "not in the slides". A solution that needs outside
  knowledge opens with a supplement-style note.
* **Worked examples**: problem, every intermediate step, final result, a closing sentence with units. When the user asks for variables explained,
  list every symbol (meaning, unit, given or constant) before the working; when they ask for "two examples per kind", label them
  (straightforward) and (sentence-based) in the title.
* **Page ceilings** (`pipeline.md`) are ceilings. If the content does not fit, say so and ask (density change before cuts: book-design.md);
  when cutting is unavoidable, cut repeated examples, secondary tables and background history first; never a syllabus topic, a key formula
  or a likely numerical.
* **Scope notes**: topics outside the examined scope go last, in `\begin{supplement}[Extended topic]...\end{supplement}`.

## 3. Macro reference (`textbook.sty`; do not edit it in a chapter)
| Element | Use |
|---|---|
| chapter | `\tbchapter[short]{N}{Title}` (also sets `\label{tbch:N}`); appendices use plain `\chapter{Title}\label{tba:file}` after `\appendix` |
| boxes | `\begin{defn}{Title}{label}` (Definition N.k, ref `def:label`), `\begin{worked}{Title}{label}` ("Example N.k", ref `ex:label`), `\begin{suppworked}{Title}{label}` (ref `sex:label`), `\begin{keyresult}[Title]` ("Key Points"), `\begin{examfocus}[Title]` ("Points to Remember"; omit it in the disguised-book voice), `\begin{supplement}[Title]` ("Further Discussion"), `\begin{objectives}` |
| key terms | `\keyterms{term; term.}` |
| code (ASCII only) | `ccode`, `bashcode` (`#SBATCH`/`#PBS` lines print as code), `plaincode`; options `[caption={..},label=..,xrightmargin=6pt]` |
| figures | `\stdfig[s|m|l|xl]{pool/id.png}{Caption.}{fig:label}`; `\stdfigpair[0.485]{pool/a.png}{pool/b.png}{Caption.}{fig:label}`; TikZ/pgfplots in `\begin{figure}[H]\centering...\caption{}\label{}\end{figure}`; TikZ styles `proc`, `box`, `msg` |
| tables | `booktabs`; text columns `>{\raggedright\arraybackslash}X` in `tabularx`; tall tables (> ~40 % of a page) in `table[htbp]`, compacted (`\footnotesize`) or split, not `[H]` |
| algorithms | `algorithm` + `algpseudocode` (numbered N.k) |
| questions | `\begin{exq}{label}` (no marks) or `\begin{exq}[10]{label}` ("[10 marks]" at the right), printed "Question N.k"; `\begin{exsol}{label}` prints "Answer to Question N.k" in smaller type |
| index (only if the book's `"index": true`) | `\index{term}`, `\index{term!subterm}`, `\index{term|see{Other}}`, `\index{term|seealso{Other}}`; first substantive occurrence only; lowercase singular subject terms, consistent names |
| labels | `fig: tab: def: ex: sex: sec: alg: eq:`; box environments add their own prefix, so write it bare and refer with the prefix. **In a multi-author book prefix every label with the chapter** (`ex:c3-matvec`): `check` sees one chapter at a time and cannot catch duplicates |
Never call `\includegraphics` outside `\stdfig`/`\stdfigpair`; never add packages; never `\newcommand` over `\see`/`\seealso`; never name a TikZ style `step`.
Do not end a `\paragraph{...}` title with a full stop (the run-in heading adds its own). In an appendix use `\section` for each paper, not `\subsection` directly under `\chapter`.

## 4. Figures
* Choose from `figures/pool/index.json` (fields id, file, slug, page, w, h, suggest, low_res, kind, dup_of; ignore `dup_of`). **Open each candidate** and its
  render; write a descriptive caption; place the figure where it is discussed and refer to it in the text.
* Pick a size so the smallest label prints at >= ~7 pt (`xl` for dense multi-panel images). Remove slide debris in a trimmed copy `<id>_c.png`
  (PIL); never overwrite or delete a pool original.
* Redraw in TikZ what is missing, low-resolution or vector-only; pgfplots for curves.
* **Publisher artwork**: redraw any diagram that looks copied from a published book, with or without a reference book in the folder: a baked-in
  "Figure N-M" caption, a "(c) publisher" line, brand or credit text, or polish that does not match the deck's hand-made diagrams. If the
  provenance gate (SKILL.md Step 2) found such captions, treat all raster figures of that source as publisher artwork and keep only those
  demonstrably the lecturer's own. For UI screenshots that cannot be redrawn (dialogs, hex editors, header dumps): drop with one descriptive sentence, or
  retypeset as a `plaincode` listing of an invented, generic specimen (placeholder domains) and write the worked example against its line numbers.
* **Mask personal or institutional details** in screenshots (user names, home paths, hostnames, domains, logos) in copies `<id>_m.png`.
* Leave out logos, decoration, exact duplicates, formula and text screenshots that you typeset instead.

## 5. Questions
* **Review questions** (3-6): definition and "explain" questions on the chapter, no marks printed.
* **Practice questions** (8-14, or as the exam format dictates): in the exact style and mark structure of the supplied papers, fresh scenarios
  and numbers, introduced by the one honest sentence (`exam-material.md` section 7). Typical mix: half descriptive (with a diagram), two derivations
  or comparisons, two numericals, one program. With "all types of question", use the typed bank (`exam-material.md` section 8).
* Past papers are not mixed into the chapters unless the user asked: they go in appendices (`exam-material.md` section 4).

## 6. Answers
One `exsol` per question, same label and order. Each is complete and **self-contained**: direct answer or definition first, structured explanation,
the diagram (refer to the chapter figure and add a compact sketch or table where a hand-drawn diagram is expected), every derivation step, numericals
with full working, units and a final sentence, short correct programs with a line per key statement, comparisons as a small table. Never answer by citing
a section number instead of explaining; restate what the answer needs. Every printed number was recomputed (scratch script) before it was written.
Typical length half a page to one and a half. Marking-scheme lines only if the exam format prints marks and the identity allows it.

## 7. Voice and identity (the book must read as one author's ordinary textbook)
* **Voice.** Plain formal English, one authorial voice ("it is worth noticing", "researchers have reported"); occasional "we" is fine. Paragraphs of five
  to nine sentences with topic sentences, reasons and transitions. Vary the rhythm between sections: framing paragraph, a historical or conceptual aside,
  a worked illustration, a limitation, a bridge to the next topic. Refer to other chapters in plain text where natural. Regroup freely; do not follow
  the slide order or slide titles. Short generic illustrations ("consider a student who ...") are welcome; never present them as research.
* **Tells to avoid** (what made a book "detectable"): subsections that echo slide titles; bullet-fragment prose and bold run-in labels; stacks of lists;
  one uniform template per chapter; boxes under every heading; exam furniture ("expect to be asked", "learn this", "ten-mark answer"); no cross-links
  and no references; emojis, arrows, ticks and other Unicode symbols; markdown (`**`, `#`) in LaTeX; stock phrases ("delve", "tapestry", "pivotal",
  "it is important to note", "in conclusion", "let's", "unlock", "key takeaways"); frequent em dashes. `tb.py voice` flags these (advisory).
* **Never print**: course codes, exam names, module numbers, "lecture", "slide(s)", "deck", "instructor/professor", "syllabus", "semester", "this course",
  institution names, URLs, source-file ids, "not in the slides", "redrawn from the slides". `tb.py scrub` must report 0 findings.
* **References.** Adding a References list is optional; if you do, every entry is verified (a research agent or catalogue pages, status per entry), source
  slides routinely misname titles or years; rewrite unconfirmable quotes as paraphrases; never fill bibliographic details from memory. List every
  author-year you cite in your report.

## 8. LaTeX hygiene
* Write `.tex`/`.py`/`.json` with the Write/Edit tools; **shell heredocs halve backslashes on some Windows setups** (they did, repeatedly).
* ASCII only: `$\rightarrow$`, `$\leq$`, `--`, ``...''; escape `_ % & # $ { }` in text; `\label` after `\caption`.
* No manual spacing hacks (`\vspace`, `\\` for paragraphs, `\newpage`) in chapters; fix overfull boxes by rephrasing or `\allowbreak`.
* A 13-column matrix exceeds `pmatrix`: use `array` with `\left( \right)`. Split a too-wide display with `align*`.
* Do not redirect a native program's stderr in Windows PowerShell 5.1 (`2>&1` turns success into an error).
* Part files have no `\tbchapter`; `tb.py new-book` makes the owner file input its partner just before the Summary. Never edit another author's file.

## 9. Verification of a chapter
`tb.py check <id> <file> --budget N` ends `PROBLEMS: 0` (0 errors, 0 overfull boxes; undefined references from cross-chapter or partner-only labels
are expected in a stand-alone check, verify them with `tb.py build <id>`); `tb.py scrub <files>` reports 0 findings; `tb.py voice <files>` read and
answered. Skim the rendered pages once for gaps, overflow, split boxes and stranded headings. Report: files, pages vs ceiling, counts (sections,
examples, figures used or excluded, supplements, questions), the slide-to-section table with omissions, recomputed numbers, corrections made,
pasted tool output, open problems. Independent recomputation of every number and page-by-page review by reviewers belong to the opt-in
higher-assurance pass (`agent-briefs.md` section 8).
