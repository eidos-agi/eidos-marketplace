# FleetBuilder

The **learning work clothes** for building Fleet.

When you say *"build Fleet,"* FleetBuilder just builds Fleet — no scoping questions. It runs one
honest build cycle the way a small team would, and it gets smarter about **your** Fleet over
time by studying your own Claude Code transcripts.

## The team

| Agent | Lens | Job |
|---|---|---|
| `fleet-product` | product | State the value from your chair; reject pretty-but-purposeless features |
| `fleet-engineer` | engineering | Build the laziest change that works (ponytail), grounded in source |
| `fleet-reviewer` | QA / adversarial | Prove it end-to-end with a real artifact; mint an antibody per failure |
| `fleet-historian` | learning | Mine your transcripts → distilled `learnings.md` the team reads each cycle |

## The cycle (`/fleetbuild`)

orient (product) → build (engineer) → verify + antibody (reviewer) → bank
(hancock commit + `staircase log-win`) → advance. Below cadence and a task is unblocked? Keep
going. See `skills/fleetbuild/SKILL.md`.

## The learning (`/fleetbuild-learn`)

`tools/learn.py` reads your raw Claude Code session jsonl for the target repo, extracts what you
actually typed (filtering skill injections, terminal dumps, the auto-titler), and hands it to
`claude -p` (fixed-cost — never the raw API) to distill `.fleetbuilder/learnings.md`:

- **What Fleet he needs** — features/priorities you keep asking for
- **How he builds** — your disciplines (ponytail, prove-it, hancock, version lineage…)
- **Antibodies** — recurring frustrations → the durable check that prevents each recurrence
- **Standing orders** — imperatives the loop obeys every cycle (e.g. *don't ask, just build*)

## Hooks (keep it moving)

- **SessionStart** — injects `learnings.md` so the standing orders are in context.
- **Stop** — advisory nudge: surfaces the staircase cadence + next unblocked task so the loop
  doesn't drift to a stop. Does not trap the session (see `hooks/keep-moving.sh` for the
  opt-in self-driving ceiling).

## Depends on

[staircase](https://github.com/eidos-agi/staircase) (cadence ledger), docket (backlog),
hancock (git gate) — all part of the Eidos build stack.

## Status

v1. Deferred: parallel-team execution is described in the skill but not yet a packaged Workflow
script; the miner's extraction is heuristic (good enough — the distiller is robust). Add the
Workflow and richer transcript signal (resume-resume structured sessions) when they earn it.
