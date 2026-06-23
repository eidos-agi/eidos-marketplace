---
name: maintain-dual-host-marketplace
description: Maintain and check the Eidos marketplace when plugins must work in both Claude Code and Codex. Use when adding, refactoring, auditing, or debugging marketplace plugins, dual-host packaging, .claude-plugin and .codex-plugin manifests, root marketplace entries, source/store/cache drift, install proof, or host-neutral plugin payloads.
---

# Maintain Dual-Host Marketplace

Use this when a marketplace plugin must stay usable from both Claude Code and Codex.

## Core Rule

The product is not a Claude plugin or a Codex plugin. The product is an Eidos plugin with host-specific packaging.

Shared payload:

- `README.md`
- `skills/`
- `assets/`
- `.mcp.json`, scripts, docs, tests, schemas, and other runtime files when present

Host adapters:

- `.claude-plugin/plugin.json`
- `.codex-plugin/plugin.json`

Root listings:

- `.claude-plugin/marketplace.json`
- `.agents/plugins/marketplace.json`

## Required Checks

Before claiming a plugin is marketplace-ready, verify:

- The plugin appears in both root marketplace files unless it is intentionally single-host.
- The plugin has both host manifests unless intentionally single-host.
- `name`, `version`, `description`, `homepage`, `repository`, `license`, and `skills` are aligned across manifests.
- Rich Codex UI metadata stays in `.codex-plugin/plugin.json`.
- Claude metadata stays portable and does not copy Codex-only `interface` blocks.
- Shared behavior lives in `README.md`, `skills/`, and assets, not in host-specific manifests.
- Audit metadata exists in `.claude-plugin/marketplace.json` under `x-eidos.audit`.
- An audit doc exists at `AUDITS/<plugin>.md`.
- Source, marketplace bundle, local cache, enabled config, and active-session visibility are treated as separate proof surfaces.

## Workflow

1. Identify the exact plugin and whether it is source-owned elsewhere or lives directly in this marketplace.
2. Read both root marketplace entries for the plugin.
3. Read both host manifests.
4. Read the README and skills to confirm the product definition is host-neutral.
5. Run JSON validation for both marketplace files and both manifests.
6. Run plugin and skill validation.
7. Run marketplace tests.
8. If a control machine is known, sync through Conduit and verify cache/install state there.
9. Report created, listed, installed, enabled, and visible-current-session states separately.

## Commands

Run from the marketplace root:

```bash
python3 -m json.tool .claude-plugin/marketplace.json >/dev/null
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool plugins/<name>/.claude-plugin/plugin.json >/dev/null
python3 -m json.tool plugins/<name>/.codex-plugin/plugin.json >/dev/null
python3 tools/marketplace_publish.py check <name>
uv run --with pytest python -m pytest tests/test_marketplace_publish.py tests/test_plugin_tester.py
```

For skill-bearing plugins:

```bash
for d in plugins/<name>/skills/*; do
  uv run --with pyyaml python /Users/dshanklinbv/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$d" || exit 1
done
```

For Codex manifest validation:

```bash
uv run --with pyyaml python /Users/dshanklinbv/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/<name>
```

## Failure Modes

- The plugin exists under `plugins/<name>` but only one root marketplace lists it.
- The plugin has only `.codex-plugin` or only `.claude-plugin` without an explicit reason.
- The README says host-neutral, but the real behavior is described only in a Codex `interface.defaultPrompt`.
- The marketplace was pushed, but the target machine cache still contains an older bundle.
- The final answer says "installed" when only source or GitHub was updated.

## Output Shape

```text
Plugin:
Shared payload:
Claude listing:
Codex listing:
Claude manifest:
Codex manifest:
Validation:
Install/cache proof:
Blockers:
Next action:
```

Keep the answer evidence-first and concise.
