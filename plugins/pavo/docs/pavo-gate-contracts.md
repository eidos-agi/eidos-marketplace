# Pavo Gate Contracts

This document defines the build contracts behind the complaint-response design.
It is intentionally less narrative than the product book. The purpose is to
make Pavo's gates testable.

Pavo's rule:

```text
No evidence span, no action.
No approval, no landing.
No known visibility, no external route.
No speaker evidence, no named commitment.
```

## Contract Vocabulary

Gate status values:

| Status | Meaning |
| --- | --- |
| `pass` | evidence is sufficient for the requested route |
| `review` | evidence may be enough after human review |
| `block` | route cannot proceed |
| `stale` | dependency changed after the route was generated |
| `not_applicable` | gate does not apply to this route |

Route risk values:

| Risk | Meaning |
| --- | --- |
| `archive_only` | private archive or local proof only |
| `internal_note` | internal note/search entry with uncertainty preserved |
| `internal_action` | task or internal workflow change |
| `team_share` | visible to a team or workspace |
| `external_action` | email, customer-facing message, CRM mutation, or public artifact |

Approval values:

| Status | Meaning |
| --- | --- |
| `not_required` | route is low-risk and policy permits it |
| `required` | user or policy approval required before Land |
| `approved` | approved version is current |
| `rejected` | user rejected the route |
| `expired` | approval no longer matches dependencies |

## Shared Gate Record Shape

Gate records should be serializable as JSON:

```json
{
  "gate": "source",
  "status": "pass",
  "route_risk": "internal_action",
  "reasons": [],
  "blocks": [],
  "review_prompts": [],
  "evidence_refs": [
    {
      "artifact_id": "source_audio",
      "span": null,
      "hash": "sha256:redacted-example"
    }
  ],
  "dependencies": {
    "source_hash": "sha256:redacted-example",
    "transcript_version": "trn_001",
    "policy_version": "policy_001"
  }
}
```

Required fields:

- `gate`
- `status`
- `route_risk`
- `reasons`
- `blocks`
- `review_prompts`
- `evidence_refs`
- `dependencies`

## Source Gate

Question: does Pavo have a durable source artifact?

Inputs:

- local audio file or Plaud download
- source adapter metadata
- owner
- created/imported timestamps

Outputs:

- source hash
- duration
- byte size
- source adapter
- redacted provenance
- source artifact id

Pass when:

- source exists locally or in approved durable storage
- hash and byte size are recorded
- provenance does not contain signed URLs or secrets

Review when:

- source exists but owner, sensitivity, or storage mode is unknown

Block when:

- source is missing
- source exists only as an expiring signed URL
- provenance would expose a secret

Plain-user message:

```text
Pavo needs the real recording before it can route anything.
```

## VAD Gate

Question: can Pavo separate speech regions from non-speech regions?

Inputs:

- source audio
- audio duration
- optional noise profile

Outputs:

- speech region list
- non-speech region list
- segmentation confidence

Pass when:

- speech regions cover the expected spoken portions
- obvious silence and non-speech are not routed as text evidence

Review when:

- noise, music, or crosstalk makes speech-region boundaries uncertain

Block when:

- audio cannot be decoded or segmented

Plain-user message:

```text
Pavo cannot reliably find the spoken parts of this recording yet.
```

## Change Gate

Question: did the speaker probably change near a span that matters?

Inputs:

- speech regions
- acoustic change candidates
- transcript timestamp alignment

Outputs:

- speaker-change candidates
- boundary confidence
- affected transcript spans

Pass when:

- route does not depend on disputed speaker boundaries
- or boundary evidence is reviewed and sufficient

Review when:

- a route depends on a span near an uncertain speaker change

Block when:

- a named commitment depends on an unresolved boundary

Plain-user message:

```text
Pavo is not sure where one speaker stops and the next starts.
```

## Anchor Gate

Question: does a named speaker have reviewed evidence?

Inputs:

- clean clips
- candidate speaker names
- human review labels

Outputs:

- approved anchors
- rejected anchors
- unknown anchors
- speaker evidence ids

Pass when:

- named route uses speaker anchors reviewed for the relevant speaker

Review when:

- speaker may be identifiable from clean clips but needs human confirmation

Block when:

- route names a speaker with no approved evidence

Plain-user message:

```text
Pavo needs a reviewed voice clip before naming this person in an action.
```

## Fingerprint Gate

Question: does the disputed segment match a reviewed speaker signature?

Inputs:

- approved anchors
- segment fingerprints
- score thresholds

Outputs:

- speaker candidate scores
- conflict markers
- unknown speaker markers

Pass when:

- score is strong enough for the route risk
- no conflict marker affects the route span

Review when:

- score is close but not route-safe
- multiple candidates are plausible

Block when:

- scores conflict or are too weak for a named commitment

Plain-user message:

```text
Pavo is not sure who said this, so it will not create a named task yet.
```

## Overlap Gate

Question: are multiple speakers mixed in a span used by a route?

