"""Shared helpers for the RepoWrite checker: read a paper's LaTeX the same way for every system, and make one sealed
model call that returns JSON.

The checker is independent of Scriptorium by rule: nothing here imports `scriptorium` or `paperanchor`
(tests/test_bench_independent.py enforces it), and Scriptorium's own number tags are stripped before anything reads
the text, so its papers are scored exactly like everyone else's.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

MODEL = os.environ.get("REPOWRITE_MODEL", "sonnet")
LIMIT_RE = re.compile(r"usage limit|limit reached|hit your limit|rate.?limit|too many requests|overloaded|\b429\b|\b529\b",
                      re.I)


# ---------------------------------------------------------------------------------------------------------------------
# The paper

def _strip_comments(s: str) -> str:
    return re.sub(r"(?<!\\)%.*", "", s)


def expand(tex: Path, seen: set | None = None) -> str:
    """The LaTeX of a paper with every \\input and \\include expanded, comments removed."""
    seen = seen or set()
    tex = tex.resolve()
    if tex in seen or not tex.exists():
        return ""
    seen.add(tex)
    s = _strip_comments(tex.read_text(errors="replace"))

    def sub(m):
        name = m.group(2)
        p = (tex.parent / name)
        if not p.suffix:
            p = p.with_suffix(".tex")
        return expand(p, seen)
    return re.sub(r"\\(input|include)\{([^}]*)\}", sub, s)


def strip_tags(s: str) -> str:
    """Remove Scriptorium's number tags (\\src{key}) and similar provenance macros, so every system reads the same."""
    s = re.sub(r"\\src\{[^{}]*\}", "", s)
    s = re.sub(r"\\providecommand\{\\src\}\[1\]\{\}", "", s)
    return s


def main_tex(paper: Path) -> Path:
    """The paper's main LaTeX file: main.tex, or the one .tex file with \\documentclass."""
    if (paper / "main.tex").exists():
        return paper / "main.tex"
    for p in sorted(paper.glob("*.tex")):
        if "\\documentclass" in p.read_text(errors="replace"):
            return p
    raise FileNotFoundError(f"no main LaTeX file in {paper}")


def body(paper: Path) -> str:
    """The paper's text from \\begin{document} to \\end{document}, tags stripped."""
    s = strip_tags(expand(main_tex(paper)))
    a, b = s.find("\\begin{document}"), s.rfind("\\end{document}")
    return s[a + len("\\begin{document}"): b if b > 0 else None] if a >= 0 else s


def chunks(text: str, limit: int = 9000) -> list[str]:
    """Split the body at section boundaries into pieces of at most about `limit` characters."""
    parts = re.split(r"(?=\\(?:section|subsection)\*?\{)", text)
    out, cur = [], ""
    for p in parts:
        if len(cur) + len(p) > limit and cur:
            out.append(cur)
            cur = ""
        while len(p) > limit:
            cut = p.rfind("\n\n", 0, limit)
            cut = cut if cut > limit // 3 else limit
            out.append(p[:cut])
            p = p[cut:]
        cur += p
    if cur.strip():
        out.append(cur)
    return out


def labels(paper: Path) -> dict[str, str]:
    """Printed numbers of tables and figures from the .aux file: {'tab:main': '2', ...}."""
    out = {}
    for aux in paper.glob("*.aux"):
        for m in re.finditer(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}", aux.read_text(errors="replace")):
            out[m.group(1)] = m.group(2)
    return out


def tables(paper: Path) -> dict[str, str]:
    """{'Table 2': its LaTeX} for every table environment, numbered from the .aux file when it exists, else in order."""
    s = body(paper)
    lab = labels(paper)
    out, k = {}, 0
    for m in re.finditer(r"\\begin\{table\*?\}(.*?)\\end\{table\*?\}", s, re.S):
        k += 1
        t = m.group(1)
        lm = re.search(r"\\label\{([^}]*)\}", t)
        n = lab.get(lm.group(1)) if lm else None
        out[f"Table {n or k}"] = t
        if lm:
            out[lm.group(1)] = t                    # also by its label, for sentences that cite \\ref{tab:...}
    return out


# ---------------------------------------------------------------------------------------------------------------------
# One sealed model call

