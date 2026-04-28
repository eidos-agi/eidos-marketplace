# Eidos Marketplace

The plugin marketplace for [Claude Code](https://docs.claude.com/en/docs/claude-code), by [Eidos AGI](https://eidosagi.com).

> **A portfolio of how we ship.** Every plugin here is built or vouched for by Eidos AGI, audited against a public [standard](STANDARD.md), and removed if it falls below the bar. Visibility is the moat.
>
> **Three layers, one bar.** Onboarding via `/eidos-install` (a progressive-reveal forge that asks what you're doing and recommends a starter set). Discovery via `marketplace.json` and `/forge recommend-for` (a forge-specific recommender). Installation via `claude plugins install <name>` (the normal Claude Code path). Each layer can fail without breaking the others.
>
> **The marketplace is its own first customer.** Audits run via `foss-forge`. Releases via `ship-forge`. Security checks via `security-forge`. Each is itself a plugin in this marketplace. If our own tools can't run our own operations, they don't belong here. See [Dogfooding](STANDARD.md#dogfooding--the-marketplace-maintains-itself-with-its-own-plugins).

## Install

Add the marketplace once:

```bash
claude plugins marketplace add eidos-agi/eidos-marketplace
```

### First time? Use the front door.

```bash
claude plugins install eidos-install
/eidos-install
```

`/eidos-install` interviews you ("what are you doing?"), recommends a coherent starter set drawn from this marketplace and the broader Eidos ecosystem, and shows the install commands. It hands off to `/forge recommend-for <project>` for ongoing forge-specific drilldown.

### Already know what you want? Install directly.

```bash
claude plugins install cept            # proprioception for coding agents
claude plugins install resume-resume   # post-crash session recovery
claude plugins install ike             # task and project management
claude plugins install visionlog       # vision, goals, guardrails, ADRs
claude plugins install forge-forge     # forge-specific recommender
```

Every plugin is directly installable. The recommenders (`eidos-install`, `forge-forge`) are optional middleware over the flat listing — if either is broken, every plugin remains installable by name.

## What's in here

### Tools — discrete capabilities

| Plugin | What it does | Quality |
|--------|-------------|---------|
| **cept** | Proprioception for coding agents — slice recent Claude Code transcript, redact, ask a model for steering | A *(2026-04-28, by-hand)* |
| **rhea** | Adversarial sparring partner — challenge, debate, simplify, unstick. Sibling to cept; the outside-perspective mirror to cept's self-perspective | (Phase 3c) |
| **emux** | Eidos mux — pick up where you left off in tmux. TUI session picker for humans (`emux`) + MCP server for agents (`emux mcp`). One shared registry of named sessions; works with any tmux session — Claude Code, shells, long-running services | (Phase 3d) |
| **resume-resume** | Post-crash session recovery, dirty repos inventory, session search across history | (audit pending) |
| **ike** | Task and project management — tasks, milestones, documents, Definition of Done | (audit pending) |
| **visionlog** | Vision, goals, guardrails, SOPs, ADRs — the contracts all execution must honor | (audit pending) |
| **research-md** | Evidence-graded, phase-gated research decisions | (audit pending) |
| **railguey** | Railway deployment management | (audit pending) |
| **clawdflare** | Cloudflare management — DNS, Workers, Pages, KV, R2 | (audit pending) |
| **eidos-mail** | Email for Claude Code — read, search, send, reply, forward | (audit pending) |

### Forges — opinionated workflows

| Plugin | What it does | Quality |
|--------|-------------|---------|
| **eidos-install** | Progressive-reveal interview that recommends a starter set for the Eidos ecosystem; delegates to `forge-forge` for ongoing forge-specific drilldown | (Phase 3) |
| **forge-forge** | Forge-specific recommender; reads the marketplace's `x-eidos.recommend` blocks | (Phase 3) |
| **probe-forge** | Probing tools | (audit pending) |

Per-plugin scorecards live in [AUDITS/](AUDITS/). Audit metadata is also published machine-readably under each plugin's `x-eidos.audit` block in `marketplace.json`.

## How it works

This marketplace is a directory of pointers, not code. Plugins ship in two shapes depending on what they distribute:

**MCP-server plugins** (like `cept`) — two small JSON files; the actual code lives on PyPI.

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

[`uvx`](https://docs.astral.sh/uv/guides/tools/) pulls the package from PyPI on demand — no pre-install needed.

**Skill-bearing plugins** (forges) ship either as `github`-source entries (when the source lives in another repo) or as local entries inside this marketplace repo (when the skill is small enough to live alongside the listings). Either way, the marketplace pulls `skills/<name>/SKILL.md` directly. No PyPI package required. See [STANDARD.md](STANDARD.md) for the source-shape spec.

## What "eidos-grade" means

See [STANDARD.md](STANDARD.md) for the full bar. The short version:

- **Community Health** — LICENSE, README, CHANGELOG, CONTRIBUTING, COC, SECURITY
- **Agentic Quality** — every tool typed, described, and built for agents to choose between
- **Engineering** — semver, ≤5 dependencies, CI green, OIDC trusted publisher (no long-lived tokens)

Each plugin is also classified as a Tool or Forge, with kind-specific bar additions (e.g., forges must populate `x-eidos.recommend`; progressive-reveal forges like `eidos-install` must be interview-driven). See [STANDARD.md § Tools and Forges](STANDARD.md#tools-and-forges--two-surfaces-one-bar).

Plugins that drop below the bar are pulled. Removal is a stronger signal than silent inclusion.

## How to contribute

See [CONTRIBUTING.md](CONTRIBUTING.md). Today the marketplace lists only Eidos-maintained plugins; third-party submissions are by issue, not PR.

## Roadmap and current state

See [PHASES.md](PHASES.md) — the runnable phased plan. Any agent or human can pick up at the current phase and execute. Each task is tickable; nothing is deleted, only checked off with a one-line note when something was learned.

[LEARNINGS.md](LEARNINGS.md) captures friction encountered along the way.

### Requirements

- [`uvx`](https://docs.astral.sh/uv/) (comes with `uv`)
- [Claude Code](https://docs.claude.com/en/docs/claude-code)

### Troubleshooting

**`Plugin "X" not found in marketplace "eidos-marketplace"`** — your local marketplace cache is stale. Run:

```bash
claude plugins marketplace update eidos-marketplace
```

`claude plugins marketplace add` only fetches the marketplace if it isn't already cached; it does not re-fetch when the marketplace.json on GitHub has changed. Every install of a newly-added plugin will fail with "not found" until the cache is refreshed. See [LEARNINGS.md § 2026-04-28](LEARNINGS.md#2026-04-28--stale-local-marketplace-cache-silently-breaks-new-plugin-installs).

## License

MIT — see [LICENSE](LICENSE).
