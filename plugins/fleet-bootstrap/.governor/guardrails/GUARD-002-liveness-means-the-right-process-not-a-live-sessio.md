---
id: "GUARD-002"
type: "guardrail"
title: "Liveness means the right process, not a live session name"
status: "active"
date: "2026-07-25"
---

Never treat `tmux has-session` as health. A session whose pane holds a dead shell is down while looking up, and a supervisor that believes it is up will never restart it. Check the pane PID's command.
