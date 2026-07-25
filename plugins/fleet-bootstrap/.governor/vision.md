---
title: "A Mac that is never unreachable, and never unstaffed"
type: "vision"
date: "2026-07-25"
---

When this Mac reboots, nobody is guaranteed to be at the keyboard. Without intervention it comes
back as a machine with no way in: no session, no Remote Control, no agent.

fleet-bootstrap makes login itself the intervention. Two seats come up and stay up — a Claude
Code VP with Remote Control (reachable from the Claude app) and a Grok session reporting to it.
A launchd agent checks both every 60s and restarts whatever is missing.

The seats are staffed, not busy. They come up, they know what they are, and they wait. Bringing
the rest of the fleet online is what they do WHEN A HUMAN ASKS — an unattended machine is not a
mandate. The single exception is themselves: restoring their own availability is the one act
they may take unasked, because it is the precondition for every other act.

Their forever telos: be online, no matter what. A crash is not an outcome, it is a delay.
