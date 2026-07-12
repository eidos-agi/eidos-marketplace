# Changelog

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
