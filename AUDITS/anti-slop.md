# Audit: anti-slop

## 2026-08-03 — Grade: PENDING

- Community Health: PENDING — run foss-forge or the marketplace audit workflow.
- Agentic Quality: PENDING — run Felix plugin doctor and skill checks.
- Engineering: PENDING — skill-only dual-host plugin (Claude + Grok); no MCP server. Lexicon continuous update via vendor submodules + weekly CI PRs in source repo.
- Notes: Published into eidos-marketplace from `https://github.com/eidos-agi/anti-slop` (Linear EID-1310). Hosts: Claude Code (`.claude-plugin`) and Grok Build (`.grok-plugin`). Skills: `anti-slop`, `anti-slop-audit`, `world-class-case-study`.

### Install

```bash
# Claude Code
claude plugins marketplace add eidos-agi/eidos-marketplace
claude plugins install anti-slop@eidos-marketplace

# Grok Build
grok plugin marketplace add eidos-agi/eidos-marketplace
grok plugin install anti-slop --trust
```

### Source-to-store

```bash
python3 tools/marketplace_publish.py check anti-slop --source /path/to/anti-slop
```
