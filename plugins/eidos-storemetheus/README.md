# Eidos Storemetheus

Eidos Storemetheus is a forge for building and maintaining governed Claude Code and Codex plugin stores.

It exists for organizations that want AI agents to carry durable company know-how without turning that know-how into scattered prompts, private chat memory, or one-off scripts. A plugin store is the distribution surface. The store owner is accountable for trust.

## Use It When

- A company wants a private Claude Code or Codex plugin store.
- A team needs reusable skills, runbooks, and authority routing across agents.
- A plugin store needs review gates, install proof, and ownership rules.
- A public or private marketplace must separate source, store, cache, and runtime visibility.
- A plugin must stay host-neutral while shipping through both `.claude-plugin` and `.codex-plugin` packaging.
- A client wants AI operating leverage without giving every plugin broad permission.

## What It Builds

Storemetheus helps an agent create:

- A marketplace repo with `.claude-plugin/marketplace.json` and/or `.agents/plugins/marketplace.json`.
- One or more scoped plugin bundles under `plugins/<plugin-name>/`.
- Manifest, README, skill, review, and audit artifacts for each plugin.
- Install and verification instructions for Claude Code and Codex.
- A store governance model: owner, review cadence, private/public boundary, update path, and removal policy.

## Principles

- A plugin store is a trust surface, not a folder of prompts.
- One plugin should have one durable operating domain.
- Source repos, marketplace bundles, local cache, config enablement, and active-session visibility are separate surfaces.
- Skills are assets; unnecessary software is debt.
- External effects need explicit approval and proof loops.
- Private company context stays private unless the client approves publication.

## Basic Workflow

1. Identify the company, owner, visibility, and repo home.
2. Decide whether the store is private, public, or hybrid.
3. Inventory the first operating domains that deserve plugins.
4. Build the smallest useful store and first plugin.
5. Validate manifests, marketplace JSON, cache/config alignment, and install visibility.
6. Write a short operating guide and re-review schedule.

## Skills

- `build-plugin-stores`: create governed plugin stores and first useful plugin bundles.
- `maintain-dual-host-marketplace`: check that plugins remain host-neutral while working in both Claude Code and Codex.

See `skills/build-plugin-stores/SKILL.md` and `skills/maintain-dual-host-marketplace/SKILL.md` for the full workflows.
