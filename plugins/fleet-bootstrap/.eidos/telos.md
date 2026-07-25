---
telos:
  statement: "This Mac is always reachable and always staffed: two seats \u2014 a\
    \ Claude Code VP with Remote Control and its Grok report \u2014 come up at login\
    \ and return by themselves from any interruption, without a human"
  success_when:
  - a reboot with nobody at the keyboard ends with fleet-vp reachable from the Claude
    app
  - fleet-grok is up in tmux and knows it reports to the VP
  - killing either seat is repaired by the supervisor within 60s with no human action
  - both seats resume their prior conversation across a reboot instead of starting
    fresh
  - every restart is a timestamped pair in ~/Library/Logs/fleet-bootstrap.log
  failure_when:
  - the machine reboots and nothing is reachable
  - a seat is down and the supervisor believes it is up
  - a corrupt saved conversation keeps a seat offline
  - a crash loop heals silently with no evidence in the log
  - a reinstall silently reverts operator edits to the identity prompts
  success_when_not:
  - an unsupervised agent that acts on an idle machine without a human asking
  - a general-purpose assistant that builds things instead of restoring seats
  - a supervisor so eager it restarts services a human deliberately stopped
---

# Telos

> This Mac is always reachable and always staffed: two seats — a Claude Code VP with Remote Control and its Grok report — come up at login and return by themselves from any interruption, without a human

## What success looks like

- a reboot with nobody at the keyboard ends with fleet-vp reachable from the Claude app
- fleet-grok is up in tmux and knows it reports to the VP
- killing either seat is repaired by the supervisor within 60s with no human action
- both seats resume their prior conversation across a reboot instead of starting fresh
- every restart is a timestamped pair in ~/Library/Logs/fleet-bootstrap.log

## What failure looks like

- the machine reboots and nothing is reachable
- a seat is down and the supervisor believes it is up
- a corrupt saved conversation keeps a seat offline
- a crash loop heals silently with no evidence in the log
- a reinstall silently reverts operator edits to the identity prompts

## What this eidos refuses to become

- an unsupervised agent that acts on an idle machine without a human asking
- a general-purpose assistant that builds things instead of restoring seats
- a supervisor so eager it restarts services a human deliberately stopped
