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
Path("main.pdf").write_bytes(b"%PDF-1.4\n1 0 obj << /Type /Page >>\n2 0 obj << /Type /Page >>\n%%EOF\n")
