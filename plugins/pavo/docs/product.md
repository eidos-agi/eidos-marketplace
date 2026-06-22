# Pavo Product Spine

Pavo is an evidence-first approval queue for captured conversations.

It catches meetings, calls, voice notes, and field recordings before they
disappear, preserves the original media, makes the record trustworthy,
recommends where the information should go, and only writes to external systems
after the user or policy approves.

For the edited reader-facing manuscript, see
[Pavo Core Manuscript](pavo-core-manuscript.md). For the expanded long-form
product canon, see
[Pavo: The Product Book](pavo-product-book.md).
For the concrete design response to Otter/Fireflies-style meeting-bot
complaints, see
[Pavo Meeting-Bot Complaint Response Design](pavo-meeting-bot-complaint-response.md).
For the executable version of that response, see
[Pavo Complaint Fixture Ledger](pavo-complaint-fixture-ledger.md) and
[Pavo Gate Contracts](pavo-gate-contracts.md).
For the final product-design pack, see
[Pavo One-Button UX Acceptance Spec](pavo-one-button-ux-acceptance.md),
[Pavo Proof-First Demo Script](pavo-proof-first-demo-script.md),
[Pavo Packaging And Trust Promises](pavo-packaging-trust-promises.md), and
[Pavo Anti-Slop Audit](pavo-anti-slop-audit.md).
For the requirement-level completion proof, see
[Pavo Product Book Completion Audit](pavo-completion-audit.md).
That book is also the canonical home for the detailed Flight Path glossary,
status vocabulary, routing packet examples, UI product specs, marketing
assets, implementation roadmap, operating doctrine, fixture ledger, scorecards,
and final book-shape guidance.

Short version:

```text
Pavo turns spoken records into approved, source-backed work.
```

## Why Pavo Is Necessary

Meeting and recording tools already create notes. That is not enough for
important conversations.

The hard problem is the path from captured speech to trusted action:

```text
recordings and meetings
-> catch fence
-> source-backed understanding
-> routing recommendations
-> approval
-> durable records, tasks, messages, or archive entries
```

Without that path, teams face the same failures repeatedly:

1. The real recording gets trapped in a capture tool or expires behind a
   temporary link.
2. The transcript looks useful but has wrong names, wrong speakers, missing
   terms, or smoothed-over overlap.
3. The AI summary is not safe enough to route directly into Drive, Linear,
   Slack, email, CRM, or a task system.
4. Follow-up work depends on manual memory instead of a reviewable queue.

Pavo exists to separate those concerns. It can preserve the source, improve the
record, recommend destinations, and hold the final action behind approval.

## The Flight Path

Every Pavo record moves through a Flight Path. A record can stop at any stage,
but each stage adds a higher level of completion.

```text
Nest -> Tune -> Scout -> Land -> Home
```

### Nest

Capture and preserve the source recording.

Completion means Pavo has the original media or a durable local copy, source
metadata, a content hash, an owner, a source system, timestamps, and an access
path. A nested record is safe even if no transcript or routing decision exists
yet.

Examples:

- Download a Plaud recording and hash the MP3.
- Import a meeting export from a local file.
- Record the source account and non-secret provenance.
- Avoid storing signed URLs as durable artifacts.

### Tune

Make the record accurate and trustworthy.

Completion means Pavo has transcript evidence, speaker evidence, reviewed or
confidence-scored terms, uncertainty markers, and enough provenance to inspect
why the record says what it says. Tuning is where Pavo improves the raw signal:
names, speakers, vocabulary, overlap, notes, and corrections.

Examples:

- Transcribe with call-specific vocabulary.
- Compare transcript engines.
- Identify likely speakers with reviewable evidence.
- Mark overlap or ambiguous regions instead of pretending certainty.
- Generate a review bundle for human correction.

### Scout

Recommend where the information should go.

Completion means Pavo has a routing packet with suggested destinations,
proposed actions, sensitivity flags, evidence references, and approval
requirements. Scouting does not write to external systems. It prepares a
decision.

