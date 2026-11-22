"""The data lock: the repository's data and code are read-only for every agent.

`take` records every file outside paper/ and .scriptorium/ when the project starts. After each stage `verify` compares
the tree with that record. A file an agent created outside the paper is moved to .scriptorium/quarantine/ (so no later
recipe can read it as data); a changed or deleted file stops the run, because the paper's numbers would no longer
trace back to the data the user brought.
"""
from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import shutil
from pathlib import Path

from .config import PAPER, WORK

SKIP_DIRS = {".git", "__pycache__", ".ipynb_checkpoints", ".venv", "venv", "node_modules", ".mypy_cache",
             ".pytest_cache", ".ruff_cache", ".claude", ".cache", ".tox", ".eggs"}
SKIP_TOP = {PAPER, WORK}
HASH_LIMIT = 64 * 1024 * 1024


def _digest(p: Path) -> str:
    st = p.stat()
    if st.st_size > HASH_LIMIT:
        return f"size:{st.st_size}:mtime:{int(st.st_mtime)}"
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _ignored(rel: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(rel, pat) for pat in patterns)


def scan(root: Path, ignore: list[str] = ()) -> dict[str, str]:
    out: dict[str, str] = {}
    ignore = list(ignore) + ["*.pyc", "scriptorium.toml", "brief.md"]
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        if rel_dir == ".":
            dirnames[:] = [d for d in dirnames if d not in SKIP_TOP and d not in SKIP_DIRS]
        else:
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.endswith(".egg-info")]
        for fn in filenames:
            rel = os.path.normpath(os.path.join(rel_dir, fn))
            if _ignored(rel, ignore):
                continue
            p = Path(dirpath) / fn
            if p.is_symlink() or not p.is_file():
                continue
            out[rel] = _digest(p)
    return out


def take(root: Path, ignore: list[str] = ()) -> Path:
    path = root / WORK / "lock.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(scan(root, ignore), indent=0, sort_keys=True))
    return path


def verify(root: Path, ignore: list[str] = (), quarantine: bool = True) -> dict[str, list[str]]:
    """Return {"created": [...], "modified": [...], "deleted": [...]}; created files are quarantined."""
    path = root / WORK / "lock.json"
    if not path.exists():
        return {"created": [], "modified": [], "deleted": [], "missing_lock": ["no lock taken"]}
    before = json.loads(path.read_text())
    now = scan(root, ignore)
    created = sorted(set(now) - set(before))
    deleted = sorted(set(before) - set(now))
    modified = sorted(k for k in set(now) & set(before) if now[k] != before[k])
    if quarantine and created:
        q = root / WORK / "quarantine"
        for rel in created:
            dst = q / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(root / rel), str(dst))
    return {"created": created, "modified": modified, "deleted": deleted}
