---
description: Eidos Medical School — teach an AI to give itself a doctor that works well. Verbs: enroll | rounds | checkup | learn.
argument-hint: "[enroll | rounds | checkup | learn] [target]"
---

# /medschool $ARGUMENTS

You are running Eidos Medical School. The student is the AI operating this
session; the goal is a self-diagnostic that meets the five-point bar in the
`the-rounds-rubric` skill. Read `give-yourself-a-doctor` for the full method.

Dispatch on the first word of `$ARGUMENTS`:

## `enroll` — build a doctor for this stack
1. Follow `give-yourself-a-doctor` step 1: inventory the components (prefer an
   existing source — registry, Procfile, `docker ps`, `systemctl`, `launchctl`).
2. Write an inventory JSON (`[{name, method, target}]`) and dry-run it with
   `scripts/probe.py --checks <file>`.
3. Stand up the usage-ledger instrument (rubric #2) at the stack's access points.
4. Grade the result with `the-rounds-rubric`. Report score + the one highest-leverage gap.

## `rounds` — run the doctor now
1. Run `scripts/probe.py` against the stack's inventory (or `--asmp <url>` for the
   Eidos fleet). Take real vitals in parallel.
2. Overlay the usage chart if a ledger exists; if not, say the chart is unknown.
3. **Triage** (method step 4): collapse the unhealthy set to root causes — same
   host:port, same dependency, same supervisor.
4. Report headline (root causes) → roster (worst-first) → blind spots.

## `checkup` — grade an existing health check
Apply `the-rounds-rubric` to whatever self-diagnostic already exists. Score each of
the five items 0/1/2, flag any auto-fail (#1 fabricated status, #4 dishonest
proxy), and name the single fix that moves the grade most.

## `learn` — improve the school from the last diagnosis
Follow `learn-from-the-patient`: record what the doctor got wrong, grade it, and
promote any miss that has recurred (≥2×) into a new rubric item, method line, or
case study. This is how the curriculum compounds from real patients instead of
decaying into opinion. Run it *after* a real `rounds`/`checkup`, never speculatively.

No verb? Explain the school in two lines and list the four verbs.
