"""Normalise every raw figure crop so the book's figures look like one set.

Per image: flatten to RGB on white; drop blank images; drop logos / repeated decoration (same perceptual hash on
>= 4 pages); auto-crop surrounding white space and add a uniform margin; bring the width into [MIN_W, MAX_W] px with
Lanczos (never upscale sources under 220 px); save an optimised PNG in figures/pool/ and write figures/pool/index.json.
Also builds numbered contact sheets in _src/contact/ so figures can be chosen by eye.
"""
import json
from collections import defaultdict

import numpy as np
from PIL import Image, ImageDraw, ImageFont

MIN_W, MAX_W, PAD, WHITE_T = 720, 1800, 14, 244


def ahash(im, n=16):
    g = np.asarray(im.convert("L").resize((n, n), Image.LANCZOS), dtype=float)
    return "".join("1" if v > g.mean() else "0" for v in g.flatten())


def autocrop(im):
    a = np.asarray(im)
    mask = (a < WHITE_T).any(axis=2)
    if not mask.any():
        return None
    ys, xs = np.where(mask)
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


def run(prj):
    RAW, POOL, SHEETS = prj.raw_figs, prj.pool, prj.contact
    if not RAW.exists():
        raise SystemExit("no raw figures yet; run  tb.py ingest  first")
    POOL.mkdir(parents=True, exist_ok=True)
    SHEETS.mkdir(parents=True, exist_ok=True)
    items = []
    for sd in sorted(p for p in RAW.iterdir() if p.is_dir()):
        for f in sorted(sd.glob("*.png")):
            page = int(f.stem.split("_")[0][1:])
            items.append({"slug": sd.name, "page": page, "src": f})
    for it in items:
        im = Image.open(it["src"]).convert("RGB")
        it["im"] = im
        it["hash"] = ahash(im)
        it["blank"] = np.asarray(im.convert("L")).std() < 4
    pages_per_hash = defaultdict(set)
    for it in items:
        pages_per_hash[it["hash"]].add((it["slug"], it["page"]))
    index, seen = [], {}
    for it in items:
        if it["blank"]:
            continue
        if len(pages_per_hash[it["hash"]]) >= 4 and it["im"].width < 900:
            continue                                   # logo / repeated decoration
        im = autocrop(it["im"])
        if im is None or im.width < 45 or im.height < 30:
            continue
        canvas = Image.new("RGB", (im.width + 2 * PAD, im.height + 2 * PAD), (255, 255, 255))
        canvas.paste(im, (PAD, PAD))
        im = canvas
        src_w = im.width
        if MIN_W > im.width >= 220:
            s = MIN_W / im.width
            im = im.resize((MIN_W, int(round(im.height * s))), Image.LANCZOS)
        elif im.width > MAX_W:
            s = MAX_W / im.width
            im = im.resize((MAX_W, int(round(im.height * s))), Image.LANCZOS)
        k = it["src"].stem.split("_")[1]
        fid = f'{it["slug"]}_p{it["page"]:03d}_{k}'
        dup = seen.get((it["slug"], it["hash"]))
        seen.setdefault((it["slug"], it["hash"]), fid)
        aspect = im.width / im.height
        suggest = "l" if (aspect >= 1.8 or src_w >= 1500) else ("s" if (aspect <= 0.85 or src_w < 420) else "m")
        colors = len(np.unique(np.asarray(im.resize((120, 120))).reshape(-1, 3), axis=0))
        im.save(POOL / f"{fid}.png", optimize=True)
        index.append({"id": fid, "file": f"pool/{fid}.png", "slug": it["slug"], "page": it["page"], "w": im.width, "h": im.height,
                      "src_w": src_w, "aspect": round(aspect, 2), "suggest": suggest, "low_res": src_w < 420,
                      "kind": "photo" if colors > 3000 else "diagram", "dup_of": dup})
    (POOL / "index.json").write_text(json.dumps(index, indent=1), encoding="utf-8")
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except Exception:
        font = ImageFont.load_default()
    by = defaultdict(list)
    for e in index:
        if not e["dup_of"]:
            by[e["slug"]].append(e)
    for slug, es in by.items():
        for k in range(0, len(es), 12):
            chunk = es[k:k + 12]
            cw, ch = 520, 400
            sheet = Image.new("RGB", (4 * cw, 3 * ch), (235, 235, 235))
            d = ImageDraw.Draw(sheet)
            for j, e in enumerate(chunk):
                im = Image.open(POOL.parent / e["file"])
                im.thumbnail((cw - 20, ch - 50))
                x, y = (j % 4) * cw + 10, (j // 4) * ch + 8
                sheet.paste(im, (x, y + 30))
                d.text((x, y), f'{e["id"]}  {e["w"]}x{e["h"]}', fill=(0, 0, 0), font=font)
            sheet.save(SHEETS / f"{slug}_{k // 12 + 1:02d}.png")
    per = defaultdict(int)
    for e in index:
        per[e["slug"]] += 1
    print(f"raw={len(items)} kept={len(index)} unique={sum(1 for e in index if not e['dup_of'])} low_res={sum(e['low_res'] for e in index)}")
    print(dict(per))
    return index
