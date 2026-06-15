# Converge

Converge is an Eidos-AGI tool for giving AI agents explicit software targets
and then driving the work through score, audit, repair, and re-score loops. It turns
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

## Proof Envelopes

Converge distinguishes a real-surface pass from a controlled-harness pass. A
passing test can still fail to prove the production claim if it ran on
localhost, used fixtures, disabled provider controls, skipped rate limits, or
mutated a control plane to make the proof possible.

Rows can therefore use proof-surface classes:

- `pass_real_surface` - the target surface passed with required controls enabled
- `pass_controlled_harness` - a controlled fixture or harness passed
- `pass_with_bypass` - the proof passed only with disabled, skipped, or
  auto-satisfied controls

Adapters should attach a `proof_envelope` whenever those boundaries matter:

- `environment`
- `surface`
- `proof_id`
- `captured_at`
- `external_dependencies`
- `bypassed_controls`
- `side_effects`
- `fails_to_test`

The aggregator reports both `score` and `qualified_score`. `score` counts only
real/full pass classes. `qualified_score` also includes controlled and bypassed
passes. This keeps progress visible without letting a bypassed harness become
false green. It also emits `generated_gap_rows` from
`proof_envelope.fails_to_test` so each unproved surface becomes an explicit
repair target.

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
cp /Users/dshanklin/plugins/converge/assets/templates/converge-spec.json ./converge-spec.json
python3 /Users/dshanklin/plugins/converge/adapters/json_reference.py ./converge-spec.json
python3 /Users/dshanklin/plugins/converge/adapters/json_reference.py ./converge-spec.json --rows
python3 /Users/dshanklin/plugins/converge/adapters/pytest_adapter.py --junit path/to/junit.xml --out pytest-rows.json
python3 /Users/dshanklin/plugins/converge/adapters/aggregate_rows.py reference-rows.json pytest-rows.json
```

Adapters emit rows. Aggregators summarize rows. Codex repairs rows. Eidos
preserves the outer evidence loop when the work is part of an Eidos task.

## Validate Adapter Examples

```bash
python3 /Users/dshanklin/plugins/converge/tests/validate_adapter_examples.py
```
