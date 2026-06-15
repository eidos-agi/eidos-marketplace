# Audit: skillopt

## 2026-06-11 - Grade: PENDING

- Community Health: PENDING - run foss-forge or the marketplace audit workflow.
- Agentic Quality: PENDING - run Felix plugin doctor and skill checks.
- Engineering: PENDING - verify upstream install/run instructions against a real SkillOpt experiment.
- Notes: Published into eidos-marketplace as a thin wrapper for `https://github.com/microsoft/SkillOpt`; audit must be completed before grading.

## 2026-06-11 - Initial marketplace packet

### Classification

- Marketplace kind: `tool`
- Signals: `single_capability`, `upstream_wrapper`, `ships_skills`
- Primitive: validation-gated optimization of reusable agent skill documents
- Safe boundary: read and optimize redacted rollout evidence only; require review before deploying generated skills into live agent workflows.

### Upstream evidence

- Upstream source: `https://github.com/microsoft/SkillOpt`
- Upstream public release ref: `v0.1.0`
- Upstream release tag object observed by `git ls-remote --tags`: `3a2b6b6b49c0c13a534ab4f3dcaa50f8c9bc84ca`
- Upstream release peeled commit observed by bootstrap checkout: `25da7cb`
- Upstream main HEAD observed by `git ls-remote`: `c1ac570d944ee7f83fc7c4273abfcb4bfdfea392`
- Upstream license shown by GitHub: MIT

### Eidos packet

- Adds Codex and Claude plugin manifests.
- Adds the `use-skillopt` skill for SkillOpt and Tokut workflows.
- Adds a bootstrap script for cloning the upstream Microsoft repo.
- Adds marketplace entries for the Eidos AGI Codex and Claude store indexes.
- Codex visibility before install: `skillopt@eidos-agi (not installed)`.
- Bootstrap smoke: `plugins/skillopt/scripts/skillopt-bootstrap /tmp/eidos-skillopt-smoke` checked out `v0.1.0`.
- Marketplace check: `python3 tools/marketplace_publish.py check skillopt` -> OK.
- Marketplace tests: `python3 -m pytest tests/test_marketplace_publish.py -q` -> `9 passed`.
- Codex install smoke: `codex plugin add skillopt@eidos-agi` -> installed to `/Users/dshanklin/.codex/plugins/cache/eidos-agi/skillopt/0.1.0`.
- Codex installed state: `skillopt@eidos-agi (installed, enabled)`.

### Remaining audit work

- Run a real SkillOpt experiment on an Eidos skill with redacted scored rollouts.
- Record baseline, optimized-skill, and held-out validation scores.
- Add a concrete Tokut cost-reduction example with before/after token waste.
