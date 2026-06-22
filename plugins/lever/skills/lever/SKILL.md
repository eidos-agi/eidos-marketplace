---
name: lever
description: Use when the user asks for Lever, leverage analysis, leverage AI, self-learning leverage reviews, agent-building decisions, bottleneck diagnosis, or whether work should become a reusable agent or system.
---

# Lever

Use the live Lever CLI for leverage framing, durable learning, and agent-build
decisions.

Prefer `lever` on `PATH`. If unavailable in this local environment, use:

```bash
/Users/dshanklin/repos-personal/lever/.venv/bin/lever doctor
/Users/dshanklin/repos-personal/lever/.venv/bin/lever manifesto
/Users/dshanklin/repos-personal/lever/.venv/bin/lever score "turn repeated triage into a bounded agent" --leverage-type automation --constraint "manual routing consumes founder attention" --compounding 5 --reversibility 4 --control 4 --optionality 4
/Users/dshanklin/repos-personal/lever/.venv/bin/lever agent-build "recurring inbox triage" --role "Inbox leverage scout" --repeatability 5 --boundedness 4 --proof-loop 5 --memory-fit 4 --refusal-boundary 4 --approval-risk medium
/Users/dshanklin/repos-personal/lever/.venv/bin/lever review --focus "current bottleneck"
/Users/dshanklin/repos-personal/lever/.venv/bin/lever agent "describe the work" --leverage-type optionality
/Users/dshanklin/repos-personal/lever/.venv/bin/lever learn "durable correction" --source "human correction" --evidence "short evidence" --leverage-type decision --confidence high
/Users/dshanklin/repos-personal/lever/.venv/bin/lever lessons --limit 5
/Users/dshanklin/repos-personal/lever/.venv/bin/lever distill --limit 20
/Users/dshanklin/repos-personal/lever/.venv/bin/lever improve --focus "Lever itself" --limit 20
```

Lever is not a generic productivity assistant. It identifies the active
constraint and decides whether the highest-leverage response is an answer,
artifact, reusable system, specialist agent, or durable lesson.

Lever's posture is intentionally sharp: find the constraint, build the reusable
thing, kill weak loops, upgrade proven loops, and record the durable lesson.

Use `lever score` or `lever prioritize` when there is a real resource-allocation
choice. It scores compounding, reversibility, control, and optionality, then
returns a kill/test/upgrade decision.

Use `lever agent-build` when deciding whether repeated work should become a
specialist agent. It scores repeatability, boundedness, proof loop, memory fit,
and refusal boundary, then returns `do-not-build`, `prototype`, or
`build-specialist`.

Treat `lever learn` as an explicit learning action. Use it when the human
corrects the frame or when verified outcomes show a durable leverage principle.
Do not silently store secrets, credentials, payment details, private messages,
or weak one-off inferences.

Use `lever distill` after several explicit lessons have accumulated. It
summarizes the learning log into operating takeaways; it does not mutate hidden
preferences or cross approval gates.

Use `lever improve` when the user asks to improve Lever or when distilled
lessons should become a concrete hardening backlog. Treat its output as a plan:
make a code, docs, tests, score-threshold, or task-state change before claiming
Lever improved.

Keep this plugin thin. Source-owned behavior and durable learning state belong
in the canonical Lever CLI repo.
