"""Compile a book (or one chapter in a stand-alone driver) with pdfLaTeX and summarise the log independently."""
import glob
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


def find_pdflatex():
    p = shutil.which("pdflatex")
    if p:
        return p
    local = os.environ.get("LOCALAPPDATA", "")
    cands = [
        os.path.join(local, "Programs", "MiKTeX", "miktex", "bin", "x64", "pdflatex.exe"),
        r"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe",
        r"C:\texlive\2025\bin\windows\pdflatex.exe", r"C:\texlive\2024\bin\windows\pdflatex.exe",
        "/Library/TeX/texbin/pdflatex", "/usr/local/texlive/*/bin/*/pdflatex", "/usr/bin/pdflatex",
    ]
    for c in cands:
        for hit in glob.glob(c):
            if os.path.exists(hit):
                return hit
    return None


def find_makeindex():
    p = shutil.which("makeindex")
    if p:
        return p
    local = os.environ.get("LOCALAPPDATA", "")
    cands = [
        os.path.join(local, "Programs", "MiKTeX", "miktex", "bin", "x64", "makeindex.exe"),
        r"C:\Program Files\MiKTeX\miktex\bin\x64\makeindex.exe",
        r"C:\texlive\2025\bin\windows\makeindex.exe", r"C:\texlive\2024\bin\windows\makeindex.exe",
        "/Library/TeX/texbin/makeindex", "/usr/bin/makeindex",
    ]
    for c in cands:
        for hit in glob.glob(c):
            if os.path.exists(hit):
                return hit
    return None


def run_makeindex_if_present(prj, main):
    """If <main>.idx exists and is non-empty (the book has \\index{...} calls and \\makeindex in its
    preamble -- see textbook.sty), (re)build <main>.ind with makeindex before the remaining pdflatex
    passes fold it back in via \\printindex.  A silent no-op for any book that never calls \\index{},
    so this is always safe to call.  Uses <project>/<main>.ist for the heading/subitem style if that
    file exists (created by  tb.py new-book  when book.json sets "index": true), else makeindex's
    own default style."""
    idx = prj.build / f"{main}.idx"
    if not idx.exists() or idx.stat().st_size == 0:
        return
    exe = find_makeindex()
    if not exe:
        print("NOTE: \\index{} entries found but makeindex is not installed or not on PATH; "
              "the printed index will be empty until it is. MiKTeX/TeX Live normally ship it "
              "alongside pdflatex.")
        return
    style = prj.root / f"{main}.ist"
    cmd = [exe]
    if style.exists():
        cmd += ["-s", str(style)]
    cmd += ["-o", str(prj.build / f"{main}.ind"), str(idx)]
    subprocess.run(cmd, cwd=str(prj.root), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def run_pdflatex(prj, main, passes=3):
    exe = find_pdflatex()
    if not exe:
        raise SystemExit("pdflatex not found.  Run  tb.py doctor  for install advice (MiKTeX on Windows, TeX Live elsewhere).")
    prj.build.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["PATH"] = os.path.dirname(exe) + os.pathsep + env.get("PATH", "")
    rc = 0
    for i in range(1, passes + 1):
        rc = subprocess.run([exe, "-interaction=nonstopmode", "-halt-on-error", "-file-line-error",
                             f"-output-directory={prj.build}", f"{main}.tex"],
                            cwd=str(prj.root), env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
        if rc != 0:
            print(f"PASS {i} FAILED (exit {rc}) - see build/{main}.log")
            break
    return rc


def log_summary(prj, main):
    log = prj.build / f"{main}.log"
    if not log.exists():
        print("no log file")
        return {"errors": 1}
    t = log.read_text(encoding="utf-8", errors="ignore")
    s = {
        "errors": len(re.findall(r"(?m)^!|:\d+: ", t)),
        "undefined references": len(re.findall(r"Reference `[^']+' on page \d+ undefined", t)),
        "undefined citations": len(re.findall(r"Citation `[^']+' .* undefined", t)),
        "multiply defined labels": len(re.findall(r"multiply defined", t)),
        "Overfull \\hbox": len(re.findall(r"Overfull \\hbox", t)),
        "Overfull \\vbox": len(re.findall(r"Overfull \\vbox", t)),
        "Missing character": len(re.findall(r"Missing character", t)),
        "rerun needed": len(re.findall(r"Rerun to get", t)),
    }
    m = re.search(r"Output written on [^(]+\((\d+) pages?", t)
    s["pages"] = int(m.group(1)) if m else 0
    print(f"--- log summary for {main} ---")
    for k, v in s.items():
        print(f"{k:28s}: {v}")
    return s


def build_book(prj, book_id_or_main, passes=3):
    main = f"{book_id_or_main}"
    if not (prj.root / f"{main}.tex").exists() and (prj.root / f"{main}-book.tex").exists():
        main = f"{main}-book"
    if not (prj.root / f"{main}.tex").exists():
        raise SystemExit(f"{main}.tex not found in {prj.root}; create it with  tb.py new-book <id>")
    rc = run_pdflatex(prj, main, passes=1)
    if rc == 0:
        run_makeindex_if_present(prj, main)   # no-op unless this book has \index{} entries
        if passes > 1:
            run_pdflatex(prj, main, passes=passes - 1)
    s = log_summary(prj, main)
    return main, s


def check_chapter(prj, book_id, file, budget=0):
    """Stand-alone driver for one chapter (or a part-file), compile, audit."""
    from . import audit as A
    ch, partner = prj.chapter_of(book_id, file)
    lay = prj.cfg["layout"]
    path = prj.root / book_id / f"{file}.tex"
    if not path.exists():
        raise SystemExit(f"{path} does not exist; run  tb.py new-book {book_id}  to create the chapter and part-file skeletons")
    src = path.read_text(encoding="utf-8", errors="ignore")
    head = ""
    if ch.get("appendix"):
        head = "\\appendix"
    elif r"\tbchapter" not in src:
        head = "\\tbchapter{%d}{Draft of part %s}" % (int(ch["number"]), file.replace("_", r"\_"))
    driver = "\n".join([
        r"\documentclass[%dpt,%s,twoside,openright]{book}" % (int(lay["font_pt"]), lay["paper"]),
        r"\usepackage{textbook}", r"\booktitle{Draft}", r"\begin{document}", r"\mainmatter", head,
        r"\input{%s/%s}" % (book_id, file), r"\end{document}", ""])
    main = f"_chk_{book_id}_{file}"
    (prj.root / f"{main}.tex").write_text(driver, encoding="ascii")
    run_pdflatex(prj, main)
    s = log_summary(prj, main)
    pdf = prj.build / f"{main}.pdf"
    problems = A.audit(prj, pdf, budget or None) if pdf.exists() else ["no PDF produced"]
    return s, problems
