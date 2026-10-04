# Grok Goals marketplace publish

## 2026-10-04 Publish

- **What changed:** Prepared the public grok-goals source (MIT community files, Claude and Grok plugin manifests, stdio `.mcp.json`, license field, `private` removed) and published it with `tools/marketplace_publish.py`. Extended the publisher whitelist with `package.json`, `package-lock.json`, `tsconfig.json`, `.gitignore`, `DESIGN.md`, `schema/`, and `examples/`. Example-pack `*.jsonl` journals are copied. `node_modules`, `dist`, and `.git` stay out.
- **Why:** The publish script copies a whitelist. A first publish dropped the Node install and build files, so `npm install` and `tsc` could not run from the marketplace tree. `GROK_GOALS_PACK` is documented as a local installer path. The default is an empty pack. No `data/` directory and no live goal documents are committed. The files under `examples/grok-goals.prim` are the fictional demo pack from the source archive.
- **Supporting Research:** Compared `plugins/apple-a-day`, `plugins/cept`, and `plugins/clawdflare` community files and manifests. Confirmed the drop by running `publish` before editing `BUNDLE_ITEMS`.

## 2026-10-04 Check

- [x] `python tools/marketplace_publish.py check grok-goals --source <source>` reported OK after the whitelist change.
- [x] `pytest tests/test_marketplace_publish.py` — 14 passed.
- [x] Copied `plugins/grok-goals` to a temp directory: `npm ci`, `npm test` (7 passed), `npm run build`. `dist/` stayed out of git.
