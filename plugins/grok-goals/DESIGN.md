# Design

Grok Goals is a durable outcome a bot can pick up tomorrow: a title, an objective, acceptance criteria, a short plan, the latest progress, a next action, and an approval policy. The MCP is a store. Planning and nudges stay in GrokGoals, the bot.

## Not a Linear Initiative

A Linear Initiative is a planning container above projects. It has a name, a health, a target date, and a rollup of the projects and issues under it. Updates are status posts for people who follow that bet. Access, teams, and the issue graph live in Linear.

A Grok Goal is one outcome with an owner bot, not a portfolio object.

- The plan is an ordered list of steps (`user` or `agent`, `todo` through `skipped`). It is not a project tree and it does not sync to issues.
- Progress is one latest summary plus an append-only journal. It is not an initiative update feed or a health color.
- `next_action` says who moves next and, optionally, when. An Initiative does not carry a bot/user gate like that.
- `approval_policy` says whether the bot may send, spend, post, or delete without asking. Initiatives do not model bot side effects.
- v1 does not read or write Linear. A goal is not a project, and this repo will not grow a Linear adapter in order to look finished.

Pause, block, complete, and abandon are statuses on the same document. History stays in the goal file and the journal. There is no archive-by-delete.

## Not a Muse Goal

Meta Muse (September 2026) put Goals in a consumer product: a place to say what you want, with Feed and Ideas beside it, and the model coaching inside that app. That is a surface. This is the object those chats were missing.

- v1 has no Feed, no Ideas, and no coaching UI. The bot already has chat, routines, and memory. The goal is what those can point at (`linked_routines`, `memory_refs`).
- Muse Code `/goal` is a harness for one coding session. A Grok Goal outlives the session. Status, next action, and approval gates are still there the next time the bot wakes up.
- This server does not decide the next step and does not rewrite the plan on its own. `goals_create` stores the steps it was given. `goals_record_progress` stores the summary it was given.
- There is no streak, coin, or reward. A completed goal is a status, not a score.

## Not a task list

`goals_list` can filter, and a plan step can be `todo`. That is as close as v1 gets to a task manager. Steps exist so the objective has a shape. They are not a second inbox, and they are not mirrored to Todoist or Kaneo.

## Persistence

The pack is the database:

```
grok-goals.prim/
  product.json
  index.json
  goals/<uuid>.json
  progress/<uuid>.jsonl
```

Goal JSON is checked against the in-repo schema before it is written and again when it is read. Unknown fields fail validation, so a sample pack cannot grow mystery keys and still load.

`index.json` is a rollup for anything that wants id, title, status, category, and `updated_at` without opening every file. If it drifts, `npm run reindex` rebuilds it. Readers that need the truth open `goals/`.

The progress journal is the one layout addition beyond the brief's three files. `last_progress` is a single `{ at, summary }` because that is the field the brief specifies. "Append" still has to go somewhere, or the second update would erase the first. Journal lines are not goal fields. The latest line's `at` and `summary` match `last_progress`.

SQLite is not used. A directory pack is enough for a person's goals and it is already the migration target. Adding a database would only create a second store to export later.

No `prim.*` profile was published in a FAMILY or registry this environment could read. `product.json` records `profile: "grok-goals.v1"` and `profile_status: "in-repo-schema"`. When an official profile exists, point `profile` at it. The goal documents use the brief's field names, so they should move without a rename if that profile adopts the same object.

## Schema choices

| Topic | v1 choice |
| --- | --- |
| `id` | UUID v4 from `crypto.randomUUID()`. The brief allows ulid or uuid. UUID needs no extra package. |
| `category` | Enum: `health`, `finance`, `career`, `shipping`, `other`. The brief lists those values. A free string would make `goals_list` filters lie. |
| `status` | `draft`, `active`, `paused`, `blocked`, `completed`, `abandoned`. Create only accepts `draft` or `active`. Update may set any of them, including reopening a completed goal. |
| `approval_policy` | `{ send, spend, post, delete }`, each `auto`, `ask`, or `deny`. Default `ask`. The brief names those actions and says the object is what may auto-run versus what must ask. |
| `plan_steps` | Current list only. Replace the list with `goals_update`, or patch a step's status while recording progress. |
| Timestamps | `created_at`, `updated_at`, and `last_progress.at` are ISO-8601 date-times. `next_action.due` may be a date or a date-time. |

Stored documents always include `acceptance_criteria`, `plan_steps`, `approval_policy`, `linked_routines`, and `memory_refs`, even when those arrays are empty, so a file that loads has a stable shape. `category`, `last_progress`, `next_action`, and `owner_bot` are omitted when empty rather than stored as null.

## What the bot still owns

Routines can list active goals and talk about a stalled `next_action`. That loop is not in this repo. Neither is sending mail, spending money, or posting. Those wait on the policy the bot reads here, and on the bot actually asking when the gate says `ask`.