Examples:

- Recommend archive to Drive.
- Recommend a Linear issue for a product follow-up.
- Recommend a CRM note for a customer call.
- Recommend a Slack or email draft, not an automatic send.
- Recommend "private" or "ignore" when the record should not move.

### Land

Execute approved actions.

Completion means a human or policy approved the route, Pavo performed the
destination write, and Pavo wrote an audit manifest of what changed. Landing is
where a recommendation becomes a real task, note, archive object, message
draft, CRM update, or other destination artifact.

Examples:

- Create a Linear issue from an approved action.
- Save the source media, transcript, and manifest into Drive.
- Create a CRM note with source references.
- Save an email draft after approval.
- Record destination ids, timestamps, and the approving actor.

### Home

Learn where future records belong.

Completion means Pavo updates routing policy from approvals, rejections,
corrections, and exceptions. Home is not blind automation. It is policy memory:
records like this usually belong there, but these content types still require
approval.

Examples:

- Learn that board calls should be archived but not summarized to Slack.
- Learn that customer follow-up tasks require approval before CRM writes.
- Learn that personal or family recordings are private by default.
- Learn redaction rules before routing sensitive topics.

## Completion States

The Flight Path gives each record a visible completion state:

```text
intake_pending
nested
tuning
tuned
needs_review
scouted
approval_pending
approved
landed
archived
private
rejected
```

The important distinction is that partial completion is still useful. A record
can be safely nested and archived without ever landing external actions. A
record can be tuned and marked private. A record can be scouted and rejected.

## Central Object: The Routing Packet

The routing packet is the product object at the center of Scout, Land, and
Home. It should be structured enough for automation and reviewable enough for a
human.

Example shape:

```json
{
  "recording_id": "plaud_c37...",
  "flight_stage": "scouted",
  "summary": "Customer call about onboarding blockers.",
  "source_refs": [
    {
      "type": "transcript_span",
      "start": 123.4,
      "end": 146.2
    }
  ],
  "suggested_destinations": [
    {
      "destination": "linear",
      "reason": "Contains product follow-up with owner and blocker.",
      "requires_approval": true
    },
    {
      "destination": "drive",
      "reason": "Durable archive for the full source record.",
      "requires_approval": false
    }
  ],
  "proposed_actions": [
    {
      "kind": "create_issue",
      "title": "Fix onboarding import failure",
      "confidence": 0.82,
      "approval_status": "pending"
    }
  ],
  "sensitivity": {
    "contains_customer_data": true,
    "contains_personal_data": false,
    "redaction_required": false
  }
}
```

## Product Principles

- Source media is the record. A summary is never the source of truth.
- Evidence comes before routing. Recommendations should cite source spans,
  transcript rows, review notes, hashes, or manifests.
- External writes require approval unless policy explicitly allows them.
- Approval should be specific: approve this archive, this task, this note, this
  draft, or this redacted export.
- Rejections and corrections are product data. They improve Home.
- Pavo should produce durable packets before adding many destination writes.
- Secrets stay in native credential stores. Pavo stores non-secret paths,
  hashes, ids, and manifests.

## Product Boundary

Pavo should not become a generic meeting assistant or a black-box transcription
model.

Pavo owns:

- capture wrappers and source ledgers
- local media preservation
- transcript and speaker evidence orchestration
- review bundles
- routing packets
- approval state
- destination write manifests
- policy memory

`eidos-transcribe` owns:

- audio processing
- multi-engine transcription
- speaker analysis
- overlap detection
- source-separation evidence
- transcript manifests

Destination adapters own only the final approved write. They should consume
approved routing packets and return proof.

## Development Implications

The first complete product loop should be narrow:

```text
Plaud or local recording
-> Nest source media
-> Tune transcript and speaker evidence
-> Scout a routing packet
-> approve one destination action
-> Land with an audit manifest
```

Pavo should add more sources and destinations only after this loop is reliable.
The product should optimize for trust, reviewability, and controlled completion
before breadth.
