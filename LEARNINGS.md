# Learnings

Friction, regressions, and surprises encountered while running the marketplace. Append-only. The format is intentionally lightweight — capture the lesson, not the ceremony.

## Format

```markdown
## YYYY-MM-DD — <one-line summary>

**Context**: what was being done
**What surprised**: the unexpected
**Why it matters**: implication for the standard or workflow
**Action**: what changed (or "none — noting only")
```

Look here before assuming a friction is novel. Most maintenance pain is repeating maintenance pain.

---

## 2026-04-28 — Stale local marketplace cache silently breaks new-plugin installs

**Context**: First round-trip install test for cept. From a fresh shell, ran `claude plugins marketplace add eidos-agi/eidos-marketplace` then `claude plugins install cept@eidos-marketplace`. Add succeeded ("already on disk"); install failed ("Plugin 'cept' not found in marketplace 'eidos-marketplace'").

**What surprised**: The marketplace cache at `~/.claude/plugins/marketplaces/eidos-marketplace/.claude-plugin/marketplace.json` was a stale snapshot from a much earlier point — listed plugins like `ojo` and `test-forge` that aren't in the current `marketplace.json` on GitHub at all. The `marketplace add` command does NOT re-fetch when the marketplace is already cached; it just confirms it exists. The user has to know to run `claude plugins marketplace update eidos-marketplace` separately.

**Why it matters**: Every plugin update or new-plugin onboarding can silently fail for any user whose cache predates the change. The error message ("not found in marketplace") gives no hint that the local cache is out of sync. This will be the #1 recurring user-facing friction unless it's surfaced.

**Action**:
- Immediate fix: `claude plugins marketplace update eidos-marketplace` re-fetches.
- Documentation: add a "Troubleshooting" section to README.md naming this exact failure ("Plugin 'X' not found in marketplace 'Y'") and the fix.
- Phase 3 design task addition: `/eidos-install` should run `claude plugins marketplace update eidos-marketplace` as its first step before recommending anything, so users always start from a fresh cache.
- Phase 6 CI consideration: there may be a way to prompt cache invalidation when the marketplace.json's `version` field bumps. Worth investigating during the operational-forges phase.
