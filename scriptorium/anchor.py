"""Bridge to PaperAnchor, run under the project's interpreter so recipes can import what the research code uses."""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from .config import Config

_NUMBERS = r'''
import json, sys
from pathlib import Path
from paperanchor.sources import parse_sources, run_recipes
root = Path(sys.argv[1]); src = root / "paper" / "sources.py"
recipes, err = parse_sources(src)
if err:
    print(json.dumps({"__module__": {"error": err}})); sys.exit(0)
res = run_recipes(root, src, {k: r.func for k, r in recipes.items()})
out = {}
for k, r in recipes.items():
    x = res.get(k) or res.get("__module__") or {"error": "recipe did not run"}
    out[k] = {"means": r.means, **{kk: x[kk] for kk in ("value", "error", "files") if kk in x}}
print(json.dumps(out))
'''


def package_path() -> str:
    try:
        import paperanchor  # noqa: F401
    except ImportError as e:
        raise SystemExit("scriptorium needs PaperAnchor: pip install git+https://github.com/thanh-huy-nguyen/paperanchor"
                         ) from e
    return str(Path(paperanchor.__file__).resolve().parent.parent)


def env(cfg: Config) -> dict[str, str]:
    """Recipes are agent-written code, so they run inside the jail (see sealing.py)."""
    from .sealing import jail_env
    e = os.environ.copy()
    lib = str(Path(__file__).resolve().parent / "recipelib")
    e["PYTHONPATH"] = os.pathsep.join(p for p in [package_path(), lib, e.get("PYTHONPATH", "")] if p)
    return jail_env(cfg, e)


def cli(cfg: Config, *args: str, capture: bool = True) -> subprocess.CompletedProcess:
    code = "import sys; from paperanchor.cli import main; sys.argv = ['paperanchor'] + sys.argv[1:]; main()"
    return subprocess.run([cfg.py(), "-c", code, *args], cwd=cfg.root, env=env(cfg), text=True,
                          capture_output=capture, timeout=3600)


def init(cfg: Config) -> None:
    r = cli(cfg, "init")
    if r.returncode:
        raise SystemExit("paperanchor init failed: " + (r.stderr or r.stdout))


def check(cfg: Config, *files: str) -> tuple[bool, str]:
    r = cli(cfg, "check", *files)
    return r.returncode == 0, (r.stdout + r.stderr).strip()


def numbers(cfg: Config) -> dict:
    r = subprocess.run([cfg.py(), "-c", _NUMBERS, str(cfg.root)], cwd=cfg.root, env=env(cfg), text=True,
                       capture_output=True, timeout=3600)
    try:
        return json.loads(r.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        return {"__module__": {"error": (r.stderr or r.stdout)[-600:]}}


def numbers_table(nums: dict) -> str:
    rows = ["| key | value | what it is | files read |", "|---|---|---|---|"]
    for k, v in sorted(nums.items()):
        val = v.get("value")
        shown = f"{val:.6g}" if isinstance(val, float) else (repr(val) if val is not None else "ERROR: " + str(v.get("error", ""))[:120])
        files = ", ".join(v.get("files", []) or [])
        rows.append(f"| `{k}` | {shown} | {v.get('means', '')} | {files} |")
    return "\n".join(rows)
