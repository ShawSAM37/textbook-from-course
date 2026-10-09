"""Create a project folder, render the book's front matter from a template, and generate chapter skeletons."""
import datetime
import json
import shutil
from pathlib import Path

from .config import ASSETS, DEFAULTS, style_asset


def tex_escape(s):
    rep = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
           "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(rep.get(c, c) for c in s)


def init_project(folder, material_dir="", style="classic"):
    root = Path(folder).resolve()
    cfg_path = root / "book.json"
    if cfg_path.exists():
        raise SystemExit(f"{cfg_path} already exists: {root} is another project (--material was ignored and its style file would be "
                         f"overwritten). Run init in a new, empty folder.")
    root.mkdir(parents=True, exist_ok=True)
    cfg = json.loads((ASSETS / "book.example.json").read_text(encoding="utf-8"))
    cfg["material_dir"] = str(Path(material_dir).resolve()).replace("\\", "/") if material_dir else ""
    cfg["sources"] = {}
    cfg["books"] = []
    cfg.setdefault("layout", {})["style"] = style
    cfg["layout"]["typeface"] = "Palatino" if style == "modern" else "Times"
    cfg_path.write_text(json.dumps(cfg, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"created {cfg_path}")
    shutil.copy(style_asset(style, "textbook.sty"), root / "textbook.sty")
    for d in ("_src", "figures/pool", "build"):
        (root / d).mkdir(parents=True, exist_ok=True)
    print(f"project ready in {root}\nnext: tb.py --project \"{root}\" scan")
    return root


def _split_title(title, width=24):
    words, lines, cur = title.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    lines.append(cur)
    return lines[:3]


def _initials(author):
    parts = [p for p in author.replace(".", ". ").split() if p]
    return r"\,".join(p[0] + "." for p in parts)


def render_book(prj, book_id, overwrite=False):
    b = prj.book(book_id)
    lay = prj.cfg["layout"]
    out = prj.root / f"{book_id}.tex"
    if out.exists() and not overwrite:
        print(f"{out.name} exists (use --overwrite to regenerate the front matter)")
        return out
    tl = b.get("title_lines") or _split_title(b["title"])
    sl = b.get("subtitle_lines") or _split_title(b.get("subtitle", ""), 34)
    style = lay.get("style", "classic")
    if b.get("subtitle"):
        if style == "modern":
            subtitle_block = ("\\vspace{0.8cm}\n{\\sffamily\\large\\itshape %s\\par}\n\\vspace{1.3cm}"
                              % "\\\\".join(tex_escape(x) for x in sl))
        else:
            subtitle_block = ("\\vspace{0.7cm}\n{\\Large\\itshape %s\\par}\n\\vspace{1.0cm}"
                              % "\\\\".join(tex_escape(x) for x in sl))
        subtitle_line = "%s\\\\[6pt]\n" % tex_escape(b["subtitle"])
    else:
        subtitle_block = "\\vspace{0.6cm}"    # no subtitle: a little breathing room, no empty italic line
        subtitle_line = ""
    longest = max(len(x) for x in tl)
    pt, lead = (34, 40) if longest <= 18 else ((30, 36) if longest <= 24 else (26, 31))
    year = int(b.get("year") or datetime.date.today().year)
    month_year = b.get("month_year") or datetime.date.today().strftime("%B %Y")
    pref = b.get("preface") or ["TODO: write the preface (2-3 short paragraphs): what the book is about, what each chapter does, and how the questions and answers are arranged."]
    inputs = [r"\InputIfFileExists{%s/%s}{}{}" % (book_id, c["file"]) for c in b["chapters"]]
    apps = b.get("appendices", [])
    if apps:
        inputs.append("\\appendix")
        inputs += [r"\InputIfFileExists{%s/%s}{}{}" % (book_id, a["file"]) for a in apps]
    chapters = "\n".join(inputs)
    brief = [r"\noindent Preface\dotfill\pageref{tb:preface}\par", r"\medskip"]
    brief += [r"\noindent\textbf{%s}\quad %s\dotfill\pageref{tbch:%s}\par" % (c["number"], tex_escape(c["title"]), c["number"])
              for c in b["chapters"]]
    if apps or b.get("index"):
        brief.append(r"\medskip")
    brief += [r"\noindent %s\dotfill\pageref{tba:%s}\par" % (tex_escape(a["title"]), a["file"]) for a in apps]
    if b.get("index"):
        brief.append(r"\noindent Index\dotfill\pageref{tb:index}\par")
    backmatter = ""
    if b.get("index"):
        ist = prj.root / f"{book_id}.ist"
        if not ist.exists():
            shutil.copy(style_asset(style, "index.ist"), ist)
            print(f"created {ist.name} (edit it freely; tb.py build/release pass it to makeindex automatically)")
        backmatter = ("\\backmatter\n\\cleardoublepage\n\\addcontentsline{toc}{chapter}{Index}\n"
                      "\\markboth{Index}{Index}\n\\label{tb:index}\n\\printindex\n")
    papername = {"a4paper": "A4", "letterpaper": "US Letter", "a5paper": "A5", "b5paper": "B5"}.get(lay["paper"], lay["paper"])
    sub = {
        "@@FONTPT@@": str(int(lay["font_pt"])), "@@PAPER@@": lay["paper"], "@@PAPERNAME@@": papername,
        "@@TYPEFACE@@": tex_escape(lay.get("typeface", "Times")),
        "@@TITLE@@": tex_escape(b["title"]),
        "@@PDFTITLE@@": tex_escape(b["title"] + (": " + b["subtitle"] if b.get("subtitle") else "")),
        "@@AUTHOR@@": tex_escape(b.get("author", "")), "@@INITIALS@@": _initials(b.get("author", "")),
        "@@AUTHOR_SP@@": (" " + tex_escape(b["author"])) if b.get("author") else "",
        "@@BRIEF_CONTENTS@@": "\n".join(brief),
        "@@TITLE_LINES@@": "\\\\".join(tex_escape(x) for x in tl), "@@TITLE_PT@@": str(pt), "@@TITLE_LEAD@@": str(lead),
        "@@SUBTITLE_BLOCK@@": subtitle_block, "@@SUBTITLE_LINE@@": subtitle_line,
        "@@YEAR@@": str(year), "@@MONTH_YEAR@@": tex_escape(month_year),
        "@@PREFACE@@": "\n\n".join(pref), "@@CHAPTER_INPUTS@@": chapters, "@@BACKMATTER@@": backmatter,
    }
    text = style_asset(style, "book.tex.tmpl").read_text(encoding="utf-8")
    for k, v in sub.items():
        text = text.replace(k, v)
    out.write_text(text, encoding="utf-8")
    print(f"wrote {out.name}")
    return out


def render_chapters(prj, book_id):
    b = prj.book(book_id)
    d = prj.root / book_id
    d.mkdir(parents=True, exist_ok=True)
    style = prj.cfg["layout"].get("style", "classic")
    tmpl = style_asset(style, "chapter.tex.tmpl").read_text(encoding="utf-8")
    app_tmpl = (ASSETS / "appendix.tex.tmpl").read_text(encoding="utf-8")
    made = []
    for i, a in enumerate(b.get("appendices", [])):
        f = d / f"{a['file']}.tex"
        if not f.exists():
            f.write_text(app_tmpl.replace("@@NUMBER@@", chr(65 + i)).replace("@@TITLE@@", tex_escape(a["title"]))
                         .replace("@@BUDGET@@", str(a.get("budget", "?"))).replace("@@FILE@@", a["file"]), encoding="utf-8")
            made.append(f.name)
    for c in b["chapters"]:
        f = d / f"{c['file']}.tex"
        if not f.exists():
            text = (tmpl.replace("@@NUMBER@@", str(c["number"])).replace("@@TITLE@@", tex_escape(c["title"]))
                    .replace("@@SHORT@@", tex_escape(c.get("short") or c["title"])).replace("@@BUDGET@@", str(c.get("budget", "?"))))
            if c.get("partner"):         # the owner pulls the partner's sections in just before the Summary
                for h in ("\\section{Chapter Summary}", "\\section{Summary}"):
                    if h in text:
                        text = text.replace(h, "\\InputIfFileExists{%s/%s}{}{}\n\n%s" % (book_id, c["partner"]["file"], h), 1)
                        break
            f.write_text(text, encoding="utf-8")
            made.append(f.name)
        p = c.get("partner")             # independent of the owner file: a partner may be added to an existing chapter
        if p and f.exists() and p["file"] not in f.read_text(encoding="utf-8", errors="ignore"):
            print(f"WARNING: {f.name} never inputs its partner file; add \\InputIfFileExists{{{book_id}/{p['file']}}}{{}}{{}} before the Summary section "
                  f"(otherwise the partner's sections are missing from the book and its labels are undefined)")
        if p:
            pf = d / f"{p['file']}.tex"
            if not pf.exists():
                n = c["number"]
                body = (f"% Part file of chapter {n} (budget {p.get('budget', '?')} pages): sections only, no tbchapter;\n"
                        f"% the owner file {c['file']}.tex inputs it.\n"
                        "\\section{TODO}\\label{sec:c" + str(n) + "-part}\nTODO\n")
                pf.write_text(body, encoding="utf-8")
                made.append(pf.name)
    print("chapter skeletons written:", made or "none (all files already exist)")
    return made
