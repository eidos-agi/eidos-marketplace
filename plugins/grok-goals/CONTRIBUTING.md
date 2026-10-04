# Contributing to grok-goals

Thanks for your interest in durable goals for Grok.

## Quick start

You need Node.js 20 or newer.

```bash
git clone https://github.com/eidos-agi/eidos-marketplace.git
cd eidos-marketplace/plugins/grok-goals
npm install
npm test
npm run build
```

`GROK_GOALS_PACK` is a local directory the installer sets. Leave it unset to start an empty pack under the process working directory (`data/grok-goals.prim`). That directory is runtime state. Keep it out of git.

The fictional sample lives at `examples/grok-goals.prim`. Copy it into a local pack when you want those sample goals. A personal goal pack stays on the machine that owns it.

## Rules

1. **Storage and validation only.** The server records goals, progress, and approval policy. Planning, sending, spending, posting, and deleting stay with the bot.
2. **Schema first.** Field changes belong in `schema/` and the TypeScript types together, with a test that the enums still match.
3. **Empty by default.** New installs start from an empty pack. Do not add a `data/` directory, and do not commit goal documents from a live pack.
4. **Small public surface.** Six tools. A new tool needs a schema, a doc in `docs/tools.md`, and a test.

## Running tests

```bash
npm test
npm run typecheck
```

## Pull requests

- One change per PR.
- Include a test for new store or tool behavior.
- Update `CHANGELOG.md` under `[Unreleased]` when you add a section, or under the version you are releasing.
- Run `npm test` before asking for review.

## Reporting issues

Open an issue with:

1. What you asked the server to store
2. The tool name and the error text
3. What you expected the pack to contain

Leave live goal documents out of the issue. A redacted fixture is enough.
