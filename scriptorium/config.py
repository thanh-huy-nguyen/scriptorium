"""Project configuration: scriptorium.toml at the root of the research repository."""
from __future__ import annotations

import os
import shutil
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

PKG = Path(__file__).resolve().parent
PLUGIN_DIR = PKG / "plugin"
TEMPLATES = PKG / "templates"
WORK = ".scriptorium"          # orchestration state, notes and logs (inside the research repository)
PAPER = "paper"                # the paper itself; PaperAnchor checks paper/*.tex

DEFAULT_TOML = '''# Scriptorium configuration. Edit, then run `scriptorium run`.

[paper]
title = "Working title"
authors = ["First Author", "Second Author"]
affiliation = "Your institution"
venue = "workshop"            # free text, shown to the agents (e.g. "AAAI-27 workshop", "ICML 2027")
page_limit = 8                # main text pages, references excluded
template = "default"          # "default", or a folder holding main.tex with %%SCRIPTORIUM:...%% placeholders

[models]                      # sonnet | opus | haiku | a full model id
default = "sonnet"
outliner = "opus"             # the storyline is the most important decision; give it the strongest model
reviewer = "sonnet"

[run]
review_rounds = 1             # revise-and-review rounds after the first review
reviewers = ["soundness", "clarity", "significance"]
parallel = 4                  # agent sessions run at the same time
session_timeout_min = 45
check_mode = "feedback"       # PaperAnchor mode for writing sessions: feedback | gate
unset_api_key = false         # true: drop ANTHROPIC_API_KEY so sessions use your Claude login instead of API billing
latex = ""                    # tectonic or latexmk; found on PATH when empty
python = ""                   # interpreter for recipes and figure scripts; the current one when empty

[lock]
ignore = []                   # extra glob patterns the data lock may ignore (e.g. "wandb/**")
'''

ROLES = ("scout", "evidence", "outliner", "librarian", "illustrator", "writer", "editor", "reviewer", "reviser")


@dataclass
class Config:
    root: Path
    title: str = "Working title"
    authors: list[str] = field(default_factory=list)
    affiliation: str = ""
    venue: str = "workshop"
    page_limit: int = 8
    template: str = "default"
    models: dict[str, str] = field(default_factory=dict)
    review_rounds: int = 1
    reviewers: list[str] = field(default_factory=lambda: ["soundness", "clarity", "significance"])
    parallel: int = 4
    session_timeout_min: float = 45
    check_mode: str = "feedback"
    unset_api_key: bool = False
    latex: str = ""
    python: str = ""
    lock_ignore: list[str] = field(default_factory=list)
    limit_max_wait_min: float = 360       # longest single wait for a usage-limit reset
    limit_max_retries: int = 12           # usage-limit retries per session before it counts as failed
    judge_parallel: int = 6               # judge sessions at the same time

    def model(self, role: str) -> str:
        return self.models.get(role) or self.models.get("default") or "sonnet"

    @property
    def work(self) -> Path:
        return self.root / WORK

    @property
    def paper(self) -> Path:
        return self.root / PAPER

    def py(self) -> str:
        return self.python or sys.executable

    def latex_engine(self) -> str | None:
        if self.latex:
            return self.latex
        for name in ("tectonic", "latexmk"):
            if shutil.which(name):
                return shutil.which(name)
        return None

    def claude_bin(self) -> str:
        return os.environ.get("SCRIPTORIUM_CLAUDE") or "claude"


def find_root(start: Path | None = None) -> Path | None:
    d = (start or Path.cwd()).resolve()
    for p in [d, *d.parents]:
        if (p / "scriptorium.toml").exists():
            return p
    return None


def load(root: Path) -> Config:
    data = tomllib.loads((root / "scriptorium.toml").read_text())
    p, r, m, lk = data.get("paper", {}), data.get("run", {}), data.get("models", {}), data.get("lock", {})
    cfg = Config(root=root.resolve())
    for k in ("title", "affiliation", "venue", "template"):
        if k in p:
            setattr(cfg, k, str(p[k]))
    cfg.authors = list(p.get("authors", []))
    cfg.page_limit = int(p.get("page_limit", cfg.page_limit))
    cfg.models = {k: str(v) for k, v in m.items()}
    for k in ("review_rounds", "parallel"):
        if k in r:
            setattr(cfg, k, int(r[k]))
    for k in ("check_mode", "latex", "python"):
        if k in r:
            setattr(cfg, k, str(r[k]))
    cfg.reviewers = list(r.get("reviewers", cfg.reviewers))
    cfg.session_timeout_min = float(r.get("session_timeout_min", cfg.session_timeout_min))
    cfg.unset_api_key = bool(r.get("unset_api_key", False)) or os.environ.get("SCRIPTORIUM_UNSET_API_KEY") == "1"
    cfg.lock_ignore = list(lk.get("ignore", []))
    cfg.limit_max_wait_min = float(r.get("limit_max_wait_min", cfg.limit_max_wait_min))
    cfg.limit_max_retries = int(r.get("limit_max_retries", cfg.limit_max_retries))
    cfg.judge_parallel = int(r.get("judge_parallel", cfg.judge_parallel))
    return cfg
