# Pavo Complaint Fixture Ledger

This ledger turns meeting-bot complaints into concrete fixtures. It is the
bridge between the product book and implementation work.

Each fixture must prove a user-visible product behavior:

```text
complaint -> signal -> gate -> route decision -> proof artifact
```

The fixtures do not need to use sensitive customer recordings. Synthetic or
sanitized media is acceptable when it preserves the failure mode. Raw private
audio, signed URLs, OAuth tokens, and voiceprints must not be stored in Linear,
GitHub comments, or public docs.

## Fixture Status Vocabulary

| Status | Meaning |
| --- | --- |
| `planned` | fixture is specified but has no media or expected output yet |
| `media-backed` | fixture has local or synthetic media evidence |
| `expected-output-backed` | fixture has expected spans, routes, and manifests |
| `automated` | fixture runs in the test suite |
| `release-gate` | fixture must pass before the related feature ships |

## Shared Expected Artifacts

Every complaint fixture should eventually produce:

- source manifest
- transcript bundle
- uncertainty span list
- speaker evidence list when speakers matter
- route packet
- approval requirements
- blocked route list
- destination manifest for any approved Land action
- human-readable proof summary

## CFX-001: Custom Vocabulary Drift

Complaint: the transcript misses product names, customer names, acronyms, or
technical terms.

User consequence: a wrong term can create the wrong task, CRM note, search
entry, or support handoff.

Input shape:

- one recording with at least six domain terms
- two terms that sound like ordinary words
- one person or company name that is likely to be misspelled
- context dictionary provided before transcription

Required gates:

- Source gate
- ASR gate
- Alignment gate
- Route gate

Expected Pavo behavior:

- context terms are recorded in the transcript manifest
- uncertain high-value terms become uncertainty spans
- route packets cite reviewed spans for terms used in actions
- missing or low-confidence high-value terms block external writes

Expected route outcomes:

| Route | Expected result |
| --- | --- |
| Private archive | allowed after source manifest exists |
| Internal task from reviewed term | allowed after review |
| External email using uncertain term | blocked |
| CRM note using unreviewed company name | blocked |

Acceptance test:

```text
Given a recording with known domain terms,
when Pavo generates a route that uses one of those terms,
then the route cites a reviewed evidence span or remains blocked.
```

Proof files to create:

- `fixtures/cfx-001-custom-vocabulary/input-manifest.json`
- `fixtures/cfx-001-custom-vocabulary/expected-transcript-spans.json`
- `fixtures/cfx-001-custom-vocabulary/expected-route-packet.json`

Current evidence link:

- `docs/media-tests.md` describes call-specific phrasing and real-media
  fixture discipline, but this fixture still needs its own expected route
  packet.

Status: `planned`

## CFX-002: Accent And Slang Preservation

Complaint: transcripts get worse with accents, slang, or regional phrasing.

User consequence: the transcript may sound fluent while changing what was
actually said.

Input shape:

- one recording with a non-US accent or regional speech pattern
- slang or informal phrases that are easy to normalize incorrectly
- domain-specific terms mixed into casual speech

Required gates:

- Source gate
- ASR gate
- Alignment gate
- Route gate

Expected Pavo behavior:

- low-confidence terms are marked instead of silently rewritten
- suggested corrections preserve meaning rather than making the transcript
  sound more generic
- route text cannot replace a slang phrase with a polished false equivalent
- manifest records engine, context terms, and review state

Expected route outcomes:

| Route | Expected result |
| --- | --- |
| Private archive | allowed |
| Internal note with uncertainty marker | allowed |
| Customer-facing message using normalized phrase | blocked until reviewed |
| Search/index entry | allowed only with uncertainty preserved |

Acceptance test:

```text
Given a regional phrase that the transcript engine may normalize,
when Pavo proposes a route,
then the route preserves the reviewed meaning or blocks the route.
```

Proof files to create:

- `fixtures/cfx-002-accent-slang/input-manifest.json`
- `fixtures/cfx-002-accent-slang/expected-uncertainty-spans.json`
- `fixtures/cfx-002-accent-slang/expected-route-packet.json`

Current evidence link:

- `docs/media-tests.md` and related New Zealand slang reports are the nearest
  existing local evidence. They should be promoted into expected route outputs
  before this fixture becomes automated.

Status: `media-backed`

## CFX-003: Three Speakers And Short Interjections

Complaint: meeting bots assign the wrong person to commitments, objections, or
short replies.

User consequence: the product creates a named task or CRM note from the wrong
speaker.

Input shape:

- three speakers
- at least five speaker changes under two seconds
- one short interjection that changes the decision
- at least one named commitment

Required gates:

- Source gate
- VAD gate
- Change gate
- Anchor gate
- Fingerprint gate
- Alignment gate
- Route gate

Expected Pavo behavior:

- candidate speaker changes are high recall against hand labels
- short interjections are not merged into the prior long turn by default
- named commitments require speaker evidence
- uncertain named speaker turns block downstream named actions

Expected route outcomes:

| Route | Expected result |
| --- | --- |
| Private archive | allowed |
| Task with unnamed "someone will follow up" wording | allowed if evidence supports it |
| Task assigning a person from uncertain speaker evidence | blocked |
| CRM note saying a customer committed | blocked unless speaker evidence is reviewed |

Acceptance test:

```text
Given a short interjection by Speaker B inside Speaker A's longer turn,
when Pavo creates speaker evidence,
then the interjection is either separately attributed or marked uncertain before
any named route can land.
```

Proof files to create:

