---
name: anti-slop-audit
description: >
  Audit prose for AI-generated patterns. Returns a punch list with file:line
  refs, category, offending phrase, and rewrite suggestion. Use after drafting
  case studies, briefs, or any recipient-facing writing; before shipping shelf
  HTML; when prose feels off. Alias of the former ai-isms-filter skill, owned
  and updated under eidos-agi/anti-slop.
---

# Anti-slop audit

Post-draft **linter for AI prose**. Does not auto-rewrite. Returns a punch list.

Usage: audit the given path(s) (default: current dir markdown/html prose).

## Four passes

### 1. Lexical (LEX)

Case-insensitive scan against [references/banned-words.md](../../references/banned-words.md) and common lists:

**Verbs:** delve, dive into, deep dive, embark, unleash, unlock (figurative), harness, leverage, navigate (figurative), elevate, propel, supercharge, empower, foster, cultivate, craft (figurative).

**Nouns:** tapestry, treasure trove, plethora, myriad, journey (figurative), realm, landscape (figurative), ecosystem (figurative), paradigm, game-changer, sweet spot.

**Adjectives:** robust, seamless, comprehensive, holistic, cutting-edge, state-of-the-art, world-class, best-in-class, unparalleled, transformative, dynamic (as empty praise).

**Phrases:** "in today's [fast-paced/digital/modern] world/landscape", "it's worth noting", "it's important to note", "at the end of the day", "in conclusion", "furthermore"/"moreover" as throat-clearing.

Output: `path:line  LEX  "<phrase>"  → delete|replace`

### 2. Structural (STR)

Flag (lean toward false positives — cheap):

| Pattern | Tell |
|---------|------|
| Reveal two-beat | "X isn't Y. It's Z." |
| Parallel maxim | "It's not about A. It's about B." |
| Not only / but also | padding contrast |
| Triplet staccato | three short declarative sentences in a row |
| Triadic stack | exactly three adjectives for flourish |
| Em-dash reveal | word — reframe clause |
| Sweep | "From X to Y" without specifics |
| Filler transitions | "Now that we've explored…" |

Output: `path:line  STR  <name>  "<excerpt>"  → suggestion`

### 3. Tonal (TON)

Judgment pass:

- Sanctimonious lesson the reader didn't ask for
- Audience positioned as catching up
- Enthusiasm standing in for evidence
- Vague gesture instead of concrete claim

### 4. Content (CON)

- Hollow generalization true of any domain
- Faux contextualization openers
- Strawman "many think X" without naming who
- Filler hedging before saying nothing

## Output format

```
<path>:<line>  <LEX|STR|TON|CON>  <pattern>
  "<excerpt>"
  → <fix or direction>
```

End with: `N findings across M files (LEX:a STR:b TON:c CON:d)`.

## Calibration

- Technical docs tolerate more structure; recipient-facing prose less.
- "X isn't Y. It's Z." is fine for a real counterintuitive fact; flag when decorative.
- This audit is a **ship gate for prose**, not a substitute for world-class-case-study structure or human intent lock.
