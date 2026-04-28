# Eidos Marketplace

The plugin marketplace for [Claude Code](https://docs.claude.com/en/docs/claude-code), by [Eidos AGI](https://eidosagi.com).

> **A portfolio of how we ship.** Every plugin here is built or vouched for by Eidos AGI, audited against a public [standard](STANDARD.md), and removed if it falls below the bar. Visibility is the moat.

## Install

```bash
claude plugins marketplace add eidos-agi/eidos-marketplace
```

Then install any plugin:

```bash
claude plugins install cept            # proprioception for coding agents
claude plugins install resume-resume   # post-crash session recovery
claude plugins install ike             # task and project management
claude plugins install visionlog       # vision, goals, guardrails, ADRs
```

## What's in here

| Plugin | What it does | Quality |
|--------|-------------|---------|
| **cept** | Proprioception for coding agents — slice recent Claude Code transcript, redact, ask a model for steering | A *(2026-04-28)* |
| **resume-resume** | Post-crash session recovery, dirty repos inventory, session search across history | (audit pending) |
| **ike** | Task and project management — tasks, milestones, documents, Definition of Done | (audit pending) |
| **visionlog** | Vision, goals, guardrails, SOPs, ADRs — the contracts all execution must honor | (audit pending) |
| **research-md** | Evidence-graded, phase-gated research decisions | (audit pending) |
| **railguey** | Railway deployment management | (audit pending) |
| **clawdflare** | Cloudflare management — DNS, Workers, Pages, KV, R2 | (audit pending) |
| **eidos-mail** | Email for Claude Code — read, search, send, reply, forward | (audit pending) |
| **forge-forge** | Meta-forge — create and manage forges | (audit pending) |
| **probe-forge** | Probing tools | (audit pending) |

Per-plugin scorecards live in [AUDITS/](AUDITS/).

## How it works

This marketplace is a directory of pointers, not code. Each MCP-server plugin is two small JSON files:

```
plugins/cept/
├── .claude-plugin/plugin.json   ← name + description
└── .mcp.json                    ← command to start the MCP server
```

The `.mcp.json` tells Claude Code how to run the server:

```json
{
  "cept": {
    "command": "uvx",
    "args": ["--from", "cept", "cept"]
  }
}
```

The actual code lives in each plugin's own repo, published to PyPI. The marketplace just says "run this command." [`uvx`](https://docs.astral.sh/uv/guides/tools/) pulls the package from PyPI on demand — no pre-install needed.

Skill-bearing plugins (forges) use a different pattern documented in [PHASES.md](PHASES.md) Phase 4 — `github` source pulling the repo's `skills/` directory directly.

## What "eidos-grade" means

See [STANDARD.md](STANDARD.md) for the full bar. The short version:

- **Community Health** — LICENSE, README, CHANGELOG, CONTRIBUTING, COC, SECURITY
- **Agentic Quality** — every tool typed, described, and built for agents to choose between
- **Engineering** — semver, ≤5 dependencies, CI green, OIDC trusted publisher (no long-lived tokens)

Plugins that drop below the bar are pulled. Removal is a stronger signal than silent inclusion.

## How to contribute

See [CONTRIBUTING.md](CONTRIBUTING.md). Today the marketplace lists only Eidos-maintained plugins; third-party submissions are by issue, not PR.

## Roadmap and current state

See [PHASES.md](PHASES.md) — the runnable phased plan. Any agent or human can pick up at the current phase and execute. Each task is tickable; nothing is deleted, only checked off with a one-line note when something was learned.

[LEARNINGS.md](LEARNINGS.md) captures friction encountered along the way.

### Requirements

- [`uvx`](https://docs.astral.sh/uv/) (comes with `uv`)
- [Claude Code](https://docs.claude.com/en/docs/claude-code)

## License

MIT — see [LICENSE](LICENSE).
