"""Proofreading polishes without rewriting; page inspection routes layout problems to their owners."""
import json
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from scriptorium import cli, proof, state
from scriptorium import config as C

from test_pipeline import HERE, make_repo


class ProofTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        make_repo(self.tmp)
        self.old = os.getcwd()
        os.chdir(self.tmp)
        self.env = {k: os.environ.get(k) for k in ("SCRIPTORIUM_CLAUDE", "PAPERANCHOR_STATE", "FAKE_REWRITE",
                                                   "FAKE_LATEX_PYTHON")}
        os.environ["SCRIPTORIUM_CLAUDE"] = str(HERE / "fake_claude.py")
        os.environ["PAPERANCHOR_STATE"] = str(self.tmp / ".pa_state")
        os.environ["FAKE_LATEX_PYTHON"] = sys.executable
        with redirect_stdout(StringIO()):
            cli.main(["init"])
        t = (self.tmp / "scriptorium.toml").read_text()
        (self.tmp / "scriptorium.toml").write_text(t.replace('latex = ""', f'latex = "{HERE / "fake_latex.py"}"'))
        self.cfg = C.load(self.tmp)

    def tearDown(self):
        os.chdir(self.old)
        for k, v in self.env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_cli(self, *args) -> str:
        buf = StringIO()
        with redirect_stdout(buf):
            try:
                cli.main(list(args))
            except SystemExit as e:
                buf.write(f"\n[exit {e.code}]")
        return buf.getvalue()

    def test_proofread_then_inspect_with_a_layout_fix(self):
        out = self.run_cli("run")
        self.assertIn("all stages done", out, out)
        s = state.load(self.cfg)
        self.assertEqual(s["stages"]["proofread"]["status"], "done")
        self.assertIn("Text text", (self.tmp / "paper" / "02_method.tex").read_text())
        self.assertTrue((self.tmp / ".scriptorium" / "proof" / "02_method.md").exists())
        self.assertTrue(list((self.tmp / ".scriptorium" / "proof" / "pages").glob("page-*.png")))
        self.assertTrue((self.tmp / ".scriptorium" / "proof" / "layout.r0.json").exists(), "first inspection kept")
        self.assertEqual(json.loads((self.tmp / ".scriptorium" / "proof" / "layout.json").read_text())["verdict"],
                         "pass")
        logs = {p.name for p in (self.tmp / ".scriptorium" / "logs" / "inspect").glob("*.json")}
        self.assertIn("figure-fig_acc-layout.json", logs, "the figure went back to its maker")
        self.assertIn("layout-caption-fig_acc.json", logs, "and its caption to the section's line editor")

    def test_a_rewrite_is_refused_and_rolled_back(self):
        os.environ["FAKE_REWRITE"] = "1"
        out = self.run_cli("run", "--pause-at", "proofread")
        self.assertIn("changed", out)
        self.assertNotIn("Completely different words", (self.tmp / "paper" / "02_method.tex").read_text())

    def test_change_ratio(self):
        self.assertLess(proof.change_ratio("a b c d e f g h", "a b c d e f g x"), 0.25)
        self.assertGreater(proof.change_ratio("a b c d", "w x y z"), 0.9)


if __name__ == "__main__":
    unittest.main()
