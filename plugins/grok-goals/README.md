# Grok Goals

**Grok Goals** is a durable Goal store and MCP so any Grok Bot can own an objective with a plan, track progress across sessions, and advance work under an approval policy — without re-explaining the goal every chat.

The server stores and validates. It does not plan, nudge, send, spend, post, or delete. That judgment stays in the bot.

## Run it in under 10 minutes

You need Node.js 20 or newer.

```bash
npm install
npm test
npm run demo
```

`npm test` creates a goal, lists it, fetches it, records progress, pauses it, and completes it through the MCP tools. It also validates the sample pack.

`npm run demo` prints that same story and checks `examples/grok-goals.prim`. The demo pack is written to `data/demo.prim` (gitignored).

Start the stdio server when a client is ready:

```bash
npm run dev
```

The process speaks MCP on stdin/stdout and logs only to stderr.

`GROK_GOALS_PACK` is the local pack path the installer sets. It names the directory this process reads and writes. When the variable is unset, the server creates an empty pack at `data/grok-goals.prim` under the process working directory. That directory is runtime state for one machine. This repository never commits a `data/` directory, and the server config never points at a personal pack.

`examples/grok-goals.prim` is a fictional demo pack. Read it in place, or copy it into the local pack when you want those sample goals:

```bash
mkdir -p "${GROK_GOALS_PACK:-$HOME/.grok-goals/pack}"
cp -R examples/grok-goals.prim/. "${GROK_GOALS_PACK:-$HOME/.grok-goals/pack}/"
GROK_GOALS_PACK="${GROK_GOALS_PACK:-$HOME/.grok-goals/pack}" npm run dev
```

Leave `GROK_GOALS_PACK` unset when you want a fresh empty pack instead.

After `npm run build`, `npm start` runs `dist/index.js` the same way. The marketplace plugin config (`.mcp.json`) launches that built file over stdio and leaves `GROK_GOALS_PACK` for the installer.

### Client config

```json
{
  "mcpServers": {
    "grok-goals": {
      "transport": "stdio",
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/dist/index.js"],
      "env": {
        "GROK_GOALS_PACK": "/path/the/installer/sets"
      }
    }
  }
}
```

Set `GROK_GOALS_PACK` to a directory on the machine that runs the server. Omit it to start an empty pack. Build first (`npm install` and `npm run build`) so `dist/index.js` exists.

## Architecture

```
Grok Bot
  chat, routines, memory, approval prompts
        |
        |  MCP stdio
        v
Grok Goals server
  six tools, JSON Schema validation, no model
        |
        v
grok-goals.prim/
  product.json
  index.json
  goals/<uuid>.json
  progress/<uuid>.jsonl
```

One process should own a pack. Writes are serialized in that process. Goal files are the source of truth. `index.json` is a status rollup refreshed on each write. `npm run reindex` rebuilds it from the files.

`last_progress` on the goal is the latest summary, as in the schema. Each `goals_record_progress` call also appends a line under `progress/` so pause and abandon do not throw away earlier notes.

## Tools

| Tool | What it does |
| --- | --- |
| `goals_list` | Filter by `status` and/or `category`. Returns full goals. |
| `goals_get` | One goal by id. |
| `goals_create` | Draft or active. Does not invent plan steps. |
| `goals_update` | Patch fields, replace `plan_steps`, or set status (`paused`, `completed`, …). |
| `goals_record_progress` | Set `last_progress`, append the journal, optional `next_action` and step updates. |
| `goals_set_approval_policy` | Set `send`, `spend`, `post`, `delete` to `auto`, `ask`, or `deny`. |

New goals default every gate to `ask`. The store records the gate. It never performs the action.

Argument and result shapes: [docs/tools.md](docs/tools.md). OpenAPI-style catalog for later plugin packaging: [docs/tools.openapi.json](docs/tools.openapi.json). Packaging sketch: [docs/grok-bot-plugin.json](docs/grok-bot-plugin.json).

## Sample pack

`examples/grok-goals.prim` holds two goals:

- **Train for a half marathon by March** (`health`) — mid-plan, long run still short of the race.
- **Ship quarterly invoice export** (`shipping`) — finance signed off on columns; the export is the next action.

```bash
npm run validate-pack
```

## Schema

[schema/goal.schema.json](schema/goal.schema.json) and [schema/plan-step.schema.json](schema/plan-step.schema.json) are the v1 contract. Field names match the product brief.

Decisions recorded in [DESIGN.md](DESIGN.md):

- Ids are UUID v4 (`crypto.randomUUID()`).
- `category` is the enum `health | finance | career | shipping | other`, not a free string.
- `approval_policy` is `{ send, spend, post, delete }`, each `auto | ask | deny`.
- No official Prim profile was available here. `product.json` uses profile `grok-goals.v1` and `profile_status: "in-repo-schema"` until one exists.

## What v1 does not do

No Feed or Ideas UI, no coins or streaks, no Linear or Todoist sync, and no model inside the MCP. Pausing or abandoning a goal keeps the file. There is no delete tool.

How this differs from Linear Initiatives and Muse Goals: [DESIGN.md](DESIGN.md).
