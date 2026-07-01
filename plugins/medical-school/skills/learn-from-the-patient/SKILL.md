---
name: learn-from-the-patient
description: Use after a diagnosis (a /medschool rounds or checkup) to capture what the doctor got wrong and feed it back into the curriculum — false alarms it raised, blind spots it hit, root causes it missed. This is the self-improvement loop: it makes the school smarter from every real patient instead of decaying into my authored opinion. Invoke on "/medschool learn", "what did that teach us", or after any real fleet diagnosis.
---

# Learn From the Patient

This is how the school improves itself. A curriculum that only reflects its
author's opinion decays; one that revises from real outcomes compounds. Every
diagnosis is a chance to make the next one better — but only if the miss gets
captured and promoted. That capture is this skill.

**Precondition (honesty, rubric #4):** a learning loop with no real diagnoses is
theater. Do not run this speculatively. Run it *after* a real `rounds`/`checkup`
produced a result you can compare against ground truth.

## 1. Record the outcome

Append one entry to `.medschool/learnings.jsonl` (create the dir if absent):

```json
{"ts":"<iso>","patient":"<stack>","doctor_said":"<the diagnosis>",
 "ground_truth":"<what was actually true>","miss":"<where it was wrong, or null>",
 "miss_class":"false_alarm|blind_spot|missed_root_cause|null"}
```

The valuable field is `miss`. A run where the doctor was exactly right is a data
point; a run where it was *wrong* is a lesson. Be specific: not "usage was off"
but "reported kernel down as critical; it was dormant-by-design, last used 33d ago."

## 2. Grade it

Score the diagnosis against [`the-rounds-rubric`](../the-rounds-rubric/SKILL.md).
Record the score alongside the entry. Falling scores over time mean the stack
changed and the doctor didn't keep up — itself a finding.

## 3. Promote recurring misses

This is the step that changes the school. Scan `learnings.jsonl` for misses that
have now appeared **≥ 2 times across patients**:

- **Recurring `blind_spot`** → propose a **new rubric item** in `the-rounds-rubric`.
  (Rubric #2, the usage chart, was born exactly this way — from the ASMP patient's
  "27 down" false alarm. See `case-studies/asmp.md`.)
- **Novel `missed_root_cause`** → write a **new case study** under `case-studies/`.
- **Recurring `false_alarm`** → tighten the method in `give-yourself-a-doctor`
  (usually: the doctor needs a signal it isn't collecting yet).

Do not promote a one-off. One miss is noise; a pattern is curriculum. Silent
single-occurrence misses stay in the ledger until they recur or get dismissed.

## 4. Close the loop

State plainly what changed: which rubric item, method line, or case study was
added/edited, and which learnings drove it. If nothing recurred, say so — "3 new
learnings recorded, none recurring yet, no curriculum change." That is a healthy
outcome, not a failed run.

## The invariant

The school's authority comes from evidence, not from its author. Every rubric item
and case study should be traceable to a real patient that taught it. When you can
no longer trace one, that item is suspect — flag it. A curriculum that can't say
*which patient taught this* is drifting back into opinion.
