# Pavo Meeting-Bot Complaint Response Design

This document defines the Pavo design that responds to common complaints about
AI meeting assistants such as Otter and Fireflies, while preserving Pavo's own
position: source-backed audio intelligence, approval-gated routing, and a user
experience simple enough for a non-technical user.

The public complaint pattern is consistent:

- transcript accuracy can drop with accents, jargon, background noise, and
  multiple speakers
- speaker identification is unreliable or requires cleanup
- summaries and action items can change the meaning of the conversation
- auto-join bots create privacy, consent, and meeting-management concerns
- users do not always understand who can see the notes or where data goes
- setup and navigation can be too complicated
- pricing, credits, and feature gates can make the product feel slippery
- meeting notes often stop at recall instead of becoming approved follow-up

Pavo should not copy the meeting-bot category and add a few features. It should
answer the category's failure modes directly.

The product promise:

```text
Pavo catches the source, produces the best transcript it can prove, shows what
is uncertain, recommends where the record should go, and asks before anything
lands.
```

## Evidence Snapshot

This snapshot is not a legal or market-research report. It is a product-design
input, gathered from public review and help pages in June 2026.

Otter public review patterns:

- G2 aggregates Otter cons around recording issues, accuracy issues, AI
  inaccuracy, general inaccuracy, and missing features such as language support
  or reliable speaker identification.
- Otter's own help documentation says speaker identification benefits from
  clear audio, participant labeling, and review.
- Otter's own transcription FAQ says accuracy is generally better when Otter
  records the internal meeting audio stream rather than relying on a device
  microphone.
- Trustpilot's Otter summary highlights transcript accuracy, speaker
  distinction, complex conversations, and inadequate summaries as recurring
  concerns.

Fireflies public review patterns:

- G2 aggregates Fireflies cons around AI inaccuracies, navigation/meeting
  management, pricing, and privacy/storage concerns.
- G2 includes user complaints that transcriptions can be wrong enough to change
  the meaning of a meeting.
- Fireflies markets high transcription accuracy, many languages, and speaker
  recognition, which means Pavo must compete on evidence and correction loops,
  not just claim better AI.

The design implication is direct: Pavo should treat accuracy, speaker identity,
consent, routing, approval, and proof as visible product surfaces.

## Product Principle

Meeting bots optimize for convenience:

```text
join meeting -> produce notes -> share/search/sync
```

Pavo should optimize for controlled completion:

```text
preserve source -> tune evidence -> recommend routes -> approve -> land -> prove
```

This changes the product. Pavo should not promise that every transcript is
perfect. It should promise that uncertainty is visible, correctable, and
prevented from becoming unsafe downstream work.

## Complaint 1: "The Transcript Is Wrong"

Users complain when transcripts miss words, distort meaning, struggle with
accents, or fail on technical terms. Pavo's answer is not one model with a
confidence score. It is a transcript quality ladder.

### Pavo Design

Pavo should create a transcript bundle, not a single transcript.

Bundle contents:

- original audio
- source hash
- baseline transcript
- context terms used
- engine and model metadata
- uncertain spans
- speaker-change candidates
- review notes
- rerun history
- transcript manifest

The user sees a simple label:

```text
Transcript status: Ready / Needs review / Weak evidence
```

Under the hood, Pavo records the reasons:

- low-confidence words
- missing custom vocabulary
- noisy audio
- overlapping speakers
- uncertain speaker boundary
- stale model or dictionary

### Deep Algorithm Work

Pavo should use the existing `eidos-transcribe` direction:

```text
audio
-> voice activity regions
-> speaker-change candidates
-> short acoustic segments
-> speaker fingerprint scoring
-> separation-on-demand for overlap or disputed regions
-> ASR on clean regions and accepted stems
-> transcript alignment
-> reviewed speaker turns
```

The key distinction is high-recall segmentation before attribution. Pavo should
first ask whether the voice event changed, then ask who spoke. That produces a
better failure mode than coarse diarization rows.

Bad failure mode:

```text
This whole row belongs to Speaker 1.
```

Better failure mode:

```text
Speaker changed around 00:18.42. Attribution is uncertain. Review before
routing as a commitment.
```

### One-Button UX

The user should not see an audio lab by default.

Primary screen:

