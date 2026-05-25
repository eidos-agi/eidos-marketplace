# Converge

Converge is a Codex plugin for giving AI agents explicit software targets and
then driving the work through score, audit, repair, and re-score loops. It turns
"done" into a table-backed contract: north stars, artifacts, layers, invariants,
tests, evidence, drift monitors, regression memory, and repair rows.

Converge is contract-first, not scorer-first. The durable abstraction is the
target/probe/evidence/repair row. Any suitable adapter can produce those rows:
tests, SQL, dbt, Playwright, CI, spreadsheets, shell commands, API probes, Eidos
evidence, or human-reviewed artifacts.

The core idea comes from the Greenmark v4 scoreboard pattern:

- deterministic checks first
- LLM reasoning on demand, not on every cell
- scoreboards as diagnostic instruments, not oracles
- safe-direction failures over premature green checks
- north-star evidence outside the model's self-judgment
- drift and regression treated as first-class signals
- iteration treated as a control loop, not busywork
- convergence style chosen per problem instead of one generic definition of done

## Biological Inspirations

Converge borrows control ideas from living systems:

- homeostasis: keep important measures inside target bands
- immune memory: turn recurring regressions into durable checks
- adaptation: weight rows by contribution to the real north star
- mutation and selection: let AI propose repairs, let checks select
- developmental stages: move targets through maturity stages
- redundancy: verify important claims through more than one evidence path
- apoptosis: retire failing or obsolete targets instead of patching forever

## Convergence Styles

Different systems need different convergence pressure. Converge supports styles
such as exact match, tolerance band, staged maturity, regression hardening,
drift homeostasis, exploratory narrowing, consensus evidence, and graceful
degradation.

## Contents

- `skills/converge/SKILL.md` - primary Codex skill
- `assets/templates/converge-spec.json` - starter target lattice
- `schemas/converge-spec.schema.json` - starter lattice schema
- `schemas/converge-row.schema.json` - portable row contract
- `adapters/README.md` - adapter contract and examples
- `adapters/json_reference.py` - reference adapter for simple JSON target lattices
- `adapters/pytest_adapter.py` - real pytest/JUnit row adapter
- `adapters/aggregate_rows.py` - reference row aggregator and repair summary

## Quick Start

These helpers are lab equipment, not the Converge engine:

```bash
cp /Users/dshanklinbv/plugins/converge/assets/templates/converge-spec.json ./converge-spec.json
python3 /Users/dshanklinbv/plugins/converge/adapters/json_reference.py ./converge-spec.json
python3 /Users/dshanklinbv/plugins/converge/adapters/json_reference.py ./converge-spec.json --rows
python3 /Users/dshanklinbv/plugins/converge/adapters/pytest_adapter.py --junit path/to/junit.xml --out pytest-rows.json
python3 /Users/dshanklinbv/plugins/converge/adapters/aggregate_rows.py reference-rows.json pytest-rows.json
```

Adapters emit rows. Aggregators summarize rows. Codex repairs rows. Eidos
preserves the outer evidence loop when the work is part of an Eidos task.

## Validate Adapter Examples

```bash
python3 /Users/dshanklinbv/plugins/converge/tests/validate_adapter_examples.py
```
