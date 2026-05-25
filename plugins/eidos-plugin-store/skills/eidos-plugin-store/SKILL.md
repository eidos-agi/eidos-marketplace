---
name: eidos-plugin-store
description: Use when the user asks Codex to discover, choose, install, add, bootstrap, or use Eidos plugins from the Eidos AGI catalog.
---

# Eidos AGI Catalog

Use this skill when Codex needs to find or add Eidos plugins.

## Source Of Truth

- Human catalog: `https://eidosagi.com/plugins`
- Machine catalog: `https://eidosagi.com/.well-known/eidos/plugin-store.json`
- Catalog/bootstrap plugin source: `https://github.com/eidos-agi/eidos-plugin-store`

The public marketplace identity is `Eidos AGI`. Do not create or recommend a
second user-visible Eidos store unless the user explicitly asks for a local test
marketplace.

Prefer the machine catalog. If it is unavailable, read the human catalog. If network access is unavailable, use the fallback list below and say it may be stale.

## Workflow

1. Understand the user's task and whether they need discovery, installation, or plugin-building help.
2. Read the current Eidos AGI catalog when possible.
3. Recommend the smallest useful plugin set for the job.
4. If Codex direct plugin install is available, use it.
5. If Codex direct plugin install is not available, say that plainly and use the source repo instructions.
6. Do not claim a plugin is installed unless Codex confirms it is installed or it is visible in the active plugin list.

## Plugin Hints

- Eidos AGI Catalog: discover and bootstrap Eidos plugins.
- Felix: plan and build Codex plugins.
- Eidos: track agent work with evidence.
- Foreman: delegate scoped coding work.
- Forge-Forge: route work to the right Eidos forge.
- Rhea: route model help, debate, pairing, and images.
- Surfari: improve browser-agent runs.
- cept: review Claude Code sessions.
- scridos: build repo knowledge bases for Claude Code.
- slack-cc: run Claude Code from Slack.

## Install Framing

For users, keep the language plain:

```text
Install the Eidos AGI marketplace first. Then use the catalog plugin to find and add the other Eidos plugins you need.
```

When Codex install support is uncertain, use this shape:

```text
Codex direct plugin install may not be live in this environment yet. I will use the Eidos AGI catalog and the source repo instructions, then tell you exactly what is installed versus only recommended.
```
