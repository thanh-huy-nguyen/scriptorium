---
name: write-paper
description: Write a research paper from the current repository with the Scriptorium agent team (scout, experimentalist, evidence, statistician, cartographer, architects, outliner, terminologist, librarian, illustrator, table setter, writers, editor, auditor, line editors, typesetter, reviewers, area chair, reviser). Every number recomputes from the data and every citation is fetched. Use when the user asks to write, draft or regenerate a paper from their repository.
---

# Write a paper with Scriptorium

You are the orchestrator. The `scriptorium` command decides the stages, writes each agent's task, and checks each
stage in code; you start the agents and pass results along. Run everything from the repository root.

## Setup (once)

1. If `scriptorium` is not installed: `pip install git+https://github.com/thanh-huy-nguyen/scriptorium`.
2. If there is no `scriptorium.toml`: run `scriptorium init`, then ask the user to fill in `brief.md` (the idea, the
   claims, where the results live) and the `[paper]` section of `scriptorium.toml` (title, authors, venue, page
   limit). Wait for them.

## Loop

Repeat until `scriptorium next` reports that every stage is done:

1. Run `scriptorium next`. It prints JSON: `{"stage": ..., "tasks": [{"agent", "label", "model", "prompt"}, ...]}`.
2. Start one subagent per task (stages run one at a time here; `scriptorium run` runs independent stages in parallel) with the Agent tool: `subagent_type` is the task's `agent` (for example
   `scriptorium:writer`), `model` is the task's `model`, and the prompt is the task's `prompt`, passed exactly as
   given. Start all tasks of a stage in one message so they run in parallel. A stage with no tasks (the final check)
   needs no agents.
3. When they finish, run `scriptorium done <stage>`. It prints `{"status": ...}`:
   - `done`: go to the next stage.
   - `fix`: it lists new `tasks` with the problems appended. Run them as in step 2, then `scriptorium done <stage>`
     again.
   - `failed`: stop and show the user the `errors`. Do not work around a failed check by editing files yourself.

Tell the user in one line when each stage starts and ends. Do not write paper text yourself; the agents do, and the
checks only cover their work when it goes through the stages.

## At the end

Show the user `.scriptorium/report.md` and point them to `paper/main.pdf`. `scriptorium status` shows every stage.
To redo part of the paper, `scriptorium run --from <stage>` reruns headless, or `scriptorium reset <stage>` and continue this
loop.
