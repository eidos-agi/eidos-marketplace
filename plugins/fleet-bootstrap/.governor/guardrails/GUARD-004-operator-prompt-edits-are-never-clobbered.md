---
id: "GUARD-004"
type: "guardrail"
title: "Operator prompt edits are never clobbered"
status: "active"
date: "2026-07-25"
---

The identity files in $STATE (vp.md, grok.md, and both seeds) are written only when absent. Reinstall, upgrade, and repair must all leave operator edits intact — the identity is the operator's to tune, and silently reverting it would be indistinguishable from the agent changing its own instructions.
