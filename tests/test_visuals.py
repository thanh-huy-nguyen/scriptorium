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
        self.assertIn("below 7.0 pt", tiny)
        self.assertIn("overlaps", tiny)
        self.assertIn("legend covers", tiny)
        self.assertIn("no value comes from scriptorium_fig.recipe()", tiny)
        wrong = " | ".join(res["wrongours"])
        self.assertIn("not in the accent colour", wrong)
        self.assertIn("reserved for our method", wrong)
        self.assertIn("does not exist", res["missing"][0])

    def test_side_by_side_labels_that_touch_are_flagged_but_stacked_rows_are_not(self):
        (self.work / "numbers.json").write_text(json.dumps({"a": {"value": 1.0}}))
        self.draw("ticks", "import scriptorium_fig as sf\nsf.use()\nfig, ax = sf.figure(1.6)\n"
                           "ax.bar([0, 0.25], [sf.recipe('a'), 1], color=sf.color('B'))\n"
                           "ax.set_xticks([0, 0.25], ['Citation auditor', 'Claim auditor'])\nsf.save(fig, 'ticks')\n")
        self.draw("rows", "import scriptorium_fig as sf\nsf.use()\nfig, ax = sf.figure(3.0, aspect=0.9)\n"
                          "ax.barh(range(20), [sf.recipe('a')] * 20, color=sf.color('B'))\n"
                          "ax.set_yticks(range(20), [f'stage number {i}' for i in range(20)])\nsf.save(fig, 'rows')\n")
        res = figlint.lint(self.cfg, [{"id": "ticks", "kind": "plot"}, {"id": "rows", "kind": "plot"}])
        self.assertTrue(any("overlaps" in x for x in res["ticks"]), res["ticks"])
        self.assertFalse(any("overlaps" in x for x in res["rows"]), res["rows"])

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
        self.draw("spill", "import scriptorium_diagram as sd\nd = sd.canvas('column', height=1.6)\n"
                           "d.box(0.2, 0.2, 0.8, 0.5, '')\nd.text(0.3, 0.45, 'a label far too long for this box', "
                           "ha='left')\nd.save('spill')\n")
        self.assertIn("runs past the edge of the box",
                      " | ".join(figlint.lint(self.cfg, [{"id": "spill", "kind": "diagram"}])["spill"]))

    def test_sentence_case_keeps_names_symbols_and_panel_tags(self):
        sys.path.insert(0, str(RECIPELIB))
        import scriptorium_fig as sf
        cases = {"repository survey": "Repository survey", "a failed check": "A failed check",
                 "(a) what the checks caught": "(a) What the checks caught", "(a)": "(a)",
                 "nnU-Net accuracy": "nnU-Net accuracy", "arXiv papers": "arXiv papers", "p-value": "p-value",
                 "x": "x", "k-fold splits": "k-fold splits", "ms per image": "ms per image",
                 "85 numbers": "85 numbers", "“reads well”": "“Reads well”", "$\\alpha$ rate": "$\\alpha$ rate"}
        for raw, want in cases.items():
            self.assertEqual(sf.sentence(raw), want, raw)

    def test_saved_plot_labels_are_in_sentence_case(self):
        (self.work / "numbers.json").write_text(json.dumps({"a": {"value": 1.0}}))
        self.draw("case", "import scriptorium_fig as sf\nsf.use()\nfig, ax = sf.figure('column')\n"
                          "ax.bar([0, 1], [sf.recipe('a'), 1], color=sf.color('B'), label='cross-entropy')\n"
                          "ax.set_xticks([0, 1], ['label noise', 'nnU-Net'])\nax.set_ylabel('test accuracy (%)')\n"
                          "ax.set_title('(a) accuracy', loc='left')\nsf.legend_above(ax)\nsf.save(fig, 'case')\n")
        texts = {t["text"] for t in json.loads((self.tmp / "paper" / "figures" / "case.layout.json").read_text())
                 ["texts"]}
        for want in ("Label noise", "nnU-Net", "Test accuracy (%)", "(a) Accuracy", "Cross-entropy"):
            self.assertIn(want, texts)

    def test_connected_arrows_share_one_height_and_cards_flag_overflow(self):
        sys.path.insert(0, str(RECIPELIB))
        os.environ["SCRIPTORIUM_ROOT"] = str(self.tmp)
        import scriptorium_diagram as sd
        d = sd.canvas("full", height=2.0)
        shapes = [d.box(0.2, 0.4, 1.0, 0.8), d.box(1.8, 0.2, 1.0, 1.4), d.box(3.4, 0.6, 1.0, 0.7)]
        before = len(d.ax.lines)
        d.flow(shapes)
        ys = {round(y, 4) for ln in d.ax.lines[before:] for y in ln.get_ydata()}
        self.assertEqual(ys, {0.9})                      # the middle of the span all three share (0.6 to 1.2)
        a, b = d.box(0.2, 0.2, 1.0, 0.5), d.box(0.2, 1.2, 1.0, 0.5)
        before = len(d.ax.lines)
        d.connect(a, b)
        xs = {round(x, 4) for ln in d.ax.lines[before:] for x in ln.get_xdata()}
        self.assertEqual(xs, {0.7})                      # stacked: a vertical arrow through the shared width
        d.card(4.6, 0.2, 0.9, 0.3, "Discovery", "scout, experimentalist, analyst, statistician", icon="database")
        self.assertTrue(any("too small for its text" in i for i in d.issues))
        t = d.text(1.0, 1.9, "noisy data")
        self.assertEqual(t.get_text(), "Noisy data")
        self.assertEqual(d.text(1.0, 1.9, "nnU-Net", case=None).get_text(), "nnU-Net")
        os.environ.pop("SCRIPTORIUM_ROOT", None)

    def test_typed_colours_are_refused(self):
        (self.tmp / "paper" / "figures").mkdir(parents=True, exist_ok=True)
        (self.tmp / "paper" / "figures" / "x.py").write_text("PUR = '#4E2A84'\nGRAY = '#9AA0A6'\n")
        from scriptorium.figlint import color_rule
        rule = color_rule(self.cfg, "x")
        self.assertEqual(len(rule), 1)
        self.assertIn("#4E2A84", rule[0])
        self.assertNotIn("#9AA0A6", rule[0])
        self.assertIn("#0B6E79", rule[0], "names the theme's colour")

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

    def test_every_theme_is_colour_blind_safe_and_readable(self):
        import itertools
        import sys
        sys.path.insert(0, str(RECIPELIB))
        import scriptorium_fig as sf
        from scriptorium.figlint import CVD, _rgb, _simulate, contrast, delta_e
        for name, t in sf.THEMES.items():
            cols = [t["ours"], t["partner"]] + t["base"]
            for a, b in itertools.combinations(cols, 2):
                for k in CVD:
                    self.assertGreaterEqual(delta_e(_simulate(_rgb(a), k), _simulate(_rgb(b), k)), 9.5,
                                            f"{name}: {a} vs {b} under {k}")
            for c in cols[:2]:
                self.assertGreaterEqual(contrast(c), 3.0, f"{name}: {c}")

    def test_theme_gallery(self):
        out = self.cli("themes", "--out", str(self.tmp / "gal"))
        self.assertIn("wrote", out, out)
        page = (self.tmp / "gal" / "index.html").read_text()
        for theme in ("harbor", "ink-amber", "forest-coral", "academia", "nature", "minimal"):
            self.assertIn(f"plot_{theme}.png", page)
            self.assertTrue((self.tmp / "gal" / "paper" / "figures" / f"diagram_{theme}.png").exists())


if __name__ == "__main__":
    unittest.main()
