"""Turn PaperWritingBench papers into RepoWrite tasks (notes mode): the system gets the sparse idea, the experimental
log and the figures with their captions; the answer key is every number in the log, each table cell with its table,
row and column as identity.

    python bench/repowrite/pwb_task.py --pwb DATA/datasets --ids cvpr2025_x iclr2025_y --out TASKS_DIR

Nothing of the original paper (its PDF, its reference lists, the dense idea) is copied into the task repository.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

VENUE = {"cvpr2025": ("cvpr", "CVPR 2025 (8 pages)", 8), "iclr2025": ("iclr", "ICLR 2025 (10 pages)", 10)}
CUTOFF = {"cvpr2025": "November 2024", "iclr2025": "October 2024"}      # the submission deadlines
NUM = re.compile(r"(?<![\w.])[-+−]?\d{1,3}(?:,\d{3})+(?:\.\d+)?(?![\w])|(?<![\w.])[-+−]?\d*\.?\d+(?:[eE][-+]?\d+)?%?(?![\w])")

BRIEF = """# Brief for the paper

## The idea
See `idea.md`: the problem, the idea and the method as the authors summarized it before writing.

## Where the results live
`experimental_log.md` holds the experimental setup and every result. Use only numbers from it, or numbers you
compute from it.

## Figures
`figures/` holds the figures the authors made; `figures/info.json` gives each figure's caption. Use the ones that
help, and refer to them by what they show.

## Venue
{venue_text}.

## Rules for this task
Treat this work as unpublished. Do not search for it, its title or its method name, and do not use any published
version of it. Cite only work that appeared before {cutoff}.
"""


def _num(s: str) -> float | None:
    t = s.replace(",", "").replace("−", "-").rstrip("%")
    try:
        return float(t)
    except ValueError:
        return None


def parse_log(text: str) -> tuple[list[dict], list[dict]]:
    """Table cells as quantities (table, row, column) and the other numbers as setup facts (the line they are on)."""
    quantities, setup = [], []
    lines = text.splitlines()
    heading, i, tno = "", 0, 0
    while i < len(lines):
        ln = lines[i]
        if ln.lstrip().startswith("#") or (ln.strip().startswith("**") and ln.strip().endswith("**")):
            heading = ln.strip("#* ").strip()
        if ln.strip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{2,}", lines[i + 1]):
            tno += 1
            header = [c.strip() for c in ln.strip().strip("|").split("|")]
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
                row = re.sub(r"[*_`]", "", cells[0]) if cells else ""
                for c, col in zip(cells[1:], header[1:]):
                    for m in NUM.finditer(c):
                        v = _num(m.group(0))
                        if v is not None:
                            quantities.append({"id": f"T{tno}|{row}|{col}", "value": v, "unit": "ratio",
                                               "dataset": f"table {tno}: {heading}"[:120], "method": row[:120],
                                               "metric": re.sub(r"[*_`]", "", col)[:120], "statistic": "as reported",
                                               "printed_in_log": m.group(0)})
                j += 1
            i = j
            continue
        for m in NUM.finditer(ln):
            v = _num(m.group(0))
            if v is not None:
                setup.append({"what": ln.strip()[:200], "value": v})
        i += 1
    return quantities, setup


def make(pdir: Path, out: Path) -> None:
    pid = pdir.name
    venue, text, pages = VENUE[pid.split("_")[0]]
    raw = pdir / "raw_materials"
    t = out / pid
    if t.exists():
        shutil.rmtree(t)
    (t / "repo" / "figures").mkdir(parents=True)
    (t / "key").mkdir()
    shutil.copy2(raw / "idea_sparse.md", t / "repo" / "idea.md")
    shutil.copy2(raw / "experimental_log.md", t / "repo" / "experimental_log.md")
    for f in (raw / "figures").iterdir():
        shutil.copy2(f, t / "repo" / "figures" / f.name)
    (t / "repo" / "brief.md").write_text(BRIEF.format(venue_text=text, cutoff=CUTOFF[pid.split("_")[0]]))
    (t / "meta.toml").write_text(f'id = "{pid}"\nsplit = "pilot"\nsource = "PaperWritingBench (Apache-2.0), sparse '
                                 f'idea setting"\nvenue = "{venue}"\nvenue_text = "{text}"\npage_limit = {pages}\n'
                                 f'results = "repo/experimental_log.md"\nmode = "notes"\n')
    Q, S = parse_log((raw / "experimental_log.md").read_text())
    vocab = {"dataset": {d: d for d in sorted({q["dataset"] for q in Q})},
             "method": {m: m for m in sorted({q["method"] for q in Q})},
             "condition": {}, "metric": sorted({q["metric"] for q in Q}), "statistic": ["as reported"]}
    (t / "key" / "key.json").write_text(json.dumps({"task": pid, "mode": "notes", "vocabulary": vocab,
                                                    "quantities": Q, "setup": S}, indent=1))
    print(f"{pid}: {len(Q)} table cells, {len(S)} other numbers")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pwb", required=True, type=Path, help="the extracted datasets/ folder")
    ap.add_argument("--ids", nargs="+", required=True)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args(argv)
    for pid in a.ids:
        make(a.pwb / pid.split("_")[0] / "papers" / pid, a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
