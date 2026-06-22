# Converge Playbook

Use Converge when an Eidos loop needs the measurable software-completion tool:
target rows, evidence envelopes, repair queues, and re-score loops rather than
a prose checklist.

## Use When

- The task asks whether software is complete, reliable, production-ready, or at 100%.
- There are target/probe comparisons: expected vs actual, spec vs implementation, PDF vs warehouse, test contract vs runtime behavior.
- Drift, stale evidence, regressions, or repeated repair loops are likely.
- Codex needs a ranked repair map from failing rows.

## Contract

- Full target lattices validate against `schemas/converge-spec.schema.json`.
- Adapter outputs validate against `schemas/converge-row.schema.json`.
- Adapters emit rows.
- Aggregators summarize rows.
- Codex repairs rows.
- Eidos preserves evidence, continuation, learning, and closeout.

## Reference Commands

```bash
python3 adapters/json_reference.py assets/templates/converge-spec.json --rows
python3 adapters/pytest_adapter.py --junit tests/fixtures/pytest-junit.xml --out pytest-rows.json
python3 adapters/aggregate_rows.py reference-rows.json pytest-rows.json
```

## Closeout

Before claiming completion, run tests and plugin validation:

```bash
python3 -m pytest tests -q
python3 tests/validate_adapter_examples.py
python3 /Users/dshanklin/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
felix plugin doctor .
```