```text
Transcript: Needs review
Why: 3 unclear words, 2 speaker changes, 1 overlap
Button: Fix the important parts
```

Clicking the button opens only the risky spans, not the entire transcript.

## Complaint 2: "It Gets Speakers Wrong"

Speaker errors are worse than word errors because they assign commitments,
claims, objections, or sensitive statements to the wrong person.

### Pavo Design

Pavo should treat speaker identity as evidence, not a label.

Speaker evidence fields:

- candidate speaker name
- source of speaker evidence
- reviewed anchors
- fingerprint score
- local cluster consistency
- overlap status
- confidence
- review state

Pavo should avoid saying "Daniel said..." when the evidence is weak. It should
say:

```text
Speaker uncertain. Do not route as named commitment.
```

### Deep Algorithm Work

Use a voiceprint-first system with reviewable anchors:

1. detect candidate speaker changes
2. select clean anchor clips
3. ask human to approve or reject anchors when needed
4. build speaker signatures from approved anchors
5. score disputed segments against signatures
6. separate overlapping regions when possible
7. transcribe accepted clean stems
8. merge only under a reviewed policy

This matches the existing Pavo proof matrix: clean anchor enrollment, speaker
fingerprint matching, conflict tests, short interjection tests, overlap boundary
tests, accepted stem ASR, and canonical preservation.

### One-Button UX

The user sees:

```text
Who is speaking?

Pavo is sure about:
- Daniel
- Customer

Pavo is unsure about:
- 4 short moments

Button: Review speaker clips
```

The review screen plays tiny clips with three buttons:

```text
Daniel / Customer / Not sure
```

No embedding graphs. No waveform science unless the user opens expert mode.

## Complaint 3: "The Summary Changed The Meaning"

Users complain when summaries and action items sound plausible but alter the
meaning of the meeting. This is especially dangerous when a summary becomes a
task, CRM note, or customer follow-up.

### Pavo Design

Pavo should separate summary from route.

Summary:

- helps recall
- can be wrong
- is never the source of truth

Route:

- cites source spans
- has approval state
- previews destination write
- can be blocked
- produces manifest after landing

Pavo should never create an action item solely from a summary. A route needs
evidence.

### Simple UX

Every proposed action shows:

```text
Why Pavo thinks this:
[Play 00:12:18-00:12:41]

What will be written:
[Destination preview]

Buttons:
Approve / Edit / Reject
```

If the transcript is uncertain, the approve button changes:

```text
Review evidence first
```

## Complaint 4: "The Bot Joined Or Shared Weirdly"

Auto-join meeting bots create anxiety. Users worry about consent, unexpected
recording, meeting guests seeing notes, and bots joining everything by default.

### Pavo Design

Pavo should not require auto-join as the first product path.

First source modes:

- local file
- Plaud recording
- manual upload/import
- explicit calendar import later

Meeting bot mode can exist later, but it must be opt-in and visible.

Consent and visibility should be first-class fields:

- consent state: known / unknown / not required / blocked
- source visibility: private / team / governed
- destination visibility: owner / selected group / workspace / external
- allowed routes
- blocked routes

### Simple UX

Before routing:

```text
Who can see this record?

( ) Just me
( ) My selected team
( ) Workspace archive

Pavo will block routes outside this choice.
```

If consent is unknown:

```text
Consent unknown.
Pavo can archive privately, but will not share or write downstream until you
confirm the record is allowed to move.
```

## Complaint 5: "The App Is Too Hard To Navigate"

Fireflies users report navigation and setup friction. Meeting assistants often
turn into large dashboards: transcripts, channels, playlists, topics, search,
CRM sync, analytics, bots, settings, credits, integrations, and sharing.

Pavo should avoid that first.

### Pavo Design

The first screen should be a queue with one question:

```text
What should happen to this recording?
```

Primary tabs:

1. Inbox
2. Review
3. Landed
4. Archive

Do not start with:

- analytics
- libraries
- bot settings
- integration catalogs
- generic AI chat
- team dashboards

### One-Button Mode

For a non-technical user, Pavo should have one default flow:

```text
Drop recording -> Pavo checks it -> Review the important parts -> Approve
```

The UI copy should be literal:

```text
1. Add recording
2. Fix unclear parts
3. Choose what to do
4. Approve
5. Done
```

Each record has one primary next button:

