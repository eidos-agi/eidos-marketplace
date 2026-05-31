# Contributing

Eidos Storemetheus is maintained by Eidos AGI as part of the Eidos marketplace.

## Development

1. Edit the plugin bundle under `plugins/eidos-storemetheus/`.
2. Keep the skill focused on plugin-store design and governance.
3. Validate the plugin before submitting changes:

```bash
python /Users/dshanklinbv/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/eidos-storemetheus
felix plugin doctor plugins/eidos-storemetheus
pytest -q
```

## Standards

- Do not include client-private facts in the public Eidos marketplace.
- Keep Storemetheus as a forge for building stores, not a package manager.
- Preserve the distinction between source, marketplace bundle, cache, config, and active-session visibility.
