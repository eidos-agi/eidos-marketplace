# SkillOpt

SkillOpt is the Eidos marketplace wrapper for
[microsoft/SkillOpt](https://github.com/microsoft/SkillOpt), a text-space
optimizer that trains reusable natural-language skills for frozen LLM agents
from scored rollouts, bounded edits, validation gates, and deployable
`best_skill.md` artifacts.

This plugin does not vendor the upstream Microsoft source tree. It gives Codex
and Claude Code an installable Eidos entrypoint for deciding when to use
SkillOpt, how to prepare local experiments, and how to turn Tokut-style
token-waste telemetry into skill remediation work.

## What It Owns

- Skill optimization from scored trajectories
- Validation-gated skill edits
- Token-thrashing remediation contracts
- Local upstream bootstrap instructions
- Safe deployment review for generated `best_skill.md` artifacts

## Tokut Bridge

Tokut is the "Token Cut" use case: collect by-the-minute token and tool-run
evidence, identify waste patterns, then use SkillOpt to improve the skill or
runbook that caused the waste.

Good Tokut signals include:

- repeated failed command loops
- repeated file reads with no new hypothesis
- context growth without useful state change
- long planning loops without a proof command
- repeated browser retries on the same blocked page
- duplicated retrieval or search queries

SkillOpt should train the procedure that prevents the waste, not simply shorten
prompts after the fact.

## Bootstrap Upstream

```bash
plugins/skillopt/scripts/skillopt-bootstrap /tmp/skillopt
```

The script clones `https://github.com/microsoft/SkillOpt.git` and checks out
the latest known public release tag used by this marketplace entry.

## Use

Use the bundled skill when a user asks to:

- optimize or evolve an agent skill
- turn rollout evidence into a better skill document
- reduce token spend from agent thrashing
- build a Tokut remediation loop
- evaluate whether a generated `best_skill.md` is safe to deploy

## Boundary

SkillOpt experiments may inspect redacted trajectories, local skills, scorer
outputs, and aggregate token telemetry. Do not include secrets, raw private
messages, account data, customer data, or unrestricted logs in training
artifacts. Stop for review before replacing a live global skill, changing
production agent policy, or deploying a generated skill into an automated
workflow.
