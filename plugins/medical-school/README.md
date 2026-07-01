# Eidos Medical School

**A school for teaching AIs how to give themselves a doctor that works well.**

Not a doctor. Not a monitoring dashboard. A *school*. The student is an AI. The
graduation product is a **self-diagnostic capability the AI installs on its own
stack** — one that meets a real bar, instead of the usual health check that
reports "fine" because it never took a pulse.

Medical School is stack-agnostic. The worked examples run on an Eidos service
fleet, but the method transfers to a k8s cluster, a systemd box, a SaaS backend,
or a laptop. The graduate builds a doctor for *its own* patient.

## Why this exists

Most self-checks lie. They are written once, wired to nothing, and drift into
decoration. The founding case study (`case-studies/asmp.md`) is a registry whose
`/health` endpoint **hardcoded** `"healthy": 0, "unchecked": 51` and never probed
anything. It looked healthy-adjacent. It was blind. When real probes ran, the
truth was 8 up / 2 degraded / 27 down — and 26 of those "down" collapsed to *one*
dead server on one port.

That gap — between a check that runs and a check that *means something* — is the
whole subject of this school.

## The bar: what "a doctor that works well" means

A graduate's doctor must pass all five. This is the rubric (`skills/the-rounds-rubric`):

1. **Vitals that don't lie.** Every status comes from an actual probe. No
   hardcoded values, no "assume up." If it can't check, it says `unchecked`, not `ok`.
2. **A chart, not just vitals.** Liveness alone produces false alarms. The doctor
   knows *last-used* and *how-often* per component, so it can tell
   dormant-by-design from actually-dying.
3. **Triage to root cause.** N correlated failures collapse to the smallest set of
   real causes. Report the patient, not every symptom.
4. **Honest blind spots.** When a signal doesn't exist, the doctor names the gap
   instead of faking it from a convenient proxy.
5. **Cheap and repeatable.** Stdlib, parallel, runs on rounds. A doctor you dread
   running is a doctor that rots.

## Curriculum

| Skill | Teaches |
|---|---|
| `give-yourself-a-doctor` | The method: inventory → probe → chart → triage → report, for your own stack |
| `the-rounds-rubric`      | The five-point bar and how to grade any self-doctor against it |
| `learn-from-the-patient` | The self-improvement loop: revise the curriculum from what real patients teach |

## Commands

```
/medschool enroll      # Assess your stack, scaffold a doctor that meets the bar
/medschool rounds      # Run the doctor: probe + chart + triage + report
/medschool checkup     # Grade an existing self-diagnostic against the rubric
/medschool learn       # Feed the last diagnosis back into the curriculum
```

The school is **self-improving**: `learn` records where the doctor was wrong and
promotes recurring misses into new rubric items and case studies. Rubric #2 (the
usage chart) was itself born this way — from the founding patient's false alarm.

## Reference implementation

`scripts/probe.py` — a stdlib, parallel prober (http / tcp / launchctl / systemd /
pid / command). It is the *worked example*, not the product. Students adapt it to
their own inventory. `case-studies/asmp.md` is the founding lecture that produced it.

## Graduates in the wild

- **`apple-a-day`** — a doctor for the "Mac" patient (vitals, cleanup). What a good
  graduate looks like when the stack is a laptop.
- **`nightingale`** — the pathologist: post-mortem study of *why agent sessions
  died*. Medical School is the live-rounds counterpart; nightingale is the autopsy.

## Status

`v0.1.0` — full loop: curriculum (method + rubric + self-improvement), reference
prober, and founding case study. The usage-ledger lesson (rubric #2) is proven on
the founding patient (ASMP grew `/services/{name}/touch` + `/usage`); feeders are
per-access-point and accrue going forward — see `give-yourself-a-doctor`.
