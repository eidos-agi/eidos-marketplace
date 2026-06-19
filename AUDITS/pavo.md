# Pavo Audit

Date: 2026-06-18

Auditor: by-hand, pending foss-forge automation

Grade: B

## Summary

Pavo is entering the Eidos Marketplace as a CLI-first meeting evidence control plane. It currently provides a bounded MCP bridge that delegates to the local `pavo` CLI, plus local proof commands for meeting batches, review queues, route recommendations, and store readiness.

## Passing Evidence

- MIT license exists in the source repo.
- README, CHANGELOG, CONTRIBUTING, CODE_OF_CONDUCT, and SECURITY exist in the source repo.
- CLI-first progressive reveal is implemented through `pavo --help`, `pavo doctor`, `pavo status`, and domain subcommands.
- Local test suite passes: `.venv/bin/python -m pytest -q`.
- Pavo has a bounded MCP bridge: `pavo mcp serve`.
- Pavo has a privacy boundary for voiceprints, raw audio, signed URLs, and credentials.

## Current Limitations

- Public PyPI package is not yet published from CI.
- Marketplace entry points to `uvx --from pavo`, which depends on release publication.
- Web app is scaffolded only.
- Some product surfaces are local, dry-run, or manifest-only rather than production integrations.

## Next Audit

2026-07-18
