---
name: meeting2action
description: Use when turning meeting artifacts from any source into grounded decisions, follow-ups, docs, CRM notes, or Linear tasks.
---

# Meeting2Action

Use this skill when the user asks what to do after a meeting, wants a meeting
turned into actions, asks to process a call/recording/transcript/notes/chat
summary, or wants meeting evidence routed into company systems.

## Rules

- Do not assume a single source type or capture pipeline.
- First identify the meeting artifact shape and provenance.
- Separate facts from inference. Mark uncertain items explicitly.
- Do not write Eidos company records into personal, Boone Voyage, or unverified
  destinations.
- Prefer source links and concise summaries over duplicating sensitive raw
  recordings.
- Do not create HubSpot records, send messages, file tickets, or publish
  transcripts without a specific user instruction and the right authenticated
  account.
- If consent, ownership, account identity, or destination identity is unclear,
  stop and report the blocker.

## Intake Shapes

Adapt to any of these shapes:

- Google Meet recording, transcript, Gemini recap, calendar event, or Drive link.
- Zoom, Teams, or other conferencing exports.
- iOS phone-call recordings or Apple Notes summaries.
- Signal, Slack, email, or chat summaries of what happened.
- Local audio/video files, manual transcripts, or pasted raw notes.
- Partial evidence where only attendees, topic, and rough memory exist.

## Workflow

1. Inventory artifacts: list source, owner/account, timestamp, attendees,
   location, and access confidence.
2. Classify source quality: recording, transcript, AI recap, notes, memory, or
   mixed.
3. Extract grounded outputs:
   - Decisions.
   - Action items with owner and due date when known.
   - Open questions.
   - Risks or commitments.
   - Customer/company/person records mentioned.
4. Propose destination updates:
   - Linear tasks for follow-ups or internal work.
   - HubSpot notes or CRM updates when the meeting concerns a company/contact.
   - Google Docs/Drive records for durable ADRs, briefs, or transcripts.
   - Repo docs when the decision belongs in source-controlled operations.
5. Execute only the writes the user explicitly asks for, and only after checking
   account/destination identity when the destination is company-owned.

## Output Format

When reporting back, use this shape:

- `Source evidence`: artifacts found and confidence.
- `Decisions`: source-grounded bullets.
- `Actions`: owner, action, destination, due date if known.
- `Updates proposed`: destination-specific writes.
- `Blocked`: missing access, consent, identity, or unclear facts.
