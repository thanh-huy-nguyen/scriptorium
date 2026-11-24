"""Build docs/index.html (the GitHub Pages site) and the example page images from examples/demo/output/.

Run after copying a finished demo run's paper to examples/demo/output/:  python tools/make_page.py
"""
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT = ROOT / "examples" / "demo-output"
URL = "https://thanh-huy-nguyen.github.io/scriptorium/"


def page_images(n=2):
    import pymupdf
    doc = pymupdf.open(str(OUT / "paper.pdf"))
    names = []
    for i in range(min(n, len(doc))):
        pix = doc[i].get_pixmap(dpi=110)
        name = f"example_p{i + 1}.png"
        pix.save(str(DOCS / "assets" / name))
        names.append(name)
    return names, len(doc)


def stats():
    st = json.loads((OUT / "run_summary.json").read_text())
    return st


TEAM = [
    ("Discovery", "A scout maps the repository; an experimentalist records the setup from the code; a results analyst "
     "writes a recipe per number; a statistician adds a paired test per comparison.",
     "setup facts quote their source; verdicts match p-values"),
    ("Literature", "A searcher maps the field right after the scout; readers card each paper from its abstract, in "
     "parallel; a librarian adds the official entries.", "only papers a search returned; nothing typed"),
    ("Story", "A cartographer builds the claim ledger; three architects pitch storylines and a panel picks one; an "
     "outliner plans the paper; a terminologist fixes the names.", "every claim has evidence, scope and strength"),
    ("Visuals", "A figure planner specs each figure; a plot maker and a diagram artist draw them from code; a critic "
     "sends weak ones back; a table setter builds tables from recipes.", "figures pass lint at print size"),
    ("Writing", "Writers draft sections in parallel, with contests for the abstract and introduction; an editor makes "
     "one paper; line editors polish each section.", "every number recomputes at each edit"),
    ("Checking", "A claim auditor checks every claim sentence; a citation auditor checks every citing sentence against "
     "the cited paper; a typesetter fixes layout.", "flagged sentences must change"),
    ("Review", "Reviewers for your venue score the paper; an area chair ranks the changes; a reviser makes them.",
     "kept only if the score holds, else rolled back"),
    ("Venue study", "Reads the target venue's recent papers on the same topic and writes a playbook for framing, "
     "Figure 1, contributions and emphasis.", "every quote occurs in the exemplar's PDF"),
    ("Finish", "A compliance agent meets the venue's requirements, proofreaders polish each section, and a layout "
     "inspector reads every rendered page and routes each flaw to its owner.", "pages inspected; nothing rewritten"),
]


def build():
    (DOCS / "assets").mkdir(parents=True, exist_ok=True)
    for f in ("banner.png", "pipeline.png", "social_preview.png"):
        shutil.copy2(ROOT / "assets" / f, DOCS / "assets" / f)
    shutil.copy2(OUT / "paper.pdf", DOCS / "assets" / "example_paper.pdf")
    imgs, npages = page_images()
    s = stats()
    css = (ROOT / "tools" / "page_head.css.html").read_text()
    team = "\n".join(
        f'<div class="agent"><span class="no">{i + 1}</span><h3>{n}</h3><p>{d}</p>'
        f'<span class="chk">&#10003; {c}</span></div>' for i, (n, d, c) in enumerate(TEAM))
    pages = "\n".join(f'<a href="assets/example_paper.pdf"><img src="assets/{im}" alt="Page {i + 1} of the example '
                      f'paper Scriptorium wrote"></a>' for i, im in enumerate(imgs))
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Scriptorium: Agents That Write Your Paper</title>
<meta name="description" content="30 Claude Code agents in nine teams write a research paper from your repository. Every number recomputes from your data, every citation is fetched and checked, every hand-off is checked in code.">
<meta property="og:title" content="Scriptorium: a team of agents writes your paper from your repository">
<meta property="og:description" content="Every number recomputes from your data. Every citation is fetched, never typed. Your data stays read-only.">
<meta property="og:image" content="{URL}assets/social_preview.png">
<meta property="og:url" content="{URL}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{URL}assets/social_preview.png">
<link rel="icon" type="image/png" href="assets/social_preview.png">
{css}
</head>
<body>
<nav><div class="wrap">
  <a class="brand" href="#">Scriptorium</a>
  <div class="links">
    <a href="#team">The team</a><a href="#checks">What is checked</a><a href="#example">Example</a>
    <a href="#start">Quickstart</a>
    <a class="gh" href="https://github.com/thanh-huy-nguyen/scriptorium">View on GitHub</a>
  </div>
