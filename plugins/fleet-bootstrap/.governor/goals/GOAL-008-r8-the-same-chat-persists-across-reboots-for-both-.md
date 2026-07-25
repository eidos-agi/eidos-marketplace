---
id: "GOAL-008"
type: "goal"
title: "R8 \u2014 The same chat persists across reboots, for both seats"
status: "in-progress"
date: "2026-07-25"
depends_on: []
unlocks: []
---

Both start with --continue against a private working directory ($STATE), so 'the most recent conversation in this directory' is unambiguously the seat's own thread. IMPLEMENTED AND EXERCISED, BUT NOT YET PROVEN ACROSS A REAL REBOOT — the resume path has only been observed on a fresh state dir, where it correctly fell back to a new conversation. Closes when a genuine restart resumes both transcripts.
