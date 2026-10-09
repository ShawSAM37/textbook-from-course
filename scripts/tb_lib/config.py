"""Project configuration.  A textbook project is a folder holding book.json plus everything derived from it."""
import json
import os
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")   # Windows consoles default to a legacy codepage
except Exception:
    pass

SKILL_DIR = Path(__file__).resolve().parents[2]
ASSETS = SKILL_DIR / "assets"


def style_asset(style, name):
    """assets/<name> for the default 'classic' style, assets/<stem>-modern<ext> for 'modern'
    (name is e.g. 'textbook.sty', 'book.tex.tmpl')."""
    if style == "modern":
        stem, _, ext = name.partition(".")
        return ASSETS / f"{stem}-modern.{ext}"
    return ASSETS / name

DEFAULTS = {
    "material_dir": "",
    "sources": {},
    "identity": {"terms": [], "patterns": [], "allow": []},
    "layout": {"paper": "a4paper", "font_pt": 11, "margin_pt": 72.0, "binding_pt": 18.0, "gap_limit_pct": 35,
               "typeface": "Times", "style": "classic"},
    "ingest": {"render_width": 1600, "crop_width": 2400, "pdf_crop_dpi": 220},
    "books": [],
}


def merge(base, extra):
    out = dict(base)
    for k, v in (extra or {}).items():
        out[k] = merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


class Project:
    def __init__(self, root, cfg):
        self.root = Path(root)
        self.cfg = cfg
        self.src = self.root / "_src"
        self.text = self.src / "text"
        self.render = self.src / "render"
        self.raw_figs = self.src / "raw_figs"
        self.ocr = self.src / "ocr"
        self.sheets = self.src / "sheets"
        self.contact = self.src / "contact"
        self.pool = self.root / "figures" / "pool"
        self.build = self.root / "build"
        self.manifest_path = self.src / "manifest.json"

    # -- convenience -------------------------------------------------------
    @property
    def material_dir(self):
        return Path(self.cfg["material_dir"]) if self.cfg.get("material_dir") else self.root

    def source_path(self, slug):
        return self.material_dir / self.cfg["sources"][slug]["file"]

    def book(self, book_id):
        for b in self.cfg["books"]:
            if b["id"] == book_id:
                return b
        raise SystemExit(f"unknown book id {book_id!r}; books in book.json: {[b['id'] for b in self.cfg['books']]}")

    def chapter_of(self, book_id, file):
        """Return (chapter dict, is_partner) for a chapter file name such as ch03 or ch03_decomp."""
        b = self.book(book_id)
        for c in b["chapters"]:
            if c["file"] == file:
                return c, False
            if c.get("partner") and c["partner"]["file"] == file:
                return c, True
        for a in b.get("appendices", []):        # restated past papers etc.: plain \chapter after \appendix
            if a["file"] == file:
                return dict(a, appendix=True, number=0), False
        raise SystemExit(f"{file!r} is not a chapter, partner or appendix file of book {book_id!r}")

    def manifest(self):
        return json.loads(self.manifest_path.read_text(encoding="utf-8-sig")) if self.manifest_path.exists() else {}

    def save_manifest(self, m):
        self.src.mkdir(parents=True, exist_ok=True)
        self.manifest_path.write_text(json.dumps(m, indent=1, ensure_ascii=False), encoding="utf-8")

    def save(self):
        (self.root / "book.json").write_text(json.dumps(self.cfg, indent=1, ensure_ascii=False), encoding="utf-8")


def find_root(start=None):
    p = Path(start or os.getcwd()).resolve()
    for d in [p, *p.parents]:
        if (d / "book.json").exists():
            return d
    raise SystemExit("book.json not found in this folder or its parents.  Create a project first:  tb.py init <folder>")


def load(root=None):
    root = Path(root).resolve() if root else find_root()
    cfg = json.loads((root / "book.json").read_text(encoding="utf-8-sig"))    # utf-8-sig: Windows PowerShell adds a BOM
    return Project(root, merge(DEFAULTS, cfg))


def slugify(name, taken):
    stem = re.sub(r"\.[A-Za-z0-9]+$", "", name)
    stem = re.sub(r"^(fallsem|winsem)[\w-]*?_(th|lo|etl)_\d{4}-\d{2}-\d{2}_", "", stem, flags=re.I)   # LMS export prefixes
    words = re.findall(r"[A-Za-z0-9]+", stem.lower())
    words = [w for w in words if w not in {"the", "and", "of", "with", "for", "a", "an", "to", "in", "on", "pdf", "pptx", "ppt", "docx"}]
    slug = ""                                   # whole words while they fit in 14 characters (readable, short)
    for w in words:
        if slug and len(slug) + len(w) > 14:
            break
        slug += w
    slug = slug[:14] or "src"
    base, n = slug, 2
    while slug in taken:
        slug = f"{base}{n}"
        n += 1
    return slug
