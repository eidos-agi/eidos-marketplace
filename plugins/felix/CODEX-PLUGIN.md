# Felix Codex Plugin

Felix is an Eidos AGI Codex plugin that tells Codex to use the live `felix` CLI for agent-building, agent standards, scaffold planning, maintainer loops, and repo-health work.

The architecture is CLI-first. Codex plugins and MCP shims should be small pointers into CLIs, not giant inventories of tools. Felix provides progressive reveal through top-level help, `doctor`, `standards`, `interview`, `scaffold-plan`, `plugin`, and agent-oriented subcommands.

## Eidos AGI Plugin Family

- `eidos@eidos-agi`: CLI-first gateway into the Eidos AGI platform and specialist systems.
- `felix@eidos-agi`: routing layer for the live Felix agent-builder CLI.
- `rhea@eidos-agi`: sovereign model routing, debate, pairing, and image tools.
- `foreman@eidos-agi`: multi-agent coding delegation and git worktree execution.
- `reeves@eidos-agi`: routing layer for the live Reeves CLI.
- `surfari@eidos-agi`: routing layer for the live Surfari CLI and browser-agent improvement loop.
- `forge-forge@eidos-agi`: routing layer for Eidos forge discovery and forge creation patterns.

## Install In Codex

Clone the repo:

```bash
mkdir -p "$HOME/repos-eidos-agi"
git clone git@github.com:eidos-agi/felix.git "$HOME/repos-eidos-agi/felix"
```

Install or refresh the Eidos AGI Codex plugin cache:

```bash
mkdir -p "$HOME/.codex/plugins/cache/eidos-agi/felix/0.1.0"
rsync -a --delete \
  --exclude '.git' \
  --exclude '__pycache__' \
  --exclude '.pytest_cache' \
  --exclude '.ruff_cache' \
  --exclude '.venv' \
  --exclude '*.egg-info' \
  "$HOME/repos-eidos-agi/felix/" \
  "$HOME/.codex/plugins/cache/eidos-agi/felix/0.1.0/"
```

Add Felix to `~/.agents/plugins/marketplace.json`:

```json
{
  "name": "felix",
  "source": {
    "source": "local",
    "path": "./plugins/felix"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "category": "Productivity"
}
```

Enable the plugin in `~/.codex/config.toml`:

```toml
[plugins."felix@eidos-agi"]
enabled = true
```

Restart Codex after editing config.

## Smoke Test

```bash
felix --help
felix doctor
felix standards
felix-of-felix --help
```
