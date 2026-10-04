# Contributing to grok-canopy

Thanks for your interest in the Grok bot canopy.

## Quick start

You need Python 3.

```bash
git clone https://github.com/eidos-agi/eidos-marketplace.git
cd eidos-marketplace/plugins/grok-canopy
python scripts/check.py
```

`scripts/check.py` reads agent profiles from `/home/box/agent-data/agents`. On a machine without that directory the script exits before the parent checks.

The BotScore store is `scripts/store/botscore.json`. Read it in place.

## Rules

1. **Parents stay.** Do not edit `PARENT`, roles, or the 11 wake cases in `scripts/check.py`.
2. **Scores stay.** Do not rescore `scripts/store/botscore.json`, and do not drop or rename the bots at score 0.
3. **Check and store stay apart.** The check records parents and wake cases. Scoring lives in the BotScore file.
4. **No extra packs.** Do not add goal packs or other people's data to this plugin.

## Pull requests

- One change per PR.
- Keep `scripts/check.py` and `scripts/store/botscore.json` byte-stable unless the canopy itself has a new published snapshot.
- Update `CHANGELOG.md` under the version you are releasing.

## Reporting issues

Open an issue with:

1. The check line that failed, or the bot name in the store
2. The command you ran
3. What you expected the parent or score to be

Leave live goal documents out of the issue.
