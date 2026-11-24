"""Copy a finished demo run into examples/demo-output/: the paper and its recipes, figure scripts and table specs, the
team's notes (setup, statistics, claim ledger, notation, literature cards, audits, figure critiques, reviews), the HTML
report, a run summary, and assets/example_pages.png (the first three pages).

Usage: python tools/export_demo.py /path/to/finished/demo/run
"""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DST = ROOT / "examples" / "demo-output"
NOTES = ("inventory.md", "setup.md", "evidence_notes.md", "numbers.md", "stats.md", "ledger.md", "notation.md",
         "outline.json", "story.json", "related.md", "audit.json", "report.md", "report.html")


def main(run: Path) -> None:
    if DST.exists():
        shutil.rmtree(DST)
    w = run / ".scriptorium"
    (DST / "paper" / "figures").mkdir(parents=True)
    for f in (run / "paper").iterdir():
        if f.is_file() and f.suffix in (".tex", ".py", ".bib"):
            shutil.copy2(f, DST / "paper" / f.name)
    for f in (run / "paper" / "figures").iterdir():
        if f.suffix in (".py", ".pdf", ".png") and not f.name.startswith("_"):    # _scratch files are not figures
            shutil.copy2(f, DST / "paper" / "figures" / f.name)
    shutil.copy2(run / "paper" / "main.pdf", DST / "paper.pdf")
    n = DST / "notes"
    n.mkdir()
    for name in NOTES:
        if (w / name).exists():
            shutil.copy2(w / name, n / name)
    for d in ("pitches", "reviews", "tables"):
        if (w / d).exists():
            shutil.copytree(w / d, n / d)
    (n / "lit").mkdir()
    for name in ("cards.md", "citecheck.json"):
        if (w / "lit" / name).exists():
            shutil.copy2(w / "lit" / name, n / "lit" / name)
    (n / "figures").mkdir()
    for f in (w / "figures").glob("*"):
        if f.suffix in (".md", ".json"):
            shutil.copy2(f, n / "figures" / f.name)
    # no absolute paths, and no links to session logs (they hold full prompts and are not exported)
    for f in n.rglob("*"):
        if f.is_file() and f.suffix in (".md", ".json", ".html"):
            t = f.read_text().replace(str(run), "examples/demo")
            t = re.sub(r"<a href='logs/[^']*'>log</a>", "", t).replace("href='../paper/main.pdf'>paper/main.pdf",
                                                                         "href='../paper.pdf'>paper.pdf")
            f.write_text(t)
    st = json.loads((w / "state.json").read_text())
    u = list(st["usage"].values()) + list(st.get("usage_earlier", {}).values())
    b = json.loads((w / "build.json").read_text())
    agents = sorted({json.loads(ln)["agent"] for ln in (w / "events.jsonl").read_text().splitlines()
                     if '"task_start"' in ln})
    summary = {"tagged": sum(p.read_text().count("\\src{") for p in (DST / "paper").glob("*.tex")
                             if p.name != "main.tex"),
               "recipes": len([k for k in json.loads((w / "numbers.json").read_text()) if k != "__module__"]),
               "citations": (DST / "paper" / "refs.bib").read_text().count("@"),
               "sessions": sum(x.get("sessions", 0) for x in u), "output_tokens": sum(x.get("output_tokens", 0) for x in u),
               "pages": b["pages"], "main_pages": b["main_pages"],
               "scores": {k: v["mean"] for k, v in st["scores"].items()}, "decisions": st.get("decisions", {}),
               "agents": agents}
    (DST / "run_summary.json").write_text(json.dumps(summary, indent=1))
    pages_png(DST / "paper.pdf", ROOT / "assets" / "example_pages.png")
    print(json.dumps(summary, indent=1))


def pages_png(pdf: Path, out: Path, n: int = 3, dpi: int = 110) -> None:
    import pymupdf
    from PIL import Image
    doc = pymupdf.open(str(pdf))
    ims = []
    for i in range(min(n, len(doc))):
        pix = doc[i].get_pixmap(dpi=dpi)
        ims.append(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
    gap = 24
    W = sum(im.width for im in ims) + gap * (len(ims) + 1)
    H = max(im.height for im in ims) + 2 * gap
    canvas = Image.new("RGB", (W, H), (241, 238, 247))
    x = gap
    for im in ims:
        canvas.paste(im, (x, gap))
        x += im.width + gap
    canvas.save(out)


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