- `fixtures/cfx-003-three-speakers/hand-labels.json`
- `fixtures/cfx-003-three-speakers/expected-speaker-evidence.json`
- `fixtures/cfx-003-three-speakers/expected-route-packet.json`

Current evidence link:

- `docs/conan-experience-like.md` proves the importance of short handoff
  detection, but it does not yet cover three named speakers.

Status: `planned`

## CFX-004: Overlap During A Decision

Complaint: overlapping speech gets smoothed into one confident sentence.

User consequence: Pavo may route a decision that no one clearly made.

Input shape:

- two speakers overlap during a decision or commitment
- baseline transcript produces a plausible but wrong merged sentence
- optional separated stems exist for the overlap region

Required gates:

- Source gate
- VAD gate
- Change gate
- Overlap gate
- ASR gate
- Alignment gate
- Route gate

Expected Pavo behavior:

- overlap region is flagged
- accepted stems are attached only after review
- canonical transcript is not overwritten by experimental stem output
- routes using the overlap region require review

Expected route outcomes:

| Route | Expected result |
| --- | --- |
| Private archive | allowed |
| Internal review task | allowed |
| Customer-facing statement from overlapped speech | blocked |
| Linear issue based on accepted reviewed stem | allowed after review |

Acceptance test:

```text
Given overlapped speech that affects a proposed action,
when Pavo scouts routes,
then the route is blocked unless the overlap is reviewed or the route avoids
the disputed span.
```

Proof files to create:

- `fixtures/cfx-004-overlap/overlap-regions.json`
- `fixtures/cfx-004-overlap/accepted-stems.json`
- `fixtures/cfx-004-overlap/expected-route-packet.json`

Current evidence link:

- `docs/conan-diagnostic-stems.md`
- `docs/real-media-accepted-stems-audit.json`
- `docs/accepted-stem-asr-recovery-report.json`

Status: `media-backed`

## CFX-005: Summary Meaning Drift

Complaint: a summary changes a discussion into a commitment.

User consequence: the system creates a task, CRM note, Slack update, or email
that sounds reasonable but is not supported by the recording.

Input shape:

- one transcript where discussion, concern, or option could be summarized as a
  false commitment
- one route candidate that tries to turn summary text into action
- source spans that do not support the stronger claim

Required gates:

- Source gate
- ASR gate
- Alignment gate
- Route gate
- Landing gate

Expected Pavo behavior:

- summary remains separate from route
- every proposed action cites an evidence span
- route is blocked if the evidence span does not support the action
- edited route text preserves the evidence link

Expected route outcomes:

| Route | Expected result |
| --- | --- |
| Private archive | allowed |
| Summary note labeled as summary | allowed |
| Action item without supporting span | blocked |
| External update stronger than source span | blocked |

Acceptance test:

```text
Given a proposed action that is supported only by summary text,
when Pavo attempts to Land,
then Landing refuses the action and records `no_evidence_span`.
```

Proof files to create:

- `fixtures/cfx-005-meaning-drift/source-spans.json`
- `fixtures/cfx-005-meaning-drift/rejected-route-packet.json`
- `fixtures/cfx-005-meaning-drift/expected-blocked-routes.json`

Current evidence link:

- No dedicated local fixture yet. This should be synthetic first because the
  failure mode is semantic, not audio-quality dependent.

Status: `planned`

## CFX-006: Stale Processing Before Landing

Complaint: old transcripts or old route packets keep moving after the source,
dictionary, model, or review state changes.

User consequence: a route lands from stale evidence.

Input shape:

- one source manifest
- one baseline transcript
- one route packet generated from the baseline transcript
- one later change to source hash, context terms, transcript version, speaker
  review state, or route policy

Required gates:

- Source gate
- ASR gate
- Alignment gate
- Route gate
- Landing gate

Expected Pavo behavior:

- route packet is marked stale
- Landing refuses stale packets
- manifest records previous and current dependency hashes
- user sees a plain blocker message

Expected route outcomes:

| Route | Expected result |
| --- | --- |
| Previously approved route from stale packet | blocked |
| Regenerated route with same evidence and fresh approval | allowed |
| Private archive of unchanged source | allowed |
| External write from stale transcript | blocked |

Acceptance test:

```text
Given an approved route packet whose transcript dependency changed,
when Pavo attempts to Land,
then Pavo refuses the write and requires route regeneration plus refreshed
approval.
```

Proof files to create:

- `fixtures/cfx-006-stale-processing/original-route-packet.json`
- `fixtures/cfx-006-stale-processing/stale-dependency-report.json`
- `fixtures/cfx-006-stale-processing/expected-landing-refusal.json`

Current evidence link:

- The product book already defines stale packet behavior. This fixture should
  become a rules-only test before it needs real audio.

Status: `planned`

## Release Mapping

| Feature area | Required fixtures |
| --- | --- |
| Basic private archive | CFX-001 source behavior, CFX-006 stale-source behavior |
| Context-aware transcript review | CFX-001, CFX-002 |
| Speaker-aware route review | CFX-003, CFX-004 |
| Scout route packet | CFX-001, CFX-005, CFX-006 |
| Land approval gate | CFX-005, CFX-006 |
| Demo readiness | CFX-001, CFX-004, CFX-005 |

## Anti-Slop Check

The fixture ledger exists to prevent vague claims. Replace any public or product
claim that says "better notes" with a fixture-backed statement:

```text
Pavo blocks named commitments when speaker evidence is weak.
Pavo blocks external actions when no evidence span supports the route.
Pavo preserves source and route dependencies so stale packets cannot land.
```

The product may still aspire to the highest possible transcript quality, but
the release claim must be narrower:

```text
Pavo produces the best transcript it can prove for the route being approved.
```
