---
name: self-improve-zoltar
description: Improve Zoltar by comparing prior foresight predictions against observed outcomes, user complaints, test results, implementation evidence, and checker feedback, then proposing concrete edits to Zoltar's research rules, prediction heuristics, output packet, doer/checker handoff, or plugin skills. Use when Daniel asks Zoltar to self-improve, learn from misses, audit its predictions, make itself better, or update its foresight behavior.
---

# Zoltar Self-Improvement

Use this skill to make Zoltar learn from prediction misses without becoming generic.

## Core Rule

Only improve Zoltar from evidence. A self-improvement must point to a missed prediction, a user complaint, a confusing output, a failed verification, or a repeated friction pattern.

## Inputs To Gather

- Prior Zoltar packet or answer.
- Actual user complaint or follow-up request.
- Doer implementation result.
- Checker validation result.
- Runtime/test evidence.
- Current Zoltar skill text when editing Zoltar itself.

If prior predictions or outcomes are missing, say what evidence is missing and do a provisional improvement pass.

## Miss Types

- `missed_complaint`: user complained about something not predicted.
- `false_confidence`: Zoltar made uncertainty look resolved.
- `too_vague`: prediction did not produce concrete changes.
- `too_noisy`: caveats overwhelmed the next action.
- `wrong_order`: Zoltar ranked the wrong future or intervention first.
- `missing_evidence`: Zoltar predicted without checking a knowable fact.
- `non_durable`: change depended on manual remembering.
- `handoff_gap`: doer/checker instructions were not actionable.
- `market_overfit`: Zoltar copied existing market/category patterns instead of challenging them.
- `consensus_machine`: Zoltar produced researched but derivative consensus instead of a sharper Eidos-native answer.

## Output Shape

```markdown
**Prediction Audit**
- Intended prediction:
- Observed outcome:
- Miss type:

**What Zoltar Should Learn**
- ...

**Skill Change**
- Add/change/remove:
- Target file:

**Future Check**
- Next time, Zoltar should ask/check:

**Validation**
- ...
```

## Edit Rule

When asked to update Zoltar, make the concrete plugin/skill edit, validate it, and reinstall/sync to the active control machine when that control machine is known.

Reject improvements that add more sections without changing decisions. If the miss was `market_overfit` or `consensus_machine`, update `challenge-market-overfit` or the shared packet rules so the Doubter changes the next action, not just the wording.
