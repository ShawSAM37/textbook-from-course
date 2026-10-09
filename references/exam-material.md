# Past papers, question banks and predicted questions

Contents: 1 Principle - 2 Intake - 3 Routing - 4 Where they are printed - 5 Restating a paper - 6 Solutions - 7 Predicted practice
questions - 8 Typed question banks - 9 Fidelity check - 10 Budget and cost

## 1. Principle
Past papers and question banks are **content**, not style guidance. A user who hands them over expects to find every question in the
book, solved (one asked: "why cant i see those questions in the pdf"; two others demanded "all the pyqs with solutions"). The papers
also fix the exam format and emphasis, so ask for them when none were supplied (SKILL.md Step 0). Predicted questions are the model's
job; everything in the papers and the notes must be present.

## 2. Intake
* Unpack zips. Copy papers into the material folder with systematic names (`paper_<n>_<QP|KEY>.pdf`); **do not trust the original
  file names** (a file called "key" was a different paper; a key may sit inside the paper's own file; two files named for different sessions
  were the same paper). De-duplicate identical papers (keep one, note the duplicate; a copy with a student's handwriting is never reproduced).
* Scanned papers are transcribed **by eye from the page renders** (OCR garbles hex, mnemonics, code, matrices and mark columns), in batches of
  4-6 papers per subagent, one transcription file per batch. For each paper record: question count, marks per question ("not printed" if so),
  pages that are answer keys, exact duplicates, illegible spots.
* If a printed exam date shows the assessment window may still be open, tell the user before including the paper.
* Papers may also reveal that topics are tested which the notes never teach; see section 3.

## 3. Routing
Build `_src/briefs/pyq_routing.md`: one row per question (tag, marks, sub-parts, target chapter or appendix, topic). Check the table against
the renders before briefing authors (marks and question order are routinely mis-OCRed). Add a topic-frequency count; it feeds the order of
the practice questions and an optional "recurring question types" table at the end of the appendix. A question with no home in any chapter
is a gap: ask the user once and, usually, add a short supporting chapter or section of supplement boxes (standard knowledge, marked as such,
never blended into course-sourced boxes), then say plainly that these sections come from outside the supplied material.

## 4. Where they are printed (default)
Appendices after the last chapter and before the index: `books[].appendices` in `book.json` (`file`, `title`, `budget`), one appendix per
five or six papers, titled honestly ("Examination Papers with Solutions", "... (continued)"). `tb.py new-book` writes the skeletons
(`assets/appendix.tex.tmpl`) and the `\appendix` line; `tb.py check <id> appA` compiles one appendix. Each paper is a `\section`, its answers a
`\section` right after it; exercise numbering runs A.1, A.2, ... Alternative when the user prefers: route each question into the chapter that
teaches it, tagged `[Paper 3, Question 2]` and labelled `cN-pK`; extras `cN-xK`. Either way the origin is stated openly. Hiding a paper's
origin was refused and was also unnecessary: a neutral label keeps the identity scrub honest.

## 5. Restating a paper
Verbatim and in the original order; keep every data value, mark and sub-part label ((b), (c) stay (b), (c)). Remove years, terms, slots, dates,
institution, names, registration numbers. If identity-bearing strings sit inside the question data (a name inside an example program), replace them
with neutral placeholders that keep the question logically consistent. Marks as printed; where none are printed, none are printed.

## 6. Solutions
* Complete and **self-contained**: restate inline every definition, formula, register or port convention, diagram or table the answer needs,
  even when a sibling solution already did. A `Section~\ref{..}` pointer may be added as an extra, never as a substitute (a user: "dont do like
  as in section x blah blah, i dont want to go back and check what that section is"). Check with a grep for `\ref{` inside every `exsol`.
* **Solve every question independently and recompute every number** in a scratch script (or compile and run code if a compiler exists; WSL
  often has gcc). Printed keys are frequently wrong or mere outlines (a covering radius, a Huffman bit count, task sets with utilisation above 1);
  where the key is wrong, solve correctly and add one neutral sentence only when a legitimate alternative convention exists. Never write "the key
  says". An infeasible question gets "not schedulable" plus the requested repair, which is a legitimate answer. State any convention adopted
  (rounding versus truncation, tie-break, pixel depth); follow the notes' convention first and mention the other.
* A solution that needs knowledge absent from the material opens with a supplement-style note ("beyond the course material"); one chapter once
  shipped an unmarked outside-knowledge solution, which breaks SKILL.md's rule.
* Length: about 1.1-1.2 pages per solved code or numerical question (measured 25 questions -> 29 pages), 0.6-0.7 for prose-only answers.
* Set solutions one size smaller (`exsol` does); no marking-scheme lines when the identity is hidden unless the paper printed them.

## 7. Predicted practice questions (every chapter)
`\section{Practice Questions}` after the review questions: eight to fourteen questions in the style and mark structure of the papers, with fresh
scenarios and fresh numbers (never recycled from a paper), and a complete answer for each in the chapter's Answers section. Open the section with
one honest sentence: these are further questions in the manner of the earlier papers, written for this book, not extracts. Order them from most
to least likely by the topic-frequency table; do not claim likelihood the evidence does not support. Optional at the chapter opening or appendix end:
a topic-frequency table and a ranked list of recurring question types; at the end, a short answering-strategy checklist.

## 8. Typed question banks ("all types of question")
When the user or the papers want objective items as well, end the chapter with unnumbered `\subsection*{Part ...}` parts inside the review/practice
sections: A objective (one `exq[n]` per type containing an `enumerate`: MCQ with inline (a)-(d) options, fill-in-the-blank, true/false with reason,
match-the-following as a `tabularx` after a `\noindent`, assertion-reason), B short, C long, D scenario case studies (lettered sub-questions with
marks), E application. Answers mirror one-to-one in matching `exsol`s. Avoid `\multirow` inside `tabularx` (overfull vbox).

## 9. Fidelity check (once per book, by an independent agent when papers were scanned)
Compare every restated question with its render: text, data values, marks, sub-part labels, order; then every routing row. Defects found in
practice: swapped source tags (OCR order opposite to the page), sub-parts relabelled (b),(c),(d) printed as (a),(b),(c), a key-contradicted
convention, missing notes content. Report what was and was not checked in the final message.

## 10. Budget and cost
Reserve about 10 % headroom in each chapter's ceiling for what the checks add. Measured: restating and solving 15 scanned papers with the notes of
four decks took 77 minutes and 3.5 M subagent tokens over 15 agents; one appendix author up to 49 minutes. A mid-size exam book (3-5 chapters, 5-8
papers) is therefore a long run: say so before starting, stage the chapters and the appendices as separate agents, and resume instead of restarting
after an interruption.
