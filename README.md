# Eidos Marketplace

Plugin marketplace for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Install Eidos tools with one command — no pip, no manual MCP config.

## Install

```bash
claude plugins marketplace add eidos-agi/eidos-marketplace
```

Then install any plugin:

```bash
claude plugins install resume-resume
claude plugins install ike
claude plugins install visionlog
```

## Available Plugins

| Plugin | What it does |
|--------|-------------|
| **resume-resume** | Post-crash session recovery, dirty repos inventory, session search across your full Claude Code history |
| **ike** | Task and project management — tasks, milestones, documents, Definition of Done |
| **visionlog** | Vision, goals, guardrails, SOPs, ADRs — the contracts all execution must honor |
| **research-md** | Evidence-graded, phase-gated research decisions with peer review |
| **railguey** | Railway deployment management — deploy, rollback, logs, health checks |
| **ojo** | Visual content moderation and safety scanning |
| **test-forge** | Test generation and execution — YAML test suites, ML model validation |
| **forge-forge** | Meta-forge for creating and managing forges |

## How It Works

Each plugin uses [uvx](https://docs.astral.sh/uv/guides/tools/) to run its MCP server — no pre-install needed. When Claude Code activates a plugin, uvx fetches the package from PyPI and starts the server automatically.

Requires `uvx` (comes with [uv](https://docs.astral.sh/uv/)).

## License

MIT
