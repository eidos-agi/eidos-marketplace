# Pavo Core Manuscript

This is the edited core manuscript for Pavo. The longer sourcebook remains in
`docs/pavo-product-book.md`; this document is the sharper reader-facing spine.
For the complaint-driven design against common meeting-bot failure modes, see
`docs/pavo-meeting-bot-complaint-response.md`.

Pavo turns spoken records into approved, source-backed work.

That sentence is the product. Recording is no longer hard. The hard part is
what happens after the recording exists. A call, memo, interview, meeting, or
field note may contain a task, a quote, a private detail, a product blocker, a
promise, a risk, or nothing that should move. Pavo exists because those records
need a controlled path into work.

Pavo is not a meeting-note product. Notes help people remember what happened.
Pavo helps decide what the record is allowed to become.

The product uses a Flight Path:

```text
Nest -> Tune -> Scout -> Land -> Home
```

- Nest preserves the source.
- Tune makes the record trustworthy enough to use.
- Scout recommends routes and non-routes.
- Land executes only approved actions.
- Home proposes scoped policy from reviewed decisions.

The rest of this manuscript explains why that path matters, what the first
product should do, what it must refuse to do, and how to build it without
turning a useful idea into blind automation.

## 1. The Problem

Most organizations already have a recording problem, even if they describe it
as follow-up, note-taking, CRM hygiene, customer evidence, recruiting notes, or
personal administration.

The path usually looks like this:

```text
conversation -> recording -> transcript or notes -> human memory -> scattered work
```

The weak point is not always capture. Capture is increasingly easy. The weak
point is conversion. A spoken record enters the world, but someone still has to
decide:

- what is true enough to use
- who said it
- what is uncertain
- what should stay private
- what should become a task
- what should become evidence
- what should become a draft
- what should be blocked
- who should approve the action
- what proof should remain afterward

Current tools solve pieces of this.

Recording devices capture clean audio. Meeting bots produce notes. Transcription
APIs produce text. CRM call intelligence helps sales workflows. Automation
tools move data between apps. General AI assistants can reason over a call.

None of those layers owns the controlled path from spoken source to approved
downstream work.

That is Pavo's opening.

## 2. Why Notes Are Not Enough

A note asks:

```text
What happened?
```

Pavo asks:

```text
What is this record allowed to become?
```

That second question is harder and more valuable.

A customer call may contain a product blocker, a renewal risk, a sensitive
commercial statement, and a useful customer quote. A note can summarize all of
it. Pavo has to split it:

- archive the source and transcript
- draft a Linear issue for the blocker
- draft a CRM note with careful account language
- block a Slack post that overstates the renewal risk
- propose a future policy only after review

A product interview may contain a user pain point and an ambiguous feature
request. A note may call it a request. Pavo should keep it as evidence until a
human decides whether it is a roadmap item.

A personal administration call may contain a deadline and sensitive family or
health context. A note may preserve both. Pavo should create the reminder and
keep the sensitive content private.

The note is an artifact. The routing decision is the product.

## 3. The Flight Path

The Flight Path is not decoration. It is a completion model.

### Nest

Nest means Pavo has the source. A nested record has a durable local copy or
approved archive path, source metadata, hash, owner, timestamps, source system,
and storage mode.

Nest is useful even when nothing else happens. A record that is safely nested
will not disappear behind a temporary link or vendor summary.

Minimum Nest behavior:

- import Plaud or local recordings
- preserve original media
- compute hash and byte size
- record non-secret source metadata
- distinguish private, team, cloud, and governed storage modes
- avoid storing signed URLs as durable artifacts
- detect duplicate imports

Nest should be boring. If Nest is unreliable, every later stage is theater.

### Tune

Tune means the record is trustworthy enough to inspect and route. It does not
mean the transcript is perfect. It means uncertainty is visible.

Minimum Tune behavior:

- transcript with source timestamps
- transcript manifest
- engine, command, and context metadata
- speaker labels with confidence or review state
- uncertain spans
- human corrections
- review notes
- stale-processing detection

Tune should make weak evidence obvious. If a speaker label is uncertain, Pavo
should not route the phrase as that person's commitment. If the audio is noisy,
Pavo should not treat a low-confidence phrase as a safety fact. If a transcript
is reprocessed, old approvals may become stale but should not vanish.

Tune is where Pavo earns the right to recommend routes.

### Scout

Scout creates the routing packet. It recommends what the record can become and
what it should not become. Scout does not write to destination systems.

Minimum Scout behavior:

- every route cites evidence
- every blocked route explains why
- high-risk destinations require approval
- uncertain evidence changes approval requirements
- private records restrict team destinations by default
- no-action is a valid outcome
- return-to-Tune is a valid outcome

Initial route types:

