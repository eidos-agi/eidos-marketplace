# forge-forge

The forge that forges forges.

## What is a Forge?

A forge is a repo that packages reusable AI agent knowledge as [Claude Code](https://claude.ai/claude-code) skills and templates. No software. No CLI. No package to install. Just knowledge.

Each forge owns a domain:
- **foss-forge** — how to publish great open-source agentic software
- **demo-forge** — how to create compelling demo content
- **security-forge** — how to secure agentic software
- **test-forge** — how to test effectively
- **forge-forge** — how to create and manage forges (this repo)

## The Forge Standard

Every forge follows the same structure:

```
<forge-name>/
├── .claude/skills/    ← agent skills (markdown files)
├── .visionlog/        ← vision, goals, guardrails
├── templates/         ← parameterized file templates
├── CLAUDE.md          ← project instructions for Claude Code
├── README.md          ← public-facing docs
└── LICENSE            ← MIT
```

Every forge:
- Has no installable software (no pyproject.toml, no package.json)
- Has a visionlog with at least a vision and the "no software" guardrail
- Is public on GitHub under `eidos-agi/`
- Is registered in this repo's `registry.yaml`

## Skills

| Skill | What |
|-------|------|
| `/forge-init` | Create a new forge — repo structure, visionlog, GitHub, registry entry |
| `/forge-audit` | Validate a forge against the Forge Standard |
| `/forge-catalog` | List all forges with their skills and status |
| `/forge-sync` | Three-way reconciliation: registry ↔ GitHub ↔ local filesystem |

## Registry

[`registry.yaml`](registry.yaml) is the canonical list of all Eidos AGI forges.

Enable the pre-commit hook to validate the registry before every commit:

```bash
git config core.hooksPath .githooks
```

The hook fails the commit if `registry.yaml` doesn't parse, is missing required
fields, or has duplicate forge names. See `.nightingale/incidents/` for the
failure modes the hook guards against.

## Usage

Clone this repo:

```bash
git clone https://github.com/eidos-agi/forge-forge.git ~/repos-eidos-agi/forge-forge
```

Copy skills into any project where you need to create or manage forges:

```bash
cp ~/repos-eidos-agi/forge-forge/.claude/skills/forge-*.md .claude/skills/
```

## License

MIT — [Eidos AGI](https://github.com/eidos-agi)