- Add source
- Review transcript
- Review routes
- Approve actions
- See proof

No page should have five equally important CTAs.

## Complaint 6: "I Don't Know Where My Data Goes"

Privacy complaints are not only legal concerns. They are product trust
concerns. Users want to know what is recorded, who can see it, what is shared,
and whether it trains anything.

### Pavo Design

Every record should show a data card:

```text
Source: Plaud local download
Storage: Private local
Shared with: Nobody
Allowed destinations: Private archive, reminder
Blocked destinations: CRM, Slack, team Drive
Training: Off
Retention: Keep until deleted
```

If Pavo cannot prove one of those fields, it should say "unknown" and restrict
routing.

### Rules

- local-first should be real, not branding
- secrets stay in native credential stores
- signed URLs do not enter docs or manifests
- shared destinations require approval
- personal records do not train team policy by default
- consent unknown blocks public/team routes

## Complaint 7: "Pricing And Credits Feel Slippery"

Pricing complaints often come from surprise: credits, limited features,
personal-use cost, or paywalls around expected behavior.

### Pavo Design

Pavo should not hide trust primitives behind pricing.

Always included:

- source preservation
- transcript manifest
- uncertainty markers
- approval state
- blocked routes
- destination manifests

Paid tiers can expand:

- storage volume
- destination adapters
- team seats
- governed retention
- advanced Home policy
- audit exports

Do not charge extra for proof. Proof is the product.

## Complaint 8: "It Captures Notes But Doesn't Finish The Work"

This is where Pavo should be most different.

Meeting bots often stop at:

```text
summary + action items + search
```

Pavo should finish the controlled path:

```text
recording -> evidence -> route -> approval -> manifest
```

Examples:

- customer blocker becomes Drive archive plus Linear draft
- product interview becomes research evidence plus blocked roadmap item
- personal call becomes private archive plus reminder
- support escalation becomes engineering issue plus blocked public claim
- recruiting screen becomes ATS factual note plus restricted evaluation note

This is not "more automation." It is safer completion.

## The Pavo Design Response

The product should have two modes.

The detailed plain-user implementation standard lives in
[Pavo One-Button UX Acceptance Spec](pavo-one-button-ux-acceptance.md).

### Simple Mode

For ordinary users:

```text
Add recording.
Pavo checks quality.
Review only risky parts.
Choose what should happen.
Approve.
See proof.
```

The product hides internal complexity unless it matters.

Visible labels:

- Ready
- Needs review
- Private
- Blocked
- Approved
- Landed
- Failed

### Expert Mode

For operators, engineers, and reviewers:

- source manifests
- transcript versions
- speaker-change candidates
- anchor clips
- voiceprint scores
- overlap regions
- separated stems
- confidence reasons
- stale processing
- route fixtures
- destination manifests

Expert mode proves the system. Simple mode keeps it usable.

## Transcript Quality Ladder

Pavo should define levels of transcript quality.

Level 0: Captured

- source exists
- no transcript yet

Level 1: Baseline

- transcript exists
- source manifest exists

Level 2: Evidence-Aware

- timestamps
- speaker labels
- uncertainty markers
- context terms

Level 3: Reviewed

- key terms corrected
- speaker anchors reviewed
- risky spans checked

Level 4: Decomposed

- overlap candidates analyzed
- separated stems reviewed
- accepted stems transcribed

Level 5: Route-Safe

- evidence is good enough for the specific route
- uncertainty is reflected in approval requirements
- stale processing checked

The goal is not Level 5 for every record. The goal is the right level for the
action. A private archive may only need Level 1. A customer-facing email may
need Level 5.

## Deep Algorithm Book Section

Pavo's audio advantage should be explained plainly:

1. Detect possible speaker changes before assigning names.
2. Over-segment when audio suggests a change.
3. Score short segments against reviewed speaker fingerprints.
4. Detect overlaps instead of smoothing them into one speaker.
5. Separate disputed overlap regions into stems.
6. Transcribe accepted clean stems as evidence.
7. Preserve the canonical transcript until a reviewed merge policy approves
   replacement.
8. Keep every step in manifests.

This is how Pavo can aim for higher transcript quality than a single-pass
meeting bot. The advantage is not just "better AI." The advantage is evidence,
review, and reprocessing.

## First Release Design

The first version should be intentionally small.

### Flow

