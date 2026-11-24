"""Product features: init flags, presets, venues (fetched style files, review and camera-ready modes)."""
import io
import os
import shutil
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from scriptorium import cli, venues
from scriptorium import config as C
from scriptorium import stages as S

from test_pipeline import make_repo


class ProductTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        make_repo(self.tmp)
        self.old = os.getcwd()
        os.chdir(self.tmp)
        self.home = os.environ.get("SCRIPTORIUM_HOME")
        os.environ["SCRIPTORIUM_HOME"] = str(self.tmp / ".home")
        cache = self.tmp / ".home" / "templates"
        cache.mkdir(parents=True)
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("Styles/neurips_2025.sty", "% official style\n")
        (cache / "neurips.zip").write_bytes(buf.getvalue())

    def tearDown(self):
        os.chdir(self.old)
        if self.home is None:
            os.environ.pop("SCRIPTORIUM_HOME", None)
        else:
            os.environ["SCRIPTORIUM_HOME"] = self.home
        shutil.rmtree(self.tmp, ignore_errors=True)

    def init(self, *flags) -> str:
        buf = StringIO()
        with redirect_stdout(buf):
            cli.main(["init", "--yes", *flags])
        return buf.getvalue()

    def test_venue_sets_limits_and_fetches_official_files(self):
        out = self.init("--venue", "neurips", "--title", "A Study", "--authors", "Ada Lovelace, Alan Turing")
        self.assertIn("fetched the official NeurIPS 2025 style files: neurips_2025.sty", out)
        cfg = C.load(self.tmp)
        self.assertEqual((cfg.page_limit, cfg.words_per_page, cfg.mode), (9, 650, "review"))
        self.assertIn("reproducibility", cfg.reviewers)
        self.assertEqual(cfg.authors, ["Ada Lovelace", "Alan Turing"])
        (cfg.work / "outline.json").write_text('{"title": "A Study", "sections": []}')
        S.render_main(cfg)
        tex = (cfg.paper / "main.tex").read_text()
        self.assertIn("\\usepackage[main]{neurips_2025}", tex)
        self.assertIn("Anonymous Authors", tex)
        self.assertNotIn("Ada Lovelace", tex)
        t = (self.tmp / "scriptorium.toml").read_text().replace('mode = "review"', 'mode = "final"')
        (self.tmp / "scriptorium.toml").write_text(t)
        S.render_main(C.load(self.tmp))
        tex = (cfg.paper / "main.tex").read_text()
        self.assertIn("\\usepackage[main, final]{neurips_2025}", tex)
        self.assertIn("Ada Lovelace \\and Alan Turing", tex)

    def test_presets_and_explicit_keys(self):
        self.init("--preset", "lite")
        cfg = C.load(self.tmp)
        self.assertEqual((cfg.contest_n, cfg.review_rounds, cfg.critic_rounds), (1, 0, 1))
        self.assertFalse(any(st.name.startswith("revise") for st in S.pipeline(cfg)))
        t = (self.tmp / "scriptorium.toml").read_text().replace("# review_rounds = 1", "review_rounds = 1")
        (self.tmp / "scriptorium.toml").write_text(t.replace('preset = "lite"', 'preset = "max"'))
        cfg = C.load(self.tmp)
        self.assertEqual(cfg.review_rounds, 1, "an explicit key beats the preset")
        self.assertEqual(cfg.model("writer"), "opus")
        self.assertEqual(cfg.critic_rounds, 3)

    def test_unknown_venue_is_refused(self):
        with self.assertRaises(SystemExit) as e:
            self.init("--venue", "nature-of-things")
        self.assertIn("unknown venue", str(e.exception))

    def test_every_venue_has_a_skeleton_with_placeholders(self):
        for v in venues.VENUES:
            tex = venues.skeleton(v).read_text()
            for ph in ("%%TITLE%%", "%%AUTHORS%%", "%%ABSTRACT%%", "%%BODY%%"):
                self.assertIn(ph, tex, f"{v}: {ph}")
            self.assertIn("\\bibliography{refs}", tex)


if __name__ == "__main__":
    unittest.main()