Inputs:

- speech regions
- overlap detector output
- optional separated stems
- review state for stems

Outputs:

- overlap region list
- accepted stem list
- rejected stem list
- canonical-preservation decision

Pass when:

- route avoids overlap
- or accepted reviewed stems support the route

Review when:

- overlap affects a proposed action and stems exist for review

Block when:

- route depends on unresolved overlap

Plain-user message:

```text
Two people may be talking here. Review this clip before Pavo uses it.
```

## ASR Gate

Question: is the transcript good enough for the route risk?

Inputs:

- source or accepted stems
- context terms
- ASR output
- confidence or uncertainty markers

Outputs:

- transcript candidate
- uncertain spans
- context term hits and misses
- engine metadata

Pass when:

- route-critical terms are reviewed or high confidence
- uncertainty is preserved for low-risk archive/search routes

Review when:

- high-value terms are uncertain
- context terms are missed

Block when:

- route-critical words are uncertain and unreviewed

Plain-user message:

```text
Pavo heard a few important words unclearly.
```

## Alignment Gate

Question: can every proposed action point to source evidence?

Inputs:

- transcript candidates
- timestamps
- source spans
- route candidates

Outputs:

- evidence spans
- route-to-span mapping
- unsupported claims

Pass when:

- every route claim has a source span

Review when:

- a route has weak but plausible support

Block when:

- a route is summary-only or lacks a source span

Plain-user message:

```text
Pavo cannot find the part of the recording that supports this action.
```

## Route Gate

Question: is the proposed destination action allowed?

Inputs:

- evidence spans
- route candidate
- sensitivity
- consent state
- source visibility
- destination visibility
- policy version

Outputs:

- allowed routes
- blocked routes
- required approvals
- destination preview

Pass when:

- evidence, consent, visibility, and policy permit the route

Review when:

- policy requires approval or redaction before landing

Block when:

- consent is unknown for team/external sharing
- destination visibility is unknown
- route risk exceeds evidence quality

Plain-user message:

```text
Pavo will not share this recording until visibility and approval are clear.
```

## Landing Gate

Question: can Pavo write the approved action now?

Inputs:

- route packet
- approval decision
- current dependency hashes
- destination adapter dry-run

Outputs:

- destination manifest
- idempotency key
- landed route list
- blocked route list
- failure report

Pass when:

- route is approved
- dependencies are current
- adapter dry-run is valid
- idempotency key prevents duplicate writes

Review when:

- destination preview changed after approval

Block when:

- route is unapproved
- approval is stale
- dependency hash changed
- adapter dry-run fails

Plain-user message:

```text
This action needs fresh approval before Pavo can write it.
```

## Route Packet Minimum Contract

A route packet must include:

```json
{
  "packet_id": "pkt_example",
  "recording_id": "rec_example",
  "source_hash": "sha256:redacted-example",
  "transcript_version": "trn_001",
  "policy_version": "policy_001",
  "created_at": "2026-06-11T00:00:00Z",
  "routes": [
    {
      "route_id": "route_001",
      "destination": "linear_draft",
      "risk": "internal_action",
      "status": "review",
      "evidence_spans": ["span_001"],
      "required_approvals": ["owner"],
      "blocked_by": [],
      "preview": {
        "title": "Investigate export retry failure",
        "body_redacted": true
      }
    }
  ],
  "blocked_routes": [
    {
      "route_id": "route_002",
      "destination": "slack",
      "risk": "team_share",
      "status": "block",
      "blocked_by": ["consent_unknown"],
      "plain_message": "Consent is unknown, so Pavo will not share this in Slack."
    }
  ]
}
```

Minimum route status values:

- `recommended`
- `review`
- `approved`
- `rejected`
- `blocked`
- `landed`
- `failed`
- `stale`

## Landing Manifest Minimum Contract

A landing manifest must include:

- route packet id
- approved route ids
- rejected route ids
- blocked route ids
- destination adapter
- dry-run result
- idempotency key
- destination artifact refs
- redaction status
- dependency hashes
- timestamp
- failure details if any

Landing manifests are proof artifacts. They should be safe to attach to a
Linear issue or support ticket after redaction.

## Test Mapping

| Gate | Fixture coverage |
| --- | --- |
| Source | CFX-001, CFX-006 |
| VAD | CFX-003, CFX-004 |
| Change | CFX-003, CFX-004 |
| Anchor | CFX-003 |
| Fingerprint | CFX-003 |
| Overlap | CFX-004 |
| ASR | CFX-001, CFX-002, CFX-004 |
| Alignment | CFX-001, CFX-005 |
| Route | CFX-001, CFX-002, CFX-003, CFX-004, CFX-005, CFX-006 |
| Landing | CFX-005, CFX-006 |

The first implementation can be rules-only. The contract does not require every
audio model to be perfect before Scout and Land become testable. It requires
Pavo to preserve uncertainty and block routes when the evidence is not good
enough.
