---
id: "ADR-001"
type: "decision"
title: "ADR-001 \u2014 Proposed charter amendment: the fleet is multi-host"
status: "proposed"
date: "2026-07-25"
---

The charter written at 12:5x describes one Mac. The requirement has since grown to include HOSTKEY (eidos-bm-e1, Ubuntu 24.04), and the two hosts are not alike: no launchd, no grok binary, no writable /tmp.

PROPOSED, NOT APPLIED. `eidos define` refuses to redefine an existing eidos, and hand-editing .eidos/telos.md would be an agent silently rewriting its own contract — the thing the guardrails exist to prevent. Daniel applies this.

Statement becomes: every machine Daniel depends on is always reachable and always staffed — a Claude Code VP with Remote Control (plus a Grok report where available) comes up at login and returns by itself from any interruption, without a human.

Add to success_when: HOSTKEY carries a VP seat under cron on the same terms as the Mac under launchd.

Add to failure_when: a seat parked on a blocking prompt while every process check calls it healthy; a host-specific assumption (writable /tmp, launchd, grok installed) silently drops a host from the fleet.

Add to success_when_not: a supervisor that types into a session blind rather than answering a prompt it can actually see.
