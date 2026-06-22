# Pavo Proof-First Demo Script

This demo exists to teach the category:

```text
Pavo turns spoken records into approved, source-backed work.
```

The demo should use a real or fixture-backed recording. Placeholder meeting
text is not acceptable for the main demo because Pavo is selling proof.

## Demo Standard

The demo must show:

- one preserved source recording
- one risky transcript or speaker span
- one correction or `Not sure` review decision
- one recommended route
- one blocked route
- one approved Land action
- one proof manifest

The blocked route is part of the win. It proves that Pavo is not silent
automation.

## Recommended Fixture

Use a customer-call style recording or synthetic fixture with:

- a product/customer name that can be mistranscribed
- a short speaker interjection
- one sentence that could become a Linear task
- one Slack/team-sharing route that should be blocked by consent or visibility
- one private archive route that should be allowed

Good fixture mapping:

- `CFX-001` for custom vocabulary
- `CFX-003` for short speaker interjection
- `CFX-005` for summary meaning drift
- `CFX-006` for stale packet refusal if showing an advanced path

## Cast

Narrator: Pavo operator.

User: non-technical person who has a recording.

Reviewer: same person when approval is required.

Pavo: product surface, not a chat persona.

## Demo Beat 1: Open With The Queue

Screen:

```text
Pavo

[Add recording]

Needs your attention

Tuesday customer call       Needs review       Fix important parts >
```

Narration:

```text
Pavo starts with the queue. It does not start with analytics, chat, or an
integration catalog. This recording has one next action.
```

Proof shown:

- record row
- source type
- status
- primary action

Avoid saying:

- "AI meeting assistant"
- "automated productivity"
- "never miss anything"

## Demo Beat 2: Preserve The Source

Action:

Add a local recording or pick a Plaud recording.

Screen:

```text
Add recording

[Drop audio file]
[Pick Plaud recording]

Storage
(*) Private local
( ) Team archive

[Start]
```

Narration:

```text
Pavo preserves the source first. It cannot route a note safely if it cannot
prove the recording it came from.
```

Proof shown:

- source manifest
- redacted provenance
- source hash
- private storage default

Expected objection:

```text
Why not connect my CRM first?
```

Answer:

```text
Because Pavo has to know what the record is before deciding where it belongs.
```

## Demo Beat 3: Show Quality Without Audio-Lab Complexity

Screen:

```text
Transcript: Needs review
Speakers: 2 confirmed, 4 uncertain moments
Visibility: Private

Why this needs review
- 3 unclear words used in proposed actions
- 2 possible speaker changes
- 1 overlapping segment

[Fix important parts]
```

Narration:

```text
Pavo does not ask the user to read the whole transcript. It shows the parts
that could affect a route.
```

Proof shown:

- risky span count
- speaker uncertainty
- overlap count
- data card

## Demo Beat 4: Review One Risky Span

Screen:

```text
Speaker uncertain at 00:18:42

[Play clip]

"We can ship that by Friday"

Who said it?
[Daniel] [Customer] [Not sure]

Why this matters
Pavo may create a Linear task from this sentence.
```

Action:

Choose the correct speaker if the clip is clear. Choose `Not sure` if it is
not.

Narration:

```text
The review is narrow. Pavo asks about the one clip that matters because a route
might depend on it.
```

Proof shown:

- evidence span
- route consequence
- review decision
- updated speaker evidence state

## Demo Beat 5: Show Recommended And Blocked Routes Together

Screen:

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

Narration:

```text
This is the product difference. Pavo recommends useful work, but it also shows
what it refuses to do.
```

Proof shown:

- route packet
- evidence span per action
- blocked route reason
- destination preview

## Demo Beat 6: Approve Only Selected Actions

Action:

Approve Drive archive and Linear draft. Reject or leave blocked the Slack route.

Narration:

```text
Approval is per action. Approving the archive does not approve a Slack post.
```

Proof shown:

- approval decision list
- rejected or blocked route list
- no outbound message sent

## Demo Beat 7: Land And Show Proof

Screen:

```text
Done

Landed
- Drive archive created
- Linear draft created

Blocked
- Slack update blocked: consent unknown

[See proof]
```

Narration:

```text
Pavo ends with proof, not a success toast. The user can see what landed, what
did not land, and why.
```

Proof shown:

- landing manifest
- destination refs
- blocked-route proof
- dependency hashes or redacted proof summary

## Advanced Demo Branch: Stale Packet Refusal

Use only if the audience is technical or skeptical.

Setup:

- generate a route packet
- change transcript version, context terms, or policy version
- attempt to Land the old packet

Expected behavior:

```text
Landing stopped because approval no longer matched the current evidence.
```

Narration:

```text
Pavo does not let old approvals write from changed evidence.
```

Proof shown:

- stale dependency report
- refused landing manifest
- refreshed approval requirement

## Buyer Questions And Answers

Question:

```text
Is this just Otter or Fireflies with tasks?
```

Answer:

```text
No. Meeting bots produce notes. Pavo controls whether a spoken record is safe
to route, what destination it can reach, and what proof remains after approval.
```

Question:

```text
Why require approval?
```

Answer:

```text
Because transcripts and summaries can be wrong. Pavo routes evidence, not vibes.
Approval is the boundary between recommendation and real-world action.
```

Question:

```text
Will this create more work?
```

Answer:

```text
Pavo should reduce cleanup by showing only route-relevant risky spans. The
review burden should scale with consequence.
```

Question:

```text
Can it be fully automatic?
```

Answer:

```text
Only where policy and evidence make that safe. Pavo treats no-action and
blocked routes as valid outcomes.
```

## Demo Acceptance Criteria

The demo passes if:

- it starts from a real or fixture-backed recording
- the first screen is the queue
- source preservation happens before routing
- a risky span is reviewed before route approval
- recommended and blocked routes are visible together
- one action lands
- one action stays blocked
- proof manifest appears at the end
- no claim says Pavo is always more accurate than competitors
- the buyer can repeat the sentence: "Pavo catches recordings and asks before
  anything lands."

The demo fails if:

- it centers a generic chat assistant
- it skips source preservation
- it hides blocked routes
- it uses a fake transcript with no fixture
- it sends or writes externally without approval
- it claims perfect transcription
- it ends with a generic "success" message instead of proof
