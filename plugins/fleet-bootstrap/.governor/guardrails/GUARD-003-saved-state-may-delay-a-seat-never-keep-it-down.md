---
id: "GUARD-003"
type: "guardrail"
title: "Saved state may delay a seat, never keep it down"
status: "active"
date: "2026-07-25"
---

Any resume path (--continue for either CLI) must fall back to a fresh seeded start when the resume attempt does not come up healthy. A corrupt transcript must never be able to hold a seat offline, because the forever telos outranks conversational continuity.
