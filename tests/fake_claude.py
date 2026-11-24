#!/usr/bin/env python3
"""Stands in for `claude -p` in tests: each agent does a fixed, minimal version of its job, with no model calls."""
import json
import os
import re
import statistics
import sys
from pathlib import Path

args = sys.argv[1:]
prompt = sys.stdin.read()
if "--agent" not in args:
    # A sealed judge or reader session: answer whatever the JSON schema asks for, minimally.
    schema = json.loads(args[args.index("--json-schema") + 1]) if "--json-schema" in args else None
    props = (schema or {}).get("properties", {})
    if "preferred" in props:
        out = {"preferred": "first", "confidence": 2, "reason": "clearer"}
    elif "match" in props:
        out = {"match": "yes", "why": "same claim"}
    elif "questions" in props:
        out = {"questions": [{"q": f"q{i}", "a": "a", "claim": "ours_acc"} for i in range(3)]}
    elif "answers" in props:
        out = {"answers": ["a", "a", "a"]}
    elif "correct" in props:
        out = {"correct": [True, True, True]}
    else:
        out = None
    print(json.dumps({"type": "result", "is_error": False, "num_turns": 1, "session_id": "judge",
                      "result": json.dumps(out) if out else "A one-sentence summary.", "structured_output": out,
                      "usage": {"input_tokens": 1, "output_tokens": 5}}))
    sys.exit(0)
agent = args[args.index("--agent") + 1].split(":", 1)[1]
root = Path.cwd()
work, paper = root / ".scriptorium", root / "paper"


def acc(method):
    rows = [json.loads(l) for l in (root / "results" / "runs.jsonl").read_text().splitlines() if l.strip()]
    return 100 * statistics.mean(r["acc"] for r in rows if r["method"] == method)


if agent == "scout":
    (work / "inventory.md").write_text("# Inventory\n" + "results/runs.jsonl holds one run per line. " * 30)
    if os.environ.get("FAKE_TAMPER"):
        (root / "results" / "runs.jsonl").write_text((root / "results" / "runs.jsonl").read_text() + "\n")
elif agent == "evidence":
    (paper / "sources.py").write_text('''import statistics

@source("acc_ours", means="accuracy (%) of ours, mean over runs")
def acc_ours():
    return 100 * statistics.mean(r["acc"] for r in load("results/runs.jsonl") if r["method"] == "ours")

@source("acc_base", means="accuracy (%) of the baseline, mean over runs")
def acc_base():
    return 100 * statistics.mean(r["acc"] for r in load("results/runs.jsonl") if r["method"] == "base")

@source("n_runs", means="number of runs per method")
def n_runs():
    return len([r for r in load("results/runs.jsonl") if r["method"] == "ours"])

from scriptorium_stats import paired_t_p

@source("p_ours_vs_base", means="p-value, paired t-test over seeds, ours vs baseline accuracy")
def p_ours_vs_base():
    rows = load("results/runs.jsonl")
    a = [r["acc"] for r in sorted(rows, key=lambda r: r["seed"]) if r["method"] == "ours"]
    b = [r["acc"] for r in sorted(rows, key=lambda r: r["seed"]) if r["method"] == "base"]
    return paired_t_p(a, b)
''')
    (work / "evidence_notes.md").write_text("Supported: ours beats base.\n")
elif agent == "cartographer":
    (work / "ledger.json").write_text(json.dumps({"claims": [
        {"id": "ours_beats_base", "text": "Ours beats the baseline.", "kind": "comparison", "scope": "all runs",
         "evidence": {"numbers": ["acc_ours", "acc_base"], "tests": ["p_ours_vs_base"]}, "strength": "strong"},
        {"id": "ours_acc", "text": "Ours reaches high accuracy.", "kind": "result", "scope": "all runs",
         "evidence": {"numbers": ["acc_ours"]}, "strength": "strong"}],
        "brief": [{"claim": "ours is better", "status": "supported", "ledger": ["ours_beats_base"]}]}))
elif agent == "architect":
    fr = re.search(r"under the ([a-z-]+) framing", prompt).group(1)
    (work / "pitches" / f"{fr}.json").write_text(json.dumps({
        "framing": fr, "title": f"Title {fr}", "insight": "Ours beats the baseline.", "abstract_sketch": "s",
        "figure1": "f", "contributions": ["We a", "We b"], "storyline": "st",
        "sections": [{"title": "Results", "claims": ["ours_beats_base"]}], "claims": ["ours_beats_base"]}))
elif agent == "tablesetter":
    tid = re.search(r"set table `([a-z0-9_]+)`", prompt).group(1)
    (work / "tables" / f"{tid}.json").write_text(json.dumps({
        "caption": "Accuracy.", "label": f"tab:{tid}", "columns": ["Method", "Accuracy"],
        "rows": [{"cells": [{"text": "Baseline"}, {"key": "acc_base"}]}, {"cells": [{"text": "Ours"}, {"key": "acc_ours"}]}],
        "best": {"1": "max"}}))