```text
Drop file or pick Plaud recording
-> Pavo nests source
-> Pavo runs baseline transcript
-> Pavo flags risky spans
-> user reviews only risky spans
-> Pavo generates route packet
-> user approves archive and Linear draft
-> Pavo lands approved actions
-> Pavo shows manifests
```

### Screens

Screen 1: Add Recording

- drop file
- pick Plaud recording
- storage mode selector
- Start button

Screen 2: Quality Check

- transcript status
- speaker status
- unclear spans count
- overlap count
- one button: Review important parts

Screen 3: Route Review

- recommended actions
- blocked actions
- evidence snippets
- approve/edit/reject buttons

Screen 4: Done

- archive proof
- created draft/issue proof
- blocked route proof
- next suggested policy if any

### Default Copy

Use:

```text
This recording is ready to archive.
This action needs review.
This route is blocked.
Pavo is not sure who said this.
Pavo will not share this record unless you approve it.
```

Avoid:

```text
Unlock insights.
AI-powered productivity.
Seamless workflow automation.
Never miss anything.
Autopilot follow-up.
```

## Product Requirements

### Accuracy Requirements

- every transcript has source references
- every uncertain span can block high-risk routes
- custom vocabulary is recorded in the manifest
- speaker labels have evidence state
- overlap regions can be routed to review
- reprocessing preserves old transcript versions

### Simplicity Requirements

- one primary next action per record
- simple mode is default
- expert mode is optional
- risky spans are reviewed before full transcript review
- every status label has a plain-English explanation
- every destination write has preview and proof

### Privacy Requirements

- storage mode chosen before routing
- consent unknown blocks sharing routes
- personal records default private
- team routes require approval
- data card visible on every record
- secrets and signed URLs redacted from manifests

### Routing Requirements

- summary never becomes action by itself
- route cites evidence
- route can be blocked
- no-action is valid
- approval is per action
- Land refuses stale or unapproved routes

## One-Button Product Design Spec

The non-technical user should not have to learn the Pavo architecture. They
should only have to answer the next real question.

Each record has exactly one primary next action:

| Record state | Primary button | What Pavo does |
| --- | --- | --- |
| No source | Add recording | Opens file/Plaud import only |
| Source nested | Check recording | Runs baseline transcript and source manifest |
| Weak evidence | Fix important parts | Opens only spans that block likely routes |
| Evidence ready | Choose destination | Shows recommended routes and blocked routes |
| Routes drafted | Approve actions | Shows destination previews with evidence |
| Actions approved | Land approved actions | Writes only approved destination artifacts |
| Land complete | See proof | Opens manifest, destination links, and blocked-route log |

Secondary controls can exist, but they cannot compete with the primary button.
If the user sees five next actions, the product has failed.

### Record Header

Every record header should show the same six fields:

```text
Title: Tuesday customer call
Source: Plaud / local file / meeting import
Transcript: Ready / Needs review / Weak evidence
Speakers: Confirmed / Needs review / Unknown
Visibility: Private / Team / Unknown
Next: Fix important parts
```

The header is the product's contract. If one of those fields is unknown, Pavo
must either ask for it or restrict routing.

### Risk Badges

Pavo should use a small fixed vocabulary of risk badges:

| Badge | Meaning | Product behavior |
| --- | --- | --- |
| `unclear words` | ASR heard something uncertain | Can block external writes |
| `speaker uncertain` | named attribution is not proved | Blocks named commitments |
| `overlap` | multiple speakers may be mixed | Requires review for high-risk routes |
| `consent unknown` | sharing permission is not established | Blocks team/external routes |
| `visibility unknown` | destination audience is unclear | Blocks landing |
| `stale transcript` | source changed or processing is old | Requires rerun before landing |
| `no evidence span` | route is summary-only | Blocks route |

The badges matter because they map directly to blocked actions. They are not
decorative warning chips.

### Review Queue

The review queue should be sorted by consequence, not timestamp.

Highest priority:

1. spans used by a proposed destination write
2. named commitments with weak speaker evidence
3. customer-facing or external-facing routes
4. consent or visibility blockers
5. internal archive cleanup

This is the plain-user version of "deep algo work": the user only sees the
places where the algorithm says a bad route could happen.

### Expert Escape Hatch

Expert mode is one click from every record but never required for normal use.
It exposes:

