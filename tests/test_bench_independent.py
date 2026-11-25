"""The RepoWrite checker must not share code with the system it scores."""
import ast
import unittest
from pathlib import Path

CHECK = Path(__file__).resolve().parents[1] / "bench" / "repowrite" / "check"


class CheckerIndependence(unittest.TestCase):
    def test_checker_imports_nothing_from_scriptorium_or_paperanchor(self):
        files = sorted(CHECK.glob("*.py"))
        self.assertTrue(files)
        for f in files:
            for node in ast.walk(ast.parse(f.read_text())):
                names = []
                if isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [node.module or ""]
                for n in names:
                    self.assertFalse(n.split(".")[0] in ("scriptorium", "paperanchor", "scriptorium_fig",
                                                         "scriptorium_diagram"), f"{f.name} imports {n}")

    def test_matcher_tells_misattributed_from_supported(self):
        import sys
        sys.path.insert(0, str(CHECK))
        import match
        key = {"quantities": [
            {"id": "a", "value": 0.926, "unit": "fraction", "dataset": "digits", "method": "filter",
             "condition": "noise=0.4", "metric": "test accuracy", "statistic": "mean"},
            {"id": "b", "value": 0.871, "unit": "fraction", "dataset": "cancer", "method": "filter",
             "condition": "noise=0.4", "metric": "test accuracy", "statistic": "mean"}], "setup": []}
        n = {"printed": "92.6\\%", "comparator": "=", "kind": "result", "method": "filter", "condition": "noise=0.4",
             "metric": "test accuracy", "statistic": "mean", "versus": ""}
        self.assertEqual(match.match_number({**n, "dataset": "digits"}, key)["verdict"], "supported")
        self.assertEqual(match.match_number({**n, "dataset": "cancer"}, key)["verdict"], "misattributed")
        self.assertEqual(match.match_number({**n, "dataset": "digits", "printed": "93.6\\%"}, key)["verdict"],
                         "unsupported")
        self.assertEqual(match.tol("1.5\\times10^{-4}"), match.tol("1.5\\times10^{-4}"))
        self.assertLess(match.tol("1.5\\times10^{-4}"), 1e-5)


if __name__ == "__main__":
    unittest.main()
