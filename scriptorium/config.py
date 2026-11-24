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
# Anything left out takes its value from the preset and the venue; any key you set here wins.

[paper]
title = "%(title)s"
authors = [%(authors)s]
affiliation = "%(affiliation)s"
venue = "%(venue)s"           # free text shown to the agents (e.g. "NeurIPS 2026 main track")
conference = "%(conference)s" # the target venue: its recent papers teach the style (cvpr, iccv, neurips, icml, iclr, acl, ...)
template = "%(template)s"     # default | neurips | iclr | icml | cvpr | acl | miccai | ieee | a folder with main.tex
mode = "%(mode)s"             # review (anonymous) or final (camera-ready)
page_limit = %(page_limit)d   # main text pages, references excluded

[run]
preset = "%(preset)s"         # lite (fast, fewest tokens) | standard | max (most agents, strongest models)
parallel = 6                  # agent sessions at the same time
# review_rounds = 1           # revise-and-review rounds after the first review
# reviewers = ["soundness", "clarity", "significance"]
# contest_n = 3               # candidates for the storyline, abstract and introduction
session_timeout_min = 45
check_mode = "feedback"       # PaperAnchor mode for writing sessions: feedback | gate
unset_api_key = false         # true: drop ANTHROPIC_API_KEY so sessions use your Claude login instead of API billing
latex = ""                    # tectonic or latexmk; found on PATH when empty
python = ""                   # interpreter for recipes and figure scripts; the current one when empty

[models]                      # sonnet | opus | haiku | a full model id, per agent; the preset fills the rest
# default = "sonnet"

[venue]
study = true                  # for a top-tier venue, learn from its recent papers on your topic (needs network)
# exemplars = 6               # how many recent papers to study (the preset sets it)

[figures]
theme = "harbor"              # harbor | ink-amber | forest-coral | academia | nature | minimal; see `scriptorium themes`
# critic_rounds = 2           # times a figure critic may send a figure back to its maker

