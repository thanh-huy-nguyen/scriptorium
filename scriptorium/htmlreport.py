"""The run report as one self-contained HTML page, .scriptorium/report.html.

It links every printed number to its recipe and the lines that print it, every citation to the database record it was
fetched from and the files that cite it, and every figure to the script that draws it. It also shows the stage graph
with time and tokens per stage, every agent session, review scores, revision decisions and open problems.
"""
from __future__ import annotations

import html
import json
import re
import time
from pathlib import Path

from . import cite, events, history, state
from . import stages as S
from .config import Config

SRC_RE = re.compile(r"\\src\{([^}]*)\}")
ID_URL = {"doi": "https://doi.org/{}", "arxiv": "https://arxiv.org/abs/{}", "openalex": "https://openalex.org/{}",
          "dblp": "https://dblp.org/rec/{}", "s2": "https://www.semanticscholar.org/paper/{}"}

CSS = """
:root{--ink:#1f1b24;--muted:#6b6475;--line:#e4e0ea;--accent:#4E2A84;--soft:#F1EEF7;--mid:#B6ACD1;--bad:#9b2c2c;
--good:#2f6b3a;--bg:#fff}
@media (prefers-color-scheme:dark){:root{--ink:#ece8f2;--muted:#a59fb0;--line:#38323f;--soft:#2a2333;--bg:#17141b;
--mid:#5d4d7a;--accent:#c7b5ec}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 -apple-system,
"Inter","Segoe UI",Roboto,sans-serif}main{max-width:1100px;margin:0 auto;padding:32px 24px 80px}
h1{font-size:26px;margin:0 0 4px;font-weight:600}h2{font-size:18px;margin:40px 0 10px;font-weight:600;
border-bottom:2px solid var(--accent);padding-bottom:4px}.sub{color:var(--muted)}
.status{margin:16px 0;padding:12px 16px;border-radius:10px;background:var(--soft);border-left:4px solid var(--accent)}
.status.bad{border-left-color:var(--bad)}.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(128px,1fr));
gap:12px;margin:16px 0}.tile{border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.tile b{display:block;font-size:22px;font-weight:600;color:var(--accent)}.tile span{color:var(--muted);font-size:13px}
table{border-collapse:collapse;width:100%;font-size:13.5px}th{text-align:left;color:var(--muted);font-weight:500;
border-bottom:1px solid var(--line);padding:6px 8px}td{border-bottom:1px solid var(--line);padding:6px 8px;
vertical-align:top}td.n{text-align:right;font-variant-numeric:tabular-nums}code{font-size:12.5px;
background:var(--soft);padding:1px 4px;border-radius:4px}a{color:var(--accent)}.pill{display:inline-block;
padding:1px 8px;border-radius:99px;font-size:12px;background:var(--soft)}.pill.done{background:#e3f1e6;color:var(--good)}
.pill.failed{background:#f6e0e0;color:var(--bad)}.figs{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));
gap:16px}.figs figure{margin:0;border:1px solid var(--line);border-radius:10px;padding:10px;background:#fff}
.figs img{width:100%}.figs figcaption{font-size:12.5px;color:#444;margin-top:6px}ul.err li{color:var(--bad)}
details{margin:6px 0}summary{cursor:pointer}
"""


def _e(x) -> str:
    return html.escape(str(x if x is not None else ""))


def _fmt(v) -> str:
    return f"{v:.6g}" if isinstance(v, float) else _e(v)


def _uses(cfg: Config) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for p in sorted(cfg.paper.glob("*.tex")):
        for i, line in enumerate(p.read_text().splitlines(), 1):
            for k in SRC_RE.findall(re.sub(r"(?<!\\)%.*", "", line)):
                out.setdefault(k, []).append(f"{p.name}:{i}")
    return out


def _sessions(cfg: Config) -> list[dict]:
    out = []
    for d in sorted((cfg.work / "logs").glob("*")) if (cfg.work / "logs").exists() else []:
        for f in sorted(d.glob("*.json")):
            try:
                r = json.loads(f.read_text())
            except (OSError, json.JSONDecodeError):
                continue
            out.append({"stage": d.name, "file": f, **{k: r.get(k) for k in ("label", "agent", "model", "turns",
                                                                               "seconds", "ok", "tokens")}})
    return out


