---
id: "GUARD-005"
type: "guardrail"
title: "The supervisor writes down every restart"
status: "active"
date: "2026-07-25"
---

Every restart logs a timestamped line with which seat and why to ~/Library/Logs/fleet-bootstrap.log. An always-on system that heals silently is one where a crash loop is invisible; the log is the only evidence that 'it is up' is not hiding 'it has been up 400 times today'.
