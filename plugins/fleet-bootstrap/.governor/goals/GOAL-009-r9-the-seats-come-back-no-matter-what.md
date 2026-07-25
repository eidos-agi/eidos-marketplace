---
id: "GOAL-009"
type: "goal"
title: "R9 \u2014 The seats come back no matter what"
status: "available"
date: "2026-07-25"
depends_on: []
unlocks: []
---

Handled today: process death, session death, dead-shell zombies, corrupt or absent saved state (resume failure falls back to a fresh seeded start, so bad state delays a seat but can never keep it down), sleep/wake, and login. NOT handled: if the LaunchAgent itself is booted out or the plist deleted, nothing restores it — the supervisor is a single point of failure and no self-check can run when the thing that runs self-checks is gone. Closing this goal means a second, independent watchdog.