</div></nav>

<header class="hero"><div class="wrap"><div class="grid">
  <div>
    <div class="kicker">Claude Code plugin &middot; open source</div>
    <h1>Scriptorium</h1>
    <p class="tagline">A team of agents writes your paper from your research repository.</p>
    <p class="lede">30 agents in nine teams split the work the way a lab would, and independent teams work at the
    same time: survey the results and the literature, plan the story, draw the figures, write, audit and review. Code
    checks every hand-off. Each number recomputes from your raw data, each citation is fetched and checked against the
    paper it cites, and your data stays read-only.</p>
    <p class="authors"><b>Thanh-Huy Nguyen</b> and <b>Ulas Bagci</b> &middot; Northwestern University</p>
    <div class="btns">
      <a class="btn primary" href="#start">Get started</a>
      <a class="btn ghost" href="assets/example_paper.pdf">Read an example paper</a>
      <a class="btn ghost" href="https://github.com/thanh-huy-nguyen/scriptorium">GitHub</a>
    </div>
  </div>
  <div class="figure" style="margin:0"><img src="assets/pipeline.png" alt="Four phases and eight teams, each checked in code"></div>
</div></div></header>

<section class="dark"><div class="wrap">
  <h2>One run of the example</h2>
  <p class="sub">What Scriptorium produced from the small label-noise study in <code>examples/demo</code>, start to finish, with no human edits.</p>
  <div class="stats">
    <div class="stat"><div class="num">{s['tagged']}</div><div class="what">numbers in the paper</div>
      <p>Every one carries a recipe and recomputes from <code>results/runs.jsonl</code>.</p></div>
    <div class="stat"><div class="num">{s['citations']}</div><div class="what">citations</div>
      <p>Every entry fetched from a bibliographic database; none typed by a model.</p></div>
    <div class="stat"><div class="num">{s['sessions']}</div><div class="what">agent sessions</div>
      <p>{s.get('main_pages') or s['pages']} pages of main text and about {round(s['output_tokens'] / 1000)}k output tokens. Every check passes on the final paper.</p></div>
  </div>
</div></section>

<section id="team"><div class="wrap">
  <h2>The team</h2>
  <p class="sub">Each agent is a Claude Code subagent whose instructions you can read and edit. Stages start as soon as the stages they need are done; after each one, plain Python checks the result before the next agent starts.</p>
  <div class="team">
{team}
  </div>
</div></section>

<section id="checks" class="alt"><div class="wrap">
  <h2>What is checked, in code</h2>
  <p class="sub">The checks do not ask a model whether the paper is right. They rerun, fetch and compare.</p>
  <div class="cols">
    <div class="code"><span class="label">paper/03_results.tex</span><pre>The filter reaches 92.6\\%<span class="b">\\src{{acc_dg_40_filter_mean}}</span>
