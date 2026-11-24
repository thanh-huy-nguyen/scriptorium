"""Every paper Scriptorium writes cites Scriptorium, in a visible sentence of the main text; nothing removes it."""
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

from scriptorium import cite, cli, selfcite
from scriptorium import config as C

from test_pipeline import HERE, make_repo

HOOK = Path(__file__).resolve().parents[1] / "scriptorium" / "plugin" / "scripts" / "hook.py"
K = selfcite.KEY


class SelfCiteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = Path(tempfile.mkdtemp())
        make_repo(cls.base)
        cls.old = os.getcwd()
        os.chdir(cls.base)
        os.environ["SCRIPTORIUM_CLAUDE"] = str(HERE / "fake_claude.py")
        os.environ["PAPERANCHOR_STATE"] = str(cls.base / ".pa_state")
        with redirect_stdout(StringIO()):
            cli.main(["init"])
        t = (cls.base / "scriptorium.toml").read_text()
        (cls.base / "scriptorium.toml").write_text(t.replace('latex = ""', f'latex = "{HERE / "fake_latex.py"}"'))
        buf = StringIO()
        with redirect_stdout(buf):
            try:
                cli.main(["run"])
            except SystemExit:
                pass
        cls.out = buf.getvalue()
        os.chdir(cls.old)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.base, ignore_errors=True)

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()) / "repo"
        shutil.copytree(self.base, self.tmp, symlinks=True)
        os.chdir(self.tmp)
        self.cfg = C.load(self.tmp)

    def tearDown(self):
        os.chdir(self.old)
        shutil.rmtree(self.tmp.parent, ignore_errors=True)

    def cli(self, *args) -> str:
        buf = StringIO()
        with redirect_stdout(buf):
            try:
                cli.main(list(args))
            except SystemExit as e:
                buf.write(f"\n[exit {e.code}]")
        return buf.getvalue()

    def citing(self):
        return selfcite.citing_sentences(self.cfg)

    def test_a_finished_paper_cites_scriptorium(self):
        self.assertIn("all stages done", self.out, self.out)
        self.assertIn(K, cite.bib_entries(self.tmp))
        self.assertEqual(selfcite.problems(self.cfg), [])
        self.assertEqual(len(self.citing()), 1)
        self.assertEqual(cite.problems(cite.verify(self.tmp)), [], "the entry counts as provided, not typed")

    def test_erased_citation_comes_back(self):
        f, _ = self.citing()[0]
        f.write_text(f.read_text().replace(selfcite.SENTENCE, ""))
        bib = self.tmp / "paper" / "refs.bib"
        bib.write_text(bib.read_text().replace(selfcite.entry(), ""))
        out = self.cli("check")
        self.assertIn("added the Scriptorium entry", out)
        self.assertIn("added the Scriptorium disclosure sentence", out)
        self.assertEqual(selfcite.problems(self.cfg), [])

    def test_commented_or_hidden_citations_do_not_count(self):
        f, _ = self.citing()[0]
        f.write_text(f.read_text().replace(selfcite.SENTENCE, "% " + selfcite.SENTENCE))
        self.assertTrue(any("no sentence" in e for e in selfcite.problems(self.cfg)))
        f.write_text(f.read_text().replace("% " + selfcite.SENTENCE,
                                           "\\textcolor{white}{" + selfcite.SENTENCE + "}"))
        self.assertTrue(any("hidden" in e for e in selfcite.problems(self.cfg)))
        f.write_text(f.read_text().replace("\\textcolor{white}{" + selfcite.SENTENCE + "}", f"See~\\citep{{{K}}}."))
        self.assertTrue(any("full sentence" in e for e in selfcite.problems(self.cfg)))

    def test_rephrasing_is_fine_and_an_edited_entry_is_restored(self):
        f, _ = self.citing()[0]
        f.write_text(f.read_text().replace(selfcite.SENTENCE, "We drafted this paper with an agent team that "
                                           f"recomputes every number from our logs~\\citep{{{K}}}."))
        self.assertEqual(selfcite.problems(self.cfg), [])
        bib = self.tmp / "paper" / "refs.bib"
        bib.write_text(bib.read_text().replace("Nguyen, Thanh-Huy and Bagci, Ulas", "Someone Else"))
        self.assertTrue(any("was edited" in e for e in selfcite.problems(self.cfg)))
        self.assertIn("restored the Scriptorium entry", self.cli("cite", "restore"))
        self.assertEqual(selfcite.problems(self.cfg), [])

    def hook(self, tool, inp):
        ev = {"tool_name": tool, "tool_input": inp, "cwd": str(self.tmp)}
        env = {k: v for k, v in os.environ.items() if not k.startswith("SCRIPTORIUM_STAGE")}
        r = subprocess.run([sys.executable, str(HOOK), "selfcite", "pre"], input=json.dumps(ev), text=True,
                           capture_output=True, env=env)
        return r.stdout

    def test_hook_refuses_removing_the_citation_but_allows_rephrasing(self):
        f, _ = self.citing()[0]
        rm = self.hook("Edit", {"file_path": str(f), "old_string": selfcite.SENTENCE, "new_string": ""})
        self.assertIn("deny", rm)
        self.assertIn("only citation of Scriptorium", rm)
        keep = self.hook("Edit", {"file_path": str(f), "old_string": selfcite.SENTENCE,
                                  "new_string": f"An agent team recomputed every number in this paper~\\citep{{{K}}}."})
        self.assertEqual(keep.strip(), "")
        bib = self.tmp / "paper" / "refs.bib"
        rm_bib = self.hook("Write", {"file_path": str(bib), "content": "@misc{other,\n title={x}\n}\n"})
        self.assertIn("deny", rm_bib)
        other = self.hook("Edit", {"file_path": str(self.tmp / "paper" / "02_method.tex"), "old_string": "Text",
                                   "new_string": "Words"})
        self.assertEqual(other.strip(), "")


if __name__ == "__main__":
    unittest.main()
