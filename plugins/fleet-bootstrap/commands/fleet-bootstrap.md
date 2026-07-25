---
description: "Install, check, or remove the supervisor that keeps this machine staffed — a Remote-Control Claude Code VP plus a Grok report. Argument: install | status | uninstall."
allowed-tools: Bash
---

Action requested: "$ARGUMENTS" (default to `status` if empty).

Run `${CLAUDE_PLUGIN_ROOT}/scripts/fleet-bootstrap.sh <action>` and report what it says.

What it sets up: two tmux seats, supervised every 60 seconds — `fleet-vp` (Claude Code with
Remote Control, reachable from the Claude app) and `fleet-grok` (a Grok session that reports
to the VP). launchd runs the check on macOS, cron on Linux. Both seats start with `--continue`
so their conversations survive reboots, falling back to a fresh seeded start if the resume
does not come up healthy.

Notes for reporting back:

- `install` prints status after ~20s. If both seats are healthy, say the machine is reachable
  and name the attach commands. If the host has no grok CLI, the VP seat alone is the correct
  outcome — not a partial failure.
- If a seat is DOWN, read the supervisor log before speculating: `~/Library/Logs/fleet-bootstrap.log`
  on macOS, `$STATE/fleet-bootstrap.log` on Linux. Repeated restart lines a minute apart mean a
  crash loop, and the seat's pane (`tmux capture-pane -p -t <session>`) usually says why.
- A seat can be running and still not ready — parked on a trust-folder prompt, an onboarding
  screen, or an update notice. `ensure` clears the trust prompt when it can see it; anything
  else needs a human to attach once.
- Do not claim it survives reboot unless the supervisor is actually installed. That launch
  agent or cron entry is the only thing making it true.

Settings are captured to `$STATE/config` at install time, because launchd and cron do not
inherit the shell you installed from. To change one, set it and re-run install:
`FLEET_VP_SESSION`, `FLEET_GROK_SESSION`, `FLEET_BOOTSTRAP_DIR`, `FLEET_BOOTSTRAP_INTERVAL`,
`FLEET_BOOTSTRAP_STATE`.
