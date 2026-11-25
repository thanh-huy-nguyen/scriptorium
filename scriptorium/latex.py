"""Build the paper: rerun every figure script from the data, then compile LaTeX and read the log."""
from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from .config import Config


@dataclass
class Build:
    ok: bool = False
    pdf: Path | None = None
    pages: int | None = None
    main_pages: int | None = None          # pages before the references heading, when it can be found
    errors: list[str] = field(default_factory=list)
    undefined: list[str] = field(default_factory=list)
    overfull: int = 0
    overfull_in: list[str] = field(default_factory=list)   # the source file of each overfull box, when the log says
    figure_errors: list[str] = field(default_factory=list)

    def problems(self, page_limit: int | None = None) -> list[str]:
        out = [f"figure script failed: {e}" for e in self.figure_errors]
        out += [f"LaTeX error: {e}" for e in self.errors]
        if not self.ok and not self.errors:
            out.append("LaTeX did not produce paper/main.pdf (see .scriptorium/logs/build.log)")
        out += [f"undefined reference or citation: {u}" for u in self.undefined]
        if page_limit and self.main_pages and self.main_pages > page_limit:
            out.append(f"main text runs {self.main_pages} pages; the limit is {page_limit}")
        return out

    def summary(self) -> str:
        if not self.ok:
            return "build failed"
        mp = f", main text {self.main_pages}" if self.main_pages else ""
        return f"{self.pages} pages{mp}, {len(self.undefined)} undefined refs, {self.overfull} overfull boxes"


_INPUT_RE = re.compile(r"\\(?:input|include|subfile)\s*\{([^}]+)\}")


def included(paper: Path, main: str = "main.tex") -> list[Path]:
    """The .tex files the paper actually typesets: main.tex and every file it inputs, recursively, in order.
    Scratch files an agent leaves in paper/ are not among them, so checks never read them."""
    out: list[Path] = []

    def walk(p: Path) -> None:
        if p in out or not p.exists():
            return
        out.append(p)
        text = re.sub(r"(?<!\\)%.*", "", p.read_text(errors="replace"))
        for m in _INPUT_RE.finditer(text):
            name = m.group(1).strip()
            walk(paper / (name if name.endswith(".tex") else name + ".tex"))
    walk(paper / main)
    return out


def run_figures(cfg: Config) -> list[str]:
    from .sealing import jail_env
    errors = []
    for script in sorted((cfg.paper / "figures").glob("*.py")):
        if script.name.startswith("_"):
            continue
        r = subprocess.run([cfg.py(), str(script)], cwd=cfg.root, capture_output=True, text=True, timeout=900,
                           env=jail_env(cfg))
        if r.returncode != 0:
            tail = (r.stderr or r.stdout).strip().splitlines()[-1:] or ["no output"]
            errors.append(f"{script.name}: {tail[0]}")
    return errors


def page_info(pdf: Path) -> tuple[int | None, int | None]:
    try:
        try:
            import pymupdf as fitz  # type: ignore
        except ImportError:
            import fitz  # type: ignore
        doc = fitz.open(str(pdf))
        n, main = len(doc), None
        for i, page in enumerate(doc):
            if re.search(r"^\s*(\d+\s+)?References\s*$", page.get_text(), re.M):
                main = i + 1
                break
        return n, main
    except Exception:
        pass
    if shutil.which("pdfinfo"):
        r = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True)
        m = re.search(r"Pages:\s+(\d+)", r.stdout)
        if m:
            n = int(m.group(1))
            main = None
            if shutil.which("pdftotext"):
                for i in range(1, n + 1):
                    t = subprocess.run(["pdftotext", "-f", str(i), "-l", str(i), str(pdf), "-"],
                                       capture_output=True, text=True).stdout
                    if re.search(r"^\s*(\d+\s+)?References\s*$", t, re.M):
                        main = i
                        break
            return n, main
    data = pdf.read_bytes()
    n = len(re.findall(rb"/Type\s*/Page[^s]", data))
    return (n or None), None


def parse_log(log: str) -> tuple[list[str], list[str], int]:
    errors = []
    lines = log.splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith("! "):
            ctx = next((x.strip() for x in lines[i + 1:i + 4] if x.startswith("l.")), "")
            errors.append((ln[2:].strip() + (f" ({ctx})" if ctx else ""))[:200])
    undefined = sorted(set(re.findall(r"(?:Citation|Reference) `([^']+)' (?:on page \d+ )?undefined", log)))
    overfull = len(re.findall(r"^Overfull \\hbox", log, re.M))
    return errors[:10], undefined, overfull


FILE_OPEN_RE = re.compile(r"\((?:\./)?([A-Za-z0-9_\-]+)(?:\.tex)?(?=[\s)]|$)")


def overfull_sources(log: str) -> list[str]:
    """For each overfull box, the last section or table file opened before it in the log."""
    out = []
    for m in re.finditer(r"^Overfull \\hbox", log, re.M):
        opened = [x for x in FILE_OPEN_RE.findall(log[:m.start()])
                  if x.startswith("table_") or re.match(r"\d\d_", x) or x == "abstract"]
        out.append(opened[-1] if opened else "?")
    return out


def build(cfg: Config, figures: bool = True, src: Path | None = None, main: str = "main.tex") -> Build:
    """Compile paper/main.tex (or `main` in another source folder, for audits of existing papers)."""
    b = Build()
    if figures and src is None:
        b.figure_errors = run_figures(cfg)
    src = src or cfg.paper
    engine = cfg.latex_engine()
    logdir = cfg.work / "logs"
    logdir.mkdir(parents=True, exist_ok=True)
    if not engine:
        b.errors = ["no LaTeX engine found: install tectonic (https://tectonic-typesetting.github.io) or latexmk, "
                    "or set run.latex in scriptorium.toml"]
        return b
    stem = Path(main).stem
    pdf = src / f"{stem}.pdf"
    if pdf.exists():
        pdf.unlink()
    if Path(engine).name.startswith("tectonic"):
        cmd = [engine, "-X", "compile", "--keep-logs", main]
    else:
        cmd = [engine, "-pdf", "-interaction=nonstopmode", "-file-line-error", main]
    try:
        r = subprocess.run(cmd, cwd=src, capture_output=True, text=True, timeout=600)
        out = r.stdout + "\n" + r.stderr
    except subprocess.TimeoutExpired:
        out = "! LaTeX build timed out after 600 s"
    (logdir / "build.log").write_text(out)
    log = (src / f"{stem}.log").read_text(errors="replace") if (src / f"{stem}.log").exists() else out
    b.errors, b.undefined, b.overfull = parse_log(log + ("\n" + out if "error:" in out else ""))
    b.overfull_in = overfull_sources(log)
    if not b.errors:
        b.errors = [ln.split("error:", 1)[1].strip()[:200] for ln in out.splitlines() if "error:" in ln][:5]
    b.ok = pdf.exists() and not b.errors
    if pdf.exists():
        b.pdf = pdf
        b.pages, b.main_pages = page_info(pdf)
    return b