[lock]
ignore = []                   # extra glob patterns the data lock may ignore (e.g. "wandb/**")
'''

TOML_DEFAULTS = {"title": "Working title", "authors": '"First Author"', "affiliation": "Your institution",
                 "venue": "workshop", "template": "default", "mode": "review", "page_limit": 8, "preset": "standard",
                 "conference": ""}

def render_toml(**kw) -> str:
    vals = {**TOML_DEFAULTS, **{k: v for k, v in kw.items() if v not in (None, "")}}
    if isinstance(vals["authors"], list):
        vals["authors"] = ", ".join(f'"{a}"' for a in vals["authors"])
    return DEFAULT_TOML % vals


PRESETS = {
    "lite": {"contest_n": 1, "review_rounds": 0, "critic_rounds": 1, "comprehension": False, "venue_exemplars": 3,
             "reviewers": ["soundness", "clarity"], "models": {"default": "sonnet"}},
    "standard": {"contest_n": 3, "review_rounds": 1, "critic_rounds": 2, "comprehension": True,
                 "models": {"default": "sonnet", "outliner": "opus"}},
    "max": {"contest_n": 3, "review_rounds": 2, "critic_rounds": 3, "comprehension": True, "venue_exemplars": 8,
            "models": {"default": "sonnet", **{r: "opus" for r in ("outliner", "architect", "writer", "editor",
                                                                     "auditor", "cite_auditor", "chair", "reviewer",
                                                                     "reviser", "figure_planner", "diagrammer")}}},
}


ROLES = ("scout", "experimentalist", "evidence", "statistician", "cartographer", "architect", "outliner",
         "terminologist", "searcher", "reader", "librarian", "figure_planner", "plotter", "diagrammer", "figure_critic", "venue_reader", "venue_analyst", "compliance", "proofreader", "layout_inspector", "tablesetter", "writer", "editor", "auditor", "cite_auditor", "line_editor",
         "typesetter", "reviewer", "chair", "reviser")


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
    contest_n: int = 3                    # candidates for the abstract and the introduction (1 turns contests off)
    comprehension: bool = True            # quiz a reader on the compiled paper after editing
    comprehension_min: float = 0.8        # share of discriminative questions the reader must get right
    theme: str = "harbor"                 # figure theme (scriptorium_fig.THEMES)
    mode: str = "review"                  # review (anonymous) or final (camera-ready)
    preset: str = "standard"              # lite | standard | max
    words_per_page: int = 480             # prose budget per page of main text (set by the venue)
    conference: str = ""                  # venue key for the venue study (defaults to the template's venue)
    venue_study: bool = True              # learn from recent papers at a top-tier venue
    venue_exemplars: int = 6              # how many recent papers the readers study
    audit: bool = False                   # an audit folder made by `scriptorium audit`
    audit_main: str = "main.tex"          # the audited paper's main file, relative to src/
    critic_rounds: int = 2                # figure critic rounds

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
    """Preset first, then the venue, then every key the toml sets explicitly."""
    from . import venues
    data = tomllib.loads((root / "scriptorium.toml").read_text())
    p, r, m, lk = data.get("paper", {}), data.get("run", {}), data.get("models", {}), data.get("lock", {})
    fg = data.get("figures", {})
    cfg = Config(root=root.resolve())
    cfg.preset = str(r.get("preset", "standard"))
    if cfg.preset not in PRESETS:
        raise SystemExit(f"scriptorium.toml: preset must be one of {', '.join(PRESETS)}")
    pre = PRESETS[cfg.preset]
    for k in ("contest_n", "review_rounds", "critic_rounds", "comprehension", "reviewers", "venue_exemplars"):
        if k in pre:
            setattr(cfg, k, pre[k])
    cfg.models = dict(pre.get("models", {}))
    for k in ("title", "affiliation", "venue", "template", "mode"):
        if k in p:
            setattr(cfg, k, str(p[k]))
    if cfg.mode not in ("review", "final"):
        raise SystemExit("scriptorium.toml: [paper] mode must be review or final")
    v = venues.VENUES.get(cfg.template)
    if v:
        cfg.page_limit, cfg.words_per_page = v["page_limit"], v["words_per_page"]
        if "reviewers" not in r:
            cfg.reviewers = list(v["reviewers"][:len(cfg.reviewers)] if cfg.preset == "lite" else v["reviewers"])
    cfg.authors = list(p.get("authors", []))
    cfg.page_limit = int(p.get("page_limit", cfg.page_limit))
    cfg.words_per_page = int(p.get("words_per_page", cfg.words_per_page))
    cfg.models.update({k: str(v) for k, v in m.items()})
    for k in ("review_rounds", "parallel", "contest_n", "judge_parallel", "limit_max_retries"):
        if k in r:
            setattr(cfg, k, int(r[k]))
    for k in ("check_mode", "latex", "python"):
        if k in r:
            setattr(cfg, k, str(r[k]))
    if "reviewers" in r:
        cfg.reviewers = list(r["reviewers"])
    for k in ("session_timeout_min", "limit_max_wait_min", "comprehension_min"):
        if k in r:
            setattr(cfg, k, float(r[k]))
    if "comprehension" in r:
        cfg.comprehension = bool(r["comprehension"])
    cfg.unset_api_key = bool(r.get("unset_api_key", False)) or os.environ.get("SCRIPTORIUM_UNSET_API_KEY") == "1"
    cfg.lock_ignore = list(lk.get("ignore", []))
    cfg.theme = str(fg.get("theme", cfg.theme))
    cfg.critic_rounds = int(fg.get("critic_rounds", cfg.critic_rounds))
    cfg.conference = str(p.get("conference", cfg.template if cfg.template not in ("", "default") else ""))
    vs = data.get("venue", {})
    cfg.venue_study = bool(vs.get("study", cfg.venue_study))
    cfg.venue_exemplars = int(vs.get("exemplars", cfg.venue_exemplars))
    cfg.audit = bool(r.get("audit", False))
    cfg.audit_main = str(r.get("audit_main", cfg.audit_main))
    return cfg
