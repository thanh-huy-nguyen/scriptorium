"""Venue study (offline: the proceedings index, citations and PDFs are stood in for) and venue requirements."""
import io
import json
import os
import shutil
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from scriptorium import cli, state, venuestudy as V
from scriptorium import config as C

from test_pipeline import HERE, make_repo


def tiny_pdf(text: str) -> bytes:
    import pymupdf
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_textbox(pymupdf.Rect(50, 50, 550, 800), text, fontsize=10)
    return doc.tobytes()


class VenueTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        make_repo(self.tmp)
        (self.tmp / "brief.md").write_text("# Brief\n## Working title\nFiltering noisy labels\n## The idea in one "
                                           "paragraph\nDrop samples whose out-of-fold prediction disagrees with the "
                                           "noisy label.\n")
        self.old = os.getcwd()
        os.chdir(self.tmp)
        self.env = {k: os.environ.get(k) for k in ("SCRIPTORIUM_CLAUDE", "PAPERANCHOR_STATE", "SCRIPTORIUM_HOME")}
        os.environ["SCRIPTORIUM_CLAUDE"] = str(HERE / "fake_claude.py")
        os.environ["PAPERANCHOR_STATE"] = str(self.tmp / ".pa_state")
        os.environ["SCRIPTORIUM_HOME"] = str(self.tmp / ".home")
        self.saved = (V.recent_years, V.citations, V._get)
        papers = [{"title": t, "pdf": f"https://example.org/{i}.pdf"} for i, t in enumerate(
            ["Learning with Noisy Labels by Sample Selection", "Filtering Noisy Labels with Disagreement",
             "A Study of Label Noise in Filtering", "Unrelated Diffusion Rendering of Scenes"] + [f"Other paper {i}"
                                                                                                for i in range(60)])]
        V.recent_years = lambda venue, n=2: [(2025, papers)]
        V.citations = lambda title: (10, "")
        V._get = lambda url, binary=False, timeout=90: tiny_pdf(
            "We study noisy labels in depth here. Our filter drops samples that disagree. It recovers accuracy well "
            "today. Figure one shows the whole idea.")

    def tearDown(self):
        V.recent_years, V.citations, V._get = self.saved
        os.chdir(self.old)
        for k, v in self.env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(self.tmp, ignore_errors=True)

    def init(self, *flags):
        with redirect_stdout(StringIO()):
            cli.main(["init", "--yes", *flags])
        t = (self.tmp / "scriptorium.toml").read_text()
        (self.tmp / "scriptorium.toml").write_text(t.replace('latex = ""', f'latex = "{HERE / "fake_latex.py"}"'))
        return C.load(self.tmp)

    def run_cli(self, *args) -> str:
        buf = StringIO()
        with redirect_stdout(buf):
            try:
                cli.main(list(args))
            except SystemExit as e:
                buf.write(f"\n[exit {e.code}]")
        return buf.getvalue()

    def test_study_picks_relevant_exemplars_and_writes_a_playbook(self):
        cfg = self.init("--venue", "iccv")
        self.assertEqual(cfg.conference, "iccv")
        out = self.run_cli("run", "--pause-at", "venuestyle")
        self.assertIn("paused after venuestyle", out, out)
        ex = V.exemplars(cfg)
        titles = [e["title"] for e in ex]
        self.assertIn("Filtering Noisy Labels with Disagreement", titles)
        self.assertNotIn("Unrelated Diffusion Rendering of Scenes", titles)
        self.assertTrue(all((self.tmp / e["file"]).exists() for e in ex))
        self.assertEqual(V.VenueStyle("venuestyle").validate(cfg), [])
        self.assertIn("venue_style.md", json.loads((self.tmp / ".scriptorium" / "logs" / "outline" /
                                                     "outline.json").read_text())["prompt"]
                      if (self.tmp / ".scriptorium" / "logs" / "outline").exists() else "venue_style.md")

    def test_invented_quotes_are_rejected(self):
        cfg = self.init("--venue", "iccv")
        self.run_cli("run", "--pause-at", "venueread")
        ex = V.exemplars(cfg)[0]
        p = self.tmp / ".scriptorium" / "venue" / "notes" / f"{ex['id']}.json"
        d = json.loads(p.read_text())
        d["quotes"].append("A sentence this paper never wrote.")
        p.write_text(json.dumps(d))
        self.assertTrue(any("not in the paper" in e for e in V.note_problems(cfg, ex)))

    def test_no_study_for_other_venues(self):
        cfg = self.init()
        self.assertFalse(V.studied(cfg))
        out = self.run_cli("run", "--pause-at", "venuestyle")
        self.assertIn("paused after venuestyle", out)
        self.assertEqual(state.load(cfg)["usage"].get("venueread", {}).get("sessions", 0), 0)

    def test_neurips_checklist_and_acl_limitations(self):
        cache = self.tmp / ".home" / "templates"
        cache.mkdir(parents=True)
        sample = ("\\documentclass{article}\\begin{document}x\n\\section*{NeurIPS Paper Checklist}\n"
                  "%%% BEGIN INSTRUCTIONS %%%\nDelete me\n%%% END INSTRUCTIONS %%%\n\\begin{enumerate}\n"
                  "\\item {\\bf Claims}\n\\item[] Answer: \\answerTODO{}\n\\item[] Justification: "
                  "\\justificationTODO{}\n\\end{enumerate}\n\\end{document}\n")
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("Styles/neurips_2025.sty", "\\newcommand{\\answerYes}[1][]{[Yes]}\n")
            z.writestr("Styles/neurips_2025.tex", sample)
        (cache / "neurips.zip").write_bytes(buf.getvalue())
        cfg = self.init("--venue", "neurips")
        ck = self.tmp / "paper" / "checklist.tex"
        self.assertTrue(ck.exists())
        self.assertNotIn("Delete me", ck.read_text())
        self.assertTrue(any("TODO" in e for e in V.requirement_problems(cfg)))
        ck.write_text(ck.read_text().replace("\\answerTODO{}", "\\answerYes{}").replace("\\justificationTODO{}", "ok"))
        self.assertEqual(V.requirement_problems(cfg), [])
        shutil.rmtree(self.tmp / "paper")
        (self.tmp / "scriptorium.toml").unlink()
        (self.tmp / "paper").mkdir()
        cfg = self.init("--venue", "emnlp")
        self.assertEqual((cfg.template, cfg.conference), ("acl", "emnlp"))
        self.assertTrue(any("Limitations" in e for e in V.requirement_problems(cfg)))


if __name__ == "__main__":
    unittest.main()
