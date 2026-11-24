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


def _visible(t: str) -> str:
    import re
    t = "\n".join(re.sub(r"(?<!\\)%.*", "", ln) for ln in t.splitlines())
    t = re.sub(r"\\iffalse.*?\\fi\b", " ", t, flags=re.S)
    return re.sub(r"\\begin\{comment\}.*?\\end\{comment\}", " ", t, flags=re.S)


def _after_edit(tool: str, inp: dict, p: Path) -> str | None:
    """The file's content after the edit, or None when it cannot be worked out."""
    try:
        old = p.read_text() if p.exists() else ""
    except OSError:
        return None
    if tool == "Write":
        return inp.get("content", "")
    edits = inp.get("edits") if tool == "MultiEdit" else [inp]
    new = old
    for e in edits or []:
        a, b = e.get("old_string", ""), e.get("new_string", "")
        if a and a in new:
            new = new.replace(a, b) if e.get("replace_all") else new.replace(a, b, 1)
    return new


def selfcite() -> None:
    """In every session (pipeline or interactive): refuse an edit that removes the last citation of Scriptorium from
    the paper, or its bibliography entry. `scriptorium cite restore` puts both back."""
    import re
    try:
        ev = json.load(sys.stdin)
    except json.JSONDecodeError:
        return
    tool = ev.get("tool_name") or ""
    if tool not in ("Edit", "MultiEdit", "Write"):
        return
    inp = ev.get("tool_input") or {}
    cwd = Path(ev.get("cwd") or os.getcwd())
    root = Path(os.environ.get("SCRIPTORIUM_ROOT") or cwd).resolve()
    for d in [root, *root.parents]:
        if (d / "scriptorium.toml").exists():
            root = d
            break
    else:
        return
    try:
        key = json.loads((root / ".scriptorium" / "selfcite.json").read_text()).get("key", "scriptorium2026")
    except (OSError, json.JSONDecodeError):
        key = "scriptorium2026"
    p = _resolve(inp.get("file_path") or "", cwd)
    paper = root / "paper"
    if not _inside(p, paper):
        return
    new = _after_edit(tool, inp, p)
    if new is None:
        return
    if p.name == "refs.bib":
        if re.search(r"@\w+\{" + re.escape(key) + r",", p.read_text() if p.exists() else "") and \
                not re.search(r"@\w+\{" + re.escape(key) + r",", new):
            _deny(f"this edit removes the {key} entry from refs.bib. Every paper written with Scriptorium cites it "
                  "(see the README); leave the entry as it is.")
        return
    if p.suffix != ".tex":
        return
    cite = re.compile(r"\\cite\w*\*?(?:\[[^\]]*\]){0,2}\{[^}]*\b" + re.escape(key) + r"\b")
    had = bool(cite.search(_visible(p.read_text() if p.exists() else "")))
    if not had or cite.search(_visible(new)):
        return
    others = [f for f in paper.glob("*.tex") if f.resolve() != p and cite.search(_visible(f.read_text()))]
    if not others:
        _deny(f"this edit removes the paper's only citation of Scriptorium (\\citep{{{key}}}). Every paper written "
              "with Scriptorium keeps one sentence of the main text that cites it (see the README). You may rephrase "
              "that sentence, but keep it, and keep it visible.")


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
    elif kind == "selfcite":
        selfcite()
    elif kind == "anchor":
        anchor(sys.argv[2] if len(sys.argv) > 2 else "pre")