- archive
- Linear draft issue
- CRM note draft
- email draft
- reminder or task
- private
- blocked route
- no action needed
- return to Tune

The routing packet is Pavo's central object. It should be structured enough for
tests and legible enough for a human.

### Land

Land executes approved routes and records proof. Land is where product risk
becomes real.

Minimum Land behavior:

- refuse unapproved routes
- validate packet version and approval id
- support dry-run previews
- use idempotency keys
- write destination manifests
- expose partial failure
- avoid duplicate retries
- redact secrets and temporary URLs

The first Land destinations should be narrow:

1. local archive
2. Drive archive
3. Linear draft or issue

CRM, email, and Slack should start as draft or blocked routes. Sending,
posting, and broad CRM writes should wait until preview, approval, idempotency,
and manifests are routine.

### Home

Home learns from reviewed routing decisions. It should begin as policy
candidates, not silent automation.

Minimum Home behavior:

- propose scoped policy from approvals and rejections
- show examples and counterexamples
- require explicit approval before activation
- preserve rejected examples
- support revocation
- keep personal and team policy separate
- explain why a later route used a policy

Home should move slowly. A one-off approval should not become broad behavior.
Repeated reviewed decisions can become useful policy, but only if the user can
see the scope and limits.

## 4. The Approval Boundary

Approval is not a lack of ambition. It is how Pavo makes AI recommendations
usable where mistakes matter.

The boundary is simple:

```text
Before approval: recommend, preview, cite, compare, block.
After approval: execute exactly what was approved and write proof.
```

The approval surface should not ask the user to "trust the AI." It should ask a
specific question:

```text
Is this action allowed to land in this destination in this form?
```

Approval actions:

- approve as-is
- edit then approve
- approve as draft-only
- reject
- block by policy
- mark private
- return to Tune
- request more evidence

Rejection is not failure. It is product data. A rejected route teaches Scout and
Home what not to do. A blocked route proves that Pavo can withhold action.

The approval queue should show:

- source
- evidence span
- uncertainty
- proposed destination
- exact destination preview
- sensitivity
- approval requirement
- expected manifest

If the user has to reread the entire transcript to approve a route, the packet
failed.

## 5. Source Is The Trust Anchor

Every route should be able to answer:

```text
Where did this claim come from?
```

The answer cannot be "the model said it." The source may be the audio, a
transcript span, a speaker-evidence record, a review correction, a redaction
decision, an approval, or a destination response.

The chain is:

```text
source -> evidence -> route -> approval -> manifest -> policy candidate
```

Break that chain and Pavo becomes another AI text generator. Preserve it and
Pavo becomes operational software.

This is why Pavo should keep manifests everywhere:

- source manifest
- transcript manifest
- review manifest
- routing packet
- approval decision
- redaction manifest
- destination manifest
- policy candidate

Manifests are not bureaucracy. They are how a user knows what happened.

## 6. First Product Requirements

The first real Pavo should prove one complete loop:

```text
one source
-> one durable record
-> one tuned evidence bundle
-> one routing packet
-> one approved destination
-> one manifest
```

The first user story:

```text
As a founder or operator with important recorded conversations, I want Pavo to
preserve the source, make the record trustworthy, recommend where follow-up
belongs, ask before writing, and prove what landed, so conversations become
controlled work instead of loose memory.
```

Required first sources:

- Plaud
- local files

Required first evidence:

- transcript
- speaker labels
- uncertainty markers
- review corrections
- source links
- manifests

Required first destinations:

- local archive
- Drive archive
- Linear draft or issue

Required first UI surfaces:

- record list
- record detail
- source and evidence viewer
- routing packet review
- approval queue
- destination manifest view
- Home candidate view

What not to build first:

- broad CRM writes
- automatic outbound email
- Slack posting
- compliance claims
- broad policy automation
- every capture source
- every integration
- enterprise admin before proof primitives

The first product should be narrower than the vision. Narrow is not a retreat.
It is how Pavo earns trust.

## 7. Core Scenarios

### Customer Blocker Call

A customer says the import workflow fails silently for certain account-name
files. They also say expansion is hard to justify if imports are not reliable.

Pavo should:

- archive the source and transcript
- correct the account and product names
- draft a Linear investigation issue
- draft a CRM note with careful wording
- block a Slack route that overstates expansion risk
- propose a scoped policy for future product blockers

Pavo should not:

- turn "hard to justify" into "expansion depends on this"
- create a roadmap commitment
- post commercial pressure to Slack
- detach the issue from evidence

This is the default demo because it shows routing, approval, blocking, and
proof in one record.

### Personal Administration Call

A user records a call with an insurer, school, doctor office, vendor, or bank.
The call includes a deadline, a name, a document request, and private context.

