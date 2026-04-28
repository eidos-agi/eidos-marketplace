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

## Plugin metadata — the `x-eidos` block

Every plugin entry in `marketplace.json` carries an `x-eidos` block. This is the public, machine-readable interface for everything downstream tools (`forge-forge`, CI, third-party indexers) need to know about the plugin's classification, audit state, and recommendation hints. Agents can filter on it; humans can verify it.

```json
{
  "name": "cept",
  "x-eidos": {
    "kind": {
      "type": "tool",
      "signals": ["single_capability", "uvx_shim"]
    },
    "audit": {
      "audited_by": "foss-forge",
      "audit_version": "0.1.0",
      "audit_date": "2026-04-28",
      "grade": "A",
      "next_audit": "2026-07-28",
      "audit_doc": "AUDITS/cept.md"
    }
  }
}
```

For forges, the block also carries `recommend` so `forge-forge` can surface the right forge for a given project context without holding its own internal registry:

```json
{
  "name": "foss-forge",
  "x-eidos": {
    "kind": {
      "type": "forge",
      "signals": ["ships_skills", "opinionated_workflow", "coordinates_with_other_forges"]
    },
    "audit": { "audited_by": "foss-forge", "grade": "A", "audit_date": "2026-04-28", "audit_doc": "AUDITS/foss-forge.md" },
    "recommend": {
      "for_projects": ["python-package", "github-repo", "open-source-prep"],
      "pairs_with": ["security-forge", "ship-forge"],
      "preflight_check": "/foss-check"
    }
  }
}
```

The schema is forward-compatible: new fields under `x-eidos` are additive, never breaking. Re-audits are quarterly. CI fails any plugin whose `audit_date` is older than 95 days (see [PHASES.md](PHASES.md) Phase 6).

---

## Tools, Forges, and Gateways — three surfaces, one bar