- source hash
- transcript versions
- engine metadata
- context terms
- speaker anchors
- voiceprint scores
- overlap regions
- separated stems
- route packet JSON
- landing manifest

Expert mode should feel like an evidence folder, not a second product.

## Screen-Level Wireframes

These are product acceptance wireframes, not visual design. The implementation
can use a native app, CLI view, or web UI, but the information architecture
should survive.

### Screen 1: Inbox

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

Rules:

- no analytics on the first screen
- no integration catalog on the first screen
- no generic chat box on the first screen
- every row has one status and one next action

### Screen 2: Add Recording

```text
Add recording

[Drop audio file]
[Pick Plaud recording]

Storage
(*) Private local
( ) Team archive

[Start]
```

Rules:

- Pavo does not ask for destinations before it has source evidence.
- Pavo does not default a personal record into team storage.
- If a signed URL is involved, Pavo downloads the source and stores only a
  redacted provenance record.

### Screen 3: Quality Check

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

Rules:

- Do not show the whole transcript unless the user asks.
- Show the count and consequence of risky spans.
- If no likely route depends on a risky span, the span can remain low priority.

### Screen 4: Risky Span Review

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

Rules:

- The user reviews the smallest meaningful clip.
- The route consequence is visible before the user decides.
- `Not sure` is a valid answer and keeps risky routes blocked.

### Screen 5: Route Review

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

Rules:

- Recommended and blocked routes appear together.
- A blocked route is proof that Pavo is doing governance work.
- No destination write can hide its evidence span.

### Screen 6: Done

```text
Done

Landed
- Drive archive created
- Linear draft created

Blocked
- Slack update blocked: consent unknown

[See proof]
```

Rules:

- The user should leave with a proof trail, not just a success toast.
- Blocked work should be preserved as a decision, not forgotten.
- The proof view should include enough redacted metadata to debug later.

## Plain-User Acceptance Tests

These tests should be written before the first full UI build.

### Test: First Recording

Given a user has never used Pavo,
when they open the app,
then they can add a recording from the first screen without opening settings.

Pass criteria:

- first screen has an `Add recording` action
- no account-wide integration setup is required for local import
- no route destination is required before source preservation

### Test: One Next Action

Given a record exists,
when it appears in the inbox,
then it has one primary next action.

Pass criteria:

- no record row has more than one primary button
- status text matches the next action
- blocked records explain the blocker in one sentence

### Test: Risky Spans Only

Given a transcript has ten pages of text and three risky spans,
when the user chooses `Fix important parts`,
then Pavo opens the three risky spans first.

Pass criteria:

- user does not need to scan the whole transcript
- every shown span explains why it matters
- user can choose `Not sure` without breaking the flow

### Test: Approval Is Real

Given Pavo recommends a Linear draft and a Drive archive,
when the user approves only the Drive archive,
then Pavo only lands the Drive archive.

Pass criteria:

- rejected and unapproved routes do not write anywhere
- proof manifest records approved, rejected, and blocked routes separately
- rerunning the same packet does not accidentally land rejected work

### Test: Data Card Always Visible

Given a record is open,
when the user views quality, route, or proof screens,
then source, storage, visibility, and training state are visible or one click
away.

Pass criteria:

- unknown fields are labeled unknown
- unknown visibility blocks external routes
- signed URLs and secrets are redacted

## Transcript Quality Acceptance Tests

Pavo should not market "highest quality" as a vibe. It should define fixtures
that prove quality improvements and block unsafe routes when quality is not
good enough.

The canonical executable fixture list is
[Pavo Complaint Fixture Ledger](pavo-complaint-fixture-ledger.md). The sections
below summarize the release-facing requirements.

### Fixture: Custom Vocabulary

Input: a recording with product names, customer names, and technical jargon.

Pass criteria:

- context terms are recorded in the manifest
- corrected terms appear in reviewed transcript spans
- terms used in routes cite reviewed evidence
- missing high-value terms create review prompts

### Fixture: Accent And Slang

Input: a recording with a non-US accent, slang, and domain-specific terms.

Pass criteria:

- low-confidence terms are flagged instead of silently rewritten
- suggested corrections preserve meaning
- uncertain spans cannot create external-facing writes without review
- manifest records the dictionary and engine used

### Fixture: Three Speakers