Pavo should:

- preserve the record in private mode
- mark sensitive fields
- correct uncertain names
- create a narrow reminder
- prepare an email draft if approved
- block team/shared destinations by default

Pavo should not:

- upload the full transcript into a team workspace
- train broad team policy from private behavior
- send messages automatically
- expose personal details in reminders

This scenario protects the personal/team boundary.

### Product Interview

A user says onboarding import is confusing, asks for a shortcut, then says they
do not want the system to make assumptions.

Pavo should:

- preserve research evidence
- mark ambiguity
- draft a discovery issue
- block a roadmap commitment
- keep uncertain competitor mentions unverified

Pavo should not:

- turn one interview into a feature promise
- flatten contradictory user language
- treat a request as a decision

This scenario proves that Pavo can preserve ambiguity.

### Recruiting Screen

A candidate shares availability, compensation expectations, logistics, and
sensitive evaluation context.

Pavo should:

- draft factual ATS notes
- keep evaluative notes restricted
- create a follow-up task
- block Slack routes containing compensation or sensitive assessment

Pavo should not:

- mix evaluation with candidate-provided facts
- expose compensation broadly
- route hiring notes without approval

This scenario tests audience and sensitivity boundaries.

### Support Escalation

A frustrated customer reports a workflow failure. Some statements are facts.
Some are emotional or broad.

Pavo should:

- route concrete reproduction details to engineering
- route account impact to customer success
- draft a leadership brief if approved
- block public or broad incident claims until confirmed

Pavo should not:

- treat anger as verified incident scope
- route unsupported claims as facts
- hide partial uncertainty

This scenario tests fact extraction under pressure.

### Legal-Adjacent Interview

A restricted interview includes allegations, uncertainty, and sensitive facts.

Pavo should:

- preserve restricted source evidence
- create an authorized review task
- block interpretive summaries
- block broad sharing

Pavo should not:

- convert allegations into findings
- produce casual summaries
- route to ordinary business systems

This scenario proves that archive-only can be the correct outcome.

## 8. Gotchas

Pavo should be built around gotchas, not only happy paths.

Key gotchas:

- transcript error becomes action
- speaker identity is overclaimed
- user pain becomes roadmap commitment
- correct action is no action
- redaction happens too late
- destination outage creates ambiguous state
- retry duplicates work
- wrong CRM account mapping
- consent state is missing
- personal content routes to business tools
- compliance-adjacent summary becomes finding
- notes become source of truth
- policy learns too broadly
- approval fatigue
- user reverses approval
- reprocessing changes key evidence
- destination API forces unsafe shape
- broad channel membership changes
- archive becomes dump
- metrics reward unsafe automation

Each gotcha should become a fixture. The first fixture suite should cover ten
records:

1. customer blocker call
2. personal administration call
3. ambiguous product interview
4. recruiting screen
5. support escalation
6. legal-adjacent interview
7. internal strategy jam
8. poor-audio field memo
9. destination outage
10. wrong account mapping

For each fixture, expected outputs should include:

- route candidates
- blocked routes
- approval requirements
- expected manifests
- Home candidate or no Home candidate
- gotchas covered

The goal is not to make Scout clever. The goal is to make it safe and testable.

## 9. Product Scorecard

Pavo should be scored by Flight Path stage. The overall score is limited by the
weakest stage required for a workflow.

Nest:

- 0: source not preserved
- 3: source, hash, metadata, owner, sensitivity, and storage mode exist
- 5: robust adapters, duplicate detection, archive proof, auditable lifecycle

Tune:

- 0: no evidence
- 3: transcript, uncertainty, speaker evidence, and review state exist
- 5: evidence versions and review corrections drive Scout behavior

Scout:

- 0: no routing packet
- 3: packet includes evidence, sensitivity, blocked routes, and approvals
- 5: fixtures prove routing behavior across gotchas

Land:

- 0: no destination writes
- 3: approved-only Land, dry-run, idempotency, and manifests exist
- 5: multiple adapters share one proof contract

Home:

- 0: no learning
- 3: policy candidates are generated from reviewed history
- 5: approved policies safely influence Scout and Land with audit

The first commercial Pavo should aim for:

- Nest: 3
- Tune: 3
- Scout: 3
- Land: 3 for one or two destinations
- Home: 2 or 3 as candidates

Anything broader should wait.

## 10. Implementation Map

Current repo strengths:

- `pavo/config.py`: local home and config
- `pavo/plaud.py`: Plaud CLI adapter
- `pavo/download.py`: audio download and hash path
- `pavo/transcribe.py`: transcription and decomposition orchestration
- `pavo/overlap.py`: mixed-speaker region analysis
- `pavo/review.py`: review sheets, review pages, corrections, gates
- `pavo/proof.py`: proof reports
- `pavo/worker.py`: private worker health/status/tick surface
- `pavo/cli.py`: operator control surface

