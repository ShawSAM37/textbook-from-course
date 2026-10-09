"""Identity scrub: find anything that ties the finished book to a course, lecturer, institution, syllabus or exam.

Generic patterns (lecture, slide, deck, instructor, syllabus, semester, "this course", module numbers, "not in the slides")
are always active.  Project-specific identity comes from book.json -> identity:
  terms    : literal strings to forbid (course code, course name, institution, lecturer, exam name), case-insensitive,
             matched as whole words (a short acronym does not fire inside "activity"; never list the book's own subject words)
  patterns : extra regular expressions
  allow    : regexes for harmless contexts around a hit (e.g. "slides a tile" in a puzzle)
Scans: TeX sources (comments and \\label/\\ref/file-path arguments are ignored), the extracted text and metadata of a finished PDF,
and the text INSIDE embedded images (OCR) -- screenshots often carry hostnames, user names or logos.
"""
import io
import re
from pathlib import Path

import fitz

GENERIC = [
    (r"\blectures?\b", "lecture"),
    (r"\bslides?\b", "slide"),
    (r"\bdecks?\b", "slide deck"),
    (r"\binstructors?\b|\bprofessors?\b|\bsyllabus\b|\bsemester\b|\bAcademic Council\b", "course staff / syllabus"),
    (r"\b[Mm]odules?\s*\d", "module number"),
    (r"\b(this|the|our)\s+course\b|\bcourse\s+(material|notes|code)\b|\bcoursework\b", "course"),
    (r"\bnot in (the )?(lecture |course )?(slides|material|notes)\b", "not-in-slides marker"),
]
GENERIC_ALLOW = [r"slides? (a |the |one )?(tile|blank|window)", r"\bslide (across|over|along|down|up|left|right)\b", r"sliding",
                 r"\b(cross|turret|press)[- ]slide\b", r"\bin the course of\b"]
IMAGE_EXTRA = [(r"\.edu\b|\.ac\.[a-z]{2}\b", "academic domain"), (r"/home/(?!user\b)\w+|/users/(?!user\b)\w+", "user directory"),
               (r"@[\w.-]+\.\w{2,}", "e-mail / host")]


def _term_rx(t):
    rx = re.escape(t).replace(r"\ ", r"\s+")
    if t[:1].isalnum():
        rx = r"(?<![A-Za-z0-9])" + rx
    if t[-1:].isalnum():
        rx += r"(?![A-Za-z0-9])"
    return rx


def _resolve(prj, f):
    """Accept a path relative to the current directory or to the project folder; fail with a message, not a Traceback."""
    for p in (Path(f), prj.root / f):
        if p.is_file():
            return p
    raise SystemExit(f"scrub: file not found: {f} (give a path relative to the current directory or to the project folder {prj.root})")


def patterns(prj, images=False):
    ident = prj.cfg["identity"]
    pats = list(GENERIC)
    for t in ident.get("terms", []):
        pats.append((_term_rx(t), f"identity term '{t}'"))
    for rx in ident.get("patterns", []):
        pats.append((rx, "identity pattern"))
    if images:
        pats += IMAGE_EXTRA
    allow = GENERIC_ALLOW + list(ident.get("allow", []))
    return pats, allow


def _scan_text(name, lines, pats, allow, tex=True):
    hits = 0
    for i, line in enumerate(lines, 1):
        code = line
        if tex:
            if line.lstrip().startswith("%"):
                continue
            code = re.sub(r"(?<!\\)%.*$", "", line)
            code = re.sub(r"\\(label|ref|eqref|pageref|input|InputIfFileExists)\{[^{}]*\}", "", code)
            code = re.sub(r"[\w/\-]*pool/[\w\-./]+", "", code)
        for rx, why in pats:
            for m in re.finditer(rx, code, flags=re.I):
                ctx = code[max(0, m.start() - 25): m.end() + 25]
                if any(re.search(a, ctx, re.I) for a in allow):
                    continue
                print(f"{name}:{i}: [{why}] ...{ctx.strip()}...")
                hits += 1
    return hits


def scan_tex(prj, files):
    pats, allow = patterns(prj)
    total = 0
    for f in files:
        with io.open(_resolve(prj, f), encoding="utf-8", errors="ignore") as fh:
            total += _scan_text(f, fh.read().splitlines(), pats, allow)
    print(f"\nSCRUB CHECK (tex): {total} finding(s)")
    return total


def scan_pdf(prj, files):
    pats, allow = patterns(prj)
    total = 0
    for f in files:
        d = fitz.open(_resolve(prj, f))
        for pno, p in enumerate(d, 1):
            total += _scan_text(f"{f} p{pno}", p.get_text().splitlines(), pats, allow, tex=False)
        for k, v in (d.metadata or {}).items():
            if v and any(re.search(rx, str(v), re.I) for rx, _ in pats):
                print(f"{f}: metadata {k}={v!r}")
                total += 1
    print(f"\nSCRUB CHECK (pdf text + metadata): {total} finding(s)")
    return total


def scan_images(prj, files):
    import numpy as np
    from PIL import Image
    from rapidocr_onnxruntime import RapidOCR
    pats, allow = patterns(prj, images=True)
    ocr = RapidOCR()
    total = 0
    for f in files:
        d = fitz.open(f)
        seen, n_img = set(), 0
        for pno, page in enumerate(d, 1):
            for img in page.get_images(full=True):
                xref = img[0]
                if xref in seen:
                    continue
                seen.add(xref)
                try:
                    pm = fitz.Pixmap(d, xref)
                    if pm.n - pm.alpha >= 4:
                        pm = fitz.Pixmap(fitz.csRGB, pm)
                    im = Image.open(io.BytesIO(pm.tobytes("png")))
                except Exception:
                    continue
                if im.width < 120 or im.height < 60:
                    continue
                n_img += 1
                res, _ = ocr(np.array(im.convert("RGB"))[:, :, ::-1])
                text = " ".join(r[1] for r in (res or []))
                for rx, why in pats:
                    for m in re.finditer(rx, text, flags=re.I):
                        ctx = text[max(0, m.start() - 30): m.end() + 30]
                        if any(re.search(a, ctx, re.I) for a in allow):
                            continue
                        print(f"{f} p{pno} image {im.width}x{im.height}: [{why}] ...{ctx}...")
                        total += 1
        print(f"{f}: {n_img} images read with OCR")
    print(f"\nIMAGE SCRUB: {total} hit(s)")
    return total
