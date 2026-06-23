---
name: challenge-market-overfit
description: Challenge whether a Zoltar prediction, product idea, plugin, workflow, category framing, or architecture is overfit to existing market patterns. Use when Daniel asks for a Challenger Matrix, anti-consensus review, category redefinition, frontier user needs, non-consensus futures, Doubter voice, or whether an answer is too derivative, market-shaped, competitor-shaped, or copied from current agent/product patterns.
---

# Challenge Market Overfit

Use this when Zoltar must challenge the present, not only research it.

## Purpose

Force Zoltar to distinguish between:

- What the market already rewards.
- What the market currently misunderstands.
- What users say they want.
- What users will actually need later.
- What existing tools make easy.
- What a genuinely better future would require.

## Three Voices

- Researcher: "What does the evidence say?"
- Forecaster: "What futures are likely?"
- Doubter: "Are these futures too constrained by what already exists?"

The Doubter is adversarial but constructive. It attacks lazy extrapolation, derivative thinking, weak assumptions, category overfit, and market availability bias. It does not reject research or novelty for sport.

## Challenger Questions

Ask the relevant subset:

- Are we copying the category, or redefining it?
- Is this prediction based on evidence, or just market availability bias?
- Are we assuming current UX patterns are inevitable?
- Are we optimizing for what people already understand instead of what they will need?
- Are we mistaking competitor precedent for truth?
- Are we predicting a local maximum rather than a better system?
- What would this look like if no existing product category constrained us?
- What would be obvious in three years but non-obvious today?
- What would Daniel likely reject as too derivative?
- What would a frontier user need that the market has not yet priced in?

## Required Matrix

```json
{
  "challenger_matrix": {
    "market_consensus": [],
    "consensus_risk": "",
    "hidden_assumptions": [],
    "overfit_signals": [],
    "non_consensus_possibilities": [],
    "frontier_user_needs": [],
    "category_redefinition": "",
    "doubter_verdict": "proceed | revise | invert | delay | reject",
    "anti_overfit_change_today": []
  }
}
```

## Field Rules

- `market_consensus`: existing tools, competitors, common patterns, best practices, GitHub examples, plugin conventions, or startup/product precedents.
- `consensus_risk`: why following consensus may produce a mediocre, derivative, fragile, or already-obsolete answer.
- `hidden_assumptions`: unstated premises behind the proposed path.
- `overfit_signals`: evidence that the answer is too shaped by existing market examples.
- `non_consensus_possibilities`: less obvious futures or designs that may be more correct.
- `frontier_user_needs`: needs advanced users will have before the broad market catches up.
- `category_redefinition`: one concise statement of how Eidos should define the category differently.
- `doubter_verdict`: one of `proceed`, `revise`, `invert`, `delay`, or `reject`.
- `anti_overfit_change_today`: concrete edits or actions that prevent copying the current market.

## Verdict Guidance

- `proceed`: research and forecast are grounded, and consensus risk is low.
- `revise`: the direction is useful, but framing or implementation is too derivative.
- `invert`: the market pattern points the wrong way; the better answer reverses it.
- `delay`: the right move depends on missing evidence or authority.
- `reject`: the proposal mainly copies a flawed present and should not ship.

## Output Rules

- Name at least one non-consensus possibility when market, category, competitor, plugin, or UX precedent affects the decision.
- If `doubter_verdict` is not `proceed`, `anti_overfit_change_today` must include at least one concrete change.
- Do not use generic warnings like "consider innovation" or "avoid groupthink."
- Tie overfit claims to inspected evidence or explicitly mark them as assumption-backed.

## Bad Output

```json
{
  "consensus_risk": "The product may be too similar to others.",
  "anti_overfit_change_today": ["Be more innovative."]
}
```

## Good Output

```json
{
  "market_consensus": [
    "Most plugin marketplaces present tools as installable capabilities with short descriptions.",
    "Most agent systems split tasks into planner, executor, and verifier roles."
  ],
  "consensus_risk": "If Zoltar is framed as just another plugin skill, it will be interpreted as a prompt pack instead of a decision primitive.",
  "hidden_assumptions": [
    "That future prediction belongs inside a tool marketplace.",
    "That validation and foresight should be separate optional steps.",
    "That users want to invoke Zoltar manually."
  ],
  "overfit_signals": [
    "The output risks becoming a generic risk checklist.",
    "The framing resembles existing agent/plugin marketplace patterns."
  ],
  "non_consensus_possibilities": [
    "Make Zoltar a mandatory foresight layer before high-impact changes.",
    "Make Zoltar emit machine-readable challenge packets consumed by doer/checker agents.",
    "Treat Zoltar as an epistemic governor, not a plugin."
  ],
  "frontier_user_needs": [
    "Agents that challenge the user's framing without losing obedience.",
    "Systems that prevent derivative architecture before code is written.",
    "Memory-aware prediction of future dissatisfaction."
  ],
  "category_redefinition": "Zoltar is not a prediction plugin. It is an anti-overfit foresight governor for agentic systems.",
  "doubter_verdict": "revise",
  "anti_overfit_change_today": [
    "Add challenger_matrix to the required output schema.",
    "Add explicit anti-consensus checks to the skill instructions.",
    "Require Zoltar to name at least one non-consensus alternative before final recommendation."
  ]
}
```
