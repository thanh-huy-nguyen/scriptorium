"""Run a single-agent baseline on one RepoWrite task: one Claude Code session writes the whole paper, optionally
followed by self-review rounds. Usage is recorded so budgets can be matched.

    python bench/baselines/run_single.py --task TASK_DIR --out OUT_DIR [--model sonnet] [--seed 1]
                                         [--selfreview 0] [--timeout-min 120]

The session runs in a fresh copy of the task repository under /tmp, so nothing it can see points at the answer key;
the finished repository (with paper/) is copied to OUT_DIR/repo. The session uses the Claude login, not an API key.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from scriptorium import venues  # noqa: E402  (templates only; the checker never imports scriptorium)

LATEX = os.environ.get("REPOWRITE_LATEX") or shutil.which("tectonic") or "/home/blam5/.miniconda3/envs/cv-hw1/bin/tectonic"
LIMIT_RE = re.compile(r"usage limit|limit reached|hit your limit|rate.?limit|too many requests|overloaded|\b429\b|\b529\b",
                      re.I)
TOOLS = ["Read", "Write", "Edit", "MultiEdit", "Glob", "Grep", "Bash", "WebSearch", "WebFetch", "TodoWrite"]


def setup_paper(repo: Path, venue: str) -> None:
    paper = repo / "paper"
    paper.mkdir(exist_ok=True)
    tpl = (ROOT / "scriptorium" / "templates" / venue / "main.tex").read_text()
    for k, v in {"MODE": "review", "TITLE": "Title", "AUTHORS": "Anonymous", "AFFILIATION": "",
                 "ABSTRACT": "% the abstract", "BODY": "% the paper"}.items():
        tpl = tpl.replace(f"%%{k}%%", v)
    (paper / "main.tex").write_text(tpl)
    (paper / "refs.bib").write_text("")
    (paper / "figures").mkdir(exist_ok=True)
    venues.fetch(venue, paper)


def session(prompt: str, cwd: Path, model: str, timeout_min: int, resume: str | None = None) -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith(("SCRIPTORIUM_", "REPOWRITE_"))
           and k != "ANTHROPIC_API_KEY"}
    settings = json.dumps({"permissions": {"blockReadsOutsideWorkingDirectories": True}})
    cmd = ["claude", "-p", "--model", model, "--output-format", "json", "--permission-mode", "acceptEdits",
           "--setting-sources", "", "--strict-mcp-config", "--settings", settings, "--allowedTools", *TOOLS]
    tokens = {"input_tokens": 0, "output_tokens": 0, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}
    turns, sid, t0 = 0, resume, time.time()
    for attempt in range(8):
        c = cmd + (["--resume", sid] if sid else [])
        p_in = prompt if not (sid and attempt) else "You were interrupted by a usage limit. Continue where you stopped."
        try:
            p = subprocess.run(c, input=p_in, cwd=cwd, env=env, text=True, capture_output=True, timeout=timeout_min * 60)
            raw, err = p.stdout, p.stderr
        except subprocess.TimeoutExpired as e:
            raw, err = (e.stdout.decode() if isinstance(e.stdout, bytes) else e.stdout or ""), "timeout"
        out = None
        for line in reversed((raw or "").strip().splitlines()):
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(d, dict) and ("result" in d or "is_error" in d):
                out = d
                break
        if out:
            for k in tokens:
                tokens[k] += int((out.get("usage") or {}).get(k, 0) or 0)
            turns += out.get("num_turns") or 0
            sid = out.get("session_id") or sid
        text = " ".join(str(x) for x in ((out or {}).get("result"), err, raw) if x)
        if out and not out.get("is_error"):
            return {"ok": True, "tokens": tokens, "turns": turns, "session_id": sid,
                    "seconds": round(time.time() - t0), "result": (out.get("result") or "")[-500:]}
        if LIMIT_RE.search(text):
            time.sleep(min(3600, 600 * (attempt + 1)))
            continue
        return {"ok": False, "tokens": tokens, "turns": turns, "session_id": sid, "seconds": round(time.time() - t0),
                "error": text[-800:]}
    return {"ok": False, "tokens": tokens, "turns": turns, "seconds": round(time.time() - t0), "error": "limit retries"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--seed", type=int, default=1, help="repetition number (recorded; the model has no seed)")
    ap.add_argument("--selfreview", type=int, default=0, help="critique-and-revise rounds after the first draft")
    ap.add_argument("--timeout-min", type=int, default=120)
    a = ap.parse_args(argv)
    meta = tomllib.loads((a.task / "meta.toml").read_text())
    work = Path(tempfile.mkdtemp(prefix="rw-single-"))
    repo = work / "repo"
    shutil.copytree(a.task / "repo", repo, ignore=shutil.ignore_patterns("scriptorium.toml", ".scriptorium"))
    setup_paper(repo, meta["venue"])
    fill = {"venue_text": meta.get("venue_text", meta["venue"]), "page_limit": meta.get("page_limit", 8), "latex": LATEX}
    rounds = [("draft", (HERE / "prompts" / "single.md").read_text().format(**fill))]
    rounds += [(f"review{i + 1}", (HERE / "prompts" / "single_selfreview.md").read_text().format(**fill))
               for i in range(a.selfreview)]
    log = {"task": meta.get("id"), "system": "single" + ("+selfreview" if a.selfreview else ""), "model": a.model,
           "seed": a.seed, "sessions": []}
    for name, prompt in rounds:
        r = session(prompt, repo, a.model, a.timeout_min)
        log["sessions"].append({"name": name, **r})
        print(f"{name}: ok={r['ok']} turns={r['turns']} output_tokens={r['tokens']['output_tokens']} "
              f"{r['seconds'] // 60} min", flush=True)
        if not r["ok"]:
            break
    pdf = repo / "paper" / "main.pdf"
    if not pdf.exists():
        subprocess.run([LATEX, "-X", "compile", "main.tex"], cwd=repo / "paper", capture_output=True)
    log["pdf"] = pdf.exists()
    log["output_tokens"] = sum(s["tokens"]["output_tokens"] for s in log["sessions"])
    a.out.mkdir(parents=True, exist_ok=True)
    if (a.out / "repo").exists():
        shutil.rmtree(a.out / "repo")
    shutil.copytree(repo, a.out / "repo")
    (a.out / "run.json").write_text(json.dumps(log, indent=1))
    shutil.rmtree(work, ignore_errors=True)
    print(f"pdf={log['pdf']} output_tokens={log['output_tokens']} -> {a.out}")
    return 0 if log["pdf"] else 1


if __name__ == "__main__":
    sys.exit(main())
