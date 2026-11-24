"""The literature team: search pool, reader cards checked against abstracts, the citation check and its fixes."""
import json
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from scriptorium import cli, lit, state
from scriptorium import config as C

from test_pipeline import HERE, make_repo


class LitTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        make_repo(self.tmp)
        self.old = os.getcwd()
        os.chdir(self.tmp)
        self.env = {k: os.environ.get(k) for k in ("SCRIPTORIUM_CLAUDE", "PAPERANCHOR_STATE", "FAKE_MISCITE")}
        os.environ["SCRIPTORIUM_CLAUDE"] = str(HERE / "fake_claude.py")
        os.environ["PAPERANCHOR_STATE"] = str(self.tmp / ".pa_state")
        with redirect_stdout(StringIO()):
            cli.main(["init"])
        t = (self.tmp / "scriptorium.toml").read_text()
        (self.tmp / "scriptorium.toml").write_text(t.replace('latex = ""', f'latex = "{HERE / "fake_latex.py"}"'))
        self.cfg = C.load(self.tmp)
        self.lit = self.tmp / ".scriptorium" / "lit"

    def tearDown(self):
        os.chdir(self.old)
        for k, v in self.env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(self.tmp, ignore_errors=True)

    def cli(self, *args) -> str:
        buf = StringIO()
        with redirect_stdout(buf):
            try:
                cli.main(list(args))
            except SystemExit as e:
                buf.write(f"\n[exit {e.code}]")
        return buf.getvalue()

    def test_search_reads_alongside_evidence_and_feeds_the_story(self):
        out = self.cli("run", "--pause-at", "story")
        self.assertIn("paused after story", out, out)
        from scriptorium import events
        idx = {(e["ev"], e.get("stage")): i for i, e in enumerate(events.read(self.cfg))}
        self.assertLess(idx[("stage_start", "search")], idx[("stage_done", "evidence")])
        self.assertGreater(idx[("stage_start", "story")], idx[("stage_done", "read")])
        self.assertIn("filters labels", (self.lit / "cards.md").read_text())
        s = state.load(self.cfg)
        self.assertEqual(s["usage"]["read"]["sessions"], 2, "12 papers in batches of 6")

    def test_shortlist_only_from_search_results_and_quotes_from_abstracts(self):
        self.cli("run", "--pause-at", "read")
        d = json.loads((self.lit / "shortlist.json").read_text())
        d["papers"].append({"id": "doi:10.9/invented", "relation": "competing", "why": "w"})
        (self.lit / "shortlist.json").write_text(json.dumps(d))
        self.assertTrue(any("never came back" in e for e in lit.shortlist_problems(self.cfg)))
        c = lit.card_path(self.cfg, "doi:10.0/1")
        card = json.loads(c.read_text())
        card["quotes"] = ["We cure all label noise."]
        c.write_text(json.dumps(card))
        self.assertTrue(any("not in the fetched abstract" in e for e in lit.card_problems(self.cfg, "doi:10.0/1")))

    def test_full_run_checks_every_citation(self):
        out = self.cli("run")
        self.assertIn("all stages done", out, out)
        todo = json.loads((self.lit / "citations_todo.json").read_text())
        self.assertGreater(len(todo), 6)
        self.assertEqual(lit.citecheck_problems(self.cfg), [])
        card = self.cli("cite", "card", "ref0a")
        self.assertIn("doi:10.0/0", card)
        self.assertIn("We filter noisy labels.", card)

    def test_miscitation_must_be_fixed(self):
        os.environ["FAKE_MISCITE"] = "1"
        out = self.cli("run", "--pause-at", "polish")
        self.assertIn("stage polish failed", out, out)
        self.assertIn("unsupported citation of ref0a is unchanged", out)

    def test_unknown_citation_key_names_its_file(self):
        from scriptorium import cite
        (self.tmp / "paper" / "09_discussion.tex").write_text("As before~\\citep{confident_learning}.\n")
        probs = cite.problems(cite.verify(self.tmp))
        self.assertTrue(any(p.startswith("09_discussion.tex cites keys that are not in refs.bib: confident_learning")
                            for p in probs), probs)

    def test_headings_may_use_title_case(self):
        from scriptorium import notation
        (self.tmp / ".scriptorium" / "notation.json").write_text(json.dumps({"terms": [
            {"canonical": "logistic regression", "kind": "baseline", "definition": "d",
             "variants": ["Logistic Regression"]}]}))
        (self.tmp / "paper" / "04_setup.tex").write_text("\\subsection{Logistic Regression}\nWe fit logistic regression.\n")
        (self.tmp / "paper" / "table_main.tex").write_text("Logistic Regression & 1 \\\\\n")
        errs = notation.check_text(self.cfg)
        self.assertEqual(len(errs), 1, errs)
        self.assertIn(".scriptorium/tables/main.json", errs[0])


if __name__ == "__main__":
    unittest.main()
