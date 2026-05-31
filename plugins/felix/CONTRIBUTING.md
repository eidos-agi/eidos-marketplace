# Contributing to Felix

Thanks for helping improve Felix.

## Quick Start

```bash
git clone https://github.com/eidos-agi/felix.git
cd felix
pip install -e ".[dev]"
```

## Development

Run tests:

```bash
python -m pytest -q
```

Run wiki lint:

```bash
scridos lint wiki/felix
```

Run CLI smoke checks:

```bash
felix doctor
felix agents list
felix standards
```

## Agentic-First Guidance

Felix is agentic-first, software-second. The software exists to carry an
agent's judgment, memory, tools, coordination, goals, boundaries, and proof.
That means:

1. Start from the agentic capability before repo, package, CLI, or plugin shape.
2. Commands should describe work concepts, not storage internals.
3. Public functions should be typed.
4. Errors should tell the agent what to do next.
5. New agent standards should include documentation, tests, wiki, task list, install path, route entry, and proof of useful agentic behavior.
6. Do not add abstractions unless they produce concrete scaffolds, audits, repairs, or better agentic behavior.
7. Before changing plugin software, identify the canonical source and duplicate derived copies.
8. Do not copy business logic into multiple plugin wrappers; factor shared behavior into the source-owned CLI/library/schema.

## Pull Requests

- Keep PRs focused.
- Include tests for new behavior.
- Update the Scridos wiki when changing operating model or agent boundaries.
- Update `CHANGELOG.md`.
- When touching plugin distribution, update the plugin-quality and duplicate-cleanup guidance if the workflow changed.
