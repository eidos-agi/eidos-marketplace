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

## Running a real fleet with emux — persistent, driveable, remote sessions

The parallel lenses above (Agent tool / Workflow) are for quick fan-out that finishes with the
cycle. A real *fleet* is different: long-running sessions you spawn, watch, steer, and come back
to — sometimes on other machines. That is what **emux** is for. When Fleet work means standing
up and managing sessions, not just a one-shot subagent, reach for emux.

The tools, and when to use each:

- **Spawn a fleet member** — `tmux_spawn(name, command, host?, gui?)`. Makes a driveable tmux
  session, on this machine or a remote one (pass `host`, an ssh target). Pass a `command` to
  launch it (e.g. `claude "..."`). Pass `gui: true` to open a window so a human can watch. This
  is how you start a member you can drive and return to.
- **Drive a member** — `tmux_send(target, keys, by_registry_name: true)` types into it;
  `tmux_capture(target, by_registry_name: true)` reads its screen back. Use to steer, nudge, or
  check on a running member.
- **Find what is already running** — `tmux_sessions(host?, match?, kind?, limit?)`. Filter by
  project (`match`), by kind (`claude` / `agent` / `shell`), most-recent first. Look here before
  you spawn — do not create a member that already exists.
- **Find any session, running OR ended** — `tmux_search(query, host?, kind?, status?)`. emux
  tracks every session it has seen, so you can find finished work, not only live work. Use it to
  resume a stalled or ended member.
- **Hook into an existing session** — register a session emux did not create (its name + host),
  then drive it. You can adopt a member someone else started.
- **Go remote** — every tool takes a `host`. One local fleet can reach through ssh to spawn and
  drive members on other machines, and nest onward.

Rules of thumb:
- Search or list before you spawn — hook into what is there instead of duplicating it.
- Watch before you steer — capture a member's screen before sending keys, especially one you
  did not spawn (you can clobber a human's input).
- For a fleet that outlives the cycle or spans machines, use emux. For a quick one-shot fan-out
  inside this cycle, the Agent tool or Workflow is lazier and right.

## Stay organism-aware — the ecosystem grows

Eidos is an organism, and its organs grow. emux, staircase, hancock, docket — each gains new
abilities over time. The emux tools listed above are true as of this writing, and that list will
grow past this page. Build as if the toolbox keeps filling, because it does.

So never treat an organ's abilities as a frozen snapshot:

- **Check the live tool list before you assume.** Before deciding emux (or any organ) cannot do
  something, look at the tools actually available to you right now. If one fits better than what
  is written here, use it — the current tools are the truth, this page is only a guide.
- **A tool being present is not a tool being understood.** Knowing a tool exists is not knowing
  when to use it. When you meet a new organ ability, learn its *when* — the judgment — not just
  its name.
- **When an organ has grown past this skill, that is a signal, not a surprise.** Fold the new
  ability into how you build, and it belongs in the next update of this file.
  `/fleetbuild-learn` should also catch new patterns from transcripts.

An agent that assumes a fixed set of tools goes blind the moment the organism grows. This skill
went blind to emux's new tools once already — do not let it happen again.

## Anti-patterns

- Asking the user to scope "build Fleet" instead of picking a task. (This is the #1 thing to
  not do — see learnings Standing orders.)
- Marking anything done without a proof artifact you actually looked at.
- Building a feature you can't justify from the user's chair.
- A big-bang branch mixing many concerns — one cycle, one coherent win, one commit.
- Spawning a fleet member that already exists — search or list with emux first, then hook in.
- Assuming a tool's abilities are frozen — the organism grows; check the live tool list before you assume an organ can't do a thing.