Missing modules:

- `pavo/records.py`: normalized recording and evidence models
- `pavo/packets.py`: routing packet schema and validation
- `pavo/scout.py`: recommendation boundary
- `pavo/approval.py`: approval state machine
- `pavo/land.py`: approved execution layer
- `pavo/destinations/`: destination adapters
- `pavo/home.py`: policy candidate generation
- `pavo/fixtures.py`: scenario fixtures and expected outputs

Build order:

1. Finish local source ledger and Drive archive work.
2. Finish Tune repeatability and stale detection.
3. Define normalized records and routing packets.
4. Build fixture tests from scenarios.
5. Implement rules-first Scout.
6. Build approval queue.
7. Implement Drive Land.
8. Implement Linear Land.
9. Add Home candidates.
10. Add higher-risk destinations only after proof behavior is boring.

## 11. Go To Market

The category line:

```text
The safe path from recordings to work.
```

The product line:

```text
Pavo turns recorded conversations into approved, source-backed work.
```

The buyer is not buying transcription. The buyer is buying controlled
follow-through:

- fewer lost customer blockers
- cleaner account notes
- better product evidence
- less manual copy-paste
- private handling of sensitive records
- proof after approved actions
- AI recommendations without surrendering judgment

Best early buyers:

- founder-led B2B teams
- product teams doing customer discovery
- customer success teams with renewal and escalation pain
- professional services teams with client commitments
- personal administration users with privacy-sensitive follow-up

Weak early buyers:

- transcription-only buyers
- zero-review automation buyers
- teams with no destination systems
- buyers demanding compliance guarantees before proof primitives exist

The demo should start with one recording. It should show:

1. source preserved
2. transcript evidence with uncertainty
3. four route recommendations
4. one blocked route
5. approval edits
6. destination manifests
7. a Home policy candidate

The blocked route is the category lesson. Pavo is not a product that creates
more output. Pavo is a product that helps a record become the right outcome.

## 12. Operating Doctrine

Product review question:

```text
What spoken record are we helping the user complete?
```

Engineering rules:

- preserve source before inference
- preserve manifests before summaries
- treat transcript confidence as data
- treat speaker identity as evidence
- never let Scout write to a destination
- never let Land execute without approval or approved policy
- make blocked routes first-class objects
- make non-action inspectable
- make retries idempotent
- make Home explicit and revocable

Release gates:

- Nest release requires source proof and duplicate behavior.
- Tune release requires uncertainty, corrections, and stale detection.
- Scout release requires schema-validated packets and fixtures.
- Land release requires approval, dry-run, idempotency, and manifests.
- Home release requires scoped, reviewable, revocable policy candidates.

Support should diagnose by Flight Path stage:

- Nest failure: missing source, wrong account, duplicate, consent state
- Tune failure: transcript, speaker, term, overlap, stale evidence
- Scout failure: wrong route, missing evidence, sensitivity error
- Land failure: unapproved write, duplicate, outage, missing manifest
- Home failure: overbroad policy, silent behavior change, bad scope

Every support incident should become a gotcha, fixture, or release gate.

## 13. What Pavo Should Refuse

Pavo should refuse product pressure that breaks the trust chain.

Refuse:

- blind CRM writes
- automatic outbound email
- Slack posting without explicit approval
- compliance claims without controls
- source-less routing
- speaker claims without evidence
- policy learning from one approval
- personal records training team behavior by default
- destination adapters without idempotency and manifests
- metrics that reward more writes regardless of correctness

This refusal is not conservatism for its own sake. It is the product's edge.
Pavo becomes valuable because it says no at the right time.

## 14. Final Shape

Pavo should become a layered control plane:

```text
source capture
-> evidence processing
-> routing intelligence
-> approval
-> destination execution
-> policy memory
-> audit
```

The first product should be smaller:

```text
Plaud or local file
-> source hash
-> tuned transcript
-> routing packet
-> approval queue
-> Drive archive
-> Linear draft
-> manifests
```

That first loop is enough to prove the product.

The long-form canon in `pavo-product-book.md` contains the full scenario
library, schemas, marketing assets, implementation roadmap, fixture ledger,
and scorecards. This core manuscript is the version to hand to a reader who
needs to understand Pavo quickly without reading every appendix.

Pavo exists because people should not have to choose between forgetting
important conversations and letting AI write blindly into their work systems.

The right middle path is controlled:

```text
Nest -> Tune -> Scout -> Land -> Home
```

Capture the source. Improve the evidence. Recommend the route. Ask before
action. Prove what landed. Learn only with review.

That is Pavo.
