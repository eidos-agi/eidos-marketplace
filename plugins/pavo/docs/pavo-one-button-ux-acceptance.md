# Pavo One-Button UX Acceptance Spec

This spec defines the plain-user surface for Pavo. It exists so Pavo can stay
simple while the evidence, transcript, routing, and landing machinery becomes
more powerful.

The target user is not an audio engineer. The target user has a recording and
wants to know:

```text
What should happen next, and is it safe?
```

## Product Rule

Each record gets one primary next action.

If a user has to choose between five equally important buttons, Pavo has failed
the plain-user test.

## Screen Contract

Every screen must answer four questions:

1. What is this recording?
2. What does Pavo know?
3. What is blocked?
4. What is the one next action?

Every screen must expose or link to the data card:

```text
Source
Storage
Visibility
Training
Retention
Allowed destinations
Blocked destinations
```

Unknown fields must be visible and must restrict routes.

## Primary Flow

```text
Inbox
-> Add Recording
-> Quality Check
-> Risky Span Review
-> Route Review
-> Done / Proof
```

The flow must work without integrations. Local file import is enough for the
first product loop.

## Screen 1: Inbox

Purpose: show the user what needs attention.

Wireframe:

```text
Pavo

[Add recording]

Needs your attention

Tuesday customer call       Needs review       Fix important parts >
Recruiting screen           Ready              Choose destination >
Personal note               Private archive    See proof >

Landed

Plaud 2026-06-10 08:15      Drive archived     See proof >
```

Visible fields:

- title
- source type
- transcript status
- route status
- visibility status
- one next action

Primary action:

- row-specific next action

Secondary actions:

- filter: Needs attention / Landed / Archive
- open expert details

Empty state:

```text
No recordings yet.
[Add recording]
```

Blocked state:

```text
Route blocked: consent unknown.
```

Acceptance tests:

- a first-time user can add a recording without opening settings
- every row has exactly one primary action
- no row uses a generic `Open` button when a more specific next action exists
- blocked rows explain the blocker in one sentence

## Screen 2: Add Recording

Purpose: preserve a source before routing.

Wireframe:

```text
Add recording

[Drop audio file]
[Pick Plaud recording]

Storage
(*) Private local
( ) Team archive

[Start]
```

Visible fields:

- source input
- storage mode
- privacy note

Primary action:

- Start

Secondary actions:

- cancel
- expert import details

Empty state:

```text
Drop an audio file or pick a Plaud recording.
```

Blocked state:

```text
Pavo could not preserve the source. It will not route this recording.
```

Acceptance tests:

- local file import does not require Drive, Slack, CRM, or Linear setup
- private local is the default storage mode
- signed URLs are never displayed or persisted in the UI
- source hash is created before route recommendations

## Screen 3: Quality Check

Purpose: tell the user whether the record is safe enough for likely routes.

Wireframe:

```text
Tuesday customer call

Transcript: Needs review
Speakers: 2 confirmed, 4 uncertain moments
Visibility: Private

Why this needs review
- 3 unclear words used in proposed actions
- 2 possible speaker changes
- 1 overlapping segment

[Fix important parts]
```

Visible fields:

- transcript status
- speaker status
- overlap count
- risky span count
- visibility status
- data card link

Primary action:

- Fix important parts

Secondary actions:

- view transcript
- open expert evidence
- archive only

Empty state:

```text
Pavo has not checked this recording yet.
[Check recording]
```

Blocked state:

```text
Pavo needs the real recording before it can check quality.
```

Acceptance tests:

- risky spans are sorted by route consequence
- full transcript is not required for the default flow
- uncertainty is shown as route impact, not raw model confidence
- user can choose archive-only when quality is weak

## Screen 4: Risky Span Review

Purpose: review the smallest clips that can change route safety.

Wireframe:

```text
Speaker uncertain at 00:18:42

[Play clip]

Transcript
"We can ship that by Friday"

Who said it?
[Daniel] [Customer] [Not sure]

Why this matters
Pavo may create a Linear task from this sentence.

[Save and next]
```

Visible fields:

- timestamp
- short clip player
- transcript span
- reason the span matters
- review choices

Primary action:

- Save and next

Secondary actions:

- not sure
- skip route
- open expert audio evidence

Empty state:

```text
No risky spans need review for the selected route.
```

Blocked state:

```text
This span cannot support a named action until the speaker is reviewed.
```

Acceptance tests:

- user reviews the risky clip, not the entire recording
- `Not sure` is a valid decision
- choosing `Not sure` keeps unsafe routes blocked
- each review choice updates speaker/evidence state

## Screen 5: Route Review

Purpose: decide what Pavo may write.

Wireframe:

```text
Recommended

1. Archive source to Drive
   Evidence: whole source
   Visibility: private
   [Approve] [Edit] [Reject]

2. Draft Linear issue: "Customer needs export retry"
   Evidence: 00:12:18-00:12:41
   Risk: speaker confirmed, transcript reviewed
   [Approve] [Edit] [Reject]

Blocked

Send Slack update
Reason: consent unknown for team sharing
```

Visible fields:

- recommended routes
- blocked routes
- evidence span for every action
- destination preview
- approval buttons
- data card

Primary action:

- Approve selected actions

Secondary actions:

- edit route
- reject route
- archive only
- open route packet JSON

Empty state:

```text
No route is recommended. Archive is still available.
```

Blocked state:

```text
This route has no evidence span, so Pavo will not land it.
```

Acceptance tests:

- every action shows an evidence span
- summary-only actions are blocked
- blocked routes are displayed, not hidden
- approval is per action
- rejecting one route does not block unrelated approved routes

## Screen 6: Done / Proof

Purpose: show what happened and what did not happen.

Wireframe:

```text
Done

Landed
- Drive archive created
- Linear draft created

Blocked
- Slack update blocked: consent unknown

[See proof]
```

Visible fields:

- landed routes
- blocked routes
- destination artifact references
- proof manifest link
- dependency hashes or redacted summary

Primary action:

- See proof

Secondary actions:

- copy proof summary
- open destination
- return to inbox

Empty state:

```text
No actions landed. The recording remains archived.
```

Blocked state:

```text
Landing stopped because approval no longer matched the current evidence.
```

Acceptance tests:

- landed and blocked routes are both visible
- proof manifest includes route packet id and dependency hashes
- unapproved routes do not appear as landed
- repeated landing attempts are idempotent

## Expert Mode

Expert mode is one click from each record. It is not the default surface.

Expert mode exposes:

- source hash
- source adapter metadata
- transcript versions
- context terms
- uncertain spans
- speaker anchors
- voiceprint scores
- overlap regions
- accepted stems
- route packet JSON
- approval history
- landing manifest

Acceptance tests:

- expert mode cannot bypass approval
- expert mode cannot expose secrets or signed URLs
- expert mode shows enough dependency state to explain stale packets

## Plain-User Release Checklist

Before the UX is release-ready:

- first-time user can add a local recording
- every record row has one primary next action
- data card is visible from quality, route, and proof screens
- risky spans open before full transcript
- blocked routes explain themselves in one sentence
- route review shows recommended and blocked routes together
- proof view shows landed and blocked outcomes
- no screen centers a generic AI chat box
- no screen requires integration setup before source preservation

## Failure Modes

Pavo fails the plain-user test if:

- the first screen is a dashboard instead of a queue
- the user has to understand audio model internals
- the user must connect integrations before trying a recording
- blocked routes disappear from the UI
- `Approve` appears before evidence is visible
- proof is replaced by a success toast
- the product uses confidence scores without route consequences

The product should feel like a review desk for spoken evidence, not a meeting
notes dashboard.