def ask(prompt: str, schema: dict, model: str = MODEL, retries: int = 6) -> dict:
    """One `claude -p` call with no tools, run in an empty directory, returning the JSON that matches `schema`.
    Waits out usage limits. Uses the Claude login (ANTHROPIC_API_KEY is dropped), so it costs no money."""
    tmp = Path(tempfile.mkdtemp(prefix="repowrite-"))
    env = {k: v for k, v in os.environ.items() if not k.startswith("SCRIPTORIUM_") and k != "ANTHROPIC_API_KEY"}
    cmd = ["claude", "-p", "--model", model, "--output-format", "json", "--no-session-persistence",
           "--setting-sources", "", "--strict-mcp-config", "--tools", "", "--json-schema", json.dumps(schema),
           "--system-prompt", "You are a careful annotator. Follow the task exactly and answer only in the requested "
                              "format."]
    try:
        for attempt in range(retries):
            p = subprocess.run(cmd, input=prompt, cwd=tmp, env=env, text=True, capture_output=True, timeout=1800)
            out = None
            for line in reversed((p.stdout or "").strip().splitlines()):
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(d, dict) and ("result" in d or "is_error" in d):
                    out = d
                    break
            if out and not out.get("is_error"):
                so = out.get("structured_output")
                data = so if so is not None else json.loads(out.get("result") or "{}")
                return {"data": data, "tokens": (out.get("usage") or {}).get("output_tokens", 0)}
            text = " ".join(str(x) for x in ((out or {}).get("result"), p.stderr, p.stdout) if x)
            if LIMIT_RE.search(text):
                time.sleep(min(3600, 300 * (attempt + 1)))
                continue
            raise RuntimeError("model call failed: " + text[-400:])
        raise RuntimeError("model call failed after waiting for usage limits")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def num(s) -> float | None:
    """A printed number as a float ('1{,}257' -> 1257, '92.6\\%' -> 92.6, '$3.1\\times10^{-4}$' -> 3.1e-4)."""
    if isinstance(s, (int, float)):
        return float(s)
    t = str(s).replace("{,}", "").replace(",", "").replace("\\,", "").replace("$", "").replace("\\%", "").replace("%", "")
    t = t.replace("\\times", "x").replace("\\cdot", "x").replace("−", "-").replace("\\textminus", "-").strip()
    t = re.sub(r"\s*x$", "", t)                                  # "5.0\\times" (five times)
    m = re.fullmatch(r"([-+]?\d*\.?\d+)\s*(?:x\s*10\^\{?([-+]?\d+)\}?)?", t)
    if m:
        return float(m.group(1)) * (10 ** int(m.group(2)) if m.group(2) else 1)
    m = re.fullmatch(r"([-+]?\d*\.?\d+)[eE]([-+]?\d+)", t)
    return float(t) if m else None


WORDS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "eleven": 11, "twelve": 12, "a dozen": 12, "dozen": 12, "twenty": 20, "a hundred": 100,
         "half": 0.5, "a half": 0.5, "a third": 1 / 3, "one third": 1 / 3, "a quarter": 0.25, "one quarter": 0.25,
         "a fifth": 0.2, "one fifth": 0.2, "two thirds": 2 / 3, "three quarters": 0.75, "twice": 2, "double": 2}


def word_num(s) -> float | None:
    """A number written in words ('five', 'a fifth'), else None."""
    return WORDS.get(str(s).strip().lower())


def exponent(s) -> int:
    """The power of ten of a number printed in scientific notation ('1.5\\times10^{-4}' -> -4), else 0."""
    m = re.search(r"(?:10\^\{?|[eE])([-+]?\d+)", str(s).replace("−", "-"))
    return int(m.group(1)) if m and ("10^" in str(s) or re.search(r"\d[eE][-+]?\d", str(s))) else 0


def decimals(s) -> int:
    """Digits after the decimal point as printed ('92.60' -> 2, '1{,}257' -> 0)."""
    t = str(s).replace("{,}", "")
    t = re.split(r"\\times|\\cdot|[eE][-+]?\d", t)[0]        # the mantissa only
    m = re.search(r"\d\.(\d+)", t)
    return len(m.group(1)) if m else 0
