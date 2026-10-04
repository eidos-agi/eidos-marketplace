# Grok Canopy

**Grok Canopy** is the parent-pointer check and the BotScore store for the Grok bot canopy.

The check covers 124 bots. Every bot except Grok Bot has one parent. The tree has no cycle. Depth stays at most 4. Eleven wake cases are recorded in the check. Scoring lives in the BotScore store.

## Files

| Path | What it is |
| --- | --- |
| `scripts/check.py` | Parent-pointer check. Parents, roles, and wake cases stay as shipped. |
| `scripts/store/botscore.json` | Persistent BotScore store, version 1, 124 bots. |

## Run the check

You need Python 3 and the agent profiles at `/home/box/agent-data/agents`.

```bash
python scripts/check.py
```

The script prints bot, chief, leaf, and depth counts, then the wake, parent, nested-chief, and depth results.

## BotScore

`scripts/store/botscore.json` is the published store.

- Version 1, 124 bots
- Base 100, floor 0
- 40 for no real name, 40 for not loaded, 30 for no description, 30 for fewer than 3 memory notes
- Wake correction added nothing
- Token burn is excluded

Eighteen bots sit at score 0. Leave their names and scores as published.

## License

MIT. See [LICENSE](LICENSE).
