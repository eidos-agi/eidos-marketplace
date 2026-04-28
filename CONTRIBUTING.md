# Contributing

The marketplace is a portfolio of how Eidos AGI ships, not a public submission queue. Today, only plugins maintained by Eidos AGI are listed.

## Proposing a third-party plugin

If you maintain a plugin you think belongs here, **open an issue** rather than a PR. Include:

- Plugin name and what it does (one paragraph)
- Link to the source repo + PyPI package (or the equivalent for skill-only plugins)
- Self-assessment against [STANDARD.md](STANDARD.md) — which checks pass, which don't, what's the plan for the gaps
- Why this plugin belongs in eidos-marketplace specifically (vs. a generic FOSS list)

We'll respond within a week. If we accept, we'll write your audit doc against [STANDARD.md](STANDARD.md) and add the entry. If we decline, we'll explain why so you can decide whether to address the gaps and resubmit.

## Submitting an Eidos-maintained plugin

Follow the phased plan in [PHASES.md](PHASES.md). Phase 3 onward documents the per-plugin onboarding steps. The short version:

1. Verify the source repo passes [STANDARD.md](STANDARD.md). Add missing artifacts where needed.
2. Add `plugins/<name>/.claude-plugin/plugin.json` and `plugins/<name>/.mcp.json` (uvx-shim pattern for MCP servers, or github-source for skill-bearing plugins — see Phase 4).
3. Add the entry to `.claude-plugin/marketplace.json`. Include `x-eidos-quality` metadata.
4. Run `python tools/test_plugins.py` to validate.
5. Audit. Write `AUDITS/<name>.md`.
6. Open a PR. The marketplace's CI re-validates the schema and lints the entry.

## Reporting issues with an existing plugin

Open an issue against the plugin's source repo first. If the plugin is unresponsive, open an issue here — we'll either re-engage the maintainer or pull the plugin per the removal policy in [STANDARD.md](STANDARD.md).
