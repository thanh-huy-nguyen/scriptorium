"""Build blinded hand-audit packets: one folder and one spreadsheet per paper, grouped by rater.

    python bench/repowrite/audit/make_packets.py --assignment AUDIT/assignment.json

AUDIT/assignment.json names the papers and who audits each one (paths relative to the file's folder):

    {"seed": 0, "table_sample": 0.25, "tasks": "../../repowrite/tasks",
     "papers": [{"run": "../runs/single/demo/s1", "paper": "repo/paper", "task": "demo", "raters": ["R2"]}, ...]}

Writes AUDIT/packets/<rater>/ (and <rater>.zip to send) with, for each paper, a folder named by a random code:
paper.pdf (metadata removed), audit.xlsx (instructions, the four sheets to fill, and the task's data) and data/ (the
task's raw result files). The checker's verdicts are not in the packet, so they cannot anchor the raters. The code
of each paper and the row ids are kept in AUDIT/private/mapping.json for import_labels.py.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import shutil
import string
import sys
import unicodedata
import urllib.parse
from pathlib import Path

import pymupdf
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "check"))
from refs import bib_text, cited_keys, parse_bib  # noqa: E402

CHOICES = {
    "numbers": ["correct", "wrong value", "wrong identity", "not checkable", "not a result"],
    "citations": ["yes", "partly", "no", "cannot tell"],
    "claims": ["yes", "overreach", "no"],
    "references": ["yes", "wrong details", "no", "cannot tell"],
}
HEAD = PatternFill("solid", fgColor="E8EEF2")
FILL = PatternFill("solid", fgColor="FFF6D6")      # the columns a rater fills in
WRAP = Alignment(wrap_text=True, vertical="top")

START = """How to audit this paper (about 90 minutes)

1. Open paper.pdf. Read the abstract and the introduction once, so you know what the paper claims.
2. Open the data: the "Data" sheet in this file lists every quantity computed from the task's results, one per row,
   with its dataset, method, setting, metric and statistic. Use the filter arrows in its header row to find a
   quantity. The raw files are in the data/ folder next to this file.
3. Fill in the yellow columns of the four sheets, top to bottom. Pick from the dropdown; write a note only when you
   are unsure or the answer needs a reason. Leave a row blank only if you skip it on purpose, and say why in the note.
     Numbers     Is each number right for what the paper says it is?
     Citations   Does each cited paper say what the sentence attributes to it?
     Claims      Do the results support each finding at the scope it is stated?
     References  Does each reference exist, with the right authors, title and year?
4. If you see a result number in the paper that is not in the Numbers sheet, add it to the "Missed" sheet.
5. Write how long the audit took in minutes on this sheet (cell B20), save the file, and send it back without
   renaming it. Do not talk about the papers with the other rater until both of you have sent all your files.

