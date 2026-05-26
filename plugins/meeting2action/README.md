# Meeting2Action

Codex plugin for turning messy meeting evidence into grounded company action.

Meeting2Action is intentionally source-agnostic. A meeting may arrive as a
Google Meet recording, Zoom export, iOS phone-call note, Signal recap, calendar
event, Drive transcript, email thread, local audio file, handwritten summary, or
raw chat paste. The plugin's job is to adapt to the source shape that exists,
extract what can be proven from it, and produce the next useful company actions.

It is not a background recorder, Drive router, or one-off Apps Script
automation.

## Outputs

- Evidence inventory: what artifacts exist and where they came from.
- Meeting brief: attendees, context, agenda, decisions, open questions, risks.
- Action register: owner, task, destination, due date if known, source evidence.
- Destination plan: Linear issues, HubSpot notes, Google Docs/Drive records, or
  repo docs that should be created or updated.
- Stop conditions: missing consent, wrong account, wrong company Drive, uncertain
  source provenance, or sensitive content that needs human approval.

## Safety

- Do not assume the meeting source. Inspect the artifact and state confidence.
- Do not write into personal, Boone Voyage, or unverified destinations for Eidos
  company records.
- Prefer links and summaries over duplicating sensitive raw recordings.
- Keep source evidence attached to every decision and action.
- Do not create HubSpot records, send messages, or publish transcripts without a
  specific user instruction and the right authenticated account.
- If consent, ownership, or destination identity is unclear, stop and report the
  blocker.
