#!/usr/bin/env python3
"""Hook entry point: `hook.py guard pre` or `hook.py anchor start|pre|post|stop`, with the event JSON on stdin.

guard   In sessions started by `scriptorium run` (SCRIPTORIUM_STAGE is set), refuse file edits outside paper/ and
        .scriptorium/. The repository's data and code stay as the authors left them. Shell commands are covered by the
        data lock, which the orchestrator checks after every stage.
anchor  PaperAnchor's hook: every tagged number in paper/*.tex must recompute from the repository's data. Active only
        where paper/sources.py exists.
"""
import json
import os
import sys
from pathlib import Path

EDIT_TOOLS = {"Edit", "MultiEdit", "Write", "NotebookEdit"}


def guard() -> None:
    if not os.environ.get("SCRIPTORIUM_STAGE"):
        return
    try:
        ev = json.load(sys.stdin)
    except json.JSONDecodeError:
        return
    if ev.get("tool_name") not in EDIT_TOOLS:
        return
    inp = ev.get("tool_input") or {}
    target = inp.get("file_path") or inp.get("notebook_path") or ""
    if not target:
        return
    root = Path(os.environ.get("SCRIPTORIUM_ROOT") or ev.get("cwd") or os.getcwd()).resolve()
    p = Path(target)
    p = (p if p.is_absolute() else Path(ev.get("cwd") or root) / p).resolve()
    for ok in (root / "paper", root / ".scriptorium"):
        if p == ok or ok in p.parents:
            return
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse", "permissionDecision": "deny",
        "permissionDecisionReason": (f"Scriptorium: {target} is outside paper/ and .scriptorium/. The repository's data "
                                     "and code are read-only for the writing agents; write only in paper/ (the paper, "
                                     "its recipes and figure scripts) or .scriptorium/ (notes).")}}))


def anchor(event: str) -> None:
    pa = os.environ.get("SCRIPTORIUM_PAPERANCHOR")
    if pa:
        sys.path.insert(0, pa)
    try:
        from paperanchor.hook import main
    except ImportError:
        if event == "start" and (Path.cwd() / "paper" / "sources.py").exists():
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": (
                "Scriptorium could not import PaperAnchor, so numbers in paper/*.tex are not checked at each edit. "
                "Install it with: pip install git+https://github.com/thanh-huy-nguyen/paperanchor")}}))
        return
    if os.environ.get("CLAUDE_PLUGIN_OPTION_MODE") and not os.environ.get("PAPERANCHOR_MODE"):
        os.environ["PAPERANCHOR_MODE"] = os.environ["CLAUDE_PLUGIN_OPTION_MODE"]
    sys.argv = ["paperanchor", event]
    main()


if __name__ == "__main__":
    kind = sys.argv[1] if len(sys.argv) > 1 else ""
    if kind == "guard":
        guard()
    elif kind == "anchor":
        anchor(sys.argv[2] if len(sys.argv) > 2 else "pre")
