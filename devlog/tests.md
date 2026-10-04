# Tests

## 2026-10-04 grok-canopy publish

- **What changed:** Ran the marketplace publish tests and the plugin smoke tester against grok-canopy 0.1.0. Re-checked the published parent map and BotScore file against the attachments.
- **Why:** Confirm `marketplace_publish.py check` stays OK, the new listing does not break the marketplace tests, and the attached check and store are unchanged.
- **Supporting Research:** `python3 -m pytest tests/test_marketplace_publish.py tests/test_plugin_tester.py` — 21 passed. `python3 tools/test_plugins.py grok-canopy` — SKIP, no `.mcp.json`. Parent map: 124 bots, max depth 3, 11 wake cases pass. BotScore: version 1, 124 bots, 18 at score 0. `cmp` against the attachments matched.

## 2026-10-04 grok-goals publish

- **What changed:** Ran the marketplace publish tests and the published plugin's own npm suite from a copy of `plugins/grok-goals`.
- **Why:** Confirm the whitelist publish still checks OK and that `npm ci`, `npm test`, and `npm run build` work without a committed `data/` pack.
- **Supporting Research:** `python3 -m pytest tests/test_marketplace_publish.py` — 14 passed after allowing the fictional example journals and the pre-existing emux jsonl fixtures. `npm test` — 7 passed. `npm run build` wrote `dist/index.js` in the temporary copy only.
