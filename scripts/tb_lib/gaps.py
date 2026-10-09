"""Syllabus coverage analysis.

topics file (JSON): [{"topic": "Amdahl's law", "chapter": "ch04", "patterns": ["amdahl", "speed-?up limit"]}, ...]
For every topic the tool counts regex hits per source (text layer + OCR) and lists the strongest sources, so the
planner can see which topics are well covered, thin, or missing.  Hits are a search aid only: a topic with hits can
still be shallow, and a topic without hits may live in an image -- always confirm thin/missing topics in the renders.
Also: `find` searches one regex across all extracted text and prints page numbers.
"""
import json
import re
from pathlib import Path


def _texts(prj):
    out = {}
    for f in list(prj.text.glob("*.txt")) + list(prj.ocr.glob("*.txt")):
        slug = f.stem
        out.setdefault(slug, "")
        out[slug] += "\n" + f.read_text(encoding="utf-8", errors="ignore")
    return out


def coverage(prj, topics_file):
    topics = json.loads(Path(topics_file).read_text(encoding="utf-8-sig"))
    texts = _texts(prj)
    roles = {s: v.get("role", "material") for s, v in prj.cfg["sources"].items()}
    print(f"{'topic':40s} {'ch':6s} {'material':>8s} {'reference':>9s}  strongest sources")
    verdicts = {"missing": [], "thin": []}
    for t in topics:
        rx = re.compile("|".join(t["patterns"]) if isinstance(t["patterns"], list) else t["patterns"], re.I)
        hits = {s: len(rx.findall(x)) for s, x in texts.items()}
        mat = sum(c for s, c in hits.items() if roles.get(s) not in ("reference", "syllabus"))   # a syllabus naming a topic is not coverage
        ref = sum(c for s, c in hits.items() if roles.get(s) == "reference")
        top = sorted(((c, s) for s, c in hits.items() if c and roles.get(s) != "syllabus"), reverse=True)[:3]
        tag = ""
        if mat == 0:
            tag = "  <-- NOT IN MATERIAL" + (" (reference textbook has it)" if ref else " (write as supplement)")
            verdicts["missing"].append(t["topic"])
        elif mat < 4:
            tag = "  <-- thin"
            verdicts["thin"].append(t["topic"])
        print(f"{t['topic'][:40]:40s} {t.get('chapter', ''):6s} {mat:8d} {ref:9d}  " + "; ".join(f"{s}={c}" for c, s in top) + tag)
    print(f"\nmissing from the material: {len(verdicts['missing'])}  thin: {len(verdicts['thin'])}")
    return verdicts


def find(prj, regex, limit=40):
    rx = re.compile(regex, re.I)
    n = 0
    for f in sorted(prj.text.glob("*.txt")) + sorted(prj.ocr.glob("*.txt")):
        page = 0
        for line in f.read_text(encoding="utf-8", errors="ignore").splitlines():
            m = re.match(r"=====PAGE (\d+)=====", line)
            if m:
                page = int(m.group(1))
                continue
            if rx.search(line):
                kind = "ocr" if f.parent.name == "ocr" else "txt"
                print(f"{f.stem}[{kind}] p{page}: {line.strip()[:150]}")
                n += 1
                if n >= limit:
                    print(f"... stopped after {limit} hits (use a narrower pattern)")
                    return
    if n == 0:
        print("no hits")
