# Audit: cept

Source repo: [eidos-agi/cept](https://github.com/eidos-agi/cept) — also on PyPI as `cept` v0.1.0.

## 2026-04-28 — Grade: A

`audited_by: by-hand (foss-forge not yet onboarded)` · `audit_version: STANDARD.md@2026-04-28` · `next_audit: 2026-07-28`

This is the inaugural marketplace audit. It is by hand because the audit instrument (`foss-forge`) is itself queued for Phase 4 onboarding. When `foss-forge` ships, this audit will be re-run via `/foss-check` and the header will update to `audited_by: foss-forge@<version>`. See [PHASES.md](../PHASES.md) Phase 4.

### Layer 1 — Community Health: **PASS**

| Requirement | Verdict | Evidence |
|---|---|---|
| `LICENSE` exists, OSI-approved | PASS | MIT, root of repo |
| `README.md` ≥20 lines, install + usage example | PASS | 40+ lines visible; install via `uv sync`, usage examples for all four modes (`steer`, `debug`, `research`, `architecture`) |
| `CHANGELOG.md` follows Keep a Changelog | PASS | Header explicitly references [keepachangelog.com](https://keepachangelog.com/en/1.1.0/); `[Unreleased]` + `[0.1.0] - 2026-04-27` sections; semver via [semver.org](https://semver.org) |
| `CONTRIBUTING.md` with dev setup | PASS | Present at repo root |
| `CODE_OF_CONDUCT.md` with enforcement contact | PASS | Present at repo root |
| `SECURITY.md` with vuln reporting + threat model | PASS | `daniel@eidosagi.com` reporting address; thorough threat-model section covering `.ceptkey` walk-up trust and redactor coverage limits |

### Layer 2 — Agentic Quality: **PASS**

| Requirement | Verdict | Evidence |
|---|---|---|
| Every `@tool` description ≥20 chars explaining *when* to use it | PASS | The single `cept` tool has a multi-line description naming the use cases ("when stuck, looping, or facing a low-confidence architectural choice") |
| Every parameter has typed schema and description | PASS | Verified in `pyproject.toml`-declared MCP server: `goal`, `cept_id`, `lookback_minutes`, `mode`, `question`, `session_id`, `include_repo_state`, `include_diff`, `max_events`, `model` — all typed (Pydantic), all with description fields |
| Error returns are actionable | PASS (provisional) | Returns include `decision`, `confidence`, `facts_to_verify`, and `recommended_next_step` so an agent can act on them. Provisional because we haven't seen all error paths in practice yet — Phase 2 friction journal will catch any bare-string failures. |
| Tool count ≤25 per server | PASS | 1 tool (`cept`) |
| MCP entry point in `pyproject.toml` | PASS | `[project.scripts]` declares `cept = "cept.server:main"` |

### Layer 3 — Engineering: **PASS**

| Requirement | Verdict | Evidence |
|---|---|---|
| `pyproject.toml` complete | PASS | name, version, description, license (MIT), classifiers (5 trove), keywords (6 entries), `[project.urls]` with Homepage/Repository/Issues/Changelog |
| ≤5 direct dependencies | PASS | 3: `mcp>=1.2.0`, `httpx>=0.27.0`, `pydantic>=2.7.0` |
| Hatchling build backend | PASS | `build-backend = "hatchling.build"` |
| CI runs lint + format + tests on Python 3.11/3.12/3.13 | PASS | `.github/workflows/ci.yml` matrix is exactly `["3.11", "3.12", "3.13"]`; runs `ruff check`, `ruff format --check`, and `pytest` |
| OIDC trusted publisher for PyPI | PASS | `.github/workflows/publish.yml` uses `pypa/gh-action-pypi-publish@release/v1` with `id-token: write` and `environment: pypi`. Triggered on `v*` tags. No long-lived `PYPI_TOKEN` secret. |
| Tag-driven release | PASS | `on: push: tags: ["v*"]` — `git tag v0.1.0 && git push --tags` triggers PyPI publish |

### Tool/Forge bar additions

cept is `kind.type: "tool"` with signals `["single_capability", "uvx_shim", "mcp_server"]`. The Tool bar requires at least one of those signals; cept has all three. PASS.

### Round-trip install test

| Action | Result |
|---|---|
| `python tools/test_plugins.py cept` (functional MCP handshake test) | PASS — server starts, responds to MCP `initialize` in 1.6s, capabilities advertised |
| `claude plugins install cept@eidos-marketplace` from a fresh Claude Code session | **PENDING** — requires a fresh session to verify the marketplace round-trip; will be ticked once Daniel runs the install end-to-end |

### Notes

- cept is the inaugural plugin audited under this standard. It clears every requirement on the first pass, which validates the bar is achievable but not trivial — cept's source repo received deliberate community-health investment before this listing.
- The threat model in `SECURITY.md` is unusually thorough for a v0.1.0 — it explicitly names the `.ceptkey` walk-up trust attack and the redactor's pattern-based coverage limits, with a concrete mitigation (`cept-cli --dry-run`). This is a model for what other plugin SECURITY.md files should look like.
- The single-tool surface (`cept`) keeps Layer 2 trivially compliant. Multi-tool plugins (`forge-forge`, `eidos-mail`, etc.) will need more careful Agentic Quality scoring when they're audited.
- "Error returns are actionable" graded provisional because the cept tool has been called four times in this session without observed error paths. If Phase 2 reveals a failure mode where cept returns an unhelpful error, downgrade this row and re-audit.
- This audit will be re-run via `/foss-check` once `foss-forge` is onboarded (Phase 4), and the header will update accordingly. The grade is expected to remain A.
