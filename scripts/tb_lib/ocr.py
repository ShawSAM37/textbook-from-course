"""OCR the text-light pages/slides (code screenshots, image-only slides) and build 2x2 contact sheets of the renders.

Needs rapidocr-onnxruntime.  `tb.py doctor --setup-ocr` creates a private virtual environment for it; `tb.py ocr`
re-runs itself inside that environment automatically.  OCR text is approximate (0/o, 1/l, dropped spaces, () read as
O): it is a search aid, never the source for code or formulas -- look at the render.
"""
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def lines_in_order(res):
    """Group OCR boxes into text rows by y-centre, then sort each row by x."""
    boxes = []
    for box, text, conf in res or []:
        ys = [p[1] for p in box]
        xs = [p[0] for p in box]
        boxes.append((sum(ys) / 4, min(xs), max(ys) - min(ys), text))
    boxes.sort()
    rows, cur, cy, ch = [], [], None, 0
    for yc, x, h, t in boxes:
        if cy is None or abs(yc - cy) <= max(ch, h) * 0.6:
            cur.append((x, t))
            cy = yc if cy is None else (cy + yc) / 2
            ch = max(ch, h)
        else:
            rows.append(cur)
            cur, cy, ch = [(x, t)], yc, h
    if cur:
        rows.append(cur)
    return ["  ".join(t for _, t in sorted(r)) for r in rows]


def run(prj, slugs=None, force=False):
    from rapidocr_onnxruntime import RapidOCR
    manifest = prj.manifest()
    if not manifest:
        raise SystemExit("no manifest; run  tb.py ingest  first")
    ocr = RapidOCR()
    prj.ocr.mkdir(parents=True, exist_ok=True)
    for slug, m in manifest.items():
        if slugs and slug not in slugs:
            continue
        out = prj.ocr / f"{slug}.txt"
        if out.exists() and not force and not slugs:
            print("skip", slug)
            continue
        t0 = time.time()
        parts = []
        for n in m["low_text_units"]:
            img = prj.render / slug / f"{n:03d}.png"
            if not img.exists():
                continue
            res, _ = ocr(str(img))
            parts.append(f"\n=====PAGE {n}=====\n" + "\n".join(lines_in_order(res)))
        out.write_text("".join(parts), encoding="utf-8")
        print(f"{slug:12s} ocr pages={len(m['low_text_units']):3d} {time.time() - t0:5.0f}s", flush=True)


def make_sheets(prj, tile_w=1000):
    """2x2 contact sheets of the page renders: _src/sheets/<slug>_NN.png (page number in a red tag)."""
    prj.sheets.mkdir(parents=True, exist_ok=True)
    try:
        font = ImageFont.truetype("arialbd.ttf", 34)
    except Exception:
        font = ImageFont.load_default()
    n_sheets = 0
    for slug in prj.manifest():
        files = sorted((prj.render / slug).glob("*.png"))
        for k in range(0, len(files), 4):
            tiles = []
            for f in files[k:k + 4]:
                im = Image.open(f).convert("RGB")
                tiles.append((int(f.stem), im.resize((tile_w, int(round(im.height * tile_w / im.width))), Image.LANCZOS)))
            th = max(t[1].height for t in tiles)
            sheet = Image.new("RGB", (2 * tile_w + 30, 2 * th + 30), (90, 90, 90))
            d = ImageDraw.Draw(sheet)
            for j, (n, im) in enumerate(tiles):
                x, y = 10 + (j % 2) * (tile_w + 10), 10 + (j // 2) * (th + 10)
                sheet.paste(im, (x, y))
                d.rectangle([x, y, x + 96, y + 44], fill=(200, 0, 0))
                d.text((x + 8, y + 3), f"{n}", fill=(255, 255, 255), font=font)
            sheet.save(prj.sheets / f"{slug}_{k // 4 + 1:02d}.png")
            n_sheets += 1
    print("sheets:", n_sheets)
