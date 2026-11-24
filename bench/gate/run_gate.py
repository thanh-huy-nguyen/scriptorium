"""The judge-validity gate (plan 3.5): build the pairs, collect votes from a panel, and test them against the
thresholds fixed in advance.

    python bench/gate/run_gate.py DATA_DIR --panel selection [--only null,improve,...] [--parallel 8]
    python bench/gate/run_gate.py DATA_DIR --panel selection --analyze

Votes are appended to DATA_DIR/votes_<panel>.jsonl, one line per vote, so a stopped run resumes where it left off.
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import random
import re
import sys
import tarfile
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scriptorium import judges as J  # noqa: E402
from scriptorium.config import Config  # noqa: E402

TASK_VERSIONS = ("You are given the text of two versions of the same research paper (extracted from the compiled "
                 "PDFs, figure captions included). Decide which version is the better paper as submitted.")
TASK_HUMAN = ("You are given the full text of two different papers submitted to the same machine learning "
              "conference. Decide which paper the conference's reviewers rated higher.")
SAMPLES = {"null_identical": 1, "null_paraphrase": 1, "improve": 1, "game": 1, "flaw": 1, "human": 1}


def pdf_cand(name: str, path: Path) -> J.Candidate:
    return J.Candidate(name, J.pdf_text(path))


def build_pairs(data: Path) -> list[dict]:
    papers = sorted(p for p in (data / "papers").iterdir() if (p / "base.pdf").exists())
    pairs = []
    for i in range(15):
        if papers:
            p = papers[i % len(papers)]
            pairs.append({"id": f"null_identical/{p.name}/{i}", "test": "null_identical", "a": str(p / "base.pdf"),
                          "b": str(p / "base.pdf"), "expect": None})
    for p in papers:
        for v in sorted((p / "variants").glob("*/variant.json")) if (p / "variants").exists() else []:
            rec = json.loads(v.read_text())
            if not rec.get("ok"):
                continue
            kind, vpdf = rec["kind"], str(v.parent / "variant.pdf")
            test = ("null_paraphrase" if kind == "paraphrase" else "improve" if kind == "improve"
                    else "game" if kind in ("padding", "hype", "injection") else "flaw")
            pairs.append({"id": f"{test}/{p.name}/{v.parent.name}", "test": test, "kind": kind,
                          "a": str(p / "base.pdf"), "b": vpdf,
                          "expect": {"improve": "b", "flaw": "a"}.get(test)})
    pairs = [x for x in pairs if x["test"] != "null_paraphrase"][:] + [x for x in pairs if x["test"] == "null_paraphrase"][:15]
    hp = data / "human_pairs.jsonl"
    if hp.exists():
        for line in hp.read_text().splitlines():
            d = json.loads(line)
            pairs.append({"id": f"human/{d['a_id']}/{d['b_id']}", "test": "human", "a_text": d["a_text"],
                          "b_text": d["b_text"], "expect": "a" if d["a_score"] > d["b_score"] else "b",
                          "gap": abs(d["a_score"] - d["b_score"])})
    return pairs


def human_pairs(data: Path, wut: Path, n: int = 100, seed: int = 7) -> int:
    """Pairs of ICLR 2024 papers (full text) whose mean human scores differ by at least 2, of similar length."""
    rng = random.Random(seed)
    papers = [json.loads(l) for l in gzip.open(wut / "2024_papers.jsonl.gz", "rt")]
    idx = {d["paper_id"]: d for d in (json.loads(l) for l in gzip.open(
        wut / "2024_paper_text_index.jsonl.gz", "rt"))}
    ok = [p for p in papers if (p.get("num_reviews") or 0) >= 3 and p.get("avg_actual_score")
          and p["paper_id"] in idx and 30000 <= (idx[p["paper_id"]].get("text_chars") or 0) <= 150000
          and not idx[p["paper_id"]].get("quality_flags")]
    rng.shuffle(ok)
    tar = tarfile.open(wut / "ICLR_2024.tar.gz")
    names = {Path(m.name).stem: m for m in tar.getmembers() if m.isfile()}

    def text(pid: str) -> str | None:
        m = names.get(pid)
        if not m:
            return None
        t = tar.extractfile(m).read().decode(errors="ignore")
        t = re.sub(r"(?im)^\s*(under review as a conference paper at iclr 2024|published as a conference paper at "
                   r"iclr 2024)\s*$", "", t)
        cut = re.search(r"(?m)^\s*REFERENCES\s*$", t)
        t = t[:cut.start()] if cut else t
        return re.sub(r"[ \t]{2,}", " ", t)[:60000]

    used, out = set(), []
    for i, a in enumerate(ok):
        if len(out) >= n:
            break
        if a["paper_id"] in used:
            continue
        for b in ok[i + 1:]:
            if b["paper_id"] in used or abs(a["avg_actual_score"] - b["avg_actual_score"]) < 2:
                continue
            la, lb = idx[a["paper_id"]]["text_chars"], idx[b["paper_id"]]["text_chars"]
            if not 0.75 <= la / lb <= 1.33:
                continue
            ta, tb = text(a["paper_id"]), text(b["paper_id"])
            if not ta or not tb:
                continue
            out.append({"a_id": a["paper_id"], "b_id": b["paper_id"], "a_score": a["avg_actual_score"],
                        "b_score": b["avg_actual_score"], "a_text": ta, "b_text": tb})
            used |= {a["paper_id"], b["paper_id"]}
            break
    with (data / "human_pairs.jsonl").open("w") as f:
        for d in out:
            f.write(json.dumps(d) + "\n")
    return len(out)


def collect(data: Path, panel: str, only: set[str] | None, parallel: int) -> None:
    cfg = Config(root=data.resolve())
    cfg.unset_api_key = True
    cfg.judge_parallel = parallel
    cfg.session_timeout_min = 30
    vf = data / f"votes_{panel}.jsonl"
    done = defaultdict(int)
    if vf.exists():
        for line in vf.read_text().splitlines():
            d = json.loads(line)
            if d["winner"] != "error":
                done[d["pair"]] += 1
    lock = threading.Lock()
    pairs = [p for p in build_pairs(data) if not only or p["test"] in only]
    todo = []
    for p in pairs:
        want = len(J.PANELS[panel]) * (1 if p["test"] == "human" else 2) * SAMPLES[p["test"]]
        if done[p["id"]] < want:
            todo.append(p)
    print(f"{len(todo)} pairs to judge on the {panel} panel", flush=True)

    def judge(p: dict) -> None:
        if p["test"] == "human":
            a, b, task = J.Candidate("a", p["a_text"]), J.Candidate("b", p["b_text"]), TASK_HUMAN
        else:
            a, b, task = pdf_cand("a", Path(p["a"])), pdf_cand("b", Path(p["b"])), TASK_VERSIONS
        one = (sum(map(ord, p["id"])) % 2) if p["test"] == "human" else None
        votes = J.compare(cfg, panel, task, a, b, samples=SAMPLES[p["test"]], canary="gate", parallel=6,
                          one_order=one)
        with lock, vf.open("a") as f:
            for v in votes:
                f.write(json.dumps({"pair": p["id"], "test": p["test"], "kind": p.get("kind"), "persona": v.persona,
                                    "model": v.model, "order": v.order, "sample": v.sample, "winner": v.winner,
                                    "confidence": v.confidence, "reason": v.reason, "tokens": v.tokens}) + "\n")
        k = sum(v.winner == "b" for v in votes)
        print(f"{p['id']}: b won {k}/{len(votes)}", flush=True)

    with ThreadPoolExecutor(max_workers=max(1, parallel // 6)) as ex:
        list(ex.map(judge, todo))


def analyze(data: Path, panel: str) -> dict:
    vs = [json.loads(l) for l in (data / f"votes_{panel}.jsonl").read_text().splitlines()]
    vs = [v for v in vs if v["winner"] != "error"]
    by = defaultdict(list)
    for v in vs:
        by[v["pair"]].append(v)
    res: dict = {"panel": panel, "votes": len(vs)}

    def first_won(v):
        return (v["winner"] == "a") == (v["order"] == "AB") if v["winner"] in ("a", "b") else None

    # 1. False keeps on null pairs: the variant (b) gets >= 10 of 12 votes.
    null = [p for p, x in by.items() if x[0]["test"].startswith("null")]
    fk = [p for p in null if J.keep([J.Vote("", "", v["order"], 0, v["winner"]) for v in by[p]], "b")]
    p_round = len(fk) / len(null) if null else float("nan")
    res["false_keep"] = {"pairs": len(null), "kept": len(fk), "per_round": p_round,
                         "per_loop_4_rounds": 1 - (1 - p_round) ** 4 if null else None,
                         "per_round_ci": J.wilson(len(fk), len(null)), "pass": null and 1 - (1 - p_round) ** 4 <= 0.05}
    # 2. Position bias over all null votes.
    fw = [first_won(v) for p in null for v in by[p] if first_won(v) is not None]
    k = sum(fw)
    lo, hi = J.wilson(k, len(fw))
    res["position"] = {"votes": len(fw), "first_share": k / len(fw) if fw else None, "ci": (lo, hi),
                       "pass": bool(fw) and lo <= 0.5 <= hi and abs(k / len(fw) - 0.5) <= 0.1}
    # 3. Small improvements: the improved version (b) wins the pair by majority.
    imp = [p for p, x in by.items() if x[0]["test"] == "improve"]
    wins = sum(sum(v["winner"] == "b" for v in by[p]) > len(by[p]) / 2 for p in imp)
    res["improve"] = {"pairs": len(imp), "b_wins": wins, "ci": J.wilson(wins, len(imp)),
                      "pass": len(imp) >= 40 and wins >= 28}
    # 4. Planted flaws, per type: the base (a) wins the pair by majority.
    flaws = defaultdict(list)
    for p, x in by.items():
        if x[0]["test"] == "flaw":
            flaws[x[0]["kind"]].append(sum(v["winner"] == "a" for v in x) > len(x) / 2)
    res["flaws"] = {k: {"pairs": len(w), "base_wins": sum(w), "pass": len(w) >= 20 and sum(w) >= 0.9 * len(w)}
                    for k, w in sorted(flaws.items())}
    # 5. Gaming probes: share of votes for the probed version (b), ties as half.
    games = defaultdict(list)
    for p, x in by.items():
        if x[0]["test"] == "game":
            games[x[0]["kind"]] += [1.0 if v["winner"] == "b" else 0.5 if v["winner"] == "tie" else 0.0 for v in x]
    res["games"] = {}
    for k, w in sorted(games.items()):
        kk = int(round(sum(w)))
        lo, hi = J.wilson(kk, len(w))
        res["games"][k] = {"votes": len(w), "probed_share": sum(w) / len(w), "ci": (lo, hi),
                           "pass": lo <= 0.5}
    # 6. Human-scored pairs: majority picks the higher-scored paper.
    hum = [(p, x) for p, x in by.items() if x[0]["test"] == "human"]
    exp = {p["id"]: p["expect"] for p in build_pairs(data) if p["test"] == "human"}
    right = sum(sum(v["winner"] == exp.get(p) for v in x) > len(x) / 2 for p, x in hum)
    res["human"] = {"pairs": len(hum), "right": right, "accuracy": right / len(hum) if hum else None,
                    "ci": J.wilson(right, len(hum)), "pass": len(hum) >= 100 and right >= 65}
    tok = defaultdict(int)
    for v in vs:
        for kk, vv in (v.get("tokens") or {}).items():
            tok[kk] += vv or 0
    res["tokens"] = dict(tok)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("data", type=Path)
    ap.add_argument("--panel", default="selection")
    ap.add_argument("--only", default="")
    ap.add_argument("--parallel", type=int, default=12)
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--human-pairs", type=Path, help="build human_pairs.jsonl from this dataset folder")
    a = ap.parse_args()
    if a.human_pairs:
        print(human_pairs(a.data, a.human_pairs), "human pairs")
    elif a.analyze:
        print(json.dumps(analyze(a.data, a.panel), indent=1))
    else:
        collect(a.data, a.panel, set(a.only.split(",")) - {""} or None, a.parallel)
