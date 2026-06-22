# Audit: apple-a-day

## 2026-06-11 — Grade: PENDING

- Community Health: PENDING — run foss-forge or the marketplace audit workflow.
- Agentic Quality: PENDING — run Felix plugin doctor and MCP/skill checks.
- Engineering: PENDING — verify package, CI, release, and install smoke evidence.
- Notes: Published into eidos-marketplace from `https://github.com/eidos-agi/apple-a-day`; audit must be completed before grading.

## 2026-06-11 — Forge-Forge release packet

### Classification

- Marketplace kind: `tool`
- Signals: `single_capability`, `uvx_shim`
- Primitive: proof and local machine health observability
- Safe boundary: read-only diagnostics by default; launchd monitor install/uninstall changes local service state; cleanup fixes remain recommendations until explicitly approved.

### Forge-Forge routing

Forge-Forge selected these release companions for this task:

- `ship-forge`: release hygiene, source-to-store verification, install smoke proof
- `security-forge`: pre-release secret and local-action boundary scan
- `foss-forge`: public FOSS quality, PyPI release readiness, launch hygiene

Forge-Forge project-specific routing for `/Users/dshanklin/repos-eidos-agi/apple-a-day`
also recommended:

- `loss-forge`: add explicit health/outcome scores so AAD can measure whether changes improve Mac cleanup outcomes
- `improve-forge`: systematic project scoring and highest-impact next improvement selection
- Optional: `brutal-forge`, `demo-forge`, and `learning-forge`

The Forge-Forge MCP tool was unavailable in this Codex run because it looked for
`registry.yaml` inside a `uv` archive path. The canonical Forge-Forge CLI was
used instead from `/Users/dshanklin/repos-eidos-agi/forge-forge`.

### Proof

- Source checkout: `/Users/dshanklin/repos-eidos-agi/apple-a-day`
- Source commit inspected: `4713aa3322ad3a5731e9e9fd0b2db03d3cefb4ed`
- Source tests: `uv run --python 3.12 --with pytest pytest -q` -> `42 passed in 111.69s`
- Source lint: `uv run --python 3.12 --with ruff ruff check .` -> pass
- Source format: `uv run --python 3.12 --with ruff ruff format --check .` -> pass
- CLI smoke: `uv run --python 3.12 aad --version` -> `apple-a-day 0.3.1`
- Schema smoke: `uv run --python 3.12 aad schema | python3 -m json.tool` -> valid JSON
- Source-to-store check: `python3 tools/marketplace_publish.py check apple-a-day --source /Users/dshanklin/repos-eidos-agi/apple-a-day` -> OK
- Forge-Forge project routing: `forge for-project --path /Users/dshanklin/repos-eidos-agi/apple-a-day --description "Release apple-a-day as an Eidos marketplace plugin and public Mac diagnostics package"` -> recommends `loss-forge`, `improve-forge`, `foss-forge`, `security-forge`, and `ship-forge`
- Marketplace tests: `python3 -m pytest tests/test_marketplace_publish.py -q` -> `8 passed`
- Codex visibility: `codex plugin list --marketplace eidos-agi` -> `apple-a-day@eidos-agi (not installed)` before install
- Codex install smoke: `codex plugin add apple-a-day@eidos-agi` -> installed to `/Users/dshanklin/.codex/plugins/cache/eidos-agi/apple-a-day/0.3.1`
- Codex installed state: `apple-a-day@eidos-agi (installed, enabled)`
- PyPI smoke: `uvx --from apple-a-day aad --version` -> `apple-a-day 0.3.1`
- Live critical check: `uvx --from apple-a-day aad checkup --json --min-severity critical --fields severity,summary,fix` -> valid JSON with three critical local findings and zero errors

### Release frontier

- Commit the `apple-a-day` source packaging changes first.
- Commit the marketplace bundle and listing changes separately, preserving unrelated in-flight marketplace work for `kai`, `lever`, `pavo`, and `converge`.
- Run `security-forge sec-scan` or equivalent secret scan before pushing.
- Run the source repo's `ship/README.md` preflight before any PyPI tag.
- Do not tag a new PyPI release unless the version is bumped beyond `0.3.1`; the current store bundle points at the existing public package version.
