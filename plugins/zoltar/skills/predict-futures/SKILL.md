---
name: predict-futures
description: Compatibility entrypoint for Zoltar foresight. Use when Daniel mentions Zoltar, asks to predict the future, asks for second-order effects, asks what he will complain about, or wants future-backed product/spec changes; route the work through researched evidence, judgment, structured output, doer/checker handoff, and self-improvement notes rather than generic prediction.
---

# Predict Futures

Use this as the broad Zoltar entrypoint, but do not behave like a passive prompt lens.

## Required Behavior

1. Research before predicting.
2. Ground every major prediction in inspected evidence.
3. Produce a judgment, not just a list of possibilities.
4. Emit structured output that other agents can consume.
5. Separate handoff instructions for the doer and checker.
6. Challenge whether the prediction is overfit to existing market/category patterns.
7. Note what Zoltar should learn if the prediction misses.

For the full workflow, follow the `research-futures` skill behavior.

## Default Question

Answer:

"What is likely to go wrong, what evidence supports that, what future complaint or failure are we preventing, and what should change today?"

Also answer:

"What is likely only because everyone is copying the same flawed present?"

## Required Packet

Use this packet when the user wants actionable foresight or agent handoff:

```json
{
  "question": "",
  "evidence_checked": [],
  "current_truth": [],
  "likely_futures": [
    {
      "future": "",
      "probability": "low | medium | high",
      "impact": "low | medium | high",
      "evidence": [],
      "early_warning_signals": [],
      "preventive_change": ""
    }
  ],
  "answer": "",
  "likely_user_complaint": "",
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
  },
  "change_today": [],
  "handoff_to_doer": [],
  "handoff_to_checker": [],
  "self_improvement_note": ""
}
```

If Zoltar does not change the action, say that clearly and stop adding commentary.
