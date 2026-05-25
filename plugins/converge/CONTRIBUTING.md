# Contributing

Converge is a contract-first plugin. Contributions should preserve that boundary.

## Development Setup

```bash
cd /Users/dshanklinbv/plugins/converge
python3 -m pytest tests -q
python3 tests/validate_adapter_examples.py
python3 /Users/dshanklinbv/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
felix plugin doctor .
```

## Design Rules

- Keep `schemas/converge-row.schema.json` as the portable adapter output contract.
- Keep adapters deterministic unless a user explicitly asks for model-assisted evaluation.
- Do not make any one adapter the Converge engine.
- Add tests for every new adapter and every schema change.
- Preserve literal evidence paths, command output, or artifact references in rows.
- Prefer safe-direction failure over false green status.

## Release Checklist

1. Run the local tests and adapter example validation.
2. Run Felix plugin doctor.
3. Run Codex plugin validation.
4. Refresh the Eidos Marketplace bundle.
5. Update `CHANGELOG.md` and the marketplace audit.
