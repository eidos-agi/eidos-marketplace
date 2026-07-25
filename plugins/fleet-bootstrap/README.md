# fleet-bootstrap

Your Mac reboots. Nobody is at the keyboard. You open the Claude app on your phone and there
is nothing to connect to.

fleet-bootstrap makes login itself the fix. Two seats come up and stay up:

| tmux session | who | what it is |
|---|---|---|
| `fleet-vp` | the VP | Claude Code with Remote Control — reachable from the Claude app as **fleet-vp** |
| `fleet-grok` | its report | a Grok session the VP can delegate to |

A launchd agent checks both every 60 seconds and restarts whatever is missing.

The seats are staffed, not busy. They come up, they know what they are, and they **wait**.
Bringing the rest of your fleet online is what they do when you ask — an unattended machine
is not a mandate. The single exception is themselves: restoring their own availability is the
one act they may take unasked, because it is the precondition for every other act.

## Install

```
/plugin marketplace add eidos-agi/eidos-marketplace
/plugin install fleet-bootstrap@eidos-marketplace
```

Then, once:

```
/fleet-bootstrap install
```

`/fleet-bootstrap status` any time, `/fleet-bootstrap uninstall` to remove it.

## How it stays up

`~/Library/LaunchAgents/com.eidos.fleet-bootstrap.plist` runs `fleet-bootstrap.sh ensure` at
login (`RunAtLoad`) and every 60s after (`StartInterval`). `ensure` checks each seat and
restarts only what is down.

Three details do the real work:

**Liveness is not `has-session`.** A tmux session whose pane holds a dead shell looks alive to
`has-session` and would never be restarted. `ensure` reads the pane's PID and confirms the
process is actually `claude` / `grok`.

**Resume can delay a seat, never keep it down.** Both seats start with `--continue` so the
conversation survives reboots. If that resume does not come up healthy within 6 seconds —
no prior session, unreadable transcript, a CLI upgrade that broke the saved state — the
supervisor logs it and starts a fresh seeded session instead. Bad state costs you continuity,
never availability.

**Every restart is written down.** `~/Library/Logs/fleet-bootstrap.log` gets a timestamped
line per restart. A system that heals silently is one where a crash loop is invisible.

Attach to either seat locally:

```
tmux attach -t fleet-vp      # ctrl-b d to detach
tmux attach -t fleet-grok
```

## The identities

Written once to `~/.local/share/fleet-bootstrap/`, then yours to tune. Reinstall never
overwrites them.

| file | what it sets |
|---|---|
| `vp.md` | the VP's role, its telos, and how to drive `fleet-grok` via `tmux send-keys` |
| `vp-seed.md` | the one human prompt the VP wakes up to |
| `grok.md` | the report's role and reporting line |
| `grok-seed.md` | the one human prompt Grok wakes up to |

The seed prompts matter: a session that boots into an empty transcript is a session with no
idea why it exists. Each seat wakes up having been asked one question, answers it, and stands by
— so when you open the app there is already a briefing there.

## Requirements

- macOS
- `tmux` (`brew install tmux`)
- Claude Code, logged in
- the Grok CLI, logged in — the agent inherits your login keychain but cannot do a first-time
  auth for you

## Configuration

Set before `/fleet-bootstrap install`; these are baked into the plist.

| Variable | Default | What it changes |
|---|---|---|
| `FLEET_VP_SESSION` | `fleet-vp` | tmux session **and** Remote Control name for the VP |
| `FLEET_GROK_SESSION` | `fleet-grok` | tmux session name for the report |
| `FLEET_BOOTSTRAP_INTERVAL` | `60` | seconds between health checks |
| `FLEET_BOOTSTRAP_STATE` | `~/.local/share/fleet-bootstrap` | prompts, runner, working directory |
| `FLEET_BOOTSTRAP_DIR` | the state dir | working directory of both seats |

The working directory defaults to the state dir on purpose: `--continue` resumes "the most
recent conversation in this directory", so a private directory is what makes the resumed chat
reliably the seat's own and not some other session that happened to run in `$HOME`.

## What this does not protect you from

- **The supervisor itself.** If the LaunchAgent is booted out or the plist deleted, nothing
  restores it. No self-check can run when the thing that runs self-checks is gone. This is the
  known gap in "no matter what" — closing it means a second, independent watchdog.
- **FileVault.** The agent starts at login, not at boot. A Mac sitting at the unlock screen is
  unreachable, and no LaunchAgent changes that.
- **Permission posture.** Both seats run with whatever permission mode their CLI defaults to,
  24 hours a day. Check what yours is (`grok` in particular may default to always-approve) and
  decide deliberately — this is a machine you are leaving logged in.
- **Usage limits.** Idle seats are cheap but they are real seats.

## Governance

The requirements, guardrails, and telos are recorded, not just implemented:

```
governor goal-list        # R1–R9, with what is proven and what is not
governor guardrail-list   # the invariants a future change must not break
eidos status              # the four-field telos contract
```

## License

MIT — see the marketplace root `LICENSE`.
