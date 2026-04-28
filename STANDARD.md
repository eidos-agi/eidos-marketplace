# The Eidos Marketplace Standard

> What "eidos-grade" means, and what every plugin in this marketplace must pass.

## Why this document exists

A plugin in `eidos-marketplace` is a public commitment that Eidos AGI built it (or vouches for it) and ships it to a known bar. **Visibility is the moat.** This document defines the bar concretely so any agent or human can verify a plugin against it without ambiguity, and so removal of a plugin (when it falls below the bar) is principled and public.

This standard is enforced through automated audits where possible (`foss-forge/foss-check`) and through human review where not. The audit result for every plugin lives in `AUDITS/<plugin-name>.md` — public, dated, and re-run quarterly.

---

## The bar — three layers

### Layer 1 — Community Health (humans contributing)

| Requirement | Why it matters |
|---|---|
| `LICENSE` exists, OSI-approved (MIT or Apache-2.0 preferred) | Legal clarity for reuse |
| `README.md` ≥20 lines, has install + usage example | An agent or human can adopt it in <5 minutes |
| `CHANGELOG.md` follows [Keep a Changelog](https://keepachangelog.com/) | Updates are legible, not silent |
| `CONTRIBUTING.md` with dev setup | Outsiders can fix bugs without asking |
| `CODE_OF_CONDUCT.md` with enforcement contact | Public-facing project hygiene |
| `SECURITY.md` with vuln reporting + threat model | Trust signal — we name the risks |

### Layer 2 — Agentic Quality (agents using it)

For MCP servers / agent tools — the layer that makes eidos-marketplace different from a generic FOSS list.

| Requirement | Why it matters |
|---|---|
| Every `@tool` has a description ≥20 chars that explains *when* to use it (not just *what*) | Agents pick from many tools; descriptions are how they decide |
| Every parameter has a typed schema and description field | Agents have no UI tooltips — descriptions are all they get |
| Error returns are actionable (what went wrong + what to try) | Bare "failed" leaves agents stuck |
| Tool count ≤25 per server | Agent context windows are finite |
| MCP entry point in `pyproject.toml` (`[project.scripts]`) | Discoverable via `uvx --from <pkg> <entry>` |

### Layer 3 — Engineering (shipping)

| Requirement | Why it matters |
|---|---|
| `pyproject.toml`: name, version (semver), description, license, classifiers, keywords, project.urls | Discoverable on PyPI, indexable, searchable |
| ≤5 direct dependencies (WARN at 6–10, FAIL >10) | Bloated dep trees break agent installs |
| Hatchling build backend (not setuptools) | Modern, fast, simpler |
| `.github/workflows/ci.yml` runs lint + format check + tests on Python 3.11/3.12/3.13 | Green CI = visible quality |
| `.github/workflows/publish.yml` triggered by `v*` tag, uses `pypa/gh-action-pypi-publish` with OIDC trusted publisher (`id-token: write`, `environment: pypi`) | No long-lived `PYPI_TOKEN` secret in CI |
| Tag a release: `git tag v0.1.0 && git push --tags` triggers PyPI publish | Versions and updates are predictable |

---

## What gets a plugin pulled

A plugin is removed from the marketplace (publicly, with a removal entry in `AUDITS/<name>.md`) when:

- Latest audit drops below B grade and isn't fixed within 30 days
- A high-severity security issue is unfixed past disclosure window (per SECURITY.md)
- The repo is unmaintained for >12 months and the maintainer is unreachable
- The license changes to a non-OSI-approved license

Removal is more honest than silently keeping low-quality plugins for breadth. The bar is the brand.

---

## How submissions work (today)

The marketplace is a portfolio of how Eidos AGI ships, not a public submission queue. Today, only plugins maintained by Eidos AGI are listed.

If you want to propose a third-party plugin, open an issue against `eidos-agi/eidos-marketplace` describing the plugin and how it meets this standard. Submission infrastructure (automated `foss-check` on PR, scorecard publication) is on the roadmap — see [PHASES.md](PHASES.md) Phase 5.

---

## Audit cadence

Every plugin is re-audited quarterly. The next audit date and previous score live in the plugin's marketplace.json entry under `x-eidos-quality`:

```json
{
  "name": "cept",
  "x-eidos-quality": {
    "foss_check": "A",
    "audited_at": "2026-04-28",
    "next_audit": "2026-07-28",
    "audit_doc": "AUDITS/cept.md"
  }
}
```

This metadata is public and machine-readable. Agents can filter on it. Humans can verify it.

---

## Dogfooding — the marketplace maintains itself with its own plugins

The marketplace lists `foss-forge`, `ship-forge`, `security-forge`, `scribe`, `visionlog`, and others. Those plugins exist precisely because Eidos AGI's maintenance operations need them. So **the marketplace's own maintenance must run through them.** No bypassing, no parallel manual workflow. If a marketplace plugin is the right tool for an internal job, it is the only tool for that job.

Concretely:

| Operation | Tool (marketplace plugin) | Phase it activates |
|---|---|---|
| Score a plugin against [STANDARD.md](STANDARD.md) | `foss-forge` (`/foss-check`) | Once onboarded in Phase 4 |
| Release a marketplace.json change | `ship-forge` (`/ship`) | Once onboarded |
| Security-audit a plugin's source repo | `security-forge` (`/secaudit`) | Once onboarded |
| Open and triage marketplace issues | `eidos-mail`, `ike` | Already onboarded |
| Record a marketplace governance decision | `visionlog` (ADR) | Already onboarded |
| Re-test marketplace.json schema validity | `test-forge` | Once onboarded |

This creates a forcing function:

1. **The marketplace cannot run a foss-check audit until `foss-forge` is itself a marketplace plugin in good standing.** That's why Phase 4 onboards `foss-forge` first, before continuing the Phase 3 audit backlog. If `foss-forge` can't pass its own bar, we can't trust its audits of others.
2. **Every audit document records which version of `foss-forge` produced it.** When `foss-forge` evolves, audits become re-runnable and comparable. The header of each `AUDITS/<name>.md` carries `audited_via: foss-forge@<version>`.
3. **A marketplace plugin that breaks in production breaks marketplace operations.** Self-interest aligns with quality. We feel our own bugs first.

The marketplace is not just a directory of plugins. It is the **first customer** of every plugin it lists. Plugins that don't support the marketplace's own maintenance get pulled — not because they're bad in the abstract, but because they fail the proof: *the people who built it use it*.

---

## The negative rule

The thesis is "trust through visibility." The negative rule that follows: **never commit something to this marketplace that you wouldn't want a stranger to read.** Every commit, every plugin entry, every audit. The bar isn't "no embarrassments" — it's "this is what good looks like."