def write(cfg: Config, errs: list[str] | None = None) -> Path:
    s = state.load(cfg)
    o = S.outline(cfg)
    nums = S.read_json(cfg.work / "numbers.json") or {}
    nums.pop("__module__", None)
    uses = _uses(cfg)
    entries = cite.bib_entries(cfg.root)
    prov = cite._prov(cfg.root)
    cited = cite.cited_keys(cfg.root)
    b = S.read_json(cfg.work / "build.json") or {}
    evs = events.read(cfg, last_run=False)
    commits = {c["stage"]: c["id"] for c in history.log(cfg)}
    errs = errs if errs is not None else (S.read_json(cfg.work / "final_errors.json") or {}).get("errors", [])
    tot = {k: sum(u.get(k, 0) for u in s["usage"].values()) for k in
           ("sessions", "output_tokens", "input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")}
    tagged = sum(len(v) for v in uses.values())
    figs = sorted((cfg.paper / "figures").glob("*.png")) if (cfg.paper / "figures").exists() else []

    h = [f"<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width,"
         f"initial-scale=1'><title>Scriptorium report: {_e(o.get('title') or cfg.title)}</title><style>{CSS}</style>"
         "</head><body><main>",
         f"<h1>{_e(o.get('title') or cfg.title)}</h1>",
         f"<div class=sub>{_e(cfg.venue)} · {_e(', '.join(cfg.authors))} · report written "
         f"{time.strftime('%Y-%m-%d %H:%M')} · <a href='../paper/main.pdf'>paper/main.pdf</a></div>"]
    h.append(f"<div class='status{' bad' if errs else ''}'>" + ("All checks pass." if not errs else
             f"{len(errs)} check(s) still fail; see Open problems.") + "</div>")
    tiles = [(b.get("main_pages") or "?", f"main-text pages (limit {cfg.page_limit})"),
             (tagged, "printed numbers, each recomputed"), (len(nums), "recipes"),
             (len(entries), "citations, all fetched"), (len(figs), "figures from code"),
             (tot["sessions"], "agent sessions"), (f"{tot['output_tokens']:,}", "output tokens")]
    h.append("<div class=tiles>" + "".join(f"<div class=tile><b>{_e(v)}</b><span>{_e(k)}</span></div>"
                                           for v, k in tiles) + "</div>")
    if o.get("storyline"):
        h.append(f"<h2>Storyline</h2><p>{_e(o['storyline'])}</p>")

    if errs:
        h.append("<h2>Open problems</h2><ul class=err>" + "".join(f"<li>{_e(e)}</li>" for e in errs) + "</ul>")

    # Stage graph
    start = {e["stage"]: e["t"] for e in evs if e["ev"] == "stage_start"}
    end = {e["stage"]: e["t"] for e in evs if e["ev"] in ("stage_done", "stage_failed")}
    h.append("<h2>Stages</h2><table><tr><th>stage</th><th>after</th><th>status</th><th class=n>sessions</th>"
             "<th class=n>output tokens</th><th class=n>minutes</th><th>history</th><th>notes</th></tr>")
    for st in S.pipeline(cfg):
        rec = s["stages"].get(st.name, {})
        u = s["usage"].get(st.name, {})
        mins = f"{(end[st.name] - start[st.name]) / 60:.1f}" if st.name in start and st.name in end else ""
        note = []
        if st.name in s["scores"]:
            note.append(f"mean review {s['scores'][st.name]['mean']}")
        if rec.get("fixes"):
            note.append(f"{rec['fixes']} fix round(s)")
        if (s.get("decisions") or {}).get(st.name):
            note.append(s["decisions"][st.name])
        status = rec.get("status", "pending")
        h.append(f"<tr><td>{_e(st.name)}</td><td>{_e(', '.join(st.deps))}</td><td><span class='pill {_e(status)}'>"
                 f"{_e(status)}</span></td><td class=n>{u.get('sessions', 0)}</td><td class=n>"
                 f"{u.get('output_tokens', 0):,}</td><td class=n>{mins}</td><td><code>{_e(commits.get(st.name, ''))}"
                 f"</code></td><td>{_e('; '.join(note))}</td></tr>")
    h.append("</table>")

    # Numbers
    h.append("<h2>Numbers</h2><p class=sub>Every number printed in the paper is tagged with a recipe in "
             "<code>paper/sources.py</code> and recomputed from the repository's data before the paper is accepted."
             "</p><table><tr><th>key</th><th class=n>value</th><th>what it is</th><th>files read</th>"
             "<th>printed at</th></tr>")
    for k, v in sorted(nums.items(), key=lambda kv: (not uses.get(kv[0]), kv[0])):
        h.append(f"<tr><td><code>{_e(k)}</code></td><td class=n>{_fmt(v.get('value', v.get('error', '')))}</td>"
                 f"<td>{_e(v.get('means', ''))}</td><td>{_e(', '.join(v.get('files', []) or []))}</td>"
                 f"<td>{_e(', '.join(uses.get(k, [])) or 'not printed')}</td></tr>")
    h.append("</table>")

    # Citations
    h.append("<h2>Citations</h2><p class=sub>Every entry was fetched from a bibliographic database; none was typed by "
             "an agent.</p><table><tr><th>key</th><th>title</th><th>year</th><th>source</th><th>cited in</th></tr>")
    for k in sorted(entries):
        p = prov.get(k, {})
        cid = str(p.get("id", ""))
        kind, _, val = cid.partition(":")
        link = f"<a href='{_e(ID_URL[kind].format(val))}'>{_e(cid)}</a>" if kind in ID_URL and val else _e(cid or "typed")
        h.append(f"<tr><td><code>{_e(k)}</code></td><td>{_e(p.get('title') or cite.entry_field(entries[k], 'title'))}"
                 f"</td><td>{_e(p.get('year', ''))}</td><td>{link}</td><td>{_e(', '.join(sorted(set(cited.get(k, [])))) or 'unused')}"
                 "</td></tr>")
    h.append("</table>")

    # Figures
    if figs:
        h.append("<h2>Figures</h2><div class=figs>")
        for f in figs:
            script = f.with_suffix(".py")
            crit = S.read_json(cfg.work / "figures" / f"{f.stem}.critique.json") or {}
            rounds = len(list((cfg.work / "figures").glob(f"{f.stem}.critique.r*.json"))) + (1 if crit else 0)
            verdict = (f" · critic: {_e(crit.get('verdict'))} after {rounds} round(s)" if crit else "")
            h.append(f"<figure><img src='../paper/figures/{_e(f.name)}' alt='{_e(f.stem)}'><figcaption><b>{_e(f.stem)}"
                     f"</b> · drawn by <code>paper/figures/{_e(script.name) if script.exists() else '?'}</code>"
                     f"{verdict}</figcaption></figure>")
        h.append("</div>")

    # Reviews
    if s["scores"]:
        h.append("<h2>Reviews</h2><table><tr><th>round</th><th class=n>mean</th><th>each reviewer</th></tr>")
        for k, v in s["scores"].items():
            h.append(f"<tr><td>{_e(k)}</td><td class=n>{v['mean']}</td><td>"
                     f"{_e(', '.join(f'{p}: {x}' for p, x in v.get('each', {}).items()))}</td></tr>")
        h.append("</table>")
        if s.get("decisions"):
            h.append("<ul>" + "".join(f"<li>{_e(k)}: {_e(v)}</li>" for k, v in s["decisions"].items()) + "</ul>")

    # Sessions
    ses = _sessions(cfg)
    if ses:
        h.append("<h2>Agent sessions</h2><table><tr><th>stage</th><th>session</th><th>agent</th><th>model</th>"
                 "<th class=n>turns</th><th class=n>minutes</th><th class=n>output tokens</th><th>log</th></tr>")
        for r in ses:
            rel = r["file"].relative_to(cfg.work)
            h.append(f"<tr><td>{_e(r['stage'])}</td><td>{_e(r['label'])}{'' if r['ok'] else ' (failed)'}</td>"
                     f"<td>{_e(r['agent'])}</td><td>{_e(r['model'])}</td><td class=n>{_e(r['turns'] or 0)}</td>"
                     f"<td class=n>{(r['seconds'] or 0) / 60:.1f}</td><td class=n>"
                     f"{(r['tokens'] or {}).get('output_tokens', 0):,}</td><td><a href='{_e(rel)}'>log</a></td></tr>")
        h.append("</table>")
    h.append("</main></body></html>")
    out = cfg.work / "report.html"
    out.write_text("\n".join(h))
    return out
