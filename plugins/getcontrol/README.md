# getcontrol

Too many terminal windows. Some are tabs, some are splits, some are ssh, some are
a Claude session someone started three days ago in a repo nobody remembers. None
of it is reachable by an agent, and none of it survives closing the window.

`getcontrol` takes stock of all of it, then gets each pane into a place where it
can be driven and found:

- **tmux** — so an agent can send keys and read the screen
- **emux** — so the session has a name and shows up in the registry
- **Linear** — so the work behind the pane has durable state

## Why the Linear part is not optional

A session with no issue behind it is unmanaged work. Close the window and it is
gone, and nobody but the person who opened it knew it existed. `getcontrol adopt`
**refuses** to run without a Linear reference — the refusal is the feature.

## Prevention: `start`, not cleanup

The sprawl has one source — a shell left sitting at a prompt after its agent
quit. It looks like a session, holds nothing, and nobody closes it.

```bash
eval "$(getcontrol shellinit)"      # adds a `gc` function to your shell
gc ~/repos/thing --issue EID-874    # born in tmux + emux, exec'd into
```

Born in tmux (the terminal app is just a viewport), `exec`'d into (the launching
shell is replaced, so the window closes when the work ends — no husk), and
attach-or-create (asking twice reuses instead of multiplying). Works the same in
iTerm, Terminal, Ghostty, Warp, Alacritty, or over ssh, because `exec` and `tmux`
are POSIX and none of it touches a terminal app's API.

Anything started this way never needs adopting. The rest of this tool is for
what got in before that was true.

## Every pane ends up in one of two states

A survey is a snapshot — nothing accumulates, so a pane you deliberately left
alone looks identical to one nobody ever examined. emux's registry can't close
that gap either: it only knows tmux sessions, so a raw iTerm pane is invisible to
it by construction. So getcontrol keeps a ledger (`~/.config/getcontrol/ledger.json`)
and every pane must be either:

- **governed** — adopted into tmux + emux + a Linear issue, or
- **accounted for** — `getcontrol account <tty> --hold --reason "…"`, a recorded
  decision with a reason (the `--reason` is required; accounting is not silencing)

`getcontrol status` is the closure check and **exits 1 while anything is loose**,
so it works as a gate or a cron. Ledger entries are pruned when their pane dies —
it can never vouch for something that no longer exists.

## Use

```bash
getcontrol doctor                        # which control paths work on this machine
getcontrol status                        # is everything accounted for? exits 1 if not
getcontrol survey                        # every pane, and what each one needs next
getcontrol survey --json --unaccounted   # just the ones nobody has decided anything about
getcontrol adopt ttys013 --linear-issue EID-874          # print the takeover plan
getcontrol adopt ttys013 --linear-issue EID-874 --apply  # run it, and record it
getcontrol account ttys009 --hold --reason "prod tail, must stay put"
getcontrol explode --times 3 --apply     # move iTerm2 splits into their own windows
```

Real output from a machine that had gotten away from its owner:

```
TTY      APP       TMUX        EMUX        LINEAR  RUNNING  CWD                              ACCT  NEXT
ttys004  tmux      fleet-vp    -           -       claude   …/seats/fleet-vp                 -     register
ttys005  tmux      fleet-grok  fleet-grok  -       grok     …/seats/fleet-grok               -     link
ttys006  iTerm2    -           -           -       ssh      …/aic-software-engineer-cockpit  -     redial
ttys013  iTerm2    -           -           -       claude   ~/repos-eidos-agi/chrime         -     resume
ttys016  Warp      -           -           -       -zsh     ~                                -     relaunch

24 panes: 0 governed, 0 accounted for by hand, 24 unaccounted.
```

`next` is the whole point: `register` → `link` → `resume`/`redial`/`relaunch` →
`hold`. Work them in that order, one at a time, verifying each.

## How it sees things

Process ancestry (`ps`), `tmux list-panes -a`, `lsof` for cwd, and the emux
registry — no AppleScript on the read path, because iTerm2's AppleScript hangs
(`-1712`) on installs with a lot of panes, which is exactly when you need this.

The cost of that choice: **it cannot see which panes share a window or a tab.**
It knows a pane belongs to iTerm2, not where iTerm2 is drawing it. `doctor` says
whether the AppleScript path is answering today.

`explode` needs Accessibility permission for your terminal (it drives iTerm2's
menu bar through System Events).

## Install

Ships in the [Eidos marketplace](https://github.com/eidos-agi/eidos-marketplace).
The CLI is stdlib Python 3 with no install step:

```bash
plugins/getcontrol/scripts/getcontrol survey
plugins/getcontrol/scripts/getcontrol selfcheck   # asserts the classification logic
```

Requires `tmux`. Pairs with [emux](https://github.com/eidos-agi/emux) — `getcontrol`
decides what needs adopting, `emux` does the adopting.
