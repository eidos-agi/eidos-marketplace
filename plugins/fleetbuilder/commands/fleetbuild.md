---
description: Run one FleetBuilder cycle — pick the next Fleet task, build it as a team (product/engineer/reviewer), prove it, bank the win, advance. No scoping questions.
allowed-tools: Bash, Read, Edit, Write, Glob, Grep, Task
---

Build Fleet. Invoke the **fleetbuild** skill and run one cycle now — do not ask the user to
scope it (Standing order #1: don't ask, just build).

Argument (optional): a task id / description to build. If empty, pick the next unblocked task
from `.docket/tasks/` (`docket-md task-list --project-id <id>`).

1. Read `.fleetbuilder/learnings.md` and obey its Standing orders + How-he-builds. If missing
   or stale, run `/fleetbuild-learn` first.
2. Follow the fleetbuild skill: orient (product) → build (engineer, ponytail) → verify+antibody
   (reviewer) → bank (hancock commit + `staircase log-win`) → advance.
3. If the staircase buffer is below cadence and a task is unblocked, take the next cycle.

$ARGUMENTS
