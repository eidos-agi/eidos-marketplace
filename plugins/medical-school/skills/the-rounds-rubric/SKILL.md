---
name: the-rounds-rubric
description: Use to grade a self-diagnostic / health check against the five-point bar for "a doctor that works well" — real vitals, usage chart, root-cause triage, honest blind spots, cheap-and-repeatable. Invoke when reviewing a health endpoint, an /status command, a monitoring setup, or when the user asks "is this health check any good", "does my doctor work", or runs /medschool checkup.
---

# The Rounds Rubric

The bar a self-diagnostic must clear to count as **a doctor that works well**.
Grade any health check — yours or an existing one — against these five. A doctor
that fails #1 or #4 is worse than none: it manufactures false confidence.

Score each 0 (absent) / 1 (partial) / 2 (met). A passing doctor scores ≥ 8 **and**
has no 0 on #1 or #4.

## 1. Vitals that don't lie — *no fabricated status*

- **2** — every status derives from a live probe this run; unreachable → `unchecked`.
- **1** — probes real components but caches/staleness can report a dead thing as up.
- **0** — any hardcoded status, or "assume healthy." *Automatic fail of the whole doctor.*

> Founding failure: `/health` returning a hardcoded `"unchecked": 51`, never probed.

## 2. A chart, not just vitals — *usage context*

- **2** — reports `last_used` + frequency per component; distinguishes dormant-by-design from failing.
- **1** — has liveness only, but explicitly flags "usage unknown" so no false alarm is drawn.
- **0** — liveness only, presented as if down = bad, with no usage context.

> Test: does "27 down" come with "26 dormant, last used 33d ago; 1 is the DB"? If not, ≤ 1.

## 3. Triage to root cause — *symptoms collapse to causes*

- **2** — clusters failures by shared host:port / dependency / supervisor; reports causes ranked by blast radius.
- **1** — groups some failures but still surfaces mostly raw symptoms.
- **0** — dumps N red rows, no clustering.

> Test: 12 services on one dead port must report as **1** outage, not 12.

## 4. Honest blind spots — *names what it can't see*

- **2** — explicitly lists unmeasured signals and why; never substitutes a proxy for a fact.
- **1** — mostly honest but occasionally dresses a proxy (log mtime as "usage") as real.
- **0** — presents guesses as measurements, or silently omits what it couldn't check. *Automatic fail.*

## 5. Cheap and repeatable — *runs on rounds without dread*

- **2** — stdlib/near-zero deps, parallel, whole checkup in seconds; safe to run on a schedule.
- **1** — works but slow or heavy enough that it won't get run often.
- **0** — manual, serial, or so noisy it gets muted.

> A doctor that is expensive to run is a doctor that isn't run. Alert fatigue is a #5 failure with a #2 root cause.

## Scoring

```
total = sum(items)                  # 0..10
pass  = total >= 8 and item1 > 0 and item4 > 0
```

Report the score, the weakest item, and the single highest-leverage fix. Most
failing doctors are one instrument short — usually the usage chart (#2) — not a
rewrite. Point at that, not at everything.
