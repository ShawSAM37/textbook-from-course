#!/usr/bin/env python3
"""tb.py -- command line for the textbook-from-course skill.

  tb.py doctor [--smoke] [--setup-ocr]     check the environment (LaTeX, OCR, Office engines)
  tb.py init <folder> [--material <dir>] [--style classic|modern]   create a NEW project (book.json, style file, folders)
  tb.py scan                               list the uploaded material and register it in book.json
  tb.py ingest [slug ...] [--engine E] [--force]   text + page renders + candidate figures for every source
  tb.py figures                            normalise the figures into figures/pool (uniform look) + contact sheets
  tb.py ocr [slug ...] [--force]           OCR the image-only pages;   tb.py sheets   2x2 contact sheets of the renders
  tb.py gaps <topics.json>                 syllabus coverage per topic;   tb.py find <regex>   search all extracted text
  tb.py new-book <id> [--overwrite]        front matter + chapter skeletons from book.json
  tb.py build <id>                         compile the whole book (3 passes) and summarise the log
  tb.py check <id> <chapter-file> [--budget N]   compile one chapter stand-alone and audit the PDF
  tb.py audit <pdf> [--budget N]           print audit of any PDF
  tb.py scrub <files.tex ...> | --pdf <pdf ...>    identity scan;   tb.py scrub-images <pdf ...>   OCR scan inside images
  tb.py voice <files.tex ...>              advisory lint for machine-written / slide-derived tells (never blocks)
  tb.py release <id>                       build + audit + scrub (+ image scan) and copy the PDF to Final/
Run from inside the project folder, or pass  --project <folder>  before the command.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tb_lib import config  # noqa: E402


def _reexec_in_ocr_venv():
    """OCR needs rapidocr; if it is only installed in the skill's private venv, run this command there."""
    from tb_lib import doctor
    import importlib.util as iu
    if iu.find_spec("rapidocr_onnxruntime") is None:
        py = doctor.venv_python()
        if py and os.environ.get("TB_IN_VENV") != "1":
            env = dict(os.environ, TB_IN_VENV="1")
            sys.exit(subprocess.call([str(py), *sys.argv], env=env))
        sys.exit("rapidocr-onnxruntime is not installed.  Run:  python tb.py doctor --setup-ocr")