elif agent == "outliner":
    sec = lambda i, f, t, w, nums: {"id": i, "file": f, "title": t, "wave": w, "words": 200, "goal": "g",
                                    "points": ["p"], "numbers": nums, "figures": [], "tables": [], "cites": ["t"]}
    o = {"title": "A Test Paper", "storyline": "Problem, idea, why it works, what it changes, in enough words here.",
         "sections": [sec("abstract", "abstract", "Abstract", 2, []), sec("intro", "01_intro", "Introduction", 2, []),
                      sec("method", "02_method", "Method", 1, []),
                      sec("results", "03_results", "Results", 1, ["acc_ours", "acc_base"])],
         "figures": [{"id": "fig_acc", "kind": "plot", "section": "results", "message": "m", "data": [], "spec": "s",
                      "caption": "c"}],
         "related": [{"id": "t", "topic": "t", "why": "w", "queries": ["q"]}]}
    o["sections"][3]["figures"] = ["fig_acc"]
    o["sections"][3]["tables"] = ["main"]
    o["sections"][3]["claims"] = ["ours_beats_base", "ours_acc"]
    o["figures"][0]["claim"] = "ours_beats_base"
    o["tables"] = [{"id": "main", "section": "results", "claim": "ours_beats_base", "content": "c",
                    "numbers": ["acc_ours", "acc_base"]}]
    (work / "outline.json").write_text(json.dumps(o))
elif agent == "librarian":
    from scriptorium import cite
    prov = {}
    bib = []
    for i in range(6):
        e = f"@article{{ref{i}a,\n  title = {{Paper {i}}},\n  author = {{Doe, Jane}},\n  year = {{2020}}\n}}"
        bib.append(e)
        prov[f"ref{i}a"] = {"id": f"doi:10.0/{i}", "title": f"Paper {i}", "year": "2020", "hash": cite._norm(e)}
    (paper / "refs.bib").write_text("\n\n".join(bib) + "\n")
    (work / "citations.json").write_text(json.dumps(prov))
    (work / "related.md").write_text("ref0a ... ref5a\n")
elif agent == "illustrator":
    fid = re.search(r"make figure `([a-z0-9_]+)`", prompt).group(1)
    (paper / "figures" / f"{fid}.py").write_text(
        "from pathlib import Path\n"
        f"Path('paper/figures/{fid}.pdf').write_bytes(b'%PDF-1.4 fake')\n"
        f"Path('paper/figures/{fid}.png').write_bytes(b'png')\n")
    import subprocess
    subprocess.run([sys.executable, f"paper/figures/{fid}.py"])
    (work / "figures" / f"{fid}.md").write_text("caption\n")
elif agent == "writer":
    f = re.search(r"Task: write paper/([a-z0-9_]+?)(__v\d+)?\.tex", prompt).group(1)
    target = re.search(r"Task: write paper/([a-z0-9_]+)\.tex", prompt).group(1)
    words = " ".join(["Text"] * 50)
    if f == "abstract":
        body = f"We study a method. {words}\n"
    else:
        body = f"\\section{{{f}}}\\label{{sec:{f}}}\n{words} \\citep{{ref0a,ref1a,ref2a,ref3a,ref4a,ref5a}}.\n"
        if f == "03_results":
            body += (f"Ours reaches {acc('ours'):.1f}\\%\\src{{acc_ours}} against {acc('base'):.1f}\\%\\src{{acc_base}}"
                     ". See Figure~\\ref{fig:fig_acc} and Table~\\ref{tab:main}.\n\\input{table_main}\n"
                     "\\begin{figure}[t]\\includegraphics{figures/fig_acc.pdf}\\caption{c}\\label{fig:fig_acc}"
                     "\\end{figure}\n")
            if os.environ.get("FAKE_BAD_NUMBER"):
                body = body.replace(f"{acc('ours'):.1f}", "99.9")
    (paper / f"{target}.tex").write_text(body)
elif agent == "reviewer":
    out = re.search(r"\.scriptorium/reviews/(\S+\.json)", prompt).group(1)
    revised = "We revised this." in (paper / "03_results.tex").read_text()
    score = 6 + (1 if revised else 0) * (-2 if os.environ.get("FAKE_REVISE_WORSE") else 1)
    (work / "reviews" / out).write_text(json.dumps({"summary": "s", "strengths": [], "questions": [],
                                                    "weaknesses": [{"issue": "i", "where": "w", "severity": "major",
                                                                    "suggestion": "x"}], "overall": score}))
elif agent == "reviser":
    p = paper / "03_results.tex"
    p.write_text(p.read_text() + "We revised this.\n")
    n = re.search(r"response(\d+)\.md", prompt).group(1)
    (work / "reviews" / f"response{n}.md").write_text("- changed\n")

print(json.dumps({"type": "result", "is_error": False, "num_turns": 2, "result": f"{agent} done", "session_id": "t",
                  "usage": {"input_tokens": 10, "output_tokens": 5, "cache_read_input_tokens": 100,
                            "cache_creation_input_tokens": 0}}))