Grey boxes in the PDF hide the few words that would name the system that wrote the paper; skip them.
The definitions of every answer are in the "Guide" sheet. Judge only what the paper says; you are not told which
system wrote it, and it does not matter for the labels."""

GUIDE = [
    ("Numbers", "correct", "the number is right for what the sentence or table says it is, at the precision printed "
     "(92.6% for 0.92593 is correct; 92.7% is not). Differences, ratios and \"a fifth\" are correct if they follow "
     "from the data."),
    ("Numbers", "wrong value", "the paper says what the number is, and the value is wrong."),
    ("Numbers", "wrong identity", "the value is real, but belongs to another dataset, method, setting or statistic "
     "than the paper says (for example the Digits result printed as the Breast Cancer one)."),
    ("Numbers", "not checkable", "the data cannot settle it: a hyperparameter not in any file, a number from a cited "
     "paper."),
    ("Numbers", "not a result", "a count of datasets, a year, a section number, an equation constant."),
    ("Numbers", "note", "write \"key gap: what it is\" when the paper computes a number correctly that the Data sheet "
     "does not list."),
    ("Citations", "yes", "the cited paper says or shows what the sentence attributes to it."),
    ("Citations", "partly", "right topic, but the sentence overstates or misstates it."),
    ("Citations", "no", "the cited paper does not say this, or is about something else."),
    ("Citations", "cannot tell", "neither the abstract nor the paper (if you can open it) settles it."),
    ("Citations", "how", "read the cited paper's abstract first (the References sheet links a search); open the full "
     "paper only when the abstract does not settle it. If a sentence cites several papers, judge each and name the "
     "wrong one in the note."),
    ("Claims", "yes", "the results support the sentence at the scope it states."),
    ("Claims", "overreach", "true in part, but stated more broadly than the results allow: more datasets, settings or "
     "certainty than shown; \"significant\" without a test; a mechanism stated as shown when it was not measured."),
    ("Claims", "no", "the results contradict it, or nothing in them bears on it."),
    ("References", "yes", "the paper exists with these authors, this title and this year (one year off is fine for "
     "an arXiv version)."),
    ("References", "wrong details", "the paper exists, but the first author, the title or the year is wrong."),
    ("References", "no", "you cannot find any such paper."),
    ("References", "cannot tell", "you could not search (say why in the note)."),
]


assert len(START.splitlines()) < 20, "the minutes cell (B20) must stay below the instructions"


def code(rng: random.Random, used: set) -> str:
    while True:
        c = "".join(rng.choice(string.ascii_uppercase) for _ in range(2)) + str(rng.randint(2, 9))
        if c not in used:
            used.add(c)
            return c


_COMBINE = {"'": "\u0301", "`": "\u0300", "^": "\u0302", '"': "\u0308", "~": "\u0303", "=": "\u0304",
            ".": "\u0307", "c": "\u0327", "v": "\u030c", "u": "\u0306", "H": "\u030b"}


def accents(s: str) -> str:
    s = re.sub(r"\\([`'^\"~=.]|[cvuH](?=[\s{]))\s*\{?\\?([a-zA-Z])\}?",
               lambda m: unicodedata.normalize("NFC", m.group(2) + _COMBINE[m.group(1)]), s)
    return re.sub(r"\\(ss|o|l)(?![a-zA-Z])\s*", lambda m: {"ss": "ß", "o": "ø", "l": "ł"}[m.group(1)], s)


def detex(s: str) -> str:
    s = accents(s)
    s = re.sub(r"\\(?:no)?cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}", lambda m: "[" + ", ".join(
        k.strip() for k in m.group(1).split(",")) + "]", s)
    s = re.sub(r"\\(?:begin|end)\{[^}]*\}", " ", s)
    s = re.sub(r"\\(?:section|subsection|paragraph)\*?\{([^}]*)\}", r"\1. ", s)
    s = re.sub(r"\\(?:ref|eqref|label)\{[^}]*\}", "#", s)
    for _ in range(3):
        s = re.sub(r"\\[a-zA-Z]+\*?\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"\\[a-zA-Z]+", " ", s).replace("~", " ").replace("{", "").replace("}", "").replace("$", "")
    return re.sub(r"\s+", " ", s).strip()


def authors(a: str) -> str:
    names = [n.strip() for n in a.replace("\n", " ").split(" and ") if n.strip()]
    names = [(n.split(",")[1].strip() + " " + n.split(",")[0].strip()) if "," in n else n for n in names]
    return ", ".join(names[:3]) + (" et al." if len(names) > 3 else "")


def sheet(wb: Workbook, title: str, cols: list[tuple[str, int]], rows: list[list], fill_from: int | None,
          choices: list[str] | None = None):
    ws = wb.create_sheet(title)
    ws.append([c for c, _ in cols])
    for i, (_, w) in enumerate(cols, 1):
        ws.column_dimensions[ws.cell(1, i).column_letter].width = w
        ws.cell(1, i).font = Font(bold=True)
        ws.cell(1, i).fill = HEAD
    for r in rows:
        ws.append(r)
    n = max(len(rows), 1) + (40 if not rows else 0)
    for row in ws.iter_rows(min_row=2, max_row=n + 1):
        for c in row:
            c.alignment = WRAP
            if fill_from is not None and c.column >= fill_from:
                c.fill = FILL
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    if choices:
        dv = DataValidation(type="list", formula1='"' + ",".join(choices) + '"', allow_blank=True,
                            showErrorMessage=True, errorTitle="Pick from the list",
                            error="Choose one of: " + ", ".join(choices))
        ws.add_data_validation(dv)
        col = ws.cell(1, fill_from).column_letter
        dv.add(f"{col}2:{col}{n + 1}")
    return ws


_ABBR = {"al.", "fig.", "figs.", "e.g.", "i.e.", "sec.", "tab.", "eq.", "eqs.", "vs.", "cf.", "no.", "vol.", "pp."}
_MARK = re.compile(r"^\[\d+\]$")


def blind_pdf(doc, pat: re.Pattern) -> int:
    """Grey out every sentence and reference entry that names the system (its required self-citation), so the rater
    cannot tell which system wrote the paper. Returns the number of passages hidden."""
    hidden, in_refs = 0, False
    for page in doc:
        words = page.get_text("words")
        spans = []
        for i, w in enumerate(words):
            if w[4].strip(".,;:") == "References" and w[7] == 0:
                in_refs = True
            if not pat.search(w[4]):
                continue
            start = next((j for j in range(i, max(i - 40, -1), -1) if _MARK.match(words[j][4]) and words[j][7] == 0),
                         None) if in_refs else None
            if start is not None:                          # a reference entry: up to the next entry's marker
                end = next((j - 1 for j in range(i + 1, min(i + 80, len(words))) if _MARK.match(words[j][4])
                            and words[j][7] == 0), min(i + 60, len(words) - 1))
            else:                                          # a sentence: from the last full stop to the next one
                def stop(j):
                    t = words[j][4]
                    return t.endswith(".") and t.lower() not in _ABBR and not re.fullmatch(r"[A-Z]\.", t)
                start = next((j + 1 for j in range(i - 1, max(i - 80, -1), -1) if stop(j)), max(i - 80, 0))
                end = next((j for j in range(i, min(i + 80, len(words))) if stop(j)), min(i + 80, len(words) - 1))
            spans.append((start, end))
        for a, b in spans:
            for w in words[a:b + 1]:
                page.add_redact_annot(pymupdf.Rect(w[:4]), fill=(0.82, 0.82, 0.82))
            hidden += 1
        if spans:
            page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE)
    return hidden


def build(paper_cfg: dict, base: Path, tasks: Path, rng: random.Random, sample: float, pcode: str, rater: str,
          out: Path, blind: re.Pattern) -> dict:
    run = (base / paper_cfg["run"]).resolve()
    paper = run / paper_cfg.get("paper", "paper")
    task = tasks / paper_cfg["task"]
    score = json.loads((run / "score" / "score.json").read_text())
    key = json.loads((task / "key" / "key.json").read_text())
    out.mkdir(parents=True, exist_ok=True)

    doc = pymupdf.open(str(paper / "main.pdf"))       # metadata can name the tool that made the PDF
    doc.set_metadata({})
    doc.del_xml_metadata()
    hidden = blind_pdf(doc, blind)
    doc.save(str(out / "paper.pdf"), garbage=3, deflate=True)
    data = out / "data"
    data.mkdir(exist_ok=True)
    for f in sorted((task / "repo").rglob("*")):
        rel = f.relative_to(task / "repo")
        if f.is_file() and (rel.parts[0] in ("results", "experiments") or f.name == "experimental_log.md"):
            (data / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, data / rel)

    # numbers: every extracted number except table cells the checker confirmed, plus a sample of those
    nums, rows_n = score["detail"]["numbers"], []
    srng = random.Random(f"{pcode}-cells")            # same sample for both raters of a paper
    for i, n in enumerate(nums):
        cell_ok = n.get("where") == "table" and n["verdict"] == "supported"
        if cell_ok and srng.random() >= sample:
            continue
        ident = "; ".join(f"{f}: {n[f]}" for f in ("dataset", "method", "versus", "condition", "metric", "statistic")
                          if n.get(f))
        if blind.search(n.get("context", "")):
            continue
        rows_n.append([f"N{i}", n["printed"], n.get("where", ""), detex(n.get("context", ""))[:900], ident, "", ""])
    bib = parse_bib(bib_text(paper))
    keys = cited_keys(paper)
    from importlib import import_module
    rep = import_module("report")
    from common import body
    cites = rep.citing(body(paper))
    rows_c = []
    for i, c in enumerate(cites):
        ks = c["keys"].split()
        if blind.search(c["sentence"]) or any(blind.search(bib.get(k, {}).get("title", "")) for k in ks):
            continue
        titles = " | ".join(f"[{k}] {bib.get(k, {}).get('title', '(no entry)')}" for k in ks)
        rows_c.append([f"C{i}", detex(c["sentence"])[:900], titles, "", ""])
    rows_cl = [[f"L{i}", c.get("type", ""), detex(c.get("sentence", ""))[:900], "", ""]
               for i, c in enumerate(score["detail"].get("claims") or json.loads(
                   (run / "score" / "extract.json").read_text()).get("claims", []))
               if not blind.search(c.get("sentence", ""))]
    rows_r = []
    for i, k in enumerate(keys):
        e = bib.get(k, {})
        t = detex(e.get("title", ""))
        if blind.search(t) or blind.search(e.get("howpublished", "") + e.get("url", "")):
            continue
        link = "https://scholar.google.com/scholar?q=" + urllib.parse.quote(t) if t else ""
        rows_r.append([f"R{i}", k, authors(detex(e.get("author", ""))), t, e.get("year", ""),
                       detex(e.get("booktitle", "") or e.get("journal", "") or e.get("eprint", "")), link, "", ""])

    wb = Workbook()
    ws = wb.active
    ws.title = "Start here"
    ws.column_dimensions["A"].width = 120
    for j, line in enumerate(START.splitlines(), 1):
        ws.cell(j, 1, line).font = Font(size=12, bold=(j == 1))
    ws.cell(20, 1, f"Paper {pcode}, rater {rater}. Minutes the audit took:").font = Font(bold=True)
    ws.column_dimensions["B"].width = 14
    ws.cell(20, 2).fill = FILL
    ws.cell(21, 1, f"Rows to label: {len(rows_n)} numbers, {len(rows_c)} citing sentences, {len(rows_cl)} claims, "
                   f"{len(rows_r)} references.")
    g = wb.create_sheet("Guide")
    g.append(["Sheet", "Answer", "Meaning"])
    for r in GUIDE:
        g.append(list(r))
    for c, w in zip("ABC", (12, 16, 110)):
        g.column_dimensions[c].width = w
    for row in g.iter_rows():
        for c in row:
            c.alignment = WRAP
    sheet(wb, "Numbers", [("id", 6), ("number", 10), ("where", 9), ("sentence or table row", 70),
                          ("what the paper says it is", 40), ("your verdict", 16), ("note", 40)], rows_n, 6,
          CHOICES["numbers"])
    sheet(wb, "Citations", [("id", 6), ("sentence", 80), ("cited papers", 50), ("supported", 13), ("note", 40)],
          rows_c, 4, CHOICES["citations"])
    sheet(wb, "Claims", [("id", 6), ("type", 12), ("sentence", 90), ("within evidence", 15), ("note", 40)], rows_cl,
          4, CHOICES["claims"])
    ws_r = sheet(wb, "References", [("id", 6), ("key", 18), ("authors", 30), ("title", 55), ("year", 7),
                                    ("venue", 25), ("search", 12), ("exists", 14), ("note", 30)], rows_r, 8,
                 CHOICES["references"])
    for row in ws_r.iter_rows(min_row=2, max_row=len(rows_r) + 1, min_col=7, max_col=7):
        for c in row:
            if c.value:
                c.hyperlink, c.value, c.style = c.value, "search", "Hyperlink"
    sheet(wb, "Missed", [("page", 6), ("number", 10), ("what the paper says it is", 50), ("your verdict", 16),
                         ("note", 40)], [], 1, None)
    qs = key["quantities"]
    fields = ("dataset", "method", "versus", "condition", "metric", "statistic")
    sheet(wb, "Data", [(f, 22) for f in fields] + [("value", 14), ("unit", 10)],
                [[q.get(f, "") for f in fields] + [float(f"{q['value']:.6g}") if isinstance(q["value"], (int, float))
                                                    else q["value"], q.get("unit", "")] for q in qs], None)
    wb.save(out / "audit.xlsx")
    return {"code": pcode, "rater": rater, "run": str(run), "paper": str(paper), "task": paper_cfg["task"],
            "hidden_passages": hidden, "rows": {"numbers": len(rows_n), "citations": len(rows_c), "claims": len(rows_cl),
                     "references": len(rows_r)}, "table_sample": sample}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--assignment", required=True, type=Path)
    a = ap.parse_args(argv)
    base = a.assignment.resolve().parent
    cfg = json.loads(a.assignment.read_text())
    tasks = (base / cfg.get("tasks", "tasks")).resolve()
    rng, used = random.Random(cfg.get("seed", 0)), set()
    blind = re.compile("|".join(cfg.get("blind_terms", ["Scriptorium"])), re.I)
    for p in cfg["papers"]:
        p["code"] = p.get("code") or code(rng, used)
    shutil.rmtree(base / "packets", ignore_errors=True)
    mapping = []
    for p in cfg["papers"]:
        for r in p["raters"]:
            mapping.append(build(p, base, tasks, rng, cfg.get("table_sample", 0.25), p["code"], r,
                                 base / "packets" / r / f"paper_{p['code']}", blind))
    for r in sorted({m["rater"] for m in mapping}):
        (base / "packets" / r / "README.txt").write_text(
            f"Hand audit, rater {r}\n\nOne folder per paper. In each, open audit.xlsx and follow its first sheet, "
            "\"Start here\".\nSend back every audit.xlsx when you are done (keep the folder names).\n\n"
            + "\n".join(f"  paper_{m['code']}: {m['rows']['numbers']} numbers, {m['rows']['citations']} citing "
                        f"sentences, {m['rows']['claims']} claims, {m['rows']['references']} references"
                        for m in mapping if m["rater"] == r) + "\n")
        shutil.make_archive(str(base / "packets" / r), "zip", base / "packets", r)
    (base / "private").mkdir(exist_ok=True)
    (base / "private" / "mapping.json").write_text(json.dumps(mapping, indent=1))
    for m in mapping:
        print(f"{m['rater']} paper_{m['code']}  {m['task']:<22} {m['rows']}  hidden passages: {m['hidden_passages']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
