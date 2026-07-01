# Eidos Medical School Audit

Status: pending

Medical School is a new Eidos marketplace forge: a stack-agnostic curriculum that
teaches an AI to give itself a self-diagnostic ("a doctor that works well").
Initial review scope is the plugin manifest, the three curriculum skills, the
`/medschool` command, and the reference prober.

## Boundaries

- Curriculum + reference implementation only; ships no daemon and no always-on process
- Reference prober (`scripts/probe.py`) is read-only: it probes (http GET / tcp
  connect / launchctl list) and reports; it never mutates, restarts, or kills
- No credential handling, no vendor API calls, no outbound messaging
- `command` probe method uses `shlex.split` (no `shell=True`) — no shell-injection surface
- The `learn` loop writes only to a local `.medschool/learnings.jsonl`

## Proof

- `python3 scripts/probe.py --selftest` — guards against fabricated status (the plugin's own rubric #1)
- `python tools/marketplace_publish.py check medical-school` — marketplace standard gate

## Next Audit

Run the plugin validator, the prober selftest, and marketplace checks before
promotion. Grade the curriculum against its own `the-rounds-rubric` once a second
real patient (beyond the ASMP founding case study) has been diagnosed.
