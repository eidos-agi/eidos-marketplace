---
name: Use Grok Canopy
description: >-
  Use when checking the Grok bot parent tree or reading the published BotScore
  store. Parents, wake cases, and scores stay as shipped.
---
# Use Grok Canopy

Grok Canopy ships the parent-pointer check and the BotScore store for the 124-bot canopy.

## Parent check

Run `python scripts/check.py` on the machine that has `/home/box/agent-data/agents`.

The script checks that every bot except Grok Bot has one parent, that the tree has no cycle, that depth stays at most 4, and that the 11 wake cases in the file still match.

Leave `PARENT`, `UNCLEAN`, `role`, and `may_wake` as they are.

## BotScore store

Read `scripts/store/botscore.json`. It is store version 1.

Scores use four penalties from a base of 100, floored at 0: 40 for no real name, 40 for not loaded, 30 for no description, 30 for fewer than 3 memory notes. Wake correction added nothing. Token burn is excluded.

Leave every score, every bot name, and the 18 bots at score 0 as published.
