# Changelog

## 0.2.0 — 2026-07-12

Two integrity bugs, found by dogfooding the runner against a real repo (emux).

- **Cases now run from the repo root, not the ctc process's cwd.** `execute()`
  passed `shell=True` with no `cwd`, so `ctc --dir <repo> run` from any other
  directory ran every relative case (`python3 tests/…`) from the wrong place.
  They failed to open their files and reported a false red.
- **A case that cannot execute is BROKEN, never red — now including exit 2.** The
  guard only caught 126/127. But a wrong-cwd `python3 missing.py`, an argparse
  usage error, and a shell parse error (an unbalanced quote) all exit 2 — none
  ran the case's logic, yet they minted falsifiability. Combined with the cwd
  bug this let a suite score 100 on reds that never actually ran. Both closed;
  regression tests added for each.

## 0.1.0 — 2026-07-11

The engine. Extracted from a session that started as "staircase should have
Complex Test Cases" and ended by finding out that it belongs upstream of every
judge in the ecosystem, not inside one of them.

- **The rule**: a case must have been OBSERVED RED at least once. `VACUOUS`
  scores zero, not green.
- **Tamper property**: falsifiability is keyed to the case's command text, so a
  case weakened until it passes loses its red history and certifies nothing.
- **Dimensions**: happy/edge/regression, plus the ones that actually catch things
  — negative, adversary, ordering, irreversible, lying_input, refusal,
  unsolicited, integration. Floor: negative + adversary + refusal.
- `ctc init | add | redcheck | run | status | amend | retire | dimensions`
- `.complextestcases/` — cases.jsonl and runs.jsonl, both append-only. runs.jsonl
  is the proof: it is the only place falsifiability can be established.
- 7 tests, zero dependencies.

Next: the generator — adversarial authoring from a telos charter (never from the
code), which is the reason this is its own repo.
