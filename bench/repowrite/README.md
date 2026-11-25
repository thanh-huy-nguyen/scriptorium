# RepoWrite

A benchmark for papers written by agents, where the truth is known: each task is a research repository with raw
results (or, in notes mode, a PaperWritingBench experimental log), and every number, reference and claim in a
generated paper can be checked against it.

| Folder | What it holds |
|---|---|
| `check/` | The checker. It imports nothing from Scriptorium or PaperAnchor (a test enforces this) and strips Scriptorium's number tags, so every system is scored the same way. |
| `pwb_task.py` | Turns PaperWritingBench papers into notes-mode tasks (sparse idea, experimental log, figures; the key is every number in the log). |
| `LABELING.md` | How the two raters label numbers, citing sentences and claims. |
| `../baselines/` | The single-agent baselines and their prompts. |

A task folder holds `repo/` (what a system sees), `meta.toml` (venue, page limit, split) and `key/` (`make_key.py`
and the `key.json` it writes from the raw results before any system runs). Development and pilot tasks live outside
this repository; test tasks will be released here after the freeze.

## Scoring a paper

```bash
python bench/repowrite/check/report.py --paper RUN/repo/paper --key TASK/key/key.json --out RUN/score
```

The checker asks a model to list every number with the identity the paper gives it (dataset, method, condition,
metric, statistic), then matches in code, identity first:

| Verdict | Meaning |
|---|---|
| supported | a key quantity with that identity has that value at the printed precision |
| derived | it follows from two key quantities (a difference, ratio or relative change) |
| misattributed | the value exists, but under another identity |
| unsupported | no key quantity has the value |
| unclear | no identity given, and the value is too common to place |

It also checks every number a sentence attributes to a table against that table's cells, and resolves every cited
reference in Crossref, OpenAlex and arXiv. Everything not supported, and a tenth of what is, goes to a person.

Requirements: Python 3.11+ with numpy and scipy for the key scripts, and the `claude` command line logged in.
