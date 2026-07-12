---
name: fleetbuild
description: Run one honest Fleet build cycle as a small team would — product states the value, an engineer builds the laziest thing that works, a reviewer adversarially verifies and mints an antibody, the win is banked in staircase, the loop advances. Use when the user says 'build Fleet', 'fleetbuild', 'keep building', 'next Fleet task', or when a Fleet build loop should take one more step. Reads .fleetbuilder/learnings.md (distilled from the user's own transcripts) so the team gets smarter about THIS user's Fleet each cycle.
---

# fleetbuild — the team-of-experts build cycle

**When the user says "build Fleet", you just build Fleet.** No scoping questions. Pick the
next unblocked task and run one cycle. Ship the lazy version; question scope in the same
breath, never instead of building.

## Before the cycle: consult the learnings

Read `.fleetbuilder/learnings.md` (in the target repo, e.g. `fleet-v1/`). It's distilled from
the user's own Claude Code transcripts — what Fleet they need, how they build, standing orders,
antibodies. **Obey its Standing orders and How-he-builds sections this cycle.** If it's missing
or stale (older than a few sessions), run `/fleetbuild-learn` first.

## The cycle (one task, one bankable win)

1. **Orient (product lens).** Pick the next unblocked task from the backlog
   (`.docket/tasks/` via `docket-md task-list`, or the arg the user gave). State its value
   **from the user's chair** in one line — "as a user, this lets me ___". If you can't, it's a
   feature not a need; pick a different task (learnings: *MVP core loop, not features*).

2. **Build (engineer lens).** Build the **laziest change that works** (ponytail ladder:
   YAGNI → stdlib → native → existing dep → one line → minimal code). Ground every claim
   against the source file:line — don't trust a doc or a checkbox.

3. **Verify + antibody (reviewer lens).** Prove it end-to-end with a real artifact you
   inspect (screenshot / command output / oracle-diff) — never "tests pass" alone. For any
   failure the build hit, leave ONE runnable check behind (an **antibody**) so it can't recur.

4. **Bank.** Route the commit through hancock (`request` → local git runs immediately). Then
   `staircase log-win <id> --proof "…" --note "…"`. The proof is the artifact from step 3.

5. **Advance.** Update the backlog. If the staircase buffer is below its daily cadence and
   there's an unblocked task, **keep going** — take the next cycle. Stop only when blocked,
   out of unblocked tasks, or told to.

## Running the team in parallel (workflows)

For a task with independent facets, fan the lenses out instead of doing them inline: spawn the
`fleet-product`, `fleet-engineer`, and `fleet-reviewer` agents (Agent tool, one message) or a
Workflow — product scopes while the engineer drafts, reviewer verifies as soon as the draft
lands. Synthesize, then bank. Solo-inline is fine for a small task; don't over-orchestrate.

## Anti-patterns

- Asking the user to scope "build Fleet" instead of picking a task. (This is the #1 thing to
  not do — see learnings Standing orders.)
- Marking anything done without a proof artifact you actually looked at.
- Building a feature you can't justify from the user's chair.
- A big-bang branch mixing many concerns — one cycle, one coherent win, one commit.