def main():
    ap = argparse.ArgumentParser(prog="tb.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", help="project folder (default: search upwards from the current folder for book.json)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("doctor"); p.add_argument("--smoke", action="store_true"); p.add_argument("--setup-ocr", action="store_true")
    p = sub.add_parser("init"); p.add_argument("folder"); p.add_argument("--material", default=""); p.add_argument("--style", default="classic", choices=["classic", "modern"])
    p = sub.add_parser("voice"); p.add_argument("files", nargs="+")
    sub.add_parser("scan")
    p = sub.add_parser("ingest"); p.add_argument("slugs", nargs="*"); p.add_argument("--engine", default="auto", choices=["auto", "com", "soffice", "pptx"]); p.add_argument("--force", action="store_true")
    sub.add_parser("figures")
    p = sub.add_parser("ocr"); p.add_argument("slugs", nargs="*"); p.add_argument("--force", action="store_true")
    sub.add_parser("sheets")
    p = sub.add_parser("gaps"); p.add_argument("topics")
    p = sub.add_parser("find"); p.add_argument("regex"); p.add_argument("--limit", type=int, default=40)
    p = sub.add_parser("new-book"); p.add_argument("id"); p.add_argument("--overwrite", action="store_true")
    p = sub.add_parser("build"); p.add_argument("id"); p.add_argument("--passes", type=int, default=3)
    p = sub.add_parser("check"); p.add_argument("id"); p.add_argument("file"); p.add_argument("--budget", type=int, default=0)
    p = sub.add_parser("audit"); p.add_argument("pdf"); p.add_argument("--budget", type=int, default=0)
    p = sub.add_parser("scrub"); p.add_argument("files", nargs="+"); p.add_argument("--pdf", action="store_true")
    p = sub.add_parser("scrub-images"); p.add_argument("files", nargs="+")
    p = sub.add_parser("release"); p.add_argument("id"); p.add_argument("--no-images", action="store_true")
    a = ap.parse_args()

    if a.cmd == "doctor":
        from tb_lib import doctor
        if a.setup_ocr:
            doctor.setup_ocr()
        sys.exit(doctor.check(smoke=a.smoke))
    if a.cmd == "init":
        from tb_lib import scaffold
        scaffold.init_project(a.folder, a.material, a.style)
        return
    if a.cmd == "voice":
        from tb_lib import voice
        voice.lint(a.files)
        return
    if a.cmd in ("ocr", "scrub-images", "release"):
        if a.cmd != "release" or not a.no_images:
            _reexec_in_ocr_venv()
    prj = config.load(a.project)
    os.chdir(prj.root)

    if a.cmd == "scan":
        from tb_lib import ingest
        rows = ingest.scan(prj)
        print(f"{len(rows)} new file(s) registered in book.json:")
        for slug, rel, role in rows:
            print(f"  {slug:12s} {role:10s} {rel}")
        print("edit book.json to correct roles (syllabus / material / reference) and slugs before ingesting.")
    elif a.cmd == "ingest":
        from tb_lib import ingest
        ingest.run(prj, a.slugs, a.engine, a.force)
    elif a.cmd == "figures":
        from tb_lib import figures
        figures.run(prj)
    elif a.cmd == "ocr":
        from tb_lib import ocr
        ocr.run(prj, a.slugs, a.force)
    elif a.cmd == "sheets":
        from tb_lib import ocr
        ocr.make_sheets(prj)
    elif a.cmd == "gaps":
        from tb_lib import gaps
        gaps.coverage(prj, a.topics)
    elif a.cmd == "find":
        from tb_lib import gaps
        gaps.find(prj, a.regex, a.limit)
    elif a.cmd == "new-book":
        from tb_lib import scaffold
        scaffold.render_book(prj, a.id, a.overwrite)
        scaffold.render_chapters(prj, a.id)
    elif a.cmd == "build":
        from tb_lib import build
        main_name, s = build.build_book(prj, a.id, a.passes)
        sys.exit(1 if s.get("errors") else 0)
    elif a.cmd == "check":
        from tb_lib import build
        s, problems = build.check_chapter(prj, a.id, a.file, a.budget)
        sys.exit(1 if (s.get("errors") or problems) else 0)
    elif a.cmd == "audit":
        from tb_lib import audit
        problems = audit.audit(prj, a.pdf, a.budget or None)
        sys.exit(1 if problems else 0)
    elif a.cmd == "scrub":
        from tb_lib import scrub
        n = scrub.scan_pdf(prj, a.files) if a.pdf else scrub.scan_tex(prj, a.files)
        sys.exit(1 if n else 0)
    elif a.cmd == "scrub-images":
        from tb_lib import scrub
        sys.exit(1 if scrub.scan_images(prj, a.files) else 0)
    elif a.cmd == "release":
        from tb_lib import audit, build, scrub
        import shutil
        b = prj.book(a.id)
        main_name, s = build.build_book(prj, a.id)
        pdf = prj.build / f"{main_name}.pdf"
        bad = 0
        print("\n=== print audit ===")
        bad += len(audit.audit(prj, pdf, b.get("page_cap")))
        print("\n=== identity scan: sources ===")
        bad += scrub.scan_tex(prj, [str(prj.root / f"{a.id}.tex")] + [str(x) for x in (prj.root / a.id).glob("*.tex")])
        print("\n=== identity scan: PDF text + metadata ===")
        bad += scrub.scan_pdf(prj, [str(pdf)])
        if not a.no_images:
            print("\n=== identity scan: text inside images ===")
            bad += scrub.scan_images(prj, [str(pdf)])
        bad += 1 if s.get("errors") or s.get("undefined references") or s.get("multiply defined labels") else 0
        print("\n=== voice lint (advisory, does not block) ===")
        from tb_lib import voice
        voice.lint([str(x) for x in sorted((prj.root / a.id).glob("*.tex"))])
        if bad:
            print(f"\nRELEASE BLOCKED: {bad} issue(s) above. Fix them and run release again; nothing was copied to Final/.")
            sys.exit(1)
        final = prj.root / "Final"
        final.mkdir(exist_ok=True)
        name = (f"{b['title']} - {b['author']}.pdf" if b.get("author") else f"{b['title']}.pdf").replace(":", "")
        target = final / name
        try:
            shutil.copy(pdf, target)
        except PermissionError:
            target = final / name.replace(".pdf", " (new).pdf")
            shutil.copy(pdf, target)
            print(f"\nFinal/{name} is locked (open in a viewer or just sent): wrote {target.name} instead -- "
                  f"close the old file, delete or rename it, and tell the user which one is current.")
        print(f"\nRELEASE CLEAN: copied to {target}")


if __name__ == "__main__":
    main()
