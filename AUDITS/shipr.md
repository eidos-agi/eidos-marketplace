# Audit: shipr

## 2026-06-11 — Grade: PENDING

- Community Health: PENDING — run foss-forge or the marketplace audit workflow.
- Agentic Quality: PENDING — run Felix plugin doctor and MCP/skill checks.
- Engineering: PENDING — verify package, CI, release, and install smoke evidence.
- Notes: Published into eidos-marketplace from `https://github.com/eidos-agi/shipr`; audit must be completed before grading.

## 2026-06-11 — Local Store Ship And Self-Use

### What Shipped

Shipr is now a source-owned Eidos plugin at `/Users/dshanklin/repos-eidos-agi/shipr`.
It ships a zero-dependency CLI plus an agent skill:

- `shipr model`: detect and optionally write a product release model
- `shipr attempt`: record a release attempt with status, notes, and proofs
- `shipr frontier`: report the current release frontier

### Store Proof

- Source tests: `uv run --python 3.12 --with pytest --with ruff pytest -q` -> `4 passed`
- Source lint: `uv run --python 3.12 --with pytest --with ruff ruff check .` -> pass
- Source format: `uv run --python 3.12 --with pytest --with ruff ruff format --check .` -> pass after formatting
- CLI smoke: `uv run --python 3.12 shipr --version` -> `shipr 0.1.0`
- Marketplace publish: `python3 tools/marketplace_publish.py publish /Users/dshanklin/repos-eidos-agi/shipr --audit-date 2026-06-11` -> `shipr: OK`
- Source-to-store check: `python3 tools/marketplace_publish.py check shipr --source /Users/dshanklin/repos-eidos-agi/shipr` -> OK
- Marketplace tests: `python3 -m pytest tests/test_marketplace_publish.py -q` -> `9 passed`
- Codex visibility before install: `codex plugin list --marketplace eidos-agi` -> `shipr@eidos-agi (not installed)`
- Codex install: `codex plugin add shipr@eidos-agi` -> installed to `/Users/dshanklin/.codex/plugins/cache/eidos-agi/shipr/0.1.0`
- Codex installed state: `shipr@eidos-agi (installed, enabled)`

### Publisher Fix

During this release, Shipr exposed that `tools/marketplace_publish.py` ignored
`.eidos-plugin.json` `recommend` overrides for forges. The publisher now
preserves the override, and `tests/test_marketplace_publish.py` covers this
case. Shipr's marketplace recommendation now pairs with:

- `forge-forge`
- `ship-forge`
- `security-forge`
- `foss-forge`
- `learning-forge`
- `loss-forge`

### Shipr Used On Itself

After installation from the Eidos marketplace, the installed Shipr package was
used against the Shipr source repo:

```bash
uv run --python 3.12 --project /Users/dshanklin/.codex/plugins/cache/eidos-agi/shipr/0.1.0 \
  shipr model --project /Users/dshanklin/repos-eidos-agi/shipr \
  --description "Shipr local Eidos marketplace release and self-use bootstrap" \
  --write --json

uv run --python 3.12 --project /Users/dshanklin/.codex/plugins/cache/eidos-agi/shipr/0.1.0 \
  shipr attempt --project /Users/dshanklin/repos-eidos-agi/shipr \
  --goal "ship Shipr into the Eidos marketplace and use it on itself" \
  --status shipped \
  --notes "Local Eidos marketplace bundle published, Codex installed and enabled; public remote push/tag not performed." \
  --proof "shipr: OK" \
  --proof "tests/test_marketplace_publish.py: 8 passed" \
  --proof "codex plugin list --marketplace eidos-agi: shipr@eidos-agi installed, enabled" \
  --proof "source pytest: 4 passed" \
  --json
```

Self-use artifacts:

- `/Users/dshanklin/repos-eidos-agi/shipr/.shipr/product-release-model.json`
- `/Users/dshanklin/repos-eidos-agi/shipr/.shipr/release-attempts/20260611T191911Z-ship-shipr-into-the-eidos-marketplace-and-use-it-on-itself.json`

### Remaining Release Frontier

- Public GitHub repo/remote was not created or pushed in this run.
- PyPI release was not tagged or published.
- Shipr needs a real learning integration next: route release outcomes into
  `learning-forge` and preserve cross-product failure patterns.
- Shipr should add adapters for common product shapes beyond Python/plugin
  packages: web apps, signed Mac apps, service deploys, document releases, and
  ops workflows.
