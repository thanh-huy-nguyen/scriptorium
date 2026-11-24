"""Build the gate corpus: recent arXiv papers whose LaTeX source compiles, cut to the main text.

    python bench/gate/corpus.py DATA_DIR ID [ID ...]

For each arXiv id: download the source, find the main .tex, drop everything from \\appendix on (the judges read the
main paper, as they will in a run), compile with tectonic, and keep papers of 6 to 16 pages. Writes
DATA_DIR/papers/<id>/{src/, base.pdf, meta.json}.
"""
from __future__ import annotations

import gzip
import io
import json
import re
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.request
from pathlib import Path

TECTONIC = shutil.which("tectonic") or "/home/blam5/.miniconda3/envs/cv-hw1/bin/tectonic"
UA = {"User-Agent": "scriptorium-bench/0.1 (research use)"}


def fetch(url: str, tries: int = 5) -> bytes:
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            if i == tries - 1:
                raise
            time.sleep(20 * (i + 1))
    raise RuntimeError("unreachable")


def unpack(blob: bytes, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    try:
        with tarfile.open(fileobj=io.BytesIO(blob)) as t:
            for m in t.getmembers():
                p = (dst / m.name).resolve()
                if dst.resolve() in p.parents and (m.isfile() or m.isdir()):
                    t.extract(m, dst, filter="data")
        return
    except tarfile.TarError:
        pass
    try:
        (dst / "main.tex").write_bytes(gzip.decompress(blob))
    except OSError:
        (dst / "main.tex").write_bytes(blob)


def main_tex(src: Path) -> Path | None:
    best = None
    for f in src.rglob("*.tex"):
        t = f.read_text(errors="ignore")
        if "\\documentclass" in t and "\\begin{document}" in t:
            if best is None or len(t) > len(best.read_text(errors="ignore")):
                best = f
    return best


def cut_appendix(tex: Path) -> None:
    t = tex.read_text(errors="ignore")
    m = re.search(r"^\s*\\appendix\b", t, re.M)
    if m:
        t = t[:m.start()] + "\n\\end{document}\n"
    tex.write_text(t)


def compile_pdf(tex: Path, timeout: int = 600) -> Path | None:
    r = subprocess.run([TECTONIC, "--keep-logs", "-Z", "continue-on-errors", tex.name], cwd=tex.parent,
                       capture_output=True, text=True, timeout=timeout)
    pdf = tex.with_suffix(".pdf")
    return pdf if pdf.exists() and r.returncode == 0 else None


def pages(pdf: Path) -> int:
    import pymupdf
    return len(pymupdf.open(str(pdf)))


def build(data: Path, aid: str) -> dict:
    out = data / "papers" / aid.replace("/", "_")
    if (out / "meta.json").exists():
        return json.loads((out / "meta.json").read_text())
    shutil.rmtree(out, ignore_errors=True)
    src = out / "src"
    unpack(fetch(f"https://arxiv.org/e-print/{aid}"), src)
    tex = main_tex(src)
    meta = {"id": aid, "ok": False}
    if not tex:
        meta["why"] = "no main tex"
    else:
        cut_appendix(tex)
        try:
            pdf = compile_pdf(tex)
        except subprocess.TimeoutExpired:
            pdf = None
        if not pdf:
            meta["why"] = "does not compile"
        else:
            n = pages(pdf)
            meta.update({"main": str(tex.relative_to(src)), "pages": n, "ok": 6 <= n <= 16})
            if meta["ok"]:
                shutil.copy2(pdf, out / "base.pdf")
            else:
                meta["why"] = f"{n} pages"
    out.mkdir(parents=True, exist_ok=True)
    (out / "meta.json").write_text(json.dumps(meta, indent=1))
    return meta


if __name__ == "__main__":
    data = Path(sys.argv[1])
    for aid in sys.argv[2:]:
        try:
            m = build(data, aid)
        except Exception as e:  # noqa: BLE001
            m = {"id": aid, "ok": False, "why": f"error: {e}"}
        print(json.dumps(m), flush=True)
        time.sleep(4)
