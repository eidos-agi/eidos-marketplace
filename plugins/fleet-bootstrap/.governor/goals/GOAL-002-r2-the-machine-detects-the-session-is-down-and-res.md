---
id: "GOAL-002"
type: "goal"
title: "R2 \u2014 The machine detects the session is down and restarts it, unattended"
status: "complete"
date: "2026-07-25"
depends_on: []
unlocks: []
---

StartInterval=60 re-runs `fleet-bootstrap.sh ensure`. Liveness is not has-session: it is has-session AND the pane process is the expected binary, so a session holding a dead shell reads as down. Verified: killed the session at 12:37:09, launchd restored it at 12:38:10 with no human action.
