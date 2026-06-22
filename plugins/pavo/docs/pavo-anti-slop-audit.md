# Pavo Anti-Slop Audit

This audit challenges the Pavo product book and complaint-response pack against
the standard:

```text
Make the artifact harder to generate from a generic prompt.
```

Audience:

- Daniel and Eidos operators deciding whether Pavo has a real product spine
- engineers turning the book into contracts, fixtures, and UI
- design partners judging whether Pavo is different from meeting-note tools

Decision context:

- The book should be credible enough to guide implementation and early sales.
- The product should answer real meeting-bot complaints without promising magic.
- The first user experience should stay simple while the machinery remains
  inspectable.

## Active Slop Tropes Found

### Trope 1: Breadth Without Commitment

Risk:

Pavo could sound like it does capture, transcription, summaries, routing,
tasks, search, and automation without choosing the one product boundary.

Correction applied:

The docs now repeat a narrower contract:

```text
preserve source -> tune evidence -> recommend routes -> approve -> land -> prove
```

Artifacts that enforce it:

- `pavo-gate-contracts.md`
- `pavo-complaint-fixture-ledger.md`
- `pavo-one-button-ux-acceptance.md`

Remaining risk:

The long product book still contains repeated broad strategy sections. That is
acceptable for a sourcebook, but final publishing should edit repetition.

### Trope 2: "Better AI" Without Mechanism

Risk:

The product could claim better transcripts without proving why.

Correction applied:

The current docs replace generic accuracy claims with mechanisms:

- transcript bundle
- uncertainty spans
- context terms
- speaker-change candidates
- reviewed anchors
- fingerprint scores
- overlap gates
- accepted stems
- route-safe evidence levels

Release claim:

```text
Pavo produces the best transcript it can prove for the route being approved.
```

Remaining risk:

Any public page should avoid saying "most accurate" unless tied to a fixture,
benchmark, or measured domain.

### Trope 3: Automation As Universal Good

Risk:

Meeting-AI copy often implies that every note should become a task and every
task should move automatically.

Correction applied:

Pavo now treats blocked routes and no-action decisions as successful outcomes.

Artifacts that enforce it:

- blocked route list in route packet
- approval state
- landing manifest
- no-action decision
- stale packet refusal

Remaining risk:

Sales demos must show a blocked route. If demos only show happy-path task
creation, Pavo will look like ordinary workflow automation.

### Trope 4: Dashboard Instead Of Decision Desk

Risk:

The UI could become a meeting-notes dashboard with analytics, integrations,
search, chat, and generic cards.

Correction applied:

The one-button UX spec starts with a queue and one next action per record.

Required first screen:

```text
Pavo

[Add recording]

Needs your attention

Tuesday customer call       Needs review       Fix important parts >
```

Remaining risk:

If a web app is built later, visual design must avoid a SaaS landing-page
composition and use record rows, evidence panels, route previews, and manifests.

### Trope 5: Privacy As Copy Instead Of Product State

Risk:

The docs could say "private and secure" without making data movement visible.

Correction applied:

Every record now needs a data card:

- source
- storage
- visibility
- training
- retention
- allowed destinations
- blocked destinations

Routes are blocked when visibility or consent is unknown.

Remaining risk:

The real implementation must make unknown fields visible. If unknown fields are
hidden, the trust model collapses.

## Opposite Moves Applied

| Slop pattern | Opposite move |
| --- | --- |
| broad AI assistant language | source-backed approval queue |
| generic accuracy claim | fixture IDs and gate contracts |
| benefits list | release gates and refusal list |
| hidden automation | route packet before Land |
| dashboard-first UI | queue with one next action |
| privacy promise | data card and blocked destinations |
| success toast | landing manifest |
| pricing vibes | trust primitives included in every tier |

## Copy To Cut Or Avoid

Avoid:

```text
Unlock insights.
AI-powered productivity.
Seamless meeting intelligence.
Never miss anything.
Autopilot follow-up.
The most accurate transcription.
Fully automated meeting workflow.
```

Use:

```text
Pavo catches the source and asks before anything lands.
Pavo blocks named commitments when speaker evidence is weak.
Pavo blocks external actions when no evidence span supports the route.
Pavo preserves source and route dependencies so stale packets cannot land.
```

## Structure Added

The product now has concrete artifacts:

- one-button UX acceptance spec
- complaint fixture ledger
- gate contracts
- proof-first demo script
- packaging and trust promises
- anti-slop audit

Those artifacts make the book harder to fake because claims must point to a
screen, fixture, gate, route packet, or proof manifest.

## First Paragraph Challenge

Current product opening:

```text
Pavo is an evidence-first approval queue for captured conversations.
```

Assessment:

This is specific enough to avoid the generic meeting-AI category. It names the
product object: approval queue. It names the input: captured conversations. It
does not overclaim model performance.

Sharper variant for public pages:

```text
Pavo catches recordings, checks the evidence, recommends where each record
should go, and asks before anything lands.
```

## First Screen Challenge

The first screen should not be a hero, dashboard, or chat box. It should be a
work queue.

Pass:

```text
Needs your attention

Tuesday customer call       Needs review       Fix important parts >
```

Fail:

```text
Ask Pavo anything about your meetings.
```

Reason:

The queue makes the product's approval boundary visible. A chat box hides the
state machine.

## Claims Audit

| Claim | Status | Required proof |
| --- | --- | --- |
| Pavo preserves source recordings | acceptable | source manifest and hash |
| Pavo produces the best transcript it can prove | acceptable with wording | fixture/gate evidence |
| Pavo is the most accurate transcription tool | cut | unsupported benchmark |
| Pavo recommends routes | acceptable | route packet |
| Pavo asks before anything lands | acceptable | approval state and landing gate |
| Pavo automates follow-up | rewrite | only approved Land actions |
| Pavo is private | rewrite | data card and blocked destinations |
| Pavo fixes Otter/Fireflies complaints | rewrite | complaint-to-fixture mapping |

## Remaining Risk

The artifacts are now specific enough to guide implementation. The remaining
risk is operational:

- fixtures are specified but not all automated
- one-button UX is specified but not rendered as a real app
- demo script is written but still needs a fixture-backed recording package
- public pricing is a doctrine, not a launched page
- the 66k-word book still needs final editorial ordering before external use

The product direction is no longer slop. The implementation must now protect
the same standard by making blocked routes, uncertainty, and proof visible in
the actual product.
