---
id: "GOAL-010"
type: "goal"
title: "R10 \u2014 HOSTKEY carries a seat on the same terms as the Mac"
status: "in-progress"
date: "2026-07-25"
depends_on: []
unlocks: []
---

eidos-bm-e1 (epyc-56223, Ubuntu 24.04) runs the same runner under cron (@reboot + every minute) instead of launchd. Three host differences had to be absorbed: no writable /tmp (tmux socket dir and claude's /tmp/claude-<uid> both relocate to the state dir), no grok CLI (the report seat is skipped, the VP is not), and settings that do not survive into cron's environment (persisted to $STATE/config at install).

BLOCKED, NOT DONE: the seat is up but parked on Claude Code's trust-folder prompt. The fix — clear_trust_gate, which answers that menu only when it is on screen — is written and copied to the host, but the reinstall that would activate it was refused by the permission classifier. HOSTKEY is running the older runner until Daniel runs the install himself.
