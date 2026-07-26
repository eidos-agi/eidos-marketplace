---
name: getcontrol
version: 0.1.0
description: "Take stock of every terminal window, tab, and split on this Mac and get them under control — one pane per tmux session, every session registered in emux, every session behind a Linear issue. Use when the terminals have gotten away from you: 'too many windows', 'I've lost track of what's running', 'get control', 'what's open', 'clean up my terminals', 'is anything running that nobody owns'."
metadata:
  requires:
    bins: [tmux]
---

# getcontrol

> **Every fix to this plugin lands with an entry in `LEARNINGS.md`** — what went
> wrong, what changed, and why. A fix without its cause is a fact nobody can
> re-check, and this tool kills processes for a living. Read that file before
> changing behaviour; most of the sharp edges in here are already paid for.

A pane nobody can find is not work — it is a leak. `getcontrol` finds them all,
then walks each one into a place where an agent can reach it: **tmux** (so it can
be driven), **emux** (so it can be found), **Linear** (so it survives the window
closing).

`${CLAUDE_PLUGIN_ROOT}/scripts/getcontrol` — stdlib Python, no install.

## The rule that makes this worth doing

**A session with no Linear issue behind it is unmanaged.** It has no durable
state: close the window and the work is gone, and nobody but the person who
opened it knows it existed. So `adopt` refuses to run without a Linear reference.
That refusal is the point of the plugin — not a safety rail around it.

When a pane has no issue, don't invent a placeholder. Work out what it actually is:

1. `cwd` from the survey → the repo.
2. `git -C <cwd> log -1` and `git branch --show-current` → the work in flight. Branch
   names very often already carry the issue id (`dan/EID-874-gates`).
3. `tmux capture-pane -p -t <session>` if it is already in tmux → what it is doing right now.
4. Search Linear for that issue. Found it → link it. Genuinely new work → create the
   issue first, then link.
5. Truly no work here (a shell someone opened and abandoned) → it is not a session to
   adopt, it is a window to close. Say so and ask.

## Prevention beats cleanup

Sprawl has one source: **work that outlives its window, and windows that outlive
their work.** A shell sitting at a prompt after its agent quit is a husk — it
looks like a session, holds nothing, and nobody ever closes it. Twelve of one
machine's twenty-four panes were husks.

So the primary verb is `start`, not `adopt`:

```bash
getcontrol start ~/repos/thing --issue EID-874    # born in tmux + emux
eval "$(getcontrol shellinit)"                    # then just: gc ~/repos/thing
```

Three properties, and each one kills a class of mess:

- **Born in tmux** — the terminal app is a viewport, not the container. Quit it and
  nothing is lost.
- **`exec`'d into** — the launching shell is *replaced*, so when the work ends the
  window has nothing to fall back to and closes itself. No husk. This is POSIX, so
  it works identically in iTerm, Terminal, Ghostty, Warp, Alacritty, or over ssh.
- **Attach-or-create** — asking twice reuses the session instead of making a
  second one. This is what stops twelve windows accumulating in one repo.

Anything started this way never needs adopting, exploding, or accounting for.
Everything below is for the panes that got in before that was true.

## Pulling a pane in is a signed action

`control --pull` closes a live process and recreates it. getcontrol asks
`hancock check` before doing that and **refuses to run it unsigned** — queue the
whole run through `mcp__hancock__request` with `--signed` on the command. Never
sign your own.

```bash
getcontrol control --pull --apply --signed      # what you queue through hancock
getcontrol control --pull --only ttys013        # dry run, safe, no signature needed
```

Two facts learned the hard way, both now enforced in code:

- **`tmux new-session -c <bad path>` does not fail — it silently uses `$HOME`.** A
  pane whose cwd could not be read got recreated in the wrong directory, so
  `claude --continue` resumed the wrong conversation. `pull` now refuses before
  killing anything if the cwd is not a real directory, and verifies afterwards
  that the session landed where it was supposed to.
- **"a pane exists" is not proof the session came back.** Check
  `#{pane_current_path}` and read the pane; a fresh agent in the wrong repo looks
  identical to a resumed one from the outside.

## Accounted for, not just surveyed

A survey is a snapshot — run it twice and nothing accumulates, so a pane you
deliberately decided to leave alone looks exactly like one nobody has ever
examined. emux's registry can't close that gap either: it only knows tmux
sessions, so a raw iTerm pane is invisible to it by construction.

