# Tests

## 2026-10-04 grok-goals publish

- **What changed:** Ran the marketplace publish tests and the published plugin's own npm suite from a copy of `plugins/grok-goals`.
- **Why:** Confirm the whitelist publish still checks OK and that `npm ci`, `npm test`, and `npm run build` work without a committed `data/` pack.
- **Supporting Research:** `python3 -m pytest tests/test_marketplace_publish.py` — 14 passed after allowing the fictional example journals and the pre-existing emux jsonl fixtures. `npm test` — 7 passed. `npm run build` wrote `dist/index.js` in the temporary copy only.
