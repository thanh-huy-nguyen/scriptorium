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
                      "caption": "c"},
                     {"id": "teaser", "kind": "diagram", "teaser": True, "role": "framework", "section": "intro",
                      "message": "m",
                      "spec": "s", "caption": "c", "claim": "ours_beats_base"}],
         "related": [{"id": "t", "topic": "t", "why": "w", "queries": ["q"]}]}
    o["sections"][3]["figures"] = ["fig_acc"]
    o["sections"][1]["figures"] = ["teaser"]
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
elif agent == "figure_planner":
    (work / "figures" / "plan.json").write_text(json.dumps({"figures": [
        {"id": "fig_acc", "kind": "plot", "width": "column", "chart": "grouped bars", "message": "ours wins",
         "layout": "bars", "data_keys": ["acc_ours", "acc_base"], "caption_draft": "Accuracy."},
        {"id": "teaser", "kind": "diagram", "teaser": True, "role": "framework", "width": "full", "chart": "teaser",
         "message": "idea",
         "layout": "two panels", "data_keys": [], "caption_draft": "Overview."}]}))
elif agent in ("plotter", "diagrammer"):
    fid = re.search(r"make figure `([a-z0-9_]+)`", prompt).group(1)
    if agent == "plotter":
        code = ("import scriptorium_fig as sf\nsf.use()\nfig, ax = sf.figure('column')\n"
                "sf.grouped_bars(ax, ['all'], {'Baseline': ([sf.recipe('acc_base')], [1.0]), "
                "'Ours': ([sf.recipe('acc_ours')], [1.0])}, ours='Ours')\n"
                "ax.set_ylabel('Accuracy (%)')\nsf.legend_above(ax)\n"
                f"sf.save(fig, '{fid}')\n")
    else:
        code = ("import scriptorium_diagram as sd\nd = sd.canvas('full', height=1.6)\n"
                "d.panel(0.1, 0.1, 3.0, 1.4, 'Noisy data', step=1)\nd.icon('images', 1.6, 0.7, 0.6)\n"
                "d.panel(3.5, 0.1, 3.0, 1.4, 'Clean model', step=2, k=1)\nd.box(4.4, 0.45, 1.2, 0.5, 'Ours', ours=True)\n"
                f"d.arrow((3.15, 0.7), (3.45, 0.7))\nd.save('{fid}')\n")
    (paper / "figures" / f"{fid}.py").write_text(code)
    import subprocess
    env = dict(os.environ, PYTHONPATH=os.pathsep.join([str(Path(__file__).resolve().parents[1] / "scriptorium" / "recipelib"),
                                                       os.environ.get("PYTHONPATH", "")]), SCRIPTORIUM_ROOT=str(root))
    subprocess.run([sys.executable, f"paper/figures/{fid}.py"], env=env, check=True)
    (work / "figures" / f"{fid}.md").write_text("caption\n")
elif agent == "figure_critic":
    fid = re.search(r"critique figure `([a-z0-9_]+)`", prompt).group(1)
    first = not list((work / "figures").glob(f"{fid}.critique.r*.json"))
    strict = fid == "teaser" and first and not os.environ.get("FAKE_EASY_CRITIC")
    (work / "figures" / f"{fid}.critique.json").write_text(json.dumps(
        {"verdict": "revise", "issues": [{"issue": "arrow too short", "fix": "lengthen it"}]} if strict
        else {"verdict": "pass", "issues": []}))
elif agent == "writer":
    f = re.search(r"Task: write paper/([a-z0-9_]+?)(__v\d+)?\.tex", prompt).group(1)
    target = re.search(r"Task: write paper/([a-z0-9_]+)\.tex", prompt).group(1)
    words = " ".join(["Text"] * 50)
    if f == "abstract":
        body = f"We study a method. {words}\n"
    else:
        body = f"\\section{{{f}}}\\label{{sec:{f}}}\n{words} \\citep{{ref0a,ref1a,ref2a,ref3a,ref4a,ref5a}}.\n"
        if f == "01_intro":
            body += ("Our key idea is that \\emph{filtering helps}. Figure~\\ref{fig:teaser} gives the idea.\n"
                     "\\begin{itemize}\n\\item \\textbf{A filter.} We propose it.\n"
                     "\\item \\textbf{A study.} We show it.\n\\end{itemize}\n\\begin{figure*}[t]\\includegraphics{figures/teaser.pdf}"
                     "\\caption{c}\\label{fig:teaser}\\end{figure*}\n")
        if f == "03_results":
            body += (f"Ours reaches {acc('ours'):.1f}\\%\\src{{acc_ours}} against {acc('base'):.1f}\\%\\src{{acc_base}}"
                     ". See Figure~\\ref{fig:fig_acc} and Table~\\ref{tab:main}.\n\\input{table_main}\n"
                     "\\begin{figure}[t]\\includegraphics{figures/fig_acc.pdf}\\caption{c}\\label{fig:fig_acc}"
                     "\\end{figure}\n")
            if os.environ.get("FAKE_BAD_NUMBER"):
                body = body.replace(f"{acc('ours'):.1f}", "99.9")
    (paper / f"{target}.tex").write_text(body)
