"""End-to-end tests of the orchestrator with a fake `claude` and a fake LaTeX engine (no model calls, no network)."""
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

from scriptorium import cli, cite, lock, state
from scriptorium import config as C

HERE = Path(__file__).resolve().parent
HOOK = C.PLUGIN_DIR / "scripts" / "hook.py"


def make_repo(d: Path) -> None:
    (d / "results").mkdir()
    rows = [{"method": m, "seed": s, "acc": a} for m, accs in (("ours", [0.91, 0.93, 0.92]), ("base", [0.85, 0.86, 0.84]))
            for s, a in enumerate(accs)]
    (d / "results" / "runs.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    (d / "train.py").write_text("print('train')\n")


class PipelineTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        make_repo(self.tmp)
        self.old = os.getcwd()
        os.chdir(self.tmp)
        self.env = {k: os.environ.get(k) for k in ("SCRIPTORIUM_CLAUDE", "FAKE_TAMPER", "FAKE_REVISE_WORSE",
                                                   "FAKE_BAD_NUMBER", "PAPERANCHOR_STATE")}
        os.environ["SCRIPTORIUM_CLAUDE"] = str(HERE / "fake_claude.py")
        os.environ["PAPERANCHOR_STATE"] = str(self.tmp / ".pa_state")
        with redirect_stdout(StringIO()):
            cli.main(["init"])
        t = (self.tmp / "scriptorium.toml").read_text()
        t = t.replace('latex = ""', f'latex = "{HERE / "fake_latex.py"}"').replace("review_rounds = 1", "review_rounds = 2")
        (self.tmp / "scriptorium.toml").write_text(t)

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

    def test_full_run(self):
        out = self.run_cli("run")
        self.assertIn("all stages done", out, out)
        cfg = C.load(self.tmp)
        s = state.load(cfg)
        self.assertEqual(s["stages"]["final"]["status"], "done")
        self.assertTrue((self.tmp / "paper" / "main.pdf").exists())
        main = (self.tmp / "paper" / "main.tex").read_text()
        self.assertIn("\\input{02_method}", main)
        self.assertLess(main.index("01_intro"), main.index("03_results"))
        self.assertIn("We revised this.", (self.tmp / "paper" / "03_results.tex").read_text())
        self.assertEqual(s["accepted"], "review2")
        self.assertIn("All checks pass", (self.tmp / ".scriptorium" / "report.md").read_text())
        self.assertGreater(s["usage"]["draft"]["sessions"], 1)

    def test_worse_revision_is_rolled_back(self):
        os.environ["FAKE_REVISE_WORSE"] = "1"
        out = self.run_cli("run")
        self.assertIn("all stages done", out, out)
        s = state.load(C.load(self.tmp))
        self.assertNotIn("We revised this.", (self.tmp / "paper" / "03_results.tex").read_text())
        self.assertIn("rolled back", s["decisions"]["revise1"])
        self.assertEqual(s["stages"]["revise2"]["status"], "skipped")
        self.assertEqual(s["accepted"], "review0")

    def test_data_tampering_stops_the_run(self):
        os.environ["FAKE_TAMPER"] = "1"
        out = self.run_cli("run")
        self.assertIn("stage scout failed", out)
        self.assertIn("modified outside paper/: results/runs.jsonl", out)

    def test_wrong_number_is_caught(self):
        os.environ["FAKE_BAD_NUMBER"] = "1"
        out = self.run_cli("run", "--to", "draft")
        self.assertIn("do not recompute", out)
        self.assertIn("stage draft failed", out)

    def test_interactive_next_done(self):
        out = json.loads(self.run_cli("next"))
        self.assertEqual(out["stage"], "scout")
        self.assertEqual(out["tasks"][0]["agent"], "scriptorium:scout")
        res = json.loads(self.run_cli("done", "scout"))
        self.assertEqual(res["status"], "fix")          # nothing was written yet
        self.assertIn("inventory.md", res["errors"][0])


class LockTest(unittest.TestCase):
    def test_created_file_is_quarantined(self):
        d = Path(tempfile.mkdtemp())
        make_repo(d)
        lock.take(d)
        (d / "results" / "new.json").write_text("{}")
        (d / "paper").mkdir()
        (d / "paper" / "x.tex").write_text("ok")
        r = lock.verify(d)
        self.assertEqual(r["created"], ["results/new.json"])
        self.assertFalse((d / "results" / "new.json").exists())
        self.assertTrue((d / ".scriptorium" / "quarantine" / "results" / "new.json").exists())
        shutil.rmtree(d)


class GuardTest(unittest.TestCase):
    def guard(self, path: str, stage: bool = True) -> str:
        env = dict(os.environ, SCRIPTORIUM_ROOT="/repo")
        env.pop("SCRIPTORIUM_STAGE", None)
        if stage:
            env["SCRIPTORIUM_STAGE"] = "draft"
        ev = {"tool_name": "Write", "tool_input": {"file_path": path}, "cwd": "/repo"}
        return subprocess.run([sys.executable, str(HOOK), "guard", "pre"], input=json.dumps(ev), text=True,
                              capture_output=True, env=env).stdout

    def test_guard(self):
        self.assertIn("deny", self.guard("/repo/results/a.json"))
        self.assertIn("deny", self.guard("/repo/paper/../train.py"))
        self.assertEqual(self.guard("/repo/paper/01_intro.tex"), "")
        self.assertEqual(self.guard(".scriptorium/notes.md"), "")
        self.assertEqual(self.guard("/repo/results/a.json", stage=False), "")


class CiteTest(unittest.TestCase):
    def test_parse_and_key(self):
        bib = ("@inproceedings{DBLP:conf/x/Han18,\n  author = {Bo Han and Quanming Yao},\n  title = {Co-teaching: "
               "Robust Training},\n  year = {2018}\n}\n@comment{x}\n@article{k2, title={The {B}est}, author={Doe, J.}, "
               "year={2020}}")
        es = cite.split_entries(bib)
        self.assertEqual(len(es), 2)
        self.assertEqual(cite.make_key(es[0], set()), "han2018coteaching")
        self.assertEqual(cite.make_key(es[1], {"doe2020best"}), "doe2020besta")
        self.assertTrue(cite.rekey(es[0], "han2018coteaching").startswith("@inproceedings{han2018coteaching,"))

    def test_verify_flags_typed_and_edited_entries(self):
        d = Path(tempfile.mkdtemp())
        (d / "paper").mkdir()
        (d / ".scriptorium").mkdir()
        e = "@article{a2020x,\n  title = {X},\n  author = {A, B},\n  year = {2020}\n}"
        (d / "paper" / "refs.bib").write_text(e + "\n@article{typed, title={Y}}\n")
        (d / ".scriptorium" / "citations.json").write_text(json.dumps({"a2020x": {"hash": cite._norm(e)}}))
        (d / "paper" / "s.tex").write_text("\\citep{a2020x, missing} % \\cite{commented}\n")
        r = cite.verify(d)
        self.assertEqual(r["missing"], ["missing"])
        self.assertEqual(r["untracked"], ["typed"])
        self.assertEqual(r["edited"], [])
        shutil.rmtree(d)



class ProseTest(unittest.TestCase):
    def test_val_and_lint(self):
        from scriptorium import lint, stages
        d = Path(tempfile.mkdtemp())
        (d / "paper").mkdir()
        (d / "scriptorium.toml").write_text(C.DEFAULT_TOML)
        (d / "paper" / "a.tex").write_text("We regularise it to \\val[1]{acc}. Analyses & -- \\\\\n% \\val{x}\n")
        cfg = C.load(d)
        probs = stages.val_problems(cfg)
        self.assertEqual(len(probs), 1)
        self.assertIn("\\val{acc}", probs[0])
        flags = lint.lint(d / "paper")
        self.assertTrue(any("British" in f for f in flags))
        self.assertTrue(any("placeholder" in f for f in flags))
        self.assertFalse(any("analys" in f.lower() for f in flags))
        shutil.rmtree(d)


if __name__ == "__main__":
    unittest.main()
