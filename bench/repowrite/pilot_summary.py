"""Collect the M0 pilot: every scored paper, its errors per type, the run's cost, and the decision table of plan v5.

    python bench/repowrite/pilot_summary.py --runs workspace/bench/pilot/runs --out workspace/bench/pilot/report.md

A run folder is RUNS/<system>/<task>/<rep>/ with run.json (usage) and score/ (from check/report.py). Errors are the
checker's verdicts until people have labeled the sheets; labeled sheets (human_verdict, supported, within_evidence
filled in) replace them, and the report says which source each row uses.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


def human(score: Path) -> dict | None:
    """Hand-confirmed errors from labeled sheets, or None if the sheets are not labeled yet."""
    def rows(name):
        p = score / name
        return list(csv.DictReader(p.open())) if p.exists() else []
    nums, cits, cls = rows("numbers.csv"), rows("citations.csv"), rows("claims.csv")
    if not any(r.get("human_verdict") for r in nums) and not any(r.get("supported") for r in cits):
        return None
    return {"number": sum(r.get("human_verdict") in ("wrong value", "wrong identity") for r in nums),
            "citation": sum(r.get("supported") in ("no", "partly") for r in cits),
            "claim": sum(r.get("within_evidence") in ("overreach", "no") for r in cls)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args(argv)
    table = []
    for score in sorted(a.runs.glob("*/*/*/score/score.json")):
        run = score.parent.parent
        system, task, rep = run.parent.parent.name, run.parent.name, run.name
        s = json.loads(score.read_text())
        usage = json.loads((run / "run.json").read_text()) if (run / "run.json").exists() else {}
        h = human(score.parent)
        machine = {"number": s["numbers"]["errors"], "text_table": s["text_table"]["not_in_table"],
                   "reference": s["references"]["not_found"] + s["references"]["wrong_metadata"]}
        errs = ({**h, "text_table": machine["text_table"], "reference": machine["reference"]} if h else machine)
        table.append({"system": system, "task": task, "rep": rep, "source": "people" if h else "checker",
                      "errors": errs, "total": sum(errs.values()), "result_numbers": s["numbers"]["result_numbers"],
                      "output_tokens": usage.get("output_tokens")})
    by = defaultdict(list)
    for r in table:
        by[(r["system"], r["task"].split("_")[0] if r["task"].startswith(("cvpr", "iclr")) else r["task"])].append(r)
    lines = ["# M0 pilot", "", "Errors per paper by type. Source `checker` means the sheets are not labeled yet: those "
             "rows are provisional and do not decide anything.", "",
             "| System | Task | Rep | Source | Numbers | Text vs table | References | Citations | Claims | Total | "
             "Result numbers | Output tokens |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in table:
        e = r["errors"]
        lines.append(f"| {r['system']} | {r['task']} | {r['rep']} | {r['source']} | {e.get('number', '')} | "
                     f"{e.get('text_table', '')} | {e.get('reference', '')} | {e.get('citation', '–')} | "
                     f"{e.get('claim', '–')} | {r['total']} | {r['result_numbers']} | {r['output_tokens'] or ''} |")
    repo_tasks = [r for r in table if r["system"] == "single" and not r["task"].startswith(("cvpr", "iclr"))]
    pwb = [r for r in table if r["system"] == "single" and r["task"].startswith(("cvpr", "iclr"))]
    per_task = defaultdict(list)
    for r in repo_tasks:
        per_task[r["task"]].append(r["total"])
    high = sum(1 for v in per_task.values() if sum(v) / len(v) >= 3)
    pwb_hit = sum(1 for r in pwb if r["total"] >= 1)
    lines += ["", "## Decision table (plan v5, thresholds fixed in advance)", "",
              f"- Repository tasks where the single agent averages at least 3 errors per paper: **{high} of "
              f"{len(per_task)}** (needs 2 of 3).",
              f"- PaperWritingBench papers with at least 1 error: **{pwb_hit} of {len(pwb)}** (needs 4 of 5).",
              "- Scriptorium against the single agent on the same tasks, and checker precision and recall against the "
              "hand labels: filled in once the sheets are labeled.", "",
              "Provisional until every row's source is `people`."]
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines[-7:]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
