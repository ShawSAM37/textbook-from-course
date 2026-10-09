"""Voice lint (advisory, never blocks a release): things that make a book read as machine-written or slide-derived.

Counts, per chapter file: stock phrases, em-dash density, markdown leaks, stacks of bullet lists, bold run-in labels,
exclamations.  Thresholds are deliberately loose: a hit is a prompt to reread the passage, not a verdict.
"""
import io
import re
from pathlib import Path

PHRASES = re.compile(
    r"\b(delv(?:e|es|ing)|tapestry|testament to|pivotal|multifaceted|holistic|seamless(?:ly)?|leverag(?:e|es|ing)|"
    r"navigat(?:e|es|ing) the (?:complexit\w+|landscape)|in today'?s|it is (?:important|worth) (?:to note|noting)|"
    r"in conclusion|let'?s|let us (?:explore|dive)|dive into|unlock(?:s|ing)?|key takeaways?|"
    r"in this chapter,? we will (?:explore|look|delve)|a (?:rich|vibrant) (?:tapestry|landscape))\b", re.I)
MARKDOWN = re.compile(r"\*\*[^*]+\*\*|^\s*#{1,6}\s|^\s*[-*]\s+\S|`[^`]+`")
RUNIN = re.compile(r"\\textbf\{[^{}]{1,40}[.:]\}|\\textbf\{[^{}]{1,40}\}\s*[.:]")
LISTS = re.compile(r"\\begin\{(itemize|enumerate)\}")
NONASCII = re.compile(r"[^\x00-\x7f]")


def _body(path):
    out = []
    for ln in io.open(path, encoding="utf-8", errors="ignore").read().splitlines():
        if ln.lstrip().startswith("%"):
            continue
        out.append(re.sub(r"(?<!\\)%.*$", "", ln))
    return "\n".join(out)


def lint(files):
    flagged = 0
    for f in files:
        p = Path(f)
        if not p.is_file():
            raise SystemExit(f"voice: file not found: {f}")
        text = _body(p)
        words = max(1, len(re.findall(r"[A-Za-z']+", re.sub(r"\\[A-Za-z]+", " ", text))))
        # objectives boxes and the summary legitimately use lists, so only count lists outside the first one
        lists = max(0, len(LISTS.findall(text)) - 1)
        notes = []
        ph = PHRASES.findall(text)
        if ph:
            notes.append(f"stock phrases x{len(ph)}: {sorted(set(m.lower() if isinstance(m, str) else m[0].lower() for m in ph))[:6]}")
        dashes = text.count("---")
        if dashes * 1000 / words > 3:
            notes.append(f"em dashes: {dashes} in {words} words (> 3 per 1000)")
        md = MARKDOWN.findall(text)
        if md:
            notes.append(f"markdown leaking into LaTeX x{len(md)}, e.g. {md[0]!r}")
        if lists > 3:
            notes.append(f"{lists} bullet/number lists outside the objectives (aim for 3 or fewer)")
        ri = RUNIN.findall(text)
        if len(ri) > 4:
            notes.append(f"bold run-in labels x{len(ri)} (reads like converted slides)")
        if text.count("!") > 2:
            notes.append(f"exclamation marks x{text.count('!')}")
        na = NONASCII.findall(text)
        if na:
            notes.append(f"non-ASCII characters x{len(na)}: {sorted(set(na))[:6]}")
        print(f"{f}: {words} words")
        for n in notes:
            print("   -", n)
        flagged += len(notes)
    print(f"\nVOICE LINT (advisory): {flagged} note(s)")
    return flagged
