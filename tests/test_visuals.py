"""The visuals team: figure plan, makers, lint, the critic loop, the teaser rule and the theme gallery."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from scriptorium import cli, consistency, figlint, state, visuals
from scriptorium import config as C
from scriptorium import stages as S

from test_pipeline import HERE, make_repo

RECIPELIB = Path(__file__).resolve().parents[1] / "scriptorium" / "recipelib"


class VisualsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        make_repo(self.tmp)
        self.old = os.getcwd()
        os.chdir(self.tmp)
        self.env = {k: os.environ.get(k) for k in ("SCRIPTORIUM_CLAUDE", "PAPERANCHOR_STATE", "FAKE_EASY_CRITIC")}
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

    def draw(self, fid: str, code: str) -> None:
        (self.tmp / "paper" / "figures").mkdir(parents=True, exist_ok=True)
        env = dict(os.environ, PYTHONPATH=str(RECIPELIB), SCRIPTORIUM_ROOT=str(self.tmp))
        r = subprocess.run([sys.executable, "-c", code], env=env, cwd=self.tmp, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_critic_loop_sends_a_figure_back_once(self):
        out = self.cli("run", "--pause-at", "critique")
        self.assertIn("paused after critique", out, out)
        s = state.load(self.cfg)
        self.assertEqual(s["stages"]["critique"]["status"], "done")
        self.assertEqual(s["stages"]["critique"].get("errors"), [])
        self.assertTrue((self.work / "figures" / "teaser.critique.r0.json").exists(), "first critique kept")
        self.assertEqual(json.loads((self.work / "figures" / "teaser.critique.json").read_text())["verdict"], "pass")
        logs = sorted(p.name for p in (self.work / "logs" / "critique").glob("*.json"))
        self.assertIn("figure-teaser-revise.json", logs)
        self.assertEqual(self.cli("figlint").count(": ok"), 2)

    def test_lint_catches_planted_defects(self):
        (self.work / "numbers.json").write_text(json.dumps({"a": {"value": 80.0}}))
        self.draw("tiny", "import scriptorium_fig as sf\nsf.use()\nfig, ax = sf.figure('column')\n"
                          "ax.bar([0, 1], [1, 2], color=sf.color('Base'), label='Base')\n"
                          "ax.plot([-0.4, 1.4], [1.0, 1.0], color=sf.color('Line'), label='Line')\n"
                          "ax.set_xlabel('x', fontsize=3)\nax.legend(loc='center left')\n"
                          "ax.text(0.5, 1.5, 'overlap here'); ax.text(0.52, 1.5, 'overlap here too')\n"
                          "sf.save(fig, 'tiny')\n")
        self.draw("wrongours", "import scriptorium_fig as sf\nsf.use()\nfig, ax = sf.figure('column')\n"
                               "ax.bar([0], [sf.recipe('a')], color=sf.color('B'), label='Ours')\n"
                               "ax.bar([1], [sf.recipe('a')], color=sf.palette()['ours'], label='Baseline')\n"
                               "sf.save(fig, 'wrongours')\n")
        res = figlint.lint(self.cfg, [{"id": "tiny", "kind": "plot"}, {"id": "wrongours", "kind": "plot"},
                                      {"id": "missing", "kind": "plot"}])
        tiny = " | ".join(res["tiny"])
        self.assertIn("below 6.2 pt", tiny)
        self.assertIn("overlaps", tiny)
        self.assertIn("legend covers", tiny)
        self.assertIn("no value comes from scriptorium_fig.recipe()", tiny)
        wrong = " | ".join(res["wrongours"])
        self.assertIn("not in the accent colour", wrong)
        self.assertIn("reserved for our method", wrong)
        self.assertIn("does not exist", res["missing"][0])

    def test_clean_diagram_passes_lint(self):
        self.draw("d", "import scriptorium_diagram as sd\nd = sd.canvas('full', height=1.6)\n"
                       "p = d.panel(0.1, 0.1, 3.0, 1.4, 'Annotate a case', step=1)\n"
                       + "".join(f"d.icon('{n}', {0.4 + 0.5 * i:.2f}, 0.6, 0.35)\n" for i, n in
                                 enumerate(['person', 'network', 'monitor', 'images', 'document']))
                       + "d.box(4.0, 0.5, 1.2, 0.5, 'Model', ours=True)\nd.arrow((3.2, 0.75), (3.9, 0.75))\n"
                       "d.save('d')\n")
        self.assertEqual(figlint.lint(self.cfg, [{"id": "d", "kind": "diagram"}])["d"], [])

    def test_kit_flags_diagonal_arrows_and_crowded_titles(self):
        self.draw("bad", "import scriptorium_diagram as sd\nd = sd.canvas('column', height=1.6)\n"
                         "d.panel(0.1, 0.1, 1.0, 1.4, 'A very long panel title here', step=1)\n"
                         "d.arrow((1.2, 1.2), (2.0, 0.4))\nd.save('bad')\n")
        probs = " | ".join(figlint.lint(self.cfg, [{"id": "bad", "kind": "diagram"}])["bad"])
        self.assertIn("is diagonal", probs)
        self.assertIn("runs to the panel's edge", probs)

    def test_outline_needs_one_teaser_and_planned_figures_must_be_included(self):
        self.cli("run", "--pause-at", "outline")
        o = json.loads((self.work / "outline.json").read_text())
        for f in o["figures"]:
            f.pop("teaser", None)
        (self.work / "outline.json").write_text(json.dumps(o))
        self.assertTrue(any("exactly one figure is the teaser" in e for e in S.Outline("outline").validate(self.cfg)))
        (self.tmp / "paper" / "03_results.tex").write_text("\\section{R} Text.\n")
        errs, _ = consistency.check(self.cfg, {})
        self.assertTrue(any("figure fig_acc is planned but never included" in e for e in errs), errs)

    def test_theme_gallery(self):
        out = self.cli("themes", "--out", str(self.tmp / "gal"))
        self.assertIn("wrote", out, out)
        page = (self.tmp / "gal" / "index.html").read_text()
        for theme in ("academia", "nature", "minimal"):
            self.assertIn(f"plot_{theme}.png", page)
            self.assertTrue((self.tmp / "gal" / "paper" / "figures" / f"diagram_{theme}.png").exists())


if __name__ == "__main__":
    unittest.main()
