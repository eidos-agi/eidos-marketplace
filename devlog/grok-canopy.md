# Grok Canopy marketplace publish

## 2026-10-04 Publish

- **What changed:** Prepared the public grok-canopy 0.1.0 source (MIT LICENSE, CHANGELOG, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT, Claude and Grok plugin manifests, skill `use-grok-canopy`) and published it with `python tools/marketplace_publish.py publish`. `scripts/check.py` is the attached parent-pointer check. `scripts/store/botscore.json` is the attached BotScore store.
- **Why:** The marketplace publish script reads `.grok-plugin/plugin.json` or `.claude-plugin/plugin.json` and writes the listing into `.grok-plugin/marketplace.json`, `.claude-plugin/marketplace.json`, and `.agents/plugins/marketplace.json`. It does not read a `.cursor-plugin` file. grok-goals 0.1.0 shipped the same community files and the same publish path. No Grok Bot catalog number is invented. Goal packs stay out.
- **Supporting Research:** `plugins/grok-goals` on `origin/main` (`15de6ee`) and `tools/marketplace_publish.py`. Parent map: 123 children plus Grok Bot, max depth 3, 11 wake cases pass, no cycle. BotScore: version 1, 124 bots, 18 at score 0, penalties 40/40/30/30 from a base of 100 floored at 0, wake penalty 0, token burn excluded. Published bytes match the attachments.

## 2026-10-04 Check

- [x] `python tools/marketplace_publish.py publish /tmp/grok-canopy-src --audit-date 2026-10-04` printed `published grok-canopy`.
- [x] `python tools/marketplace_publish.py check grok-canopy --source /tmp/grok-canopy-src` reported OK.
- [x] `cmp` of `plugins/grok-canopy/scripts/check.py` and `plugins/grok-canopy/scripts/store/botscore.json` against the attachments matched.
- [x] `python3 -m pytest tests/test_marketplace_publish.py tests/test_plugin_tester.py` — 21 passed.
- [x] `python3 tools/test_plugins.py grok-canopy` — SKIP, no `.mcp.json`. The canopy ships a check and a store.
