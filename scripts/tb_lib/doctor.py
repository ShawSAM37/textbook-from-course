"""Environment check.  Reports what is present and what is missing, with the exact fix.  Never installs LaTeX itself:
installing software is a system change, so the person (or the calling agent, after asking) does that."""
import importlib.util as iu
import os
import shutil
import subprocess
import sys
from pathlib import Path

from .build import find_pdflatex
from .config import ASSETS

OCR_HOME = Path.home() / ".textbook-from-course"
OCR_VENV = OCR_HOME / "ocr-venv"


def venv_python():
    exe = OCR_VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    return exe if exe.exists() else None


def ocr_importable(python=None):
    if python is None:
        return iu.find_spec("rapidocr_onnxruntime") is not None
    r = subprocess.run([str(python), "-c", "import rapidocr_onnxruntime"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return r.returncode == 0


def setup_ocr():
    OCR_HOME.mkdir(parents=True, exist_ok=True)
    print(f"prior state: {OCR_VENV} existed = {OCR_VENV.exists()}   (revert: delete that folder)")
    if not OCR_VENV.exists():
        subprocess.check_call([sys.executable, "-m", "venv", "--system-site-packages", str(OCR_VENV)])
    py = venv_python()
    subprocess.check_call([str(py), "-m", "pip", "install", "rapidocr-onnxruntime"])
    print("OCR environment ready:", ocr_importable(py))


def check(smoke=False):
    rows = []

    def add(name, ok, fix=""):
        rows.append((name, ok, fix))

    add("python >= 3.9", sys.version_info >= (3, 9), "install a current Python 3")
    for mod, pipname, need in (("fitz", "pymupdf", True), ("PIL", "pillow", True), ("numpy", "numpy", True),
                               ("pptx", "python-pptx", False), ("docx", "python-docx", False)):
        add(f"python module {mod}" + ("" if need else " (optional)"), iu.find_spec(mod) is not None, f"pip install {pipname}")
    if os.name == "nt":
        add("pywin32 / PowerPoint COM (best PPT/PPTX fidelity, optional)", iu.find_spec("win32com") is not None, "pip install pywin32")
    add("LibreOffice 'soffice' (fallback converter for Office files, optional)", shutil.which("soffice") is not None or
        any(Path(p).exists() for p in (r"C:\Program Files\LibreOffice\program\soffice.exe", "/Applications/LibreOffice.app/Contents/MacOS/soffice")),
        "install LibreOffice only if PowerPoint/Word are unavailable")
    pl = find_pdflatex()
    add("pdflatex", bool(pl), "Windows: winget install --id MiKTeX.MiKTeX --scope user   |  macOS: brew install --cask mactex-no-gui  |  Linux: apt install texlive-full")
    ocr_ok = ocr_importable() or (venv_python() is not None and ocr_importable(venv_python()))
    add("OCR engine rapidocr-onnxruntime (for image-only slides / scanned pages)", ocr_ok, "python tb.py doctor --setup-ocr")
    w = max(len(r[0]) for r in rows)
    for name, ok, fix in rows:
        print(f"{'OK     ' if ok else 'MISSING'} {name:<{w}}" + ("" if ok else f"   -> {fix}"))
    if pl:
        print(f"\npdflatex: {pl}")
    if smoke and pl:
        print("\nsmoke test: compiling the shipped style with a tiny document (first run may download LaTeX packages) ...")
        import tempfile
        tmp = Path(tempfile.mkdtemp(prefix="tb_smoke_"))
        shutil.copy(ASSETS / "textbook.sty", tmp / "textbook.sty")
        (tmp / "t.tex").write_text(
            "\\documentclass[11pt,a4paper,twoside,openright]{book}\\usepackage{textbook}\\booktitle{T}\\begin{document}\\mainmatter"
            "\\tbchapter{1}{Smoke}\\section{A}Text \\begin{defn}{D}{d}x\\end{defn}\\begin{exq}[10]{q}Q\\end{exq}\\begin{exsol}{q}S\\end{exsol}"
            "\\end{document}\n", encoding="utf-8")
        r = subprocess.run([pl, "-interaction=nonstopmode", "-halt-on-error", "t.tex"], cwd=str(tmp),
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="ignore")
        print("smoke test:", "PASSED" if r.returncode == 0 and (tmp / "t.pdf").exists() else "FAILED\n" + r.stdout[-1500:])
    missing_required = [r for r in rows if not r[1] and "optional" not in r[0]]
    return 0 if not missing_required else 1
