"""Print audit -- reads the compiled PDF itself (never the LaTeX log), so it catches what a log cannot.

Checks
  1  page size equals the configured paper on every page          2  every font is embedded
  3  header/footer sit at one y position; footer number == physical page - front pages
  4  chapter openers sit on recto (odd) pages; blank versos carry no header or number
  5  text, figures and TikZ drawings never leave the (mirrored) text block
  6  big white gaps: a page that is not the last of its chapter with > gap_limit % of the text block empty at the bottom
  7  optional page budget
"""
import re
import statistics
from collections import Counter

import fitz

PAPER = {"a4paper": (595.276, 841.89), "letterpaper": (612.0, 792.0), "a5paper": (419.528, 595.276),
         "b5paper": (498.9, 708.66), "legalpaper": (612.0, 1008.0)}


def audit(prj, pdf, budget=None, quiet=False):
    lay = prj.cfg["layout"]
    W, H = PAPER.get(lay["paper"], PAPER["a4paper"])
    m, b = float(lay["margin_pt"]), float(lay["binding_pt"])
    LMR, RMR = m + b, W - m          # recto: binding offset on the left
    LMV, RMV = m, W - m - b          # verso: binding offset on the right
    hz = m - 10                      # header / footer zones (pt from the page edge)
    TOL, gap_limit = 3.0, float(lay["gap_limit_pct"]) / 100.0
    problems = []
    out = (lambda *a: None) if quiet else print

    def bad(msg):
        problems.append(msg)

    d = fitz.open(str(pdf))
    sizes = Counter((round(p.rect.width, 1), round(p.rect.height, 1)) for p in d)
    out("page sizes:", dict(sizes))
    if set(sizes) != {(round(W, 1), round(H, 1))}:
        bad(f"page size is not {lay['paper']}: {dict(sizes)}")
    if budget:
        out(f"page budget: {len(d)} pages of {budget} allowed")
        if len(d) > budget:
            bad(f"{len(d)} pages exceeds the budget of {budget}")
    fonts_bad = set()
    for p in d:
        for f in p.get_fonts(full=True):
            if f[0] == 0 and not f[3].endswith("Type3"):
                fonts_bad.add(f[3])
    out("fonts not embedded:", sorted(fonts_bad) or "none")
    if fonts_bad:
        bad(f"non-embedded fonts: {sorted(fonts_bad)}")

    info = []
    for i, p in enumerate(d, 1):
        blocks = [x for x in p.get_text("blocks") if x[4].strip()]
        head = [x for x in blocks if x[3] < hz]
        foot = [x for x in blocks if x[1] > H - hz]
        body = [x for x in blocks if x[3] >= hz and x[1] <= H - hz]
        objs = [fitz.Rect(im["bbox"]) for im in p.get_image_info() if im["bbox"][3] >= hz and im["bbox"][1] <= H - hz]
        for dr in p.get_drawings():
            r = dr["rect"]
            if r.y1 < hz or r.y0 > H - hz or (r.width > W * 0.98 and r.height > H * 0.9):
                continue
            objs.append(r)
        info.append(dict(n=i, head=head, foot=foot, body=body, objs=objs,
                         ftxt=foot[0][4].strip() if foot else "", text=" ".join(x[4] for x in blocks)))
    head_y = sorted({round(x[1], 1) for r in info for x in r["head"]})
    foot_y = sorted({round(x[1], 1) for r in info for x in r["foot"]})
    out("distinct header y positions :", head_y)
    out("distinct footer y positions :", foot_y)
    if len(head_y) > 1 and max(head_y) - min(head_y) > 1.5:
        bad(f"header y varies: {head_y}")
    if len(foot_y) > 1 and max(foot_y) - min(foot_y) > 1.5:
        bad(f"footer y varies: {foot_y}")

    arab = [(r["n"], int(r["ftxt"])) for r in info if re.fullmatch(r"\d+", r["ftxt"])]
    first_main = 1
    if arab:
        off, cnt = Counter(n - v for n, v in arab).most_common(1)[0]
        out(f"main matter starts at physical page {max(1, off + 1)}; footer offset consistent on {cnt}/{len(arab)} numbered pages")
        for n, v in arab:
            if n - v != off:
                bad(f"page {n}: footer shows {v}, expected {n - off}")
        first_main = max(1, off + 1)       # an excerpt that starts at folio 88 has a negative offset: main matter is page 1

    openers = []
    for r in info:
        mm = re.match(r"\s*(?:CHAPTER|APPENDIX)\s*(\d+|[A-Z]\b)", r["text"], re.I)
        if r["n"] >= first_main and mm and not r["head"]:
            openers.append((r["n"], mm.group(1)))
    out("chapter openers (physical page, chapter):", openers)
    for n, c in openers:
        if n % 2 == 0:
            bad(f"chapter {c} opens on a verso (physical page {n})")
    for r in info:
        if not r["body"] and not r["head"] and r["ftxt"]:
            bad(f"page {r['n']}: blank page carries a number '{r['ftxt']}'")

    for r in info:
        if r["n"] < first_main:
            continue
        L, R = (LMR, RMR) if r["n"] % 2 else (LMV, RMV)
        for x in r["body"]:
            if x[0] < L - TOL or x[2] > R + TOL:
                bad(f"page {r['n']}: text outside margins x={x[0]:.0f}..{x[2]:.0f} (allowed {L:.0f}..{R:.0f}): {x[4].strip()[:40]!r}")
        for o in r["objs"]:
            if o.x0 < L - TOL or o.x1 > R + TOL:
                bad(f"page {r['n']}: figure/drawing outside text block x={o.x0:.0f}..{o.x1:.0f} (allowed {L:.0f}..{R:.0f})")
                break

    widths = []
    for i, p in enumerate(d, 1):
        if i < first_main:
            continue
        for im in p.get_image_info():
            x0, y0, x1, y1 = im["bbox"]
            if x1 - x0 < 60:
                continue
            widths.append(round(x1 - x0))
            if y1 > H - hz + 2 or y0 < hz - 2:
                bad(f"page {i}: figure runs into the header/footer zone")
    out(f"raster figures: {len(widths)}; width pt min/median/max = "
        f"{min(widths) if widths else '-'}/{statistics.median(widths) if widths else '-'}/{max(widths) if widths else '-'}")

    # Unnumbered openers (index, appendix without a label, formula sheet) also have no running header: treat any
    # headerless page with body text as an opener, so the page before it counts as the last page of its chapter.
    ends = {o[0] for o in openers} | {r["n"] for r in info if r["n"] >= first_main and r["body"] and not r["head"]}
    last = {len(d)}
    for n in sorted(ends):
        k = n - 1
        while k > first_main and not info[k - 1]["body"]:
            k -= 1
        if k > first_main:
            last.add(k)
    gaps = []
    for r in info:
        if r["n"] < first_main or r["n"] in ends or r["n"] in last or not (r["body"] or r["objs"]):
            continue
        bottom = max([x[3] for x in r["body"]] + [o.y1 for o in r["objs"]])
        if bottom < H - m - gap_limit * (H - 2 * m):
            gaps.append((r["n"], round((H - m - bottom) / (H - 2 * m) * 100)))
    out(f"pages with >{int(gap_limit * 100)}% empty at the bottom (page, % empty):", gaps or "none")
    for n, pct in gaps:
        bad(f"page {n}: {pct}% of the text block empty at the bottom")

    out("\nPROBLEMS:", len(problems))
    for msg in problems[:60]:
        out(" -", msg)
    return problems