So getcontrol keeps its own ledger at `~/.config/getcontrol/ledger.json`, keyed by
a pane identity that outlives a tty number (`tmux:<session>@<created>` or
`proc:<pid>@<start>` — tty numbers get recycled within minutes, pids too).

**Every pane must end up in one of two states, and `status` is the closure check:**

| state | how it gets there |
|---|---|
| **governed** | adopted — tmux + emux + a Linear issue |
| **accounted for** | `getcontrol account <tty> --hold\|--unmanaged-ok --reason "…"` |

```bash
getcontrol status              # counts + the loose ones; exits 1 if any are unaccounted
```

Exit 1 is the point: it is a gate. Nothing is "under control" while `status` is
red, and a decision without a `--reason` is refused — accounting for a pane means
saying why, not silencing it.

Entries are pruned when their pane dies, so the ledger can never vouch for a pane
that no longer exists, and a recreated tmux session with an old name does not
inherit the old decision.

## Procedure

```bash
getcontrol doctor                # which control paths work on this machine
getcontrol status                # is everything accounted for? (start and end here)
getcontrol survey                # every pane + what it needs next
getcontrol survey --json         # same, for reasoning over
getcontrol survey --unaccounted  # only panes nobody has decided anything about
getcontrol survey --ungoverned   # only panes with no Linear issue behind them
```

Every pane comes back with a `next`. Work them in this order — cheapest and safest first:

| next | what it means | what you do |
|---|---|---|
| `ok` | tmux + emux + Linear | nothing |
| `register` | in tmux, invisible to emux | `emux register <name> <session> --linear-issue ID` |
| `link` | registered, no issue behind it | find/create the issue, re-register with `--linear-issue` |
| `resume` | claude/codex/grok running raw in a terminal | start it again under tmux, confirm alive, **then** close the original |
| `redial` | raw `ssh` | re-dial the same host inside tmux, close the original |
| `relaunch` | idle shell | `emux new` in the same cwd, close the original — or just close it |
| `hold` | a busy foreground process that cannot move without being killed | leave it running, `getcontrol account <tty> --hold --reason "…"`, and `explode` it to its own window so it can at least be acted on |

`getcontrol adopt <tty> --linear-issue ID` prints the plan for one pane.
`--apply` runs it and writes the ledger entry. Adopt one pane at a time and check
it came up; a loop that adopts twenty in a row will report success for windows
that never opened.

Work until `getcontrol status` exits 0. A pane you cannot adopt is not a failure —
it just has to be accounted for out loud, with a reason someone else can read.

## Splitting iTerm2 apart (last resort)

Terminal-app-specific automation is a dead end — there is an iTerm way, a Warp
way, a Ghostty way, and none of them compose. `explode` exists only for iTerm2
because that is where the legacy splits are; it is the one arm of this plugin
that does not generalise, and every pane you `start` or `adopt` makes it less
necessary.

An AI cannot address a pane that is one of four in a tab — it can only address a
window. `getcontrol explode --times N --apply` moves the focused session into its
own window, N times, via iTerm2's `Session > Move Session > Move Session to Window`.

But reach for it last, not first. **A pane that gets adopted into tmux does not need
exploding** — you drive it with `emux send`/`tmux send-keys`, and which window it
lives in stops mattering. Explode is for `hold` panes: the ones that must stay where
they are and still be reachable by a human or by computer-use.

## What this cannot see

- **iTerm2 window/tab topology.** The survey is built from process ancestry, tmux, and
  the emux registry — never from iTerm2's AppleScript, which hangs (`-1712`) on busy
  installs. So you know a pane is iTerm2's; you do **not** know which panes share a
  window or a tab. Do not narrate a window layout you cannot observe. `doctor` tells
  you whether the AppleScript path is answering today.
- **Remote panes.** Anything behind an `ssh` is one row here, not the tree of panes on
  the far side. Get control of that machine from that machine.

## Rules

- **Never close a pane you have not replaced and verified.** Start the tmux copy,
  capture it, see the prompt, and only then close the original.
- **Two live copies of one Claude session corrupt the transcript.** `resume` is not
  done until the original is closed.
- **Ask before closing anything.** Deciding a window is disposable is the human's call,
  not yours — bring them the list, not the aftermath.
- Report the count honestly: `24 panes, 24 not under control` is a useful finding.
  Adopting three and calling the fleet controlled is not.
