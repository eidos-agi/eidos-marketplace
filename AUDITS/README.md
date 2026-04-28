# Audits

Per-plugin scorecards against [STANDARD.md](../STANDARD.md). One file per plugin: `<plugin-name>.md`.

Each audit is dated and graded (A–F). Re-audits append; nothing is deleted. The full history is the trust signal — fixes, regressions, and removals all visible.

## File shape

```markdown
# Audit: <plugin-name>

## 2026-04-28 — Grade: A

- Community Health: PASS — LICENSE, README, CHANGELOG, CONTRIBUTING, COC, SECURITY all present
- Agentic Quality: PASS — N tools, all with descriptions; N parameters, all typed
- Engineering: PASS — pyproject.toml complete, 3 deps, hatchling, CI green, OIDC publish
- Notes: <anything else worth recording>

## YYYY-MM-DD — Grade: <letter>

- (next audit)
```

Audits are re-run quarterly (next: 2026-07-28). They are also re-run on demand when a maintainer reports significant changes (new release, breaking change, security update).
