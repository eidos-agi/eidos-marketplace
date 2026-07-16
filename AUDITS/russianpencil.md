# Audit: russianpencil

## 2026-07-16 — Grade: PENDING

- Community Health: PENDING — run foss-forge or the marketplace audit workflow.
- Agentic Quality: PENDING — run Felix plugin doctor and skill checks.
- Engineering: PENDING — verify install smoke evidence. Skill-only plugin; no MCP server, no runtime, no dependencies.
- Notes: Authored in-repo (marketplace-native, no upstream source repo). Claude host only — `.codex-plugin`/`.grok-plugin` deliberately skipped; add when a non-Claude host actually wants it.

### Self-descent (dogfood)

Per STANDARD.md's dogfooding rule, the skill was run on itself. It found a pencil, and the
first draft of this plugin was the space pen.

- **Task we were grinding on:** build something that decides whether a plan is too expensive.
- **Actual goal, no solution nouns:** notice when difficulty is coming from the framing rather
  than from the problem.
- **Ways to reach that goal:** (a) a keyword that changes altitude — a written first-principles
  move, invoked by saying one word; (b) an always-on hook, ponytail-style; (c) already-installed
  generalist challengers — `rhea_simplify`, `rhea_challenge`, `pal challenge`; (d) don't build
  anything — just remember to think differently in the moment.
- **Verdict:** `PENCIL: (a), the keyword.`

The first draft was a seven-step cost descent — carry vs. migration vs. sunk cost, prices to an
order of magnitude, a 10x rule, three verdicts. It was well-built and wrongly framed, which is
the exact failure it exists to catch. **Cost was never the mechanism.** Cheaper is what happens
*after* you find the easier way; pricing the options you already thought of does nothing to get
you out of the cage. Deleting the accounting made the skill both shorter and better, which is
the tell.

Rejected classes, honestly:
- **(b) hook** — contradiction. The trigger is a human going "whoa, wtf," and that flinch is not
  detectable from tool calls. A hook cannot fire on it.
- **(c) rhea** — the near-miss, and the strongest rival: installed, free, and genuinely good at
  arguing. Loses on one thing only — it has no *move*. No forced restatement of the goal without
  solution nouns, no mandatory null option, no permission to come back with "it's hard because
  it's hard." It will simplify what you show it; it will not tell you that you're looking at the
  wrong thing.
- **(d) don't build it** — argued seriously and nearly won. It loses because "remember to zoom
  out" is not a thing anyone remembers precisely when they most need to, which is while being
  excellent inside the cage.

**Known ceiling.** Invoked-only, so it is bounded by the user reaching for it. It fires on
intimidation, not excitement — so it misses the case where you are *thrilled* about the thing
you're overbuilding. That is ponytail's territory and is left there deliberately. Upgrade path,
if that gap ever bites: not a hook (see above), but a habit — someone else saying the word.