elif agent == "experimentalist":
    facts = [{"id": f"f{i}", "topic": t, "text": f"Fact {i}.", "source": "train.py", "quote": "print('train')"}
             for i, t in enumerate(["data", "splits", "models", "training", "evaluation"])]
    (work / "setup.json").write_text(json.dumps({"facts": facts, "gaps": ["hardware"]}))
elif agent == "statistician":
    (work / "stats.json").write_text(json.dumps({"comparisons": [
        {"id": "ours_vs_base", "a": "ours", "b": "base", "setting": "all runs", "test_key": "p_ours_vs_base",
         "verdict": "not significant" if os.environ.get("FAKE_BAD_VERDICT") else "significant"}]}))
elif agent == "terminologist":
    (work / "notation.json").write_text(json.dumps({"terms": [
        {"canonical": "Ours", "kind": "method", "definition": "our method", "variants": ["OursNet"]},
        {"canonical": "Baseline", "kind": "baseline", "definition": "the baseline", "variants": []},
        {"canonical": "accuracy", "kind": "metric", "definition": "share correct", "variants": []}],
        "abbreviations": [{"short": "XYZ", "long": "ex why zed"}], "symbols": []}))
elif agent == "auditor" and "existing paper" in prompt:
    (work / "audit.json").write_text(json.dumps({"findings": [
        {"file": "01_paper.tex", "quote": "Our method is the best on every dataset.", "claim": None,
         "verdict": "overclaim", "fix": "name the datasets where it wins"},
        {"file": "abstract.tex", "quote": "We study things.", "claim": None, "verdict": "ok"}]}))
elif agent == "auditor":
    (work / "audit.json").write_text(json.dumps({"findings": [
        {"file": "03_results.tex", "quote": "See Figure~\\ref{fig:fig_acc} and Table~\\ref{tab:main}.",
         "claim": "ours_beats_base", "verdict": "overclaim", "fix": "say what they show"},
        {"file": "01_intro.tex", "quote": "Text Text Text", "claim": None, "verdict": "ok"}]}))
elif agent == "line_editor":
    f = re.search(r"line-edit paper/([a-z0-9_]+)\.tex", prompt).group(1)
    p = paper / f"{f}.tex"
    if not os.environ.get("FAKE_LAZY_EDITOR"):
        p.write_text(p.read_text().replace("See Figure~\\ref{fig:fig_acc} and Table~\\ref{tab:main}.",
                                           "Figure~\\ref{fig:fig_acc} and Table~\\ref{tab:main} show the gain."))
elif agent == "chair":
    out = re.search(r"\.scriptorium/reviews/(\S+_meta\.json)", prompt).group(1)
    (work / "reviews" / out).write_text(json.dumps({"decision": "minor revision", "summary": "s",
        "required_changes": [{"change": "c", "where": "w", "action": "edit text"}]}))
elif agent == "searcher":
    lit = work / "lit"
    lit.mkdir(parents=True, exist_ok=True)
    pool = {f"doi:10.0/{i}": {"id": f"doi:10.0/{i}", "title": f"Paper {i}", "year": "2020", "queries": ["q"]}
            for i in range(12)}
    (lit / "pool.json").write_text(json.dumps(pool))
    (lit / "shortlist.json").write_text(json.dumps({"topics": ["noise"], "papers": [
        {"id": k, "topic": "noise", "relation": "competing", "why": "close"} for k in pool]}))
elif agent == "reader":
    lit = work / "lit"
    (lit / "abstracts").mkdir(parents=True, exist_ok=True)
    for cid in re.findall(r"^- (doi:\S+):", prompt, re.M):
        s = cid.replace(":", "_").replace("/", "_")
        (lit / "abstracts" / f"{s}.json").write_text(json.dumps(
            {"id": cid, "title": "T", "year": "2020", "abstract": "We filter noisy labels. It works well.",
             "source": "openalex"}))
        (lit / "cards" / f"{s}.json").write_text(json.dumps(
            {"id": cid, "title": "T", "year": "2020", "relation": "competing", "summary": "filters labels",
             "supports": ["filtering helps"], "quotes": ["We filter noisy labels."]}))
elif agent == "cite_auditor":
    todo = json.loads((work / "lit" / "citations_todo.json").read_text())
    out = []
    for t in todo:
        bad = os.environ.get("FAKE_MISCITE") and t["file"] == "03_results.tex" and t["key"] == "ref0a"
        out.append({"file": t["file"], "key": t["key"], "quote": t["sentence"],
                    "verdict": "unsupported" if bad else "supported", "evidence": "abstract",
                    "fix": "cite something else" if bad else ""})
    (work / "lit" / "citecheck.json").write_text(json.dumps({"findings": out}))
elif agent == "reviewer":
    out = re.search(r"\.scriptorium/reviews/(\S+\.json)", prompt).group(1)
    res = paper / "03_results.tex"
    revised = res.exists() and "We revised this." in res.read_text()
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