The marketplace classifies every plugin as one of three `kind.type` values: `tool`, `forge`, or `gateway`. The distinction matters because **discovery patterns differ**, even though the [Standard's three layers](#the-bar--three-layers) apply equally to all three.

### Tool — a discrete capability

A *tool* does one thing. Users install it à-la-carte by name. Examples: `cept`, `eidos-mail`, `ike`, `visionlog`, `resume-resume`, `research-md`, `railguey`, `clawdflare`. Signals (any one is sufficient):

- `single_capability` — solves one job, doesn't orchestrate other plugins
- `uvx_shim` — Python package on PyPI, started via `uvx --from <pkg>`
- `mcp_server` — exposes an MCP server with bounded tool surface (≤25 tools)

Tools live flat on the front of the marketplace. Users find them by name or by browsing. No middleware required.

### Forge — an opinionated workflow

A *forge* is a method for a class of work. It typically ships skills (markdown), often coordinates with other forges, and is most useful in clusters. Examples: `foss-forge`, `ship-forge`, `security-forge`, `mcp-forge`, `test-forge`, `scribe`, `brand-forge`. Signals (any one is sufficient):

- `ships_skills` — distributes `skills/<name>/SKILL.md` files, not just MCP tools
- `opinionated_workflow` — encodes a specific way of doing the job, not a primitive
- `coordinates_with_other_forges` — most valuable in combination (`foss-forge` + `security-forge` for audits; `ship-forge` + `test-forge` for releases)

Forges live both flat in `marketplace.json` *and* are surfaced through `forge-forge`'s recommender (see below). Users get two paths to find them: direct browse, or contextual recommendation.

### Gateway — the front door

A *gateway* is a progressive-reveal entry point to the broader Eidos ecosystem. It asks the user what they're trying to do and recommends a coherent starter set — which may span tools, forges, and even non-marketplace pointers (other Eidos repos like `helios`, `omni`, `eidos-v5`). Gateways are skill-only: no MCP server, no PyPI package, just a `SKILL.md` that knows how to interview and recommend. Example: `eidos-install`. Signals (any one is sufficient):

- `progressive_reveal` — interviews the user before recommending; doesn't dump a catalog
- `cross_ecosystem_pointers` — can recommend repos and services beyond the marketplace
- `delegates_to_recommenders` — hands off to forge-specific recommenders (e.g., `forge-forge`) for deeper drill-down

Gateways live as headline entries on the marketplace front. They are the recommended first install for users who don't yet know what they want.

### Onboarding vs Discovery vs Installation — three separate layers

This is the design that prevents any single recommender (`eidos-install` or `forge-forge`) from becoming a point of failure for the ecosystem:

```
ONBOARDING LAYER    eidos-install (skill-only gateway)
                    /eidos-install asks "what are you doing?" and
                    recommends a coherent starter set, then hands off
                    to the discovery layer for ongoing exploration.
                              │
                              ▼
DISCOVERY LAYER     marketplace.json — the source of truth
                    (lists every plugin: tool, forge, or gateway)
                              │
                              ├──── direct browse (this README, AUDITS/)
                              │
                              └──── forge-forge (forge-specific recommender)
                                     reads marketplace.json's x-eidos.recommend
                                     blocks and produces contextual suggestions
                              │
                              ▼
INSTALLATION LAYER  claude plugins install <name>
                    (Claude Code's normal install flow — the only install path)
```

Both `eidos-install` and `forge-forge` are **recommenders**, not **package managers**. Neither installs anything itself; both produce install commands the user (or Claude Code) executes through the normal install flow.

**Consequences of this separation:**

1. **No single point of failure.** If `eidos-install` is broken, `forge-forge` still works. If both are broken, every plugin is still installable directly via `claude plugins install <name>`. The marketplace's flat listing is always the ultimate fallback.
2. **No version divergence.** Recommenders never pin versions; they always defer to whatever `marketplace.json` currently advertises. There is no parallel registry to drift out of sync.
3. **No privileged install path.** `eidos-install` and `forge-forge` are entries in `marketplace.json` like any other plugin. They hold no special permissions, and their recommendations derive purely from public `x-eidos.recommend` blocks.
4. **Audit trail intact.** Every recommendation shows audit grades inline, so the user sees STANDARD.md's verdict before deciding to install.

### Bar additions per kind

Beyond the [three-layer bar](#the-bar--three-layers), each kind has additional requirements:

| Kind | Requirement | Why it matters |
|---|---|---|
| Tool | `x-eidos.kind.signals` populated with at least one of `single_capability`, `uvx_shim`, `mcp_server` | Lets agents and indexers route correctly |
| Forge | `x-eidos.recommend` block populated with `for_projects`, `pairs_with`, and (if applicable) `preflight_check` | `forge-forge` needs structured hints to recommend; missing hints = invisible to the recommender |
| Forge | Directly installable as fallback: `claude plugins install <forge-name>` works without any recommender | Graceful degradation; recommenders are optional middleware, not the install path |
| Gateway | Skill-only (no MCP server, no PyPI dependency); shipped via `github` source | Keeps the front door light and trivially installable |
| Gateway | Skill content is interview-driven (asks before recommending) and shows audit grades inline | A gateway that dumps a catalog isn't progressive reveal — it's a directory |
| Gateway | Documents which recommenders it delegates to (e.g., `eidos-install` → `forge-forge` for forge-specific drilldown) | Keeps the layering legible; prevents one gateway from absorbing the whole ecosystem |

If a plugin can't be installed directly without its own recommender, it doesn't ship.

---

## Dogfooding — the marketplace maintains itself with its own plugins

The marketplace lists `foss-forge`, `ship-forge`, `security-forge`, `scribe`, `visionlog`, and others. Those plugins exist precisely because Eidos AGI's maintenance operations need them. So **the marketplace's own maintenance must run through them.** No bypassing, no parallel manual workflow. If a marketplace plugin is the right tool for an internal job, it is the only tool for that job.

Concretely:

| Operation | Plugin used | Status |
|---|---|---|
| First-time onboarding | `eidos-install` (`/eidos-install`) | Gateway plugin — designed during Phase 2, shipped Phase 3 |
| Recommend forges by project context | `forge-forge` (`/forge recommend-for`) | Forge-specific recommender — shipped Phase 3 alongside `eidos-install` |
| Score a plugin against [STANDARD.md](STANDARD.md) | `foss-forge` (`/foss-check`) | Bootstrapped via self-audit, Phase 4 |
| Release a marketplace.json change | `ship-forge` (`/ship`) | Once onboarded |
| Security-audit a plugin's source repo | `security-forge` (`/secaudit`) | Once onboarded |
| Open and triage marketplace issues | `eidos-mail`, `ike` | Already available |
| Record a marketplace governance decision | `visionlog` (ADR) | Already available |
| Re-test marketplace.json schema validity | `test-forge` | Once onboarded |

This creates a forcing function:

1. **The marketplace cannot run a foss-check audit until `foss-forge` is itself a marketplace plugin in good standing.** Bootstrap order: `forge-forge` (gateway/recommender) is onboarded first; then `foss-forge` is onboarded; then `foss-forge` audits itself; then it audits everyone else. If `foss-forge` can't self-audit to grade ≥B, we can't trust its audits of others. See [PHASES.md](PHASES.md) Phase 3.
2. **Audit results publish to two interfaces simultaneously.** Machine-readable: the `x-eidos.audit` block in `marketplace.json` (filterable by agents and external indexers). Human-readable: `AUDITS/<name>.md` with the foss-check output verbatim plus a one-paragraph summary. Both carry `audited_by` + `audit_version`, so re-runs are comparable across versions.
3. **A marketplace plugin that breaks in production breaks marketplace operations.** Self-interest aligns with quality. We feel our own bugs first.

The marketplace is not just a directory of plugins. It is the **first customer** of every plugin it lists. Plugins that don't support the marketplace's own maintenance get pulled — not because they're bad in the abstract, but because they fail the proof: *the people who built it use it*.

---

## The negative rule

The thesis is "trust through visibility." The negative rule that follows: **never commit something to this marketplace that you wouldn't want a stranger to read.** Every commit, every plugin entry, every audit. The bar isn't "no embarrassments" — it's "this is what good looks like."