Input: a recording with three speakers, short interjections, and speaker
changes under two seconds.

Pass criteria:

- candidate speaker changes are high recall against the hand-labeled fixture
- short interjections are not automatically merged into the prior speaker
- named commitments require speaker evidence
- uncertain speaker turns block named downstream actions

### Fixture: Overlap

Input: a recording where two speakers talk over each other during a decision.

Pass criteria:

- overlap region is flagged
- separated-stem output is attached as evidence only if accepted
- canonical transcript is not overwritten without a reviewed merge policy
- any route using the overlap region requires review

### Fixture: Meaning Drift

Input: a meeting where a summary model could turn a discussion into a false
commitment.

Pass criteria:

- proposed action cites the exact source span
- if no source span supports the action, the route is blocked
- summary text alone cannot create a task, CRM note, Slack message, or email
- edited route text keeps the evidence link

### Fixture: Stale Processing

Input: a record whose source, transcript, or context terms changed after route
generation.

Pass criteria:

- route packet is marked stale
- `Land` refuses the packet until regeneration
- manifest records previous and current source hashes
- user sees a plain sentence explaining why approval must be refreshed

## Algorithm Pipeline Gates

The audio system should be organized around gates. A gate either advances the
record, marks it reviewable, or blocks a route.

The canonical build contracts for these gates live in
[Pavo Gate Contracts](pavo-gate-contracts.md). The table below is the
plain-language summary.

| Gate | Input | Output | Blocks when |
| --- | --- | --- | --- |
| Source gate | audio file or Plaud download | hash, duration, provenance | source missing or not durable |
| VAD gate | source audio | speech regions | audio cannot be segmented |
| Change gate | speech regions | speaker-change candidates | high-risk route depends on uncertain boundary |
| Anchor gate | clean clips | reviewed speaker anchors | named speaker has no evidence |
| Fingerprint gate | anchors plus segments | speaker scores | scores conflict or are too weak |
| Overlap gate | mixed regions | overlap flags and optional stems | overlap affects proposed action |
| ASR gate | clean regions/stems | transcript candidates | important terms are uncertain |
| Alignment gate | transcript plus timestamps | evidence spans | route has no span |
| Route gate | evidence plus policy | route packet | consent, visibility, or evidence is insufficient |
| Landing gate | approved route packet | destination proof | approval missing or packet stale |

The important product decision is that gates are visible in simple language.
The user does not need to know what VAD means. They do need to know:

```text
Pavo is not sure who said this, so it will not create a named task yet.
```

## Complaint-To-Pavo Fix Matrix

| Complaint | Pavo fix | Mechanism | Acceptance test |
| --- | --- | --- | --- |
| Transcript wrong | transcript bundle, uncertainty spans, context terms | ASR manifest, dictionary, risky-span review | custom vocabulary and accent fixtures |
| Speaker wrong | speaker identity as evidence | anchors, fingerprints, change candidates, overlap flags | three-speaker and overlap fixtures |
| Summary changed meaning | route requires evidence | source span required for every action | meaning-drift fixture |
| Bot joined weirdly | auto-join is not V1 default | local/Plaud/manual import first | first-recording test |
| Data destination unclear | data card on every record | source, storage, visibility, retention, training fields | data-card test |
| Hard to navigate | one queue and one next action | Inbox, Review, Landed, Archive | one-next-action test |
| Pricing feels slippery | proof is not a paid add-on | manifests and approval included by default | packaging review |
| Notes do not finish work | approved landing and proof | route packet, landing manifest, blocked-route log | approval-is-real test |

This matrix is the anti-slop check. If a product claim cannot point to a
mechanism and a test, remove or rewrite it.

## What Pavo Refuses In V1

Pavo should be willing to leave things out.

V1 refuses:

- automatic meeting join as the default path
- summary-only task creation
- unapproved destination writes
- hidden training or unclear data use
- external sharing when consent is unknown
- named commitments without speaker evidence
- overwriting canonical transcripts with experimental output
- pricing plans that charge extra for basic proof
- a generic AI chat screen as the product center
- integration setup before source preservation

The refusals are part of the product. They make Pavo easier to trust and easier
to build.

## Release Criteria

Pavo should not call the complaint-response product ready until these criteria
pass.

### Product Criteria

