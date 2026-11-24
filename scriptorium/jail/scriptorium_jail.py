"""Scriptorium's Python jail. Every Python process an agent session starts loads it (the session puts this folder first
on PYTHONPATH, where sitecustomize.py imports it), and PaperAnchor's isolated recipe runner preloads it through
PAPERANCHOR_PRELOAD. Active only when SCRIPTORIUM_JAIL_ROOT is set.

It refuses, through a sys.addaudithook hook:
- opening or listing anything under the sealed folders (judge prompts, verdicts) or Claude's own transcripts;
- writing anywhere outside the research repository, the temp folder and plotting caches;
- starting any program other than Python and the LaTeX and PDF tools.

This stops an agent's recipe or figure script from reading what the judges see. It is not a defense against code
written to escape it (ctypes, for example); the canary scan after each stage catches what this misses.
"""
import os
import sys


def _install():
    root = os.environ.get("SCRIPTORIUM_JAIL_ROOT")
    if not root:
        return
    real = os.path.realpath
    root = real(root)
    home = os.path.expanduser("~")
    sh = os.environ.get("SCRIPTORIUM_HOME") or os.path.join(home, ".scriptorium")
    here = os.path.dirname(real(__file__))  # scriptorium/jail
    deny = [real(os.path.join(sh, "sealed")), real(os.path.join(os.path.dirname(here), "judging")),
            real(os.path.join(home, ".claude", "projects")), real(os.path.join(home, ".claude.json")),
            real(os.path.join(root, ".scriptorium", "atlas", "judges"))]
    write_ok = [root, real("/tmp"), real(os.environ.get("TMPDIR", "/tmp")), "/dev/null", "/dev/shm",
                real(os.path.join(home, ".cache")), real(os.path.join(home, ".config", "matplotlib")),
                real(os.path.join(home, ".matplotlib"))]
    prog_ok = ("python", "tectonic", "latexmk", "pdflatex", "xelatex", "lualatex", "bibtex", "biber", "pdfinfo",
               "pdftotext", "pdftoppm", "kpsewhich", "claude-noop")

    def under(p, bases):
        return any(p == b or p.startswith(b.rstrip(os.sep) + os.sep) for b in bases)

    def path_of(x):
        if isinstance(x, int):
            return None
        try:
            return real(os.fsdecode(x))
        except (TypeError, ValueError):
            return None

    def refuse(what):
        raise PermissionError(f"Scriptorium jail: {what} is not allowed in a writing session")

    def hook(event, args):
        if event == "open":
            p = path_of(args[0])
            if p is None:
                return
            if under(p, deny):
                refuse(f"reading {p}")
            mode, flags = args[1], args[2] if len(args) > 2 else 0
            writing = (isinstance(mode, str) and any(c in mode for c in "wax+")) or (
                isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND))
            if writing and not under(p, write_ok):
                refuse(f"writing {p}")
        elif event in ("os.listdir", "os.scandir", "os.chdir", "os.remove", "os.rename", "os.rmdir", "shutil.rmtree",
                       "shutil.copyfile", "os.symlink", "os.link"):
            for a in args:
                p = path_of(a) if isinstance(a, (str, bytes, os.PathLike)) else None
                if p and under(p, deny):
                    refuse(f"{event} on {p}")
        elif event in ("subprocess.Popen", "os.exec", "os.posix_spawn", "os.spawn", "os.system"):
            exe = args[0] if event != "os.system" else "sh"
            name = os.path.basename(os.fsdecode(exe)) if isinstance(exe, (str, bytes, os.PathLike)) else ""
            if event == "subprocess.Popen" and not name and args[1]:
                a1 = args[1]
                first = a1[0] if isinstance(a1, (list, tuple)) and a1 else a1
                name = os.path.basename(os.fsdecode(first)) if isinstance(first, (str, bytes)) else ""
            if not any(name.startswith(ok) for ok in prog_ok):
                refuse(f"starting {name or exe!r}")

    sys.addaudithook(hook)


_install()
