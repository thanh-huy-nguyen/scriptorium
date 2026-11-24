"""The specialist stages: setup facts, statistics, notation, the audit and line edits, layout, area chair, packaging."""
import json
import os
import shutil
import tarfile
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from scriptorium import cli, events, notation, state, team
from scriptorium import config as C

from test_pipeline import HERE, make_repo


class TeamTest(unittest.TestCase):
    ENV = ("SCRIPTORIUM_CLAUDE", "PAPERANCHOR_STATE", "FAKE_BAD_VERDICT", "FAKE_LAZY_EDITOR")

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        make_repo(self.tmp)
        self.old = os.getcwd()
        os.chdir(self.tmp)
        self.env = {k: os.environ.get(k) for k in self.ENV}
        os.environ["SCRIPTORIUM_CLAUDE"] = str(HERE / "fake_claude.py")
        os.environ["PAPERANCHOR_STATE"] = str(self.tmp / ".pa_state")
        with redirect_stdout(StringIO()):
            cli.main(["init"])
        t = (self.tmp / "scriptorium.toml").read_text()
        (self.tmp / "scriptorium.toml").write_text(t.replace('latex = ""', f'latex = "{HERE / "fake_latex.py"}"'))
        self.cfg = C.load(self.tmp)
        self.work = self.tmp / ".scriptorium"

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

    def test_full_team_run(self):
        out = self.cli("run")
        self.assertIn("all stages done", out, out)
        s = state.load(self.cfg)
        for name in ("experiments", "stats", "notation", "audit", "polish", "fit", "chair0", "package"):
            self.assertEqual(s["stages"][name]["status"], "done", name)
        self.assertEqual(s["usage"].get("fit", {}).get("sessions", 0), 0, "the typesetter runs only on problems")
        evs = events.read(self.cfg)
        idx = {(e["ev"], e.get("stage")): i for i, e in enumerate(evs)}
        self.assertLess(idx[("stage_start", "evidence")], idx[("stage_done", "experiments")])
        self.assertLess(idx[("stage_start", "notation")], idx[("stage_done", "library")])
        self.assertIn("show the gain", (self.tmp / "paper" / "03_results.tex").read_text())
        self.assertTrue((self.work / "setup.md").exists() and (self.work / "notation.md").exists())
        prompt = json.loads((self.work / "logs" / "revise1" / "revise-1.json").read_text())["prompt"]
        self.assertIn("review0_meta.json", prompt)
        tar = self.work / "dist" / "arxiv.tar.gz"
        with tarfile.open(tar) as t:
            names = t.getnames()
            self.assertIn("./main.tex", names)
            self.assertIn("./figures/fig_acc.pdf", names)
            self.assertNotIn("./main.pdf", names)

    def test_setup_quotes_must_match(self):
        self.cli("run", "--pause-at", "experiments")
        d = json.loads((self.work / "setup.json").read_text())
        d["facts"][0]["quote"] = "lr: 0.5"
        d["facts"][1]["source"] = "../outside.py"
        (self.work / "setup.json").write_text(json.dumps(d))
        errs = team.setup_problems(self.cfg)
        self.assertTrue(any("does not appear in train.py" in e for e in errs), errs)
        self.assertTrue(any("not a file in the repository" in e for e in errs), errs)

    def test_verdict_must_match_p_value(self):
        os.environ["FAKE_BAD_VERDICT"] = "1"
        out = self.cli("run", "--pause-at", "stats")
        self.assertIn("stage stats failed", out, out)
        self.assertIn("but the verdict says 'not significant'", out)

    def test_notation_is_enforced_on_the_text(self):
        self.cli("run", "--pause-at", "notation")
        (self.tmp / "paper" / "02_method.tex").write_text(
            "\\section{Method}\\label{sec:method} OursNet uses XYZ here. Later, ex why zed (XYZ) is defined.\n")
        errs = notation.check_text(self.cfg)
        self.assertTrue(any("'OursNet' appears 1 time(s)" in e for e in errs), errs)
        self.assertTrue(any("'XYZ' is used before it is defined" in e for e in errs), errs)
        (self.tmp / "paper" / "02_method.tex").write_text(
            "\\section{Method}\\label{sec:method} Ours uses ex why zed (XYZ). XYZ helps. \\label{fig:OursNet}\n")
        self.assertEqual(notation.check_text(self.cfg), [])

    def test_unchanged_flagged_sentence_fails_polish(self):
        os.environ["FAKE_LAZY_EDITOR"] = "1"
        out = self.cli("run", "--pause-at", "polish")
        self.assertIn("stage polish failed", out, out)
        self.assertIn("the overclaim sentence is unchanged", out)

    def test_audit_quotes_must_be_in_the_paper(self):
        self.cli("run", "--pause-at", "audit")
        d = json.loads((self.work / "audit.json").read_text())
        d["findings"][0]["quote"] = "A sentence nobody wrote."
        d["findings"][1]["verdict"] = "unsupported"
        (self.work / "audit.json").write_text(json.dumps(d))
        errs = team.audit_problems(self.cfg)
        self.assertTrue(any("quote is not in 03_results.tex" in e for e in errs), errs)
        self.assertTrue(any("needs a concrete `fix`" in e for e in errs), errs)


if __name__ == "__main__":
    unittest.main()
