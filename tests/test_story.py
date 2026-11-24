"""Storytelling rules: numbers in the prose, emphasis where strong papers put it, the framework figure."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scriptorium import config as C
from scriptorium import story


class StoryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "paper").mkdir()
        (self.tmp / ".scriptorium").mkdir()
        (self.tmp / "scriptorium.toml").write_text(C.render_toml())
        self.cfg = C.load(self.tmp)
        self.outline({"figures": [{"id": "overview", "kind": "diagram", "role": "framework"}],
                      "sections": [{"file": "abstract"}, {"file": "01_intro", "figures": ["overview"]},
                                   {"file": "02_related"}, {"file": "05_results"}]})

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def outline(self, o):
        (self.tmp / ".scriptorium" / "outline.json").write_text(json.dumps(o))

    def w(self, name, text):
        (self.tmp / "paper" / f"{name}.tex").write_text(text)

    def good(self):
        self.w("abstract", "We study filters. \\emph{Disagreement finds flips.} It reaches 92\\%\\src{a}.")
        self.w("01_intro", "\\section{Introduction}\nNoise hurts (Figure~\\ref{fig:overview}).\n\n"
                           "\\begin{itemize}\n\\item \\textbf{A measurement.} We measure it.\n"
                           "\\item \\textbf{A filter.} We revisit it.\n\\end{itemize}\n")
        self.w("02_related", "\\section{Related work}\n\\paragraph{Noisy labels.} " + "Prior work filters. " * 10 + "\n")
        self.w("05_results", "\\section{Results}\nThe filter wins most at high noise, 9.0\\src{g} points "
                             "(Table~\\ref{tab:t}).\n\n\\begin{table}[t]\\begin{tabular}{l}1\\src{a} 2\\src{b} "
                             "3\\src{c}\\end{tabular}\\end{table}\n")

    def test_a_well_told_paper_passes(self):
        self.good()
        self.assertEqual(story.problems(self.cfg), [])
        self.assertEqual(story.framework_problems(self.cfg), [])

    def test_numbers_belong_in_tables(self):
        self.good()
        self.w("05_results", "\\section{Results}\nX gets 1\\src{a}, Y gets 2\\src{b}, Z gets 3\\src{c}.\n")
        self.w("02_related", "\\section{Related}\n\\paragraph{A.} " + "Work. " * 30 + " It reached 5\\src{d}.\n")
        errs = " | ".join(story.number_problems(self.cfg))
        self.assertIn("05_results.tex: paragraph 1", errs)
        self.assertIn("related work carries none", errs)

    def test_emphasis_rules(self):
        self.good()
        self.w("01_intro", "\\section{Introduction}\nWe \\textbf{really} \\textbf{truly} \\textbf{do} it.\n\n"
                           "\\begin{itemize}\n\\item We measure it.\n\\end{itemize}\n")
        self.w("abstract", "We study filters.")
        self.w("02_related", "\\section{Related work}\n" + "Prior work filters noisy labels. " * 10 + "\n")
        errs = " | ".join(story.emphasis_problems(self.cfg))
        self.assertIn("contribution 1 should open with a bold lead-in", errs)
        self.assertIn("central claim, once, in italics", errs)
        self.assertIn("bold run-in head", errs)
        self.assertIn("3 bold phrases in running text", errs)

    def test_framework_figure_is_required_and_presented(self):
        self.good()
        self.outline({"figures": [{"id": "plot", "kind": "plot"}], "sections": [{"file": "01_intro"}]})
        self.assertIn("framework figure", story.framework_problems(self.cfg)[0])
        self.outline({"figures": [{"id": "overview", "kind": "diagram", "role": "framework"}],
                      "sections": [{"file": "01_intro"}]})
        self.w("01_intro", "\\section{Introduction}\nNo figure here.\n")
        self.assertTrue(story.framework_ref_problems(self.cfg))


if __name__ == "__main__":
    unittest.main()
