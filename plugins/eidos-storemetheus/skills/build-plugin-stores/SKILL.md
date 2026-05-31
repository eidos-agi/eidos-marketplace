---
name: build-plugin-stores
description: Use when building, auditing, or planning a private or public company plugin store, Codex marketplace, internal AI operating layer, plugin catalog, store governance model, or client-specific plugin distribution surface.
---

# Build Plugin Stores

Use this skill when a user wants Eidos to build a plugin store for a company, team, client, or operating domain.

## Core Framing

A successful plugin store is a governed distribution system for AI operating capability. It is not just a plugin list.

The store must answer:

1. Who owns the store?
2. Which organization or client does it represent?
3. What is private, public, or client-shareable?
4. Which plugins are installed by default, available, or blocked?
5. What authority surfaces does each plugin route to?
6. What can a plugin cause an agent to do without approval?
7. What evidence proves a plugin is installed, visible, and current?
8. How are stale, risky, or low-quality plugins removed?

## First Move

Start by identifying placement:

- Local repo root, such as `/Users/dshanklinbv/repos-eidos-agi`, `/Users/dshanklinbv/repos-greenmark-waste-solutions`, or another company root.
- GitHub owner or organization.
- Visibility: private by default for client/company stores unless the user explicitly approves public release.
- Store identity, for example `eidos-agi`, `greenmark-waste-solutions`, or a client-specific namespace.

If the user already supplied these fields, state the inferred placement and proceed.

## Store Architecture

Prefer this layout for Codex stores:

```text
<store-repo>/
├── .agents/plugins/marketplace.json
├── plugins/
│   └── <plugin-name>/
│       ├── .codex-plugin/plugin.json
│       ├── README.md
│       └── skills/<skill-name>/SKILL.md
└── README.md
```

Use `.claude-plugin/marketplace.json` and `.claude-plugin/plugin.json` as needed for Claude Code distribution.

Treat source, store, cache, config, and active session as separate proof surfaces:

- Source repo or canonical plugin folder.
- Marketplace entry and bundled payload.
- Local cache under `~/.codex/plugins/cache/<store>/<plugin>/<version>`.
- Enabled config in `~/.codex/config.toml`.
- Current session skill/tool visibility.

Do not claim a plugin is installed or usable until the relevant surfaces have been checked.

## Plugin Scope Rules

Build narrowly scoped plugins:

- Good: `cerebro`, `holiday-management`, `gate-approvals`, `phone-agent`.
- Bad: one giant plugin that owns every company workflow.

Each plugin needs:

- Manifest.
- README.
- Triggering skill.
- Owner.
- Authority surfaces.
- Safe actions.
- Unsafe actions requiring approval.
- Verification commands.
- Update procedure.
- Rollback or removal notes.

## Governance Checklist

Before a store is presented as ready, verify:

- Marketplace JSON parses.
- Plugin manifests validate.
- `felix plugin doctor <plugin-path>` passes where Felix is available.
- Plugin names are sorted if the store enforces sorted listings.
- Store repo visibility matches the user’s intent.
- Private client facts are not published into public Eidos surfaces.
- Install instructions name the exact marketplace root.
- The final answer separates created, installed, enabled, and visible-current-session states.

## Review Gates

Use review gates based on risk:

- Low risk: skills and docs only.
- Medium risk: local file edits or repo operations.
- High risk: credentials, production deploys, external writes, customer data, or money movement.

High-risk plugins must document approval requirements and fail-closed behavior. If the company has a Gate-style approval system, route external effects through it.

## Operating Cadence

Every store should have a recurring review cadence:

- Weekly or biweekly for active client/company stores.
- Monthly for stable private stores.
- Quarterly for public Eidos marketplace entries.

The review should check stale docs, broken install paths, cache/config drift, private-data leakage, and whether any plugin should be split, promoted, paused, or removed.

## Deliverable Shape

When building a store, produce:

1. Store repo or branch.
2. First useful plugin.
3. Marketplace entry.
4. Validation evidence.
5. Install/view handoff.
6. Governance note describing owner, visibility, review cadence, and approval boundaries.

Keep the first store small. The value is trust, repeatability, and discoverability, not breadth.
