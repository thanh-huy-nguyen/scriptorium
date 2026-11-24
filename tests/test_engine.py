"""The stage graph engine: parallel stages, history and rollback, watch, the HTML report and handoff validation."""
import json
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from scriptorium import cli, events, history, state
from scriptorium import config as C
from scriptorium import stages as S

from test_pipeline import HERE, make_repo


class EngineTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        make_repo(self.tmp)
        self.old = os.getcwd()
        os.chdir(self.tmp)
        self.env = {k: os.environ.get(k) for k in ("SCRIPTORIUM_CLAUDE", "PAPERANCHOR_STATE")}
        os.environ["SCRIPTORIUM_CLAUDE"] = str(HERE / "fake_claude.py")
        os.environ["PAPERANCHOR_STATE"] = str(self.tmp / ".pa_state")
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

    def cli(self, *args) -> str:
        buf = StringIO()
        with redirect_stdout(buf):
            try:
                cli.main(list(args))
            except SystemExit as e:
                buf.write(f"\n[exit {e.code}]")
        return buf.getvalue()

    def test_graph_order_is_topological(self):
        seen = set()
        for st in S.pipeline(self.cfg):
            self.assertTrue(set(st.deps) <= seen, st.name)
            seen.add(st.name)

    def test_independent_stages_run_together(self):
        out = self.cli("run")
        self.assertIn("all stages done", out, out)
        evs = events.read(self.cfg)
        idx = {(e["ev"], e.get("stage")): i for i, e in enumerate(evs)}
        branch = ("notation", "library", "figplan", "tables")
        first_done = min(idx[("stage_done", b)] for b in branch)
        for b in branch:
            self.assertLess(idx[("stage_start", b)], first_done, f"{b} waited for a sibling")
        self.assertGreater(idx[("stage_start", "draft")], max(idx[("stage_done", b)] for b in branch + ("critique",)))
        self.assertEqual(evs[-1]["ev"], "run_end")
        self.assertEqual(evs[-1]["status"], "done")

    def test_history_rollback_and_reset(self):
        self.cli("run")
        stages_logged = [c["stage"] for c in history.log(self.cfg)]
        for name in ("scout", "outline", "draft", "final"):
            self.assertIn(name, stages_logged)
        self.assertIn("outline: accepted", self.cli("history"))
        intro = self.tmp / "paper" / "01_intro.tex"
        self.assertTrue(intro.exists())
        out = self.cli("rollback", "outline")
        self.assertIn("restored to outline", out, out)
        self.assertFalse(intro.exists(), "files written after the outline should be gone")
        self.assertTrue((self.tmp / ".scriptorium" / "outline.json").exists())
        s = state.load(self.cfg)
        self.assertEqual(s["stages"]["outline"]["status"], "done")
        self.assertEqual(s["stages"]["draft"]["status"], "pending")
        self.assertGreater(s["usage"]["draft"]["sessions"], 0, "token use is kept across a rollback")
        out = self.cli("run")
        self.assertIn("all stages done", out, out)
        self.assertTrue(intro.exists())
        # reset touches only the stage and what depends on it
        self.cli("reset", "figures")
        s = state.load(self.cfg)
        self.assertEqual(s["stages"]["figures"]["status"], "pending")
        self.assertEqual(s["stages"]["critique"]["status"], "pending")
        self.assertEqual(s["stages"]["figplan"]["status"], "done")
        self.assertEqual(s["stages"]["draft"]["status"], "pending")
        self.assertEqual(s["stages"]["library"]["status"], "done")
        self.assertEqual(s["stages"]["tables"]["status"], "done")

    def test_pause_at(self):
        out = self.cli("run", "--pause-at", "story")
        self.assertIn("paused after story", out, out)
        s = state.load(self.cfg)
        self.assertEqual(s["stages"]["story"]["status"], "done")
        self.assertNotEqual(s["stages"].get("outline", {}).get("status"), "done")

    def test_watch_and_report(self):
        self.cli("run")
        w = self.cli("watch", "--once")
        self.assertIn("figures", w)
        self.assertIn("output tokens", w)
        self.assertIn("(done)", w)
        page = (self.tmp / ".scriptorium" / "report.html").read_text()
        self.assertIn("All checks pass", page)
        self.assertIn("acc_ours", page)
        self.assertIn("printed at", page)
        self.assertIn("Agent sessions", page)

    def test_validate_handoffs(self):
        self.cli("run", "--pause-at", "outline")
        self.assertIn(": ok", self.cli("validate", ".scriptorium/outline.json"))
        bad = self.tmp / ".scriptorium" / "reviews" / "x_clarity.json"
        bad.parent.mkdir(exist_ok=True)
        bad.write_text(json.dumps({"overall": 12, "weaknesses": [{"issue": "i"}]}))
        out = self.cli("validate", str(bad))
        self.assertIn("[exit 1]", out)
        self.assertIn("overall", out)
        self.assertIn("severity", out)
        self.assertIn("not a handoff file", self.cli("validate", "results/runs.jsonl"))


if __name__ == "__main__":
    unittest.main()
