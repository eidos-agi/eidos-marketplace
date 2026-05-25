# Converge Agent Wakeup

Read these files before changing Converge:

1. `README.md`
2. `skills/converge/SKILL.md`
3. `schemas/converge-row.schema.json`
4. `schemas/converge-spec.schema.json`
5. `adapters/README.md`
6. `tests/test_adapter_foundation.py`

Core boundary:

- Converge is the contract and method.
- Adapters emit rows.
- Aggregators summarize rows.
- Codex repairs rows.
- Eidos preserves the outer evidence loop.

Do not turn a reference adapter into the engine. Add new adapters by producing
valid Converge rows and adding tests that prove the rows validate.
