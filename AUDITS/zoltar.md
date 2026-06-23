# Audit: zoltar

Source: `plugins/zoltar`

## 2026-06-23 - Grade: PENDING

`audited_by: Codex plugin validator + skill quick validation + dual-host marketplace checks` · `audit_version: STANDARD.md`

Zoltar is classified as a forge because it ships an opinionated foresight workflow through skills. It is not an MCP server and does not own external write authority. Its value is judgment: researched future prediction, market-overfit challenge, complaint prediction, and doer/checker handoff.

### Verification

| Action | Result |
|---|---|
| `uv run --with pyyaml python /Users/dshanklinbv/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/zoltar` | PASS |
| `uv run --with pyyaml python /Users/dshanklinbv/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/zoltar/skills/<skill>` | PASS for all bundled skills |
| `python tools/marketplace_publish.py check zoltar` | PASS |
| `uv run --with pytest python -m pytest tests/test_marketplace_publish.py tests/test_plugin_tester.py` | PASS |

### Layer 1 - Community Health

| Requirement | Verdict | Evidence |
|---|---|---|
| README | PASS | README leads with the Zoltar visual identity, describes the role, output contract, safety boundary, and verification |
| License | PASS | Marketplace-level MIT license |
| Audit doc | PASS | This file |

### Layer 2 - Agentic Quality

| Requirement | Verdict | Evidence |
|---|---|---|
| Progressive reveal | PASS | Skills route broad requests into research, complaint prediction, Challenger Matrix, and handoff |
| Bounded authority | PASS | README and skills preserve read-first behavior and explicit approval for outbound writes |
| Host neutrality | PASS | Shared README/assets/skills are packaged through both `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` |

### Layer 3 - Engineering

| Requirement | Verdict | Evidence |
|---|---|---|
| Marketplace entries | PASS | Listed in both `.claude-plugin/marketplace.json` and `.agents/plugins/marketplace.json` |
| JSON validity | PASS | Both marketplace files and both host manifests parse |
| Skill validation | PASS | All seven Zoltar skills validate |

### Notes

The grade remains `PENDING` until a fresh Claude Code install smoke test is captured. Codex install was verified on `mac-mini-01` after the `0.3.0` bundle was created.
