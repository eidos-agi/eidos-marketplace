# Grok Goals tools

MCP tools for the Grok Goals pack. The server stores and validates. It does not plan, nudge, or perform side effects.

Every successful result is JSON: `{ "ok": true, ... }`. Store failures are tool errors with `{ "ok": false, "error": { "code", "message", "details?" } }`. `code` is `not_found`, `validation`, or `io`. Arguments that fail the tool schema come back as an MCP invalid-params error instead.

`null` clears `category`, `next_action`, and `owner_bot` on update, and clears `next_action` on progress. Omitted fields stay as they are.

## goals_list

List full goal documents, newest `updated_at` first.

| Arg | Required | Notes |
| --- | --- | --- |
| `status` | no | `draft`, `active`, `paused`, `blocked`, `completed`, `abandoned` |
| `category` | no | `health`, `finance`, `career`, `shipping`, `other` |

Returns `{ ok, goals }`.

## goals_get

| Arg | Required |
| --- | --- |
| `id` | yes, UUID |

Returns `{ ok, goal }`.

## goals_create

Creates a draft (default) or active goal. Step ids are optional; the server assigns any that are missing. Approval gates default to `ask`.

| Arg | Required | Notes |
| --- | --- | --- |
| `title` | yes | |
| `objective` | yes | |
| `acceptance_criteria` | no | string array |
| `category` | no | |
| `plan_steps` | no | `{ title, owner, status?, notes?, id? }` |
| `status` | no | `draft` or `active` only |
| `approval_policy` | no | partial `{ send, spend, post, delete }` |
| `linked_routines` | no | string array |
| `memory_refs` | no | string array |
| `owner_bot` | no | |
| `next_action` | no | `{ summary, owner, due? }` |

`owner` is `user` or `agent`. Step `status` is `todo`, `doing`, `done`, or `skipped` (default `todo`). `due` is `YYYY-MM-DD` or an ISO-8601 date-time.

```json
{
  "title": "Train for a half marathon by March",
  "objective": "Finish a half marathon in March. Build the mileage, keep the long run, and show up on race day.",
  "acceptance_criteria": ["Finish the March half marathon"],
  "category": "health",
  "status": "active",
  "plan_steps": [
    { "title": "Pick the March race and write the weekly mileage", "owner": "user" },
    { "title": "Build the long run to 10 miles", "owner": "user" },
    { "title": "Taper for two weeks and run the race", "owner": "user" }
  ]
}
```

## goals_update

Patch one goal. `plan_steps`, when sent, replaces the whole list. This does not change approval gates and does not append the progress journal.

| Arg | Required | Notes |
| --- | --- | --- |
| `id` | yes | |
| `title`, `objective`, `acceptance_criteria`, `plan_steps`, `linked_routines`, `memory_refs` | no | replacement values |
| `category`, `owner_bot`, `next_action` | no | value, or `null` to clear |
| `status` | no | any lifecycle status, including `paused` and `completed` |

Pause, block, abandon, and complete keep the document. A completed goal can be moved back to `active` if that was a mistake.

## goals_record_progress

Sets `last_progress`, appends `progress/<id>.jsonl`, and can update the plan. Does not change goal `status`.

| Arg | Required | Notes |
| --- | --- | --- |
| `id` | yes | |
| `summary` | yes | what actually happened |
| `at` | no | ISO-8601 date-time, default now |
| `next_action` | no | object to replace, `null` to clear, omit to keep |
| `step_updates` | no | `{ id, status, notes? }`. `notes: null` clears notes |

Returns `{ ok, goal, progress_entry }`.

## goals_set_approval_policy

Stores gates. It does not send, spend, post, or delete.

| Arg | Required | Notes |
| --- | --- | --- |
| `id` | yes | |
| `send`, `spend`, `post`, `delete` | at least one | `auto`, `ask`, or `deny` |

Omitted gates stay as they are. `ask` means the bot stops for confirmation. `deny` means the bot refuses. `auto` means the bot may proceed. The default for a new goal is `ask` on every gate.
