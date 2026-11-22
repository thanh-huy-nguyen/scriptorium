"""Copy a finished demo run into examples/demo-output/ (the paper, its recipes, figures, reviews and the report).

Usage: python tools/export_demo.py /path/to/finished/demo/run
"""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DST = ROOT / "examples" / "demo-output"


def main(run: Path) -> None:
    if DST.exists():
        shutil.rmtree(DST)
    (DST / "paper" / "figures").mkdir(parents=True)
    for f in (run / "paper").iterdir():
        if f.is_file() and f.suffix in (".tex", ".py", ".bib", ".pdf"):
            shutil.copy2(f, DST / "paper" / f.name)
    for f in (run / "paper" / "figures").iterdir():
        if f.suffix in (".py", ".pdf", ".png"):
            shutil.copy2(f, DST / "paper" / "figures" / f.name)
    shutil.copy2(run / "paper" / "main.pdf", DST / "paper.pdf")
    w = run / ".scriptorium"
    (DST / "notes").mkdir()
    for name in ("report.md", "outline.json", "evidence_notes.md", "inventory.md", "related.md", "numbers.md"):
        if (w / name).exists():
            shutil.copy2(w / name, DST / "notes" / name)
    (DST / "notes" / "reviews").mkdir()
    for f in sorted((w / "reviews").glob("*")):
        if f.suffix in (".json", ".md"):
            shutil.copy2(f, DST / "notes" / "reviews" / f.name)
    st = json.loads((w / "state.json").read_text())
    rep = (w / "report.md").read_text()
    tagged = int(re.search(r"(\d+) tagged numbers", rep).group(1))
    cites = int(re.search(r"\| Citations \| (\d+) entries", rep).group(1))
    build = json.loads((w / "build.json").read_text())
    logs = [json.loads(f.read_text()) for f in (w / "logs").glob("*/*.json")]   # the latest session per task
    tot = lambda k: (len(logs) if k == "sessions" else sum((r.get("turns") or 0) for r in logs) if k == "turns"
                     else sum((r.get("tokens") or {}).get(k, 0) for r in logs))
    scores = [v["mean"] for k, v in sorted(st["scores"].items())]
    summary = {"tagged": tagged, "citations": cites, "sessions": tot("sessions"), "turns": tot("turns"),
               "output_tokens": tot("output_tokens"), "pages": build["pages"], "score_first": scores[0],
               "score_last": scores[-1], "decisions": st.get("decisions", {})}
    (DST / "run_summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