on digits at 40% label noise.</pre></div>
    <div class="code"><span class="label">paper/sources.py</span><pre><span class="k">@source</span>(<span class="s">"acc_dg_40_filter_mean"</span>,
        means=<span class="s">"test accuracy (%) on clean test split, digits,</span>
<span class="s">               noise 0.4, filter, mean over 5 seeds"</span>)
<span class="k">def</span> acc_dg_40_filter_mean():
    <span class="k">return</span> _mean(_accs(<span class="s">"dg"</span>, 40, <span class="s">"filter"</span>))</pre></div>
  </div>
  <div class="rules">
    <div class="rule"><b>Numbers recompute</b><span>PaperAnchor reruns the recipe at every edit; a number that does not follow goes back to the writer with the value the data gives.</span></div>
    <div class="rule"><b>Citations resolve and support</b><span>Entries come only from <code>scriptorium cite add</code>; every citing sentence is checked against the cited abstract.</span></div>
    <div class="rule"><b>Claims stay in scope</b><span>Every claim sentence is audited against the claim ledger and the statistical tests; flagged sentences must change.</span></div>
    <div class="rule"><b>Figures come from code</b><span>Drawn from recipe values at print size; a lint and a critic check them.</span></div>
    <div class="rule"><b>Data stays read-only</b><span>A hook refuses edits outside <code>paper/</code>; a lock quarantines new files and stops the run on any change.</span></div>
  </div>
</div></section>

<section id="example"><div class="wrap">
  <h2>An example paper</h2>
  <p class="sub">The first pages of the {npages}-page paper Scriptorium wrote from <code>examples/demo</code>. Click for the PDF.</p>
  <div class="pages">
{pages}
  </div>
</div></section>

<section id="start" class="alt"><div class="wrap">
  <h2>Quickstart</h2>
  <p class="sub">You need Claude Code and a LaTeX engine (<a href="https://tectonic-typesetting.github.io">tectonic</a> or latexmk).</p>
  <div class="code"><span class="label">terminal</span><pre id="q1">pip install git+https://github.com/thanh-huy-nguyen/scriptorium
cd my-research-repo
scriptorium init --venue neurips  <span class="c"># official style files; locks your data</span>
scriptorium doctor                <span class="c"># checks Claude Code, LaTeX, the databases</span>
scriptorium run                   <span class="c"># the whole team; writes paper/main.pdf</span>
scriptorium watch                 <span class="c"># live view, in a second terminal</span></pre><button class="copy" data-t="q1">Copy</button></div>
  <div class="cols" style="margin-top:20px">
    <div class="code"><span class="label">inside Claude Code</span><pre id="q2">claude plugin marketplace add thanh-huy-nguyen/scriptorium
claude plugin install scriptorium@scriptorium
<span class="c"># then, in a session:</span> /scriptorium:write-paper</pre><button class="copy" data-t="q2">Copy</button></div>
    <div class="code"><span class="label">steer, undo, audit</span><pre id="q3">scriptorium run --pause-at story
scriptorium rollback outline
scriptorium audit path/to/paper  <span class="c"># check any LaTeX paper</span></pre><button class="copy" data-t="q3">Copy</button></div>
  </div>
</div></section>

<section id="cite"><div class="wrap">
  <h2>Citation</h2>
  <div class="code bib"><pre id="bib">@software{{nguyen2026scriptorium,
  title  = {{Scriptorium: A Team of Agents That Writes a Paper From Your Repository, With Every Number and Citation Checked}},
  author = {{Nguyen, Thanh-Huy and Bagci, Ulas}},
  year   = {{2026}},
  url    = {{https://github.com/thanh-huy-nguyen/scriptorium}}
}}</pre><button class="copy" data-t="bib">Copy</button></div>
</div></section>

<footer><div class="wrap">
  <img src="assets/northwestern.svg" alt="Northwestern University">
  <span>Scriptorium is MIT licensed. Numbers are checked by <a href="https://github.com/thanh-huy-nguyen/paperanchor">PaperAnchor</a>.</span>
  <a href="https://github.com/thanh-huy-nguyen/scriptorium">github.com/thanh-huy-nguyen/scriptorium</a>
</div></footer>

<script>
document.querySelectorAll(".copy").forEach(function (b) {{
  b.addEventListener("click", function () {{
    var t = document.getElementById(b.dataset.t).innerText;
    try {{ navigator.clipboard.writeText(t); b.textContent = "Copied"; }} catch (e) {{ b.textContent = "Select and copy"; }}
    setTimeout(function () {{ b.textContent = "Copy"; }}, 1600);
  }});
}});
</script>
</body>
</html>
"""
    (DOCS / "index.html").write_text(html)
    print("wrote docs/index.html with", imgs)


if __name__ == "__main__":
    build()
