#!/usr/bin/env python3
"""Stands in for latexmk in tests: fails on a missing \\input or figure, else writes a two-page 'PDF'."""
import re
import sys
from pathlib import Path

tex = Path("main.tex").read_text()
missing = [f for f in re.findall(r"\\input\{([^}]+)\}", tex) if not Path(f + ".tex").exists()]
body = tex + "".join(Path(f + ".tex").read_text() for f in re.findall(r"\\input\{([^}]+)\}", tex) if Path(f + ".tex").exists())
missing += [g for g in re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", body) if not Path(g).exists()]
if missing:
    Path("main.log").write_text("".join(f"! LaTeX Error: File `{m}' not found.\n" for m in missing))
    sys.exit(1)
Path("main.log").write_text("Output written\n")
import os
import subprocess
try:                                   # a real two-page PDF when PyMuPDF is there, so pages can be rendered
    import pymupdf
    doc = pymupdf.open()
    for i in range(2):
        doc.new_page().insert_text((72, 72), f"Page {i + 1} of a test paper. Figure 1: a figure.")
    doc.save("main.pdf")
except ImportError:
    py = os.environ.get("FAKE_LATEX_PYTHON")
    if py and not os.environ.get("FAKE_LATEX_REEXEC"):
        sys.exit(subprocess.run([py, __file__], env={**os.environ, "FAKE_LATEX_REEXEC": "1"}).returncode)
    Path("main.pdf").write_bytes(b"%PDF-1.4\n1 0 obj << /Type /Page >>\n2 0 obj << /Type /Page >>\n%%EOF\n")
