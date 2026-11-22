#!/usr/bin/env python3
"""Hook entry point: `hook.py guard pre` or `hook.py anchor start|pre|post|stop`, with the event JSON on stdin.

guard   In sessions started by `scriptorium run` (SCRIPTORIUM_STAGE is set): file edits only in paper/ and
        .scriptorium/; file reads only inside the repository and never in a sealed location; shell commands only from
        a short read-only list plus `scriptorium`, with every path inside the repository. Python runs only through
        `scriptorium` commands, inside the jail (scriptorium/jail). The data lock is checked after every stage.
anchor  PaperAnchor's hook: every tagged number in paper/*.tex must recompute from the repository's data. Active only
        where paper/sources.py exists.
"""
import json
import os
import sys
from pathlib import Path

EDIT_TOOLS = {"Edit", "MultiEdit", "Write", "NotebookEdit"}


READ_TOOLS = {"Read", "Grep", "Glob", "NotebookRead", "LS"}
SHELL_OK = {"scriptorium", "ls", "wc", "head", "tail", "cat", "grep", "diff", "echo", "sort", "uniq"}
SEALED_WORDS = ("sealed", "judging", "atlas/judges", ".claude/projects", ".claude.json")


def _deny(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                             "permissionDecisionReason": "Scriptorium: " + reason}}))


def _inside(p: Path, base: Path) -> bool:
    return p == base or base in p.parents


def _resolve(target: str, cwd: Path) -> Path:
    p = Path(os.path.expanduser(target))
    return (p if p.is_absolute() else cwd / p).resolve()


def _shell_problem(cmd: str, root: Path, cwd: Path) -> str:
    import shlex
    if any(t in cmd for t in ("$(", "`", "${", "<(", ">(")):
        return "command substitution is not allowed"
    try:
        lex = shlex.shlex(cmd, posix=True, punctuation_chars=";|&<>")
        lex.whitespace_split = True
        toks = list(lex)
    except ValueError as e:
        return f"could not parse the command ({e})"
    expect_cmd, redirect = True, False
    for t in toks:
        if t and set(t) <= set(";|&"):
            expect_cmd = True
            continue
        if t and set(t) <= set("<>"):
            redirect = True
            continue
        low = t.lower()
        if any(w in low for w in SEALED_WORDS):
            return f"'{t}' names a sealed location"
        if expect_cmd:
            if "=" in t and not t.startswith("-"):
                return "setting environment variables is not allowed"
            if os.path.basename(t) not in SHELL_OK:
                return f"'{t}' is not an allowed command (allowed: {', '.join(sorted(SHELL_OK))})"
            expect_cmd = False
            continue
        looks_path = ("/" in t or t.startswith("~") or t.startswith("..")) and not t.startswith("-")
        if looks_path or redirect:
            if t.startswith("/dev/null"):
                redirect = False
                continue
            p = _resolve(t, cwd)
            if not _inside(p, root):
                return f"'{t}' is outside the repository"
            if redirect and not (_inside(p, root / "paper") or _inside(p, root / ".scriptorium")):
                return f"writing to '{t}' is outside paper/ and .scriptorium/"
        redirect = False
    return ""


def guard() -> None:
    if not os.environ.get("SCRIPTORIUM_STAGE"):
        return
    try:
        ev = json.load(sys.stdin)
    except json.JSONDecodeError:
        return
    tool = ev.get("tool_name") or ""
    inp = ev.get("tool_input") or {}
    root = Path(os.environ.get("SCRIPTORIUM_ROOT") or ev.get("cwd") or os.getcwd()).resolve()
    cwd = Path(ev.get("cwd") or root)
    if tool in EDIT_TOOLS:
        target = inp.get("file_path") or inp.get("notebook_path") or ""
        if not target:
            return
        p = _resolve(target, cwd)
        if not (_inside(p, root / "paper") or _inside(p, root / ".scriptorium")):
            _deny(f"{target} is outside paper/ and .scriptorium/. The repository's data and code are read-only for "
                  "the writing agents; write only in paper/ (the paper, its recipes and figure scripts) or "
                  ".scriptorium/ (notes).")
        return
    if tool in READ_TOOLS:
        target = inp.get("file_path") or inp.get("path") or inp.get("notebook_path") or ""
        if not target:
            return
        if any(w in target.lower() for w in SEALED_WORDS):
            _deny(f"{target} is a sealed location.")
            return
        if not _inside(_resolve(target, cwd), root):
            _deny(f"{target} is outside the repository; agents read only inside {root}.")
        return
    if tool == "Bash":
        why = _shell_problem(inp.get("command") or "", root, cwd)
        if why:
            _deny(why + ". Use `scriptorium` commands for recipes, figures, builds and checks.")


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
