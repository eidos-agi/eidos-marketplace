# Audit: russianpencil

## 2026-07-16 — Grade: PENDING

- Community Health: PENDING — run foss-forge or the marketplace audit workflow.
- Agentic Quality: PENDING — run Felix plugin doctor and skill checks.
- Engineering: PENDING — verify install smoke evidence. Skill-only plugin; no MCP server, no runtime, no dependencies.
- Notes: Authored in-repo (marketplace-native, no upstream source repo). Claude host only — `.codex-plugin`/`.grok-plugin` deliberately skipped; add when a non-Claude host actually wants it.

### Self-descent (dogfood)

Per STANDARD.md's dogfooding rule, the plugin was run against itself before publishing.

- **Stripped requirement:** notice, at the moment of flinching, whether a thing is genuinely complicated or only looks it.
- **Obvious path:** this plugin — a few hours, one marketplace slot, ~nil carry (prose only, nothing to break).
- **Classes priced:** (a) invoked skill [this]; (b) always-on hook, ponytail-style; (c) already-installed generalist challengers — `rhea_simplify`, `rhea_challenge`, `pal challenge`; (d) null — do nothing, keep flinching.
- **Verdict:** `NO PENCIL` — nothing is 10x cheaper. Class (c) is the strongest rival and was the near-miss: rhea is installed and free. It loses on method, not price — no stripped requirement, no cost table, no null class, and no verdict it is willing to give you that you did not want. Class (b) was rejected on contradiction: a hook cannot fire on "whoa, wtf" because the flinch is human and undetectable from tool calls.
- **Known ceiling:** invoked-only, so it is bounded by the user remembering to reach for it. Fails silently in exactly the cases where excitement, not intimidation, is driving the build — ponytail's territory, deliberately left there.
