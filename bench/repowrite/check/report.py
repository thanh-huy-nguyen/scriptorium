"""Score one paper against its task's answer key, and write the sheets a person adjudicates.

    python bench/repowrite/check/report.py --paper RUN/paper --key TASK/key/key.json --out RUN/score
                                           [--no-refs] [--sample 0.1] [--seed 0]

Writes into --out: extract.json (the model's annotation, cached), score.json (verdicts and counts), and three CSV
sheets for people: numbers.csv (every number not supported, plus a sample of supported ones), citations.csv (every
citing sentence, for support labels) and claims.csv (every sentence stating a finding).
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import body, pdf_tables, tables  # noqa: E402
from extract import extract  # noqa: E402
from match import match_all, summary, text_table  # noqa: E402


def sentences(tex: str) -> list[str]:
    t = re.sub(r"\\begin\{(table|figure)\*?\}.*?\\end\{\1\*?\}", " ", tex, flags=re.S)
    t = re.sub(r"\s+", " ", t)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z\\])", t) if s.strip()]


def citing(tex: str) -> list[dict]:
    out = []
    for s in sentences(tex):
        keys = [k.strip() for m in re.finditer(r"\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}", s)
                for k in m.group(1).split(",")]
        if keys:
            out.append({"sentence": s[:600], "keys": " ".join(keys)})
    return out


def write_csv(path: Path, rows: list[dict], cols: list[str]) -> None:
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paper", required=True, type=Path)
    ap.add_argument("--key", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--no-refs", action="store_true")
    ap.add_argument("--refresh-refs", nargs="?", const="all", default="",
                    help="look references up again: all, or only those not found or unverified ('unverified')")
    ap.add_argument("--sample", type=float, default=0.1, help="share of supported numbers sent to a person")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    key = json.loads(a.key.read_text())
    ext = extract(a.paper, key, a.out / "extract.json")
    matched = match_all(ext, key)
    tt = text_table(matched, {**tables(a.paper), **pdf_tables(a.paper)})
    refs = []
    cache = a.out / "refs.json"
    if not a.no_refs:
        if cache.exists() and not a.refresh_refs:
            refs = json.loads(cache.read_text())
        else:
            from refs import check_refs
            refs = check_refs(a.paper)
            cache.write_text(json.dumps(refs, indent=1))
        if a.refresh_refs == "unverified" and cache.exists():
            from refs import check_entry, parse_bib, bib_text
            bib = parse_bib(bib_text(a.paper))
            refs = [({"key": r["key"], "title": r.get("title", ""), **check_entry(bib[r["key"]])}
                     if r["verdict"] in ("unverified", "not found") and r["key"] in bib else r) for r in refs]
            cache.write_text(json.dumps(refs, indent=1))
    tex = body(a.paper)
    cites = citing(tex)
    score = {"paper": str(a.paper), "key": str(a.key), "numbers": summary(matched),
             "text_table": {"checked": len(tt), "not_in_table": sum(t["table_verdict"] == "not in table" for t in tt)},
             "references": {"cited": len(refs), "found": sum(r["verdict"] == "found" for r in refs),
                            "wrong_metadata": sum(r["verdict"] == "wrong metadata" for r in refs),
                            "not_found": sum(r["verdict"] in ("not found", "missing entry") for r in refs),
                            "unverified": sum(r["verdict"] == "unverified" for r in refs)},
             "citing_sentences": len(cites), "claims": len(ext.get("claims", [])),
             "extraction_tokens": ext.get("tokens", 0),
             "detail": {"numbers": matched, "text_table": tt, "references": refs}}
    (a.out / "score.json").write_text(json.dumps(score, indent=1))
    rng = random.Random(a.seed)
    review = [n for n in matched if n["verdict"] not in ("supported", "ignored", "derived")]
    review += [n for n in matched if n["verdict"] in ("supported", "derived") and rng.random() < a.sample]
    for n in review:
        n["identity"] = "; ".join(f"{f}={n.get(f)}" for f in ("dataset", "method", "versus", "condition", "metric",
                                                              "statistic") if n.get(f))
        n["key_ids"] = " / ".join(n.get("key_ids") or [])
        n["human_verdict"], n["human_note"] = "", ""
    write_csv(a.out / "numbers.csv", review, ["printed", "verdict", "where", "attributed_to", "identity", "context",
                                              "key_ids", "human_verdict", "human_note"])
    write_csv(a.out / "citations.csv", [{**c, "supported": "", "note": ""} for c in cites],
              ["keys", "sentence", "supported", "note"])
    write_csv(a.out / "claims.csv", [{**c, "within_evidence": "", "note": ""} for c in ext.get("claims", [])],
              ["type", "sentence", "within_evidence", "note"])
    s = score["numbers"]
    print(f"{s['result_numbers']} result numbers: {s['verdicts']}; errors {s['errors']}; "
          f"text vs table: {score['text_table']['not_in_table']} of {score['text_table']['checked']} not in the table; "
          f"references: {score['references']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