- a new user can import a local recording and understand the next action
- a Plaud recording can be nested with durable local provenance
- a transcript bundle includes source hash, engine metadata, timestamps, and
  uncertainty state
- risky spans are generated and reviewable without reading the full transcript
- a route packet can recommend, block, and preview destination actions
- landing refuses unapproved, stale, or evidence-free routes
- proof manifest records what landed and what stayed blocked

### UX Criteria

- every record row has one primary next action
- data card is visible from quality, route, and proof screens
- plain-user mode can complete archive plus one approved route
- expert mode exposes manifests without changing default flow
- all blocker states use plain sentences

### Quality Criteria

- custom-vocabulary fixture passes
- accent/slang fixture passes
- three-speaker fixture passes
- overlap fixture passes
- meaning-drift fixture passes
- stale-processing fixture passes

### Go-To-Market Criteria

- the first demo shows a real recording, not placeholder text
- the demo includes one blocked route
- the demo includes one corrected risky span
- the demo includes one approved landed destination
- marketing copy says "source-backed" and "approval-gated" before it says AI
- no public claim says Pavo is always more accurate than competitors without a
  fixture-backed proof statement

## Product Tasks For The 150-Page Book

The book should not become a 150-page pitch deck. It should become a product
operating manual.

Recommended parts:

1. The category problem: why meeting notes are not completion.
2. Public complaint evidence: Otter/Fireflies failure patterns and what they
   imply.
3. Pavo thesis: source-backed, approval-gated routing.
4. Flight Path: Nest, Tune, Scout, Land, Home.
5. User stories: founder, customer success, product research, recruiting,
   personal administration, support escalation, field notes.
6. Data model: source, transcript bundle, speaker evidence, route packet,
   landing manifest.
7. UX spec: one-button mode, expert mode, queue, review, route, proof.
8. Algorithm spec: source gate through landing gate.
9. Fixture ledger: the quality tests Pavo must pass.
10. Privacy and consent doctrine.
11. Pricing and packaging doctrine.
12. Failure modes and gotchas.
13. Demo scripts and launch narrative.
14. Roadmap and refusal list.

Each chapter should include:

- one user scenario
- one product mechanism
- one artifact example
- one acceptance test
- one gotcha

That chapter template is how the book stays useful instead of becoming bulk.

## Positioning

The proof-first demo path lives in
[Pavo Proof-First Demo Script](pavo-proof-first-demo-script.md). Packaging
boundaries live in
[Pavo Packaging And Trust Promises](pavo-packaging-trust-promises.md). The
editorial challenge pass lives in [Pavo Anti-Slop Audit](pavo-anti-slop-audit.md).

Against meeting bots:

```text
They capture meetings. Pavo controls what recordings are allowed to become.
```

Against transcription tools:

```text
They produce text. Pavo produces source-backed evidence and approved outcomes.
```

Against automation tools:

```text
They move data after rules are known. Pavo decides whether spoken evidence is
safe to route at all.
```

Against generic assistants:

```text
They can reason over a record. Pavo preserves the record, approval, manifest,
and policy trail.
```

## Success Criteria

Pavo wins if a user can say:

```text
I dropped in a recording. Pavo told me what was unclear, let me fix only the
important parts, showed what should happen next, blocked risky routes, landed
what I approved, and proved what happened.
```

Pavo loses if the user says:

- the transcript sounded confident but was wrong
- I could not tell who said what
- the summary changed the meaning
- the bot joined or shared without clear permission
- I did not know where my data went
- I got lost in the interface
- it created more cleanup work
- it wrote something I did not approve

The first release should be judged against those sentences.

## Source Links Used For This Design

- Otter G2 pros/cons: https://www.g2.com/products/otter-ai/reviews?page=3&qs=pros-and-cons
- Otter speaker identification help: https://help.otter.ai/hc/en-us/articles/37817241040535-Best-Practices-to-Maximize-Speaker-Identification
- Otter transcription accuracy FAQ: https://help.otter.ai/hc/en-us/articles/360048322533-Speech-transcription-accuracy-FAQ
- Otter Trustpilot summary: https://www.trustpilot.com/review/otter.ai
- Fireflies G2 pros/cons: https://www.g2.com/products/fireflies-ai/reviews?qs=pros-and-cons
- Fireflies product page: https://fireflies.ai/
