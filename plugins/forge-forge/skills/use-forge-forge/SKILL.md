---
name: use-forge-forge
description: Use when the user asks about Eidos forges, forge discovery, creating a new forge, checking whether a forge exists, applying a forge pattern, registry.yaml, company-forge, or repo-local forge manifests. This skill tells Codex to use forge-forge's registry, CLI, and MCP tools as the source of truth.
---

# Use Forge-Forge

Use Forge-Forge for forge-shaped questions. Do not invent a new forge, pattern, or registry entry before checking the canonical registry and live repo state.

## Primary Rule

Start with Forge-Forge:

```bash
cd ~/repos-eidos-agi/forge-forge
.venv/bin/forge list
.venv/bin/forge find "<task or domain>"
.venv/bin/forge info <forge-name>
.venv/bin/forge how <forge-name>
.venv/bin/forge for-project /path/to/project
```

If Codex has MCP tools available, prefer:

- `forge_find`
- `forge_list`
- `forge_info`
- `forge_how`
- `forge_for_project`

## Canonical Surfaces

```text
~/repos-eidos-agi/forge-forge/registry.yaml
~/repos-eidos-agi/forge-forge/README.md
~/repos-eidos-agi/forge-forge/.claude/skills/
~/repos-eidos-agi/forge-forge/.visionlog/
```

`registry.yaml` is the first lookup point for whether a forge already exists and what scope it owns.

## Operating Guidance

- Check `registry.yaml` and GitHub/local repo state before saying a forge exists or does not exist.
- Preserve adjacent scope boundaries: forge-forge, ship-forge, foss-forge, nightingale-forge, company-forge, landfall-forge, etc. are intentionally separate.
- If the registry lacks a needed capability, derive the new forge from the established forge-forge pattern.
- For new forges, follow the Forge Standard and update `registry.yaml`.
- Keep forges knowledge-first: skills, templates, docs, and registry entries before software.

## Boundary

Forge-Forge is the progressive-reveal doorway for forge knowledge. It is not a replacement for reading the target forge repo when exact behavior matters.
