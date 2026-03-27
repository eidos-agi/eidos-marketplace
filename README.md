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
| **railguey** | Railway deployment management — deploy, rollback, logs, health checks |
| **clawdflare** | Cloudflare management — DNS records, Workers, Pages, KV, R2, and analytics |

All plugins are tested on every change — see `tools/test_plugins.py`.

## How It Works

This marketplace is a directory of pointers, not code. Each plugin is two small JSON files:

```
plugins/resume-resume/
├── .claude-plugin/plugin.json   ← name + description
└── .mcp.json                    ← command to start the MCP server
```

The `.mcp.json` tells Claude Code how to run the server:

```json
{
  "resume-resume": {
    "command": "uvx",
    "args": ["--from", "resume-resume", "resume-resume-mcp"]
  }
}
```

The actual code lives in each tool's own repo, published to PyPI. The plugin just says "run this command." [uvx](https://docs.astral.sh/uv/guides/tools/) pulls the package from PyPI on demand — no pre-install needed.

### For developers already using these tools

If you already have a tool installed via `pip install` + `claude mcp add`, you don't need the plugin. Your local install takes priority. The marketplace is for new users who want zero-config setup.

Installing both creates a duplicate MCP registration. Use one or the other:
- **Plugin** (marketplace): `claude plugins install resume-resume` — uses uvx, auto-updates
- **Manual** (pip): `pip install resume-resume && claude mcp add resume-resume -- resume-resume-mcp` — uses your local Python environment

### Requirements

- [uvx](https://docs.astral.sh/uv/) (comes with uv)
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)

## Adding a New Plugin

1. Create a directory under `plugins/` with `.claude-plugin/plugin.json` and `.mcp.json`
2. The `.mcp.json` should use `uvx --from <pypi-package> <entry-point>`
3. Add an entry to `.claude-plugin/marketplace.json`
4. Validate: `claude plugins validate .`

## License

MIT
