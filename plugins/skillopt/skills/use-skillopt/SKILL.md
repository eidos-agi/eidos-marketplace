---
name: use-skillopt
description: Use when the user wants Microsoft SkillOpt, self-evolving agent skills, skill optimization from rollouts, validation-gated skill edits, token-cost reduction, thrashing detection, or Tokut/Token Cut remediation.
---

# Use SkillOpt

SkillOpt trains a natural-language skill document as the external state of a
frozen agent. Use it when the work has scored rollout evidence and the output
should be a reusable `best_skill.md`, not a one-off prompt rewrite.

## Start With A Training Contract

Before running an optimization loop, identify:

- target skill path
- task corpus or rollout batch
- scoring function
- train and validation split
- allowed edit budget
- deployment target
- rollback path

If any of these are missing, create the contract first. Do not treat vague
"make this better" feedback as enough evidence for SkillOpt.

## Tokut: Token Cut Workflow

For Tokut-style cost reduction, turn token telemetry into scored rollout
evidence. Look for:

- repeated tool calls with unchanged inputs
- retry loops after the same verifier failure
- repeated file reads or searches with no new state
- context growth without a concrete proof command
- long planning loops with no execution
- duplicate browser or API attempts against the same blocker

Score the runs on both task success and waste reduction. The optimized skill
should prevent the repeated behavior, preserve successful behavior, and make
the next run cheaper without hiding required verification.

## Bootstrap Upstream

Use the bundled bootstrap script when the upstream Microsoft repo is not
already present:

```bash
plugins/skillopt/scripts/skillopt-bootstrap /tmp/skillopt
```

The script clones `https://github.com/microsoft/SkillOpt.git` and checks out
the release ref configured by `SKILLOPT_REF`, defaulting to `v0.1.0`.

## Run Discipline

1. Redact trajectories before optimization.
2. Keep train and validation data separate.
3. Accept skill edits only through a validation gate.
4. Preserve rejected edit notes when they explain real failures.
5. Compare against the no-skill and current-skill baselines.
6. Review the final `best_skill.md` as code before deployment.

## Deliverables

A useful SkillOpt run should end with:

- generated `best_skill.md`
- validation result and baseline comparison
- concise diff against the prior skill
- token-waste before/after summary when Tokut is in scope
- deployment and rollback instructions

## Safety Boundary

Do not put secrets, private messages, customer data, account data, raw browser
sessions, or unrestricted logs into SkillOpt datasets. Stop before replacing a
live global skill, changing production agent policy, or enabling an automated
remediation loop unless the user explicitly approves that deployment.
