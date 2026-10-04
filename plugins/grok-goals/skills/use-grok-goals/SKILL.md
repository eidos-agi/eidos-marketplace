---
name: Use Grok Goals
description: >-
  Use when creating, updating, coaching, or checking progress on durable Grok
  Goals (not Linear Initiatives, not a task inbox).
---
# Use Grok Goals

Grok Goals is a durable outcome store (Prim pack + MCP). The connector only stores and validates. Planning, nudges, and side effects stay with the bot.

## When this applies

- The user wants a lasting objective with a plan, progress, next action, or approval gates
- A routine or coaching pass should review active/blocked goals
- Work finished that should be recorded against a goal

Do **not** use this for Linear Initiatives, Kaneo/Todoist task lists, or Muse-style Feed/Ideas UI.

## Discover tools first

Look up the `grok-goals` (or `user-grok-goals`) connector schema before calling. Typical tools: `goals_list`, `goals_get`, `goals_create`, `goals_update`, `goals_record_progress`, `goals_set_approval_policy`.

## Create

Pass a clear title, objective, plan steps you already decided (`owner`: `user` or `agent`), optional category (`health` | `finance` | `career` | `shipping` | `other`), acceptance criteria, and `next_action`. Omitted approval gates default to `ask`. Status on create is only `draft` or `active`.

Never invent plan steps inside the store — decide them, then store them.

## Coach / weekly check

1. List `active` and `blocked` goals.
2. For each: note `next_action` (who owns it, whether it looks stalled), open plan steps, and `approval_policy`.
3. If nothing needs a nudge, stay quiet (routines) or say so briefly (chat).
4. If something needs a nudge: say the goal title, the stuck next action, and who moves — do not invent progress.
5. After real work lands, call `goals_record_progress` with a honest summary; update step statuses and `next_action` in the same call when you can.
6. Before send / spend / post / delete for a goal: read that goal’s `approval_policy`. `ask` means ask the user; `deny` means do not do it; `auto` means the bot may proceed under normal send rules. The store never performs those actions.

## Status moves

Use `goals_update` for `paused`, `blocked`, `completed`, `abandoned`. Documents stay; do not delete goals to archive them.

## Not in scope for the connector

Coaching copy, routines, memory, email, spend, and posts live in the bot. Link routines via `linked_routines` and memory via `memory_refs` when useful.
