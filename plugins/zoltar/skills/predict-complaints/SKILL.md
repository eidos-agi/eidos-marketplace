---
name: predict-complaints
description: Predict the specific future user complaint, regret, or trust failure a change is likely to trigger, grounding each complaint in inspected evidence and converting the top complaint into concrete preventive changes. Use when Daniel asks what he will complain about, what future user objection is likely, or how to prevent a poor future before shipping.
---

# Predict Complaints

Predict the complaint that matters, not a generic list of concerns.

## Complaint Formula

Use this shape:

```text
Daniel will object that <specific behavior> because <evidence-backed mismatch>.
```

Examples:

- "Daniel will object that this is a local-only scaffold instead of an Eidos Store plugin."
- "Daniel will object that Teams is described as ready even though it is only a stale indexed cache."
- "Daniel will object that this copies current agent marketplace language instead of defining an Eidos-native primitive."

## Workflow

1. Inspect the current implementation or plan.
2. Identify the user's explicit preferences and prior corrections.
3. Predict 1-3 likely complaints.
4. Rank the top complaint by probability and impact.
5. Check whether the top complaint is about being derivative, consensus-shaped, or overfit to the current market.
6. Convert the top complaint into a preventive change today.

## Overfit Complaint Check

When a product, plugin, agent, workflow, UX, or architecture uses market/category precedent, ask:

- Would Daniel reject this as too derivative?
- Are we making what existing tools make easy instead of what the better future needs?
- Is the complaint really "this works, but it is the wrong category"?

If yes, include the Challenger Matrix or route to `challenge-market-overfit`.

## Avoid

- "Users may want better UX."
- "Consider scalability."
- "Security could be an issue."

Those are not complaints. Name the actual future sentence the user will say.
