# kai

> Internal multitool for **Daniel kai Vybhav**.

`kai` is the single entry point for the eidos-agi internal dev team. It dispatches to the underlying tools — `railguey`, `research-md`, `ike`, `visionlog`, `cept`, the forge family, etc. — under one progressive-reveal namespace.

## What "kai" means

| Layer | Meaning |
|---|---|
| Greek (καί) | "and" — the conjunction that joins two things |
| Japanese 解 | "to solve, to unravel" |
| Japanese 開 / Chinese 开 | "to open, to begin" |
| Hawaiian | "sea, ocean" |
| Maori | "food" |

It connects, solves, opens, supports, and sustains. Daniel **kai** Vybhav, and `kai` is the dispatcher that joins everything they build.

## Install (dev)

```bash
git clone git@github.com:eidos-agi/kai.git
cd kai
pip install -e .
```

Then:

```bash
kai                    # list domains
kai deploy             # list commands in the deploy domain
kai deploy status      # shells to `railguey status`
```

## Pattern: progressive reveal

`kai` follows the progressive-reveal pattern:

1. `kai` (no args) → lists domains
2. `kai <domain>` → lists commands in that domain
3. `kai <domain> <command>` → executes (shells to the underlying tool)

`kai` is a **dispatcher**, not a reimplementation. Each underlying tool keeps its independent release cadence. `kai` just gives you one entry point and one help surface.

## Domains

| Domain | Underlying tool(s) | Status |
|---|---|---|
| `deploy` | `railguey` | active |
| `ops` | company procedures and process guardrails | active |
| `slack` | Slack app/workspace operations | active |
| `decide` | `research-md` | planned |
| `plan` | `ike` | planned |
| `vision` | `visionlog` | planned |
| `forge` | `forge-forge` family | planned |
| `session` | `resume-resume`, `claudoctor` | planned |
| `disk` | `space-hog`, `apple-a-day` | planned |
| `orient` | `lighthouse`, `hone`, `scribe` | planned |
| `llm` | `cept` | planned |
| `mcp` | `cockpit-mcp`, `eidos-mcp` | planned |

## Public counterpart

`kai` is for the internal dev team only. The public CLI for Claude Code users is [`eidos-cli`](https://github.com/eidos-agi/eidos-cli).

## Tests

```bash
pip install pytest
pytest
```
