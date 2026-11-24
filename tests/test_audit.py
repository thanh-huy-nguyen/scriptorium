"""`scriptorium audit`: an existing paper is copied, flattened, built and checked; the original is never changed."""
import json
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from scriptorium import audit, cite, cli, engine, lit
from scriptorium import config as C

from test_pipeline import HERE

MAIN = r"""\documentclass{article}
\usepackage{natbib}
\title{A Paper Worth Auditing}
\begin{document}
\maketitle
\begin{abstract}
We study things. % a comment
\end{abstract}
\input{sec/intro}
\bibliographystyle{plainnat}
\bibliography{refs}
\end{document}
"""
INTRO = r"""\section{Introduction}\label{sec:intro}
Our method is the best on every dataset. Prior work filters noisy labels~\citep{real2020}.
A survey covers it all~\citep{fake2021}.
"""
BIB = """@article{real2020,
  title = {Learning with Noisy Labels},
  author = {Doe, Jane},
  year = {2020}
}

@article{fake2021,
  title = {A Survey That Does Not Exist},
  author = {Nobody, Ann},
  year = {2021}
}
"""


class AuditTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.src = self.tmp / "mypaper"
        (self.src / "sec").mkdir(parents=True)
        (self.src / "main.tex").write_text(MAIN)
        (self.src / "sec" / "intro.tex").write_text(INTRO)
        (self.src / "refs.bib").write_text(BIB)
        self.old = os.getcwd()
        os.chdir(self.tmp)
        self.env = {k: os.environ.get(k) for k in ("SCRIPTORIUM_CLAUDE", "PAPERANCHOR_STATE")}
        os.environ["SCRIPTORIUM_CLAUDE"] = str(HERE / "fake_claude.py")
        os.environ["PAPERANCHOR_STATE"] = str(self.tmp / ".pa_state")
        self.saved = (cite.search, lit.fetch_abstract)
        cite.search = lambda q, n=5, sources=(): ([{"id": "doi:10.1/real", "title": "Learning with Noisy Labels",
                                                    "year": "2020", "authors": ["Jane Doe"]}]
                                                  if "noisy" in q.lower() else [])
        lit.fetch_abstract = lambda cid: {"title": "Learning with Noisy Labels", "year": "2020",
                                          "abstract": "We filter noisy labels.", "source": "openalex", "errors": []}

    def tearDown(self):
        cite.search, lit.fetch_abstract = self.saved
        os.chdir(self.old)
        for k, v in self.env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_audit_end_to_end(self):
        before = {p: p.read_text() for p in self.src.rglob("*") if p.is_file()}
        with redirect_stdout(StringIO()):
            cli.main(["audit", str(self.src), "--setup-only"])
        out = self.tmp / "mypaper-audit"
        flat = (out / "paper" / "01_paper.tex").read_text()
        self.assertIn("Our method is the best on every dataset.", flat, "the \\input was expanded")
        self.assertNotIn("a comment", (out / "paper" / "abstract.tex").read_text())
        t = (out / "scriptorium.toml").read_text().replace('latex = ""', f'latex = "{HERE / "fake_latex.py"}"')
        (out / "scriptorium.toml").write_text(t)
        cfg = C.load(out)
        self.assertTrue(cfg.audit)
        os.chdir(out)
        buf = StringIO()
        with redirect_stdout(buf):
            status = engine.run_graph(cfg)
        self.assertEqual(status, "done", buf.getvalue())
        refs = {r["key"]: r for r in json.loads((out / ".scriptorium" / "audit" / "refs.json").read_text())}
        self.assertTrue(refs["real2020"]["found"])
        self.assertFalse(refs["fake2021"]["found"])
        report = (out / ".scriptorium" / "audit" / "report.md").read_text()
        self.assertIn("1 not found in any database", report)
        self.assertIn("A Survey That Does Not Exist", report)
        self.assertIn("[overclaim] \"Our method is the best on every dataset.\"", report)
        self.assertIn("area chair: minor revision", report)
        self.assertTrue((out / ".scriptorium" / "audit" / "report.html").exists())
        after = {p: p.read_text() for p in self.src.rglob("*") if p.is_file()}
        self.assertEqual(before, after, "the audited paper is never changed")


if __name__ == "__main__":
    unittest.main()
