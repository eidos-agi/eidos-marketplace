---
name: anti-slop
description: >
  Produce human-sounding prose that avoids detectable AI writing patterns.
  Use when writing or rewriting any reader-facing text: case studies, emails,
  docs, posts, briefs. Also when user says anti-slop, no AI slop, make this
  sound human, or not AI. Load banned-words from package references/ when drafting.
---

# Anti-slop (write)

Generate natural, direct prose. Kill predictable LLM style.

**This skill constrains generation.** For post-draft review use `anti-slop-audit`.  
For Northstar case-study structure use `world-class-case-study`.

## Before writing

Read [references/banned-words.md](../../references/banned-words.md) if available in the package. Never use listed words or phrases. Prefer concrete specifics.

House composite merges community upstreams (jalaalrd, adewale, petergyang) plus Eidos overrides. After `./scripts/sync-upstream.sh`, the list regenerates with provenance tags.

## Structural rules

- **No rule of three by default.** Use 1, 2, or 4 unless content truly has three items.
- **Vary sentence length.** No three consecutive same-length sentences.
- **No parataxis stacks.** Don't chain punchy fragments unless they earn it. Connect thoughts.
- **No false contrast.** Avoid "It's not X, it's Y" / "not just X but Y" unless the contrast is load-bearing and true.
- **No hedging seesaw.** Pick a side; one counterpoint sentence max.
- **No corporate pep talk.** Admit friction, uncertainty, cost.
- **Active voice.** Prefer "the team shipped X" over "X was shipped."
- **Specifics over adjectives.** Numbers, names, mechanisms — not "robust" or "seamless."
- **Em dashes:** at most one per ~500 words. Prefer commas, parentheses, new sentences.
- **End on a concrete detail or action**, not a bright summary paragraph.

## Voice

Default: direct, slightly informal, contractions, trusts the reader. Match the user's voice when known.

## Silent self-check before output

1. Banned words/phrases?
2. Three-in-a-row same-length sentences?
3. Artificial threes?
4. Em-dash pile?
5. Generic opener restating the prompt?
6. Motivational closer?
7. Could any AI write this for any person? → add something specific.

Apply silently. Do not mention the skill or "as per guidelines."

## Case studies

If writing shelf HTML or long case-study prose, also load **world-class-case-study**. Do not turn the essay into a filled template. Multi-model boards and full archive detail belong in the pack/appendix, not the face of the prose.
