---
name: handoff-to-doer-checker
description: Convert Zoltar foresight findings into separate doer implementation instructions and checker validation instructions. Use when foresight needs to be handed to other agents, when Daniel asks for doer/checker splits, or when a future risk must become concrete acceptance criteria.
---

# Handoff To Doer And Checker

Use this skill to make foresight operational.

## Role Split

- Doer: changes the system to prevent the likely bad future and amplify the good future.
- Checker: validates whether the work passes, including whether the future complaint was actually prevented.
- Zoltar: decides whether the work is likely to be regretted even if it passes tests.
- Doubter: decides whether the work is too derivative, overfit to market consensus, or trapped in the wrong category.

## Handoff Shape

```json
{
  "handoff_to_doer": [
    "Make the smallest change that prevents <specific complaint>.",
    "Keep authority boundary: <source/store/runtime/etc.>.",
    "Apply anti-overfit change: <specific Challenger Matrix change>.",
    "Do not <forbidden action>."
  ],
  "handoff_to_checker": [
    "Verify <command/test/output>.",
    "Confirm <complaint> is no longer true.",
    "Confirm the work is not merely copying <market/category precedent>.",
    "Confirm no new false-confidence path was introduced."
  ]
}
```

## Doer Instructions Should Include

- Files or surfaces to edit.
- The specific bad future to prevent.
- The concrete desired future.
- Constraints and forbidden writes.
- The smallest useful implementation.
- The Challenger Matrix `anti_overfit_change_today` items when present.

## Checker Instructions Should Include

- Tests or commands to run.
- Output fields or behavior to inspect.
- Source authority/freshness checks.
- Evidence that the anti-overfit change actually changed the shipped behavior or framing.
- Regression checks for false confidence.

Do not give the checker vague criteria like "make sure it is good."
