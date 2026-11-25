"""Read the raters' returned spreadsheets, check them, and score the checker against them.

    python bench/repowrite/audit/import_labels.py --audit AUDIT [--strict]

Put each returned file at AUDIT/returned/<rater>/paper_<code>/audit.xlsx (unzip what a rater sends into
AUDIT/returned/<rater>/). For each labeled paper this writes <run>/score/human/<rater>_<sheet>.csv (the checker's
verdict next to the rater's label), and AUDIT/summary.md with:

  - what is still blank or not a listed answer, per file (fix with the rater before trusting anything else);
  - agreement on papers both raters audited (raw agreement and Cohen's kappa per sheet), and the rows they disagree
    on, in AUDIT/disagreements_<code>.csv; fill its `resolved` column together, then run this again;
  - the checker against the labels: of the numbers it flagged, how many people call errors (precision), and of the
    numbers people call errors, how many it flagged (recall; sampled table cells count 1/sample each).
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from openpyxl import load_workbook

SHEETS = {  # sheet: (id column, label column, note column, allowed answers)
    "Numbers": ("id", "your verdict", "note", ["correct", "wrong value", "wrong identity", "not checkable",
                                               "not a result"]),
    "Citations": ("id", "supported", "note", ["yes", "partly", "no", "cannot tell"]),
    "Claims": ("id", "within evidence", "note", ["yes", "overreach", "no"]),
    "References": ("id", "exists", "note", ["yes", "wrong details", "no", "cannot tell"]),
}
ERROR = {"Numbers": {"wrong value", "wrong identity"}, "Citations": {"partly", "no"}, "Claims": {"overreach", "no"},
         "References": {"wrong details", "no"}}
FLAGGED = {"misattributed", "unsupported", "unclear"}


def read(path: Path) -> dict:
    wb = load_workbook(path, data_only=True)
    out = {"minutes": wb["Start here"]["B20"].value, "missed": [], "sheets": {}}
    for name, (idc, lab, note, _) in SHEETS.items():
        rows = list(wb[name].iter_rows(values_only=True))
        head = [str(h or "").strip() for h in rows[0]]
        i, j, k = head.index(idc), head.index(lab), head.index(note)
        out["sheets"][name] = {str(r[i]): {"label": str(r[j] or "").strip().lower(), "note": str(r[k] or "").strip()}
                               for r in rows[1:] if r[i]}
    for r in list(wb["Missed"].iter_rows(values_only=True))[1:]:
        if any(r):
            out["missed"].append([str(x or "") for x in r])
    return out


def kappa(a: list[str], b: list[str]) -> float | None:
    n = len(a)
    if not n:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[c] * cb[c] for c in set(a) | set(b)) / n / n
    return None if pe == 1 else (po - pe) / (1 - pe)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", required=True, type=Path)
    a = ap.parse_args(argv)
    mapping = json.loads((a.audit / "private" / "mapping.json").read_text())
    lines, labeled = ["# Hand audit: import", ""], {}
    problems = []
    for m in mapping:
        f = a.audit / "returned" / m["rater"] / f"paper_{m['code']}" / "audit.xlsx"
        if not f.exists():
            lines.append(f"- paper_{m['code']} ({m['rater']}): not returned yet")
            continue
        got = read(f)
        labeled[(m["code"], m["rater"])] = got
        for name, rows in got["sheets"].items():
            allowed = SHEETS[name][3]
            blank = [i for i, r in rows.items() if not r["label"] and not r["note"]]
            bad = [i for i, r in rows.items() if r["label"] and r["label"] not in allowed]
            if blank or bad:
                problems.append(f"- paper_{m['code']} ({m['rater']}) {name}: {len(blank)} blank"
                                + (f" ({', '.join(blank[:8])}{' …' if len(blank) > 8 else ''})" if blank else "")
                                + (f", {len(bad)} not a listed answer ({', '.join(bad[:8])})" if bad else ""))
        lines.append(f"- paper_{m['code']} ({m['rater']}): returned, {got['minutes'] or '?'} minutes, "
                     f"{len(got['missed'])} missed numbers added")
        # write next to the run's score, with the checker's verdict for numbers
        score = json.loads((Path(m["run"]) / "score" / "score.json").read_text())
        nums = score["detail"]["numbers"]
        hd = Path(m["run"]) / "score" / "human"
        hd.mkdir(exist_ok=True)
        for name, rows in got["sheets"].items():
            with (hd / f"{m['rater']}_{name.lower()}.csv").open("w", newline="") as fh:
                w = csv.writer(fh)
                w.writerow(["id", "checker", "label", "note"])
                for i, r in rows.items():
                    chk = nums[int(i[1:])]["verdict"] if name == "Numbers" else ""
                    w.writerow([i, chk, r["label"], r["note"]])
        if got["missed"]:
            with (hd / f"{m['rater']}_missed.csv").open("w", newline="") as fh:
                csv.writer(fh).writerows([["page", "number", "identity", "verdict", "note"], *got["missed"]])
    lines += ["", "## Blank or invalid answers", ""] + (problems or ["None."])

    # agreement on papers with two raters
    lines += ["", "## Agreement on papers both raters audited", ""]
    final: dict[str, dict] = {}                  # code -> sheet -> id -> label used for the checker scores
    by_code: dict[str, list] = {}
    for (c, r), got in labeled.items():
        by_code.setdefault(c, []).append((r, got))
    for c, lst in sorted(by_code.items()):
        if len(lst) == 1:
            final[c] = {n: {i: v["label"] for i, v in rows.items()} for n, rows in lst[0][1]["sheets"].items()}
            continue
        (r1, g1), (r2, g2) = lst[:2]
        res_path = a.audit / f"disagreements_{c}.csv"
        resolved = {}
        if res_path.exists():
            for row in csv.DictReader(res_path.open()):
                if row.get("resolved"):
                    resolved[(row["sheet"], row["id"])] = row["resolved"].strip().lower()
        lines += [f"paper_{c} ({r1}, {r2}):", "", "| Sheet | Rows | Raw agreement | Cohen's kappa |", "|---|---|---|---|"]
        dis, final[c] = [], {}
        for name in SHEETS:
            s1, s2 = g1["sheets"][name], g2["sheets"][name]
            ids = [i for i in s1 if s1[i]["label"] and s2.get(i, {}).get("label")]
            x, y = [s1[i]["label"] for i in ids], [s2[i]["label"] for i in ids]
            k = kappa(x, y)
            raw = sum(p == q for p, q in zip(x, y)) / len(ids) if ids else None
            lines.append(f"| {name} | {len(ids)} | {raw:.2f} | {k:.2f} |" if ids and k is not None else
                         f"| {name} | {len(ids)} | {'' if raw is None else f'{raw:.2f}'} | – |")
            final[c][name] = {}
            for i in s1:
                l1, l2 = s1[i]["label"], s2.get(i, {}).get("label", "")
                if l1 == l2:
                    final[c][name][i] = l1
                elif (name, i) in resolved:
                    final[c][name][i] = resolved[(name, i)]
                else:
                    dis.append({"sheet": name, "id": i, r1: l1, r2: l2, f"{r1} note": s1[i]["note"],
                                f"{r2} note": s2.get(i, {}).get("note", ""), "resolved": ""})
        if dis:
            old = res_path.exists()
            if not old:
                with res_path.open("w", newline="") as fh:
                    w = csv.DictWriter(fh, fieldnames=list(dis[0]))
                    w.writeheader()
                    w.writerows(dis)
            lines += ["", f"{len(dis)} rows still differ; " + (f"resolve them in `{res_path.name}` (the `resolved` "
                      "column) and run this again." if not old else f"`{res_path.name}` exists; fill in the rest.")]
        lines.append("")

    # the checker against the labels (numbers)
    lines += ["## The checker against the labels (numbers)", "",
              "| Paper | Flagged | Flagged and wrong | Precision | Wrong (weighted) | Wrong and flagged | Recall |",
              "|---|---|---|---|---|---|---|"]
    tot, werr = Counter(), {}
    for m in {x["code"]: x for x in mapping}.values():
        lab = final.get(m["code"], {}).get("Numbers")
        if not lab:
            continue
        nums = json.loads((Path(m["run"]) / "score" / "score.json").read_text())["detail"]["numbers"]
        w_cell = 1 / m["table_sample"]
        c = Counter()
        for i, l in lab.items():
            n = nums[int(i[1:])]
            if not l or l in ("not a result",):
                continue
            wt = w_cell if (n.get("where") == "table" and n["verdict"] == "supported") else 1
            flag, err = n["verdict"] in FLAGGED, l in ERROR["Numbers"]
            c["flag"] += flag
            c["tp"] += flag and err
            c["err"] += wt * err
            c["err_flag"] += wt * (err and flag)
        tot.update(c)
        werr[m["code"]] = round(c["err"])
        p = f"{c['tp'] / c['flag']:.2f}" if c["flag"] else "–"
        r = f"{c['err_flag'] / c['err']:.2f}" if c["err"] else "–"
        lines.append(f"| paper_{m['code']} ({m['task']}) | {c['flag']} | {c['tp']} | {p} | {c['err']:.0f} | "
                     f"{c['err_flag']:.0f} | {r} |")
    if tot:
        lines.append(f"| All | {tot['flag']} | {tot['tp']} | "
                     f"{tot['tp'] / tot['flag'] if tot['flag'] else 0:.2f} | {tot['err']:.0f} | "
                     f"{tot['err_flag']:.0f} | {tot['err_flag'] / tot['err'] if tot['err'] else 0:.2f} |")
    lines += ["", "Errors per sheet (labels used above; numbers weighted for the sampled table cells):", "", "| Paper | Numbers | Citations | Claims | References |",
              "|---|---|---|---|---|"]
    counts = {}
    for m in {x["code"]: x for x in mapping}.values():
        lab = final.get(m["code"])
        if not lab:
            continue
        e = {n: sum(v in ERROR[n] for v in lab[n].values()) for n in SHEETS}
        e["Numbers"] = werr.get(m["code"], e["Numbers"])        # sampled table cells count 1/sample each
        counts[m["run"]] = e
        lines.append(f"| paper_{m['code']} ({m['task']}) | " + " | ".join(str(e[n]) for n in SHEETS) + " |")
    (a.audit / "human_errors.json").write_text(json.dumps(counts, indent=1))
    (a.audit / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
