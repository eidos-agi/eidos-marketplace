# Pavo: The Product Book

Working subtitle: **From captured conversations to approved, source-backed
work.**

This book is the long-form product canon for Pavo. It is intended to become a
roughly 150-page working book about what Pavo is, why it should exist, how the
Flight Path works, who it serves, what can go wrong, how it should be marketed,
and how the product should be built without losing its trust model.

This is not a polished marketing brochure. It is a product operating document:
part strategy, part scenario library, part design spec, part warning label, and
part build map.

## How To Read This Book

Pavo should be understood through one sentence:

```text
Pavo turns spoken records into approved, source-backed work.
```

Everything else in this book expands that sentence.

The core product model is the **Pavo Flight Path**:

```text
Nest -> Tune -> Scout -> Land -> Home
```

- **Nest:** capture and preserve the source recording.
- **Tune:** make the record accurate and trustworthy.
- **Scout:** recommend routes and actions.
- **Land:** execute approved actions.
- **Home:** learn where future records belong.

The book uses that Flight Path as the organizing principle for product design,
user education, technical architecture, trust boundaries, and marketing.

## Target Size And Page Budget

The target manuscript size is roughly 150 pages. In Markdown, "page" is not a
stable physical measure, so this book uses an editorial page budget. A printed
page is assumed to hold roughly 450 to 550 words after headings, examples,
tables, and diagrams. The finished book should be approximately 70,000 to
80,000 words, plus artifacts such as example routing packets, scenario tables,
policy examples, launch copy, and checklists.

This first manuscript pass creates the full structure and writes substantial
initial chapters. Later passes should expand the scenario library, destination
adapters, gotchas, marketing comparisons, and implementation playbooks until
the book reaches the intended size.

## Table Of Contents And Page Budget

| Part | Title | Target Pages |
| --- | --- | ---: |
| 1 | Why Pavo Exists | 18 |
| 2 | The Flight Path | 28 |
| 3 | Users And Scenarios | 30 |
| 4 | Product Mechanics | 24 |
| 5 | Trust, Safety, And Gotchas | 18 |
| 6 | Marketing And Positioning | 16 |
| 7 | Build Roadmap And Operating Model | 16 |
| **Total** |  | **150** |

Detailed target:

1. **Why Pavo Exists** - 18 pages
   - The broken path from capture to action
   - Why meeting notes are not enough
   - Why approval is not a bolt-on
   - Why Pavo is not "just transcription"
   - The control-plane thesis
2. **The Flight Path** - 28 pages
   - Nest
   - Tune
   - Scout
   - Land
   - Home
   - Completion states
   - Cross-stage invariants
3. **Users And Scenarios** - 30 pages
   - Founder/operator
   - Sales
   - Customer success
   - Product manager
   - Recruiter
   - Field worker
   - Personal chief-of-staff
   - Family/health/finance-sensitive use
   - Consulting/professional services
   - Legal and compliance-adjacent teams
4. **Product Mechanics** - 24 pages
   - Recording ledger
   - Evidence records
   - Routing packets
   - Approval queue
   - Policy memory
   - Destination adapters
   - Audit manifests
   - Search and retrieval relationship
5. **Trust, Safety, And Gotchas** - 18 pages
   - Consent
   - Privacy
   - Speaker identity errors
   - Hallucinated tasks
   - Over-routing
   - Approval fatigue
   - Sensitive destinations
   - Enterprise readiness
6. **Marketing And Positioning** - 16 pages
   - Category narrative
   - Wedge
   - Messaging
   - Comparisons
   - Demo paths
   - Objections
   - Launch assets
7. **Build Roadmap And Operating Model** - 16 pages
   - Narrow first loop
   - Milestones
   - What not to build yet
   - Metrics
   - Internal docs
   - Product reviews

---

# Part 1: Why Pavo Exists

## Chapter 1: The Broken Path From Capture To Action

People are recording more of their working lives than ever. Meetings are
recorded. Sales calls are recorded. Customer support calls are recorded. Voice
notes are captured during walks. Founders leave field memos between meetings.
Recruiters record candidate screens. Product teams record user interviews.
Families capture health updates and school calls. Professionals record client
discussions. Modern life produces a growing layer of spoken records.

At first glance, the tooling seems solved. Plaud records. Zoom records. Google
Meet records. Otter records. Fireflies records. Granola makes notes. Slack has
huddles. Phones have voice memos. CRMs have call recorders. Every platform can
claim some version of capture and transcription.

The unsolved problem is what happens after capture.

A recording is not useful merely because it exists. A transcript is not useful
merely because it is readable. A summary is not safe merely because it sounds
reasonable. The gap between "something was said" and "the right thing happened"
is where operational value is won or lost.

Today, that gap is usually crossed by a person doing manual work:

- finding the recording
- trusting or correcting the transcript
- remembering who spoke
- deciding what mattered
- deciding where it belongs
- copying notes into a document
- creating follow-up tasks
- drafting an email
- updating a CRM
- tagging a project
- filing evidence for later
- deciding what should remain private

The AI layer can help, but the moment AI begins moving information into other
systems, the risk changes. It is one thing for an AI to summarize a call. It is
another thing for an AI to create a customer-facing follow-up, update a deal,
open a task for an engineer, post into Slack, or archive private family notes
into the wrong folder.

That is the opening for Pavo.

Pavo exists because capture tools and destination tools do not share a trusted
control layer. Capture tools know where the audio came from. Destination tools
know where work happens. The missing layer is an evidence-first approval queue
that can take a spoken record, preserve the source, improve the data, recommend
what should happen, and hold external action behind approval.

That is what Pavo should become.

## Chapter 2: Why Meeting Notes Are Not Enough

Most meeting AI products frame the job as note generation. They promise better
summaries, action items, follow-up emails, searchable transcripts, and maybe
some integrations. Those features are valuable. They are not enough.

There are four reasons.

### Notes Are Not Source Artifacts

A note is an interpretation. A transcript is also an interpretation, though a
more granular one. The source artifact is the recording itself: the original
audio or video, its metadata, its timestamp, its source system, and the proof
that it has not silently changed.

For casual meetings, a summary may be fine. For high-value or sensitive
conversations, the source matters:

- A customer says something specific about a blocker.
- A candidate says something that affects hiring evaluation.
- A doctor or school administrator gives instructions.
- A founder discusses investor commitments.
- A product user describes a bug in their own words.
- Two people talk over each other and the transcript assigns the phrase to the
  wrong speaker.

If the system cannot return to the source, it cannot correct itself. It can
only compound the initial interpretation.

Pavo's first principle is therefore simple:

```text
Source media is the record. A summary is never the source of truth.
```

### Notes Do Not Preserve Enough Uncertainty

Meeting summaries tend to smooth uncertainty into readable prose. They collapse
pauses, interruptions, false starts, overlaps, laughter, side comments, and
ambiguous references into clean bullets. That is useful for skim reading, but
it hides the places where a downstream action should be cautious.

Pavo should treat uncertainty as product data. A tuned record should know when
speaker identity is weak, when a term was guessed, when a transcript span came
from a low-confidence engine, when a source-separation stem is diagnostic
rather than accepted, and when a human review is required.

The goal is not to make every record perfect. The goal is to know what level of
trust each record has reached.

### Notes Do Not Decide Where Information Belongs

Most spoken information has more than one possible destination:

- A customer commitment belongs in CRM and maybe in a project tracker.
- A product bug belongs in Linear and perhaps a research archive.
- A board update belongs in Drive and maybe a finance follow-up queue.
- A recruiting note belongs in an applicant tracking system, not Slack.
- A family health note may belong in a private folder and nowhere else.

The destination decision is contextual. It depends on people, projects,
sensitivity, organizational policy, confidence, and user preference. A generic
meeting summary cannot know enough without a routing layer.

### Notes Do Not Create Safe Action

The hardest step is not summarizing. It is acting safely.

Pavo should not default to "AI writes everywhere." It should default to "AI
prepared a decision." The user or policy can then approve specific outcomes:

- archive this record
- create these two tasks
- draft but do not send this email
- update this CRM note
- mark this private
- redact and route this excerpt
- reject all proposed actions

That approval step is not friction added after the fact. It is the product.

## Chapter 3: The Control-Plane Thesis

Pavo should be built as a control plane for spoken records.

A control plane does not replace every worker. It coordinates them. Pavo should
not become the transcription model, the meeting recorder, the CRM, the project
tracker, the file archive, the email client, and the search engine. It should
coordinate the path among them.

That has several implications.

### Pavo Owns Recording Lifecycle State

Pavo should know that a recording exists, where it came from, whether the
source media is preserved, what hash identifies it, what processing happened,
what evidence exists, what review state exists, what routing packet was
generated, what approvals were granted, and what external writes happened.

This lifecycle state is more important than any single transcript. It is what
lets a spoken record move through the Flight Path without losing provenance.

### Pavo Delegates Audio Intelligence

The current boundary with `eidos-transcribe` is correct. Pavo should call an
audio intelligence package rather than embedding every transcription,
diarization, fingerprinting, overlap, and source-separation algorithm. This
keeps Pavo focused on the product lifecycle while allowing the audio layer to
improve independently.

### Pavo Should Produce Packets Before It Produces Writes

The routing packet is the key product object. It is the bridge between
understanding and action. Before Pavo writes to Linear, Drive, CRM, Slack,
email, or any other system, it should be able to produce a packet that says:

- what was captured
- what was understood
- what evidence supports it
- where it might belong
- what actions are proposed
- what risks or sensitivities exist
- what approval is required

Destination adapters should consume approved packets. That architecture keeps
integrations from becoming the product too early.

### Pavo Learns Policy From Review

Every approval and rejection is a signal. Pavo should learn, but not by hiding
automation behind vague personalization. It should learn explicit policy:

- Records from this source are private by default.
- These customers require CRM notes.
- These projects create Linear tasks only after review.
- These meetings should archive to Drive automatically.
- These topics require redaction before routing.
- These people should never be mentioned in broad Slack summaries.

The learning should be inspectable. Home is policy memory, not magic.

---

# Part 2: The Flight Path

## Chapter 4: Overview

The Flight Path gives Pavo a product language and a state machine. The names
are memorable, but they are not decorative. Each one represents a level of
completion.

```text
Nest -> Tune -> Scout -> Land -> Home
```

The point of the model is not to force every recording through every stage.
Many records should stop early. Some should be archived and never routed. Some
should be tuned and marked private. Some should be scouted and rejected. Some
should land into several destination systems. Some should become policy
examples for future records.

The model is useful because it gives every record a truthful status. Pavo can
say "this is nested but not tuned," "this is tuned but not scouted," "this is
scouted but approval is pending," or "this landed with proof." That is much
better than a vague state like "processed."

## Chapter 5: Nest

Nest is the preservation stage.

The user's first job is not to get a beautiful summary. The first job is to
make sure the record is safe. If the original audio is lost, every later layer
is weaker. If the source account is unknown, the operator may not know whether
the right recording was captured. If the recording is only represented by a
temporary link, the system has not really preserved anything.

Nest should answer:

- What is the source system?
- Who owns the source account?
- What is the recording id?
- Where is the original media stored locally?
- What hash identifies the file?
- When was the recording created?
- What metadata came from the source?
- What credentials or native stores are needed to reacquire it?
- What should not be persisted because it is secret or temporary?

For Plaud, Nest means the recording can be discovered through Plaud, the real
audio can be downloaded, the file can be hashed, the authenticated account can
be shown, and non-secret metadata can be recorded in a manifest.

For imported meetings, Nest means a local media file or export is copied into a
controlled Pavo location, hashed, and associated with source metadata. The
import may be manual at first. That is fine. The invariant is preservation.

Nest should not require transcription. A record can be nested and still have no
transcript. That is acceptable and often useful. Pavo should make this visible:
the record is safe, but not yet understood.

### Nest Completion Checklist

A record is nested when:

- original media or durable local media copy exists
- content hash is recorded
- source system is recorded
- source id or import id is recorded
- source timestamp is recorded when available
- non-secret account identity is recorded when available
- local path is recorded
- temporary URLs are not treated as durable records
- original acquisition command or method is recorded

### Nest Failure Modes

Nest can fail quietly if the product is not disciplined. Common failures:

- The product stores only a transcript and loses the audio.
- The product stores a signed URL that expires.
- The product downloads from the wrong account.
- The product silently overwrites an older file.
- The product stores secrets in a manifest.
- The product treats a cloud note as equivalent to media.
- The product cannot prove whether two files are the same recording.

Pavo should be strict here. A weak Nest creates weak everything.

## Chapter 6: Tune

Tune is the trust stage.

The name matters. Pavo is about spoken records, so the product should feel
connected to audio without becoming cute or obscure. Tune means making the
record accurate and trustworthy. It covers transcript quality, speaker
identity, vocabulary, overlap, human review, and uncertainty.

Tune should answer:

- What was said?
- Who likely said it?
- Which terms may have been misheard?
- Which transcript spans are low confidence?
- Which speakers are named, inferred, or unknown?
- Which overlapping regions need special handling?
- What human corrections exist?
- What evidence supports the tuned record?

The key product move is to avoid false certainty. If Pavo does not know who
spoke, it should say so. If two people overlap, it should mark the region. If a
speaker label is only a diarization guess, it should not pretend to be a named
person. If a source-separated stem is useful for diagnosis but not accepted, it
should be labeled as such.

Tune is where Pavo's relationship with `eidos-transcribe` matters most.
`eidos-transcribe` can run engines, compare outputs, detect speaker changes,
build speaker fingerprints, flag overlaps, and produce manifests. Pavo should
attach that evidence to the record and expose it in reviewable form.

### Tune Completion Checklist

A record is tuned when:

- transcript evidence exists
- transcript provenance is recorded
- engine and context terms are recorded
- speaker labels are preserved
- named speaker claims are evidence-backed
- uncertain spans are marked
- overlap or mixed-speaker regions are marked when detected
- human review state is available when needed
- corrections are recorded without destroying original evidence

### Tune Failure Modes

Tune is where many products overclaim. Common failures:

- "Speaker 1" is treated as a known person.
- A summary hides transcript uncertainty.
- A user correction overwrites raw evidence.
- A known term is misheard repeatedly because no dictionary exists.
- Overlap is forced into one speaker.
- A low-confidence transcript produces high-confidence tasks.
- Human review artifacts exist but are not connected to the record.

Pavo should treat corrections as additive. Raw outputs, tuned outputs, and
human corrections are separate layers. That separation makes the record more
auditable over time.

## Chapter 7: Scout

Scout is the recommendation stage.

This is where Pavo stops being only a recording/transcription system and
becomes a routing product. Scout looks at the tuned record and proposes what
should happen next. It does not write externally. It prepares a decision.

Scout should answer:

- What kind of record is this?
- Which people, projects, customers, or entities are involved?
- What destinations might be appropriate?
- What actions are suggested?
- What evidence supports each suggestion?
- What sensitivity or privacy issues exist?
- What approval is required?
- What should be ignored?

The output of Scout is a routing packet.

### Routing Packet As Product Object

The routing packet is the central object of Pavo's product future. It should be
viewable by humans, machine-readable by adapters, and durable enough to audit.

Minimum packet fields:

- recording id
- current Flight Path stage
- short summary
- evidence references
- detected entities
- detected projects or workstreams
- sensitivity flags
- suggested destinations
- proposed actions
- confidence and uncertainty
- approval requirements
- rejection/private/archive options

The routing packet should not be a wall of prose. It should be a structured
decision document. A user should be able to approve, reject, redact, split, or
defer parts of it.

### Scout Completion Checklist

A record is scouted when:

- routing packet exists
- suggested destinations are explicit
- proposed actions are explicit
- each recommendation has a reason
- each recommendation points back to evidence
- sensitivity flags are present
- approval requirements are present
- the packet can be reviewed without replaying the whole recording

### Scout Failure Modes

Scout can fail by doing too much or too little.

Doing too much:

- creates tasks before approval
- posts broad summaries to Slack
- updates CRM from weak evidence
- sends emails instead of drafting
- assumes every record needs action

Doing too little:

- produces generic summaries with no destination
- fails to distinguish archive from task
- ignores sensitivity
- does not cite evidence
- cannot explain why a route was recommended

Pavo's Scout should be conservative. A good route recommendation is useful even
if the user rejects it, because the rejection teaches Home.

## Chapter 8: Land

Land is the approved action stage.

Landing is not "the AI did something." Landing is "an approved route was
executed, and Pavo can prove what changed." That distinction is essential. The
product should make every external write feel deliberate, inspectable, and
recoverable.

Land should answer:

- Who or what approved the action?
- What destination was written?
- What exact content was sent or created?
- What source evidence supported it?
- What destination id was returned?
- What redactions were applied?
- When did the write happen?
- Did the write succeed, fail, or partially succeed?
- How can the user trace or undo it?

Destination adapters should be narrow. A Linear adapter should create or update
Linear artifacts from approved packets. A Drive adapter should archive media
and manifests from approved packets. A CRM adapter should create notes or tasks
from approved packets. The adapters should not invent new product policy.

### Land Completion Checklist

A record has landed when:

- approval is recorded
- destination adapter executes the approved action
- destination id or proof is recorded
- write manifest is recorded
- source packet remains linked
- redactions are recorded
- failures are visible
- retries do not duplicate writes

### Land Failure Modes

Land is where mistakes become real. Common failures:

- Duplicate task creation after retry.
- Posting private content into a public channel.
- Creating a CRM note under the wrong account.
- Sending an email instead of saving a draft.
- Losing the connection between action and source evidence.
- Treating partial write success as full completion.
- Failing to record who approved the write.

Landing should be boring. The intelligence should happen before approval; the
write should be deterministic and fully logged.

## Chapter 9: Home

Home is the learning stage.

Pavo should learn where records belong. But Home must not be a vague promise
that the AI gets smarter. It should mean explicit, inspectable policy memory.

Home should answer:

- What did the user approve?
- What did the user reject?
- What did the user redact?
- Which destinations are normal for this source?
- Which topics require approval?
- Which people or projects imply a destination?
- Which categories should stay private?
- Which actions can be auto-archived?
- Which actions always require review?

Home is where Pavo becomes personal or organizational without becoming unsafe.
It remembers policy, not secrets. It remembers preferences, not raw sensitive
content unless explicitly configured. It turns review work into future routing
quality.

### Home Completion Checklist

Home is working when:

- approvals and rejections update policy candidates
- policy candidates can be reviewed
- stable policies can be promoted
- policies are source-aware and destination-aware
- policies include approval thresholds
- policies include privacy exceptions
- policies can be exported or audited

### Home Failure Modes

Home can become dangerous if it hides automation:

- The system silently broadens a rule.
- A private exception becomes a general policy.
- A one-time approval becomes permanent auto-routing.
- The user cannot inspect why a recommendation happened.
- The policy engine stores sensitive text unnecessarily.

Home should make policies readable:

```text
For Plaud recordings tagged "customer call":
  recommend CRM note and Drive archive.
  require approval before CRM write.
  never post full summary to Slack.
```

That kind of rule is boring in the best way. It is clear enough to trust.

---

# Part 3: Users And Scenarios

## Chapter 10: Founder And Operator Scenario

A founder records constantly. Investor calls, candidate screens, product
reviews, customer escalations, advisor conversations, family logistics, and
private voice notes all mix together. The pain is not lack of notes. The pain
is that every conversation creates residue.

The founder wants a catch fence:

- Do not lose the recording.
- Do not force me to decide immediately.
- Tell me what probably matters.
- Tell me where it probably belongs.
- Ask before you write into systems that other people see.
- Learn my preferences so the review queue gets lighter.

### Example Flow

The founder finishes a customer call captured on Plaud.

Nest:

- Pavo downloads the audio.
- Pavo records the Plaud account and recording id.
- Pavo hashes the MP3.
- Pavo stores a source manifest.

Tune:

- Pavo transcribes the recording.
- Pavo applies customer and product vocabulary.
- Pavo marks uncertain speaker spans.
- Pavo notes one overlap near a key blocker.

Scout:

- Pavo generates a routing packet.
- It recommends a Drive archive.
- It recommends a Linear issue for a product bug.
- It recommends a CRM note.
- It marks the CRM note as approval required.
- It cites the transcript span where the customer described the bug.

Land:

- The founder approves Drive archive and Linear issue.
- The founder edits the CRM note and approves it.
- Pavo writes destination manifests with ids.

Home:

- Pavo learns that this customer account usually routes to CRM and product
  follow-up, but CRM writes require approval.

### What Success Feels Like

The founder does not feel like they are using a transcription tool. They feel
like conversations are no longer leaking out of the operating system of the
company. Pavo catches them, cleans them, proposes where they belong, and waits
for approval.

## Chapter 11: Sales Scenario

Sales teams already record calls. The common problem is not that there is no
call recording. The problem is that the recording does not reliably become
clean CRM state and follow-up work.

A sales user needs:

- account and contact recognition
- action item extraction
- objection tracking
- competitor mentions
- deal risk detection
- follow-up draft creation
- CRM update suggestions
- manager visibility without overexposing sensitive details

Pavo's value is not to replace the CRM call recorder. Its value is to preserve
evidence and gate the path from call intelligence to CRM mutation.

### Sales Routing Packet

Suggested destinations:

- CRM note
- deal risk field
- follow-up email draft
- internal product feedback issue
- Drive archive for full source

Approval rules:

- CRM note requires approval unless low-risk and from a known call type.
- Follow-up emails are drafts by default.
- Product feedback can create an internal issue but should cite source spans.
- Sensitive pricing comments should not route to broad Slack channels.

### Sales Gotchas

Sales calls contain tactical nuance. A bad summary can damage a deal. A wrong
speaker can attribute a commitment to the wrong person. An overconfident CRM
update can pollute pipeline data. Pavo should therefore make evidence and
approval central, especially when modifying customer-facing systems.

## Chapter 12: Customer Success Scenario

Customer success conversations often contain a mix of support, product
feedback, renewal risk, relationship context, and promises made by either side.
The customer success user needs the conversation to become durable account
memory without turning every call into noisy tasks.

Pavo should help distinguish:

- a support issue
- a product request
- a renewal risk
- a relationship note
- an implementation blocker
- a commitment
- a private aside

The Scout stage is especially important. Many customer calls should produce
more than one recommendation, but not every recommendation should land.

### Example

The customer says:

"We can live with the current dashboard for now, but if SSO is not working by
the end of the quarter, procurement will probably block expansion."

A generic summary might write: "Customer discussed dashboard and SSO."

Pavo should propose:

- CRM risk note: expansion risk tied to SSO by quarter end
- Linear issue or link: SSO blocker
- Customer success task: follow up before procurement review
- Sensitivity flag: commercial risk
- Evidence span: exact quote and timestamp

The user can approve the CRM risk note, reject the Linear issue if one already
exists, and create a follow-up task.

## Chapter 13: Product And Research Scenario

Product teams collect user interviews, discovery calls, bug reports, and
feedback snippets. The capture problem is often solved by research tools, but
the routing problem remains.

User research needs to become:

- evidence in a research repository
- product insights
- bugs
- roadmap candidates
- quotes
- persona updates
- support escalations

Pavo should not pretend every user quote is a roadmap item. It should preserve
the source and recommend routes with confidence.

### Product Routing Principles

- Bugs need reproduction details and evidence spans.
- Feature requests need user context and frequency.
- Quotes need consent and source attribution.
- Roadmap suggestions should not land directly without product review.
- Sensitive customer context should be redacted before broad sharing.

Pavo's Tune stage matters because product decisions are only as good as the
record. If the transcript mishears a product name, the route may be wrong. If
the speaker identity is wrong, the team may misattribute the feedback to the
wrong customer segment.

## Chapter 14: Personal Chief-Of-Staff Scenario

Pavo is not only a business product. A user may want to capture personal voice
notes, school calls, health conversations, finance calls, contractor calls, or
family logistics. These records are often more sensitive than business calls.

The product posture must change:

- private by default
- no broad sharing
- careful destination rules
- strong approval gates
- local-first storage options
- clear deletion and retention controls

Example destinations:

- private Drive folder
- personal task system
- health admin folder
- finance evidence folder
- relationship memory
- no destination beyond archive

The Home stage should learn that personal categories require stronger review.
It should not treat personal notes like sales calls.

## Chapter 15: Field Work Scenario

Field workers, inspectors, event operators, construction managers, and service
professionals often capture voice notes because typing is impractical. The
value of Pavo here is turning rough field audio into structured follow-up.

Examples:

- inspection notes become a report draft
- site issues become tasks
- customer requests become CRM notes
- safety concerns become escalations
- photos and audio become a field packet

Pavo should handle noisy audio, incomplete phrases, and location/time metadata.
The Tune stage may be weaker, but Nest and Scout can still be useful.

---

# Part 4: Product Mechanics

## Chapter 16: The Recording Ledger

The recording ledger is Pavo's durable state for captured records. It should be
small, inspectable, and boring.

Minimum ledger fields:

- `recording_id`
- `source_system`
- `source_account_ref`
- `source_recording_id`
- `title`
- `created_at`
- `captured_at`
- `media_path`
- `media_sha256`
- `duration_seconds`
- `flight_stage`
- `transcript_status`
- `routing_status`
- `approval_status`
- `archive_status`
- `sensitivity_class`

The ledger should not store secrets. It should store references to native
credential stores or non-secret account identifiers.

## Chapter 17: Evidence Records

Evidence records are the outputs of Tune. They should attach to a recording
without replacing the source.

Evidence types:

- transcript bundle
- raw engine output
- speaker diarization
- speaker signature
- overlap report
- source-separation report
- human review note
- correction
- vocabulary context
- confidence summary

Every evidence record should have provenance:

- command or process that created it
- input file hash
- output path
- model or engine
- timestamp
- confidence or status
- review state

## Chapter 18: Approval Queue

The approval queue is where Pavo becomes a product rather than a pipeline. A
user should see pending decisions, not raw processing artifacts.

An approval item should show:

- source record
- recommended action
- destination
- reason
- evidence
- sensitivity
- preview of external write
- approve/reject/edit/redact options
- policy suggestion when appropriate

Approval should be granular. The user may approve archive but reject CRM. They
may approve a Linear issue after editing the title. They may mark a record
private and reject all other routes.

## Chapter 19: Destination Adapters

Destination adapters should be late-bound and narrow.

Good adapter contract:

```text
approved routing packet -> destination write -> destination proof manifest
```

Bad adapter contract:

```text
raw transcript -> adapter invents task and writes it
```

Adapters should not own product policy. They should enforce destination
constraints and return proof.

Potential adapters:

- Google Drive
- Linear
- Slack
- Gmail or email drafts
- HubSpot or CRM
- Notion or docs
- personal task systems
- local archive folders

The first adapters should be chosen for proof, not breadth. Drive archive plus
one task system is enough to prove Land.

---

# Part 5: Trust, Safety, And Gotchas

## Chapter 20: Consent

Pavo deals with recordings. Consent is not a footnote.

The product should help users record consent posture:

- source system consent handled
- explicit consent captured
- consent unknown
- internal-only
- external sharing prohibited
- retention restricted

Pavo should not claim to solve every legal consent issue. It should make
consent state visible and prevent downstream routing from pretending consent is
irrelevant.

## Chapter 21: Privacy And Sensitive Content

Pavo may handle customer data, personal data, health-related content,
financial information, employment discussions, family details, and confidential
company strategy. The product should assume sensitive content appears often.

Safety rules:

- private categories default to no external routing
- broad Slack summaries require explicit approval
- email sends are drafts by default
- customer-facing writes require review
- redaction should happen before routing, not after
- audit manifests should avoid storing secrets

## Chapter 22: Speaker Identity Errors

Speaker identity is one of the most dangerous error classes. A task attributed
to the wrong person can create confusion. A quote attributed to the wrong
customer can damage trust. A commitment attributed to the wrong executive can
affect real decisions.

Pavo should distinguish:

- diarization label
- inferred speaker
- reviewed speaker
- known speaker
- uncertain speaker

Named speaker claims should be evidence-backed and reviewable. Unknown should
be acceptable.

## Chapter 23: Hallucinated Tasks

AI will sometimes infer tasks that were not actually agreed. A statement like
"we should think about SSO later" can become "Implement SSO." That is not a
small error if it lands in a work tracker.

Pavo should classify proposed actions:

- explicit commitment
- suggested follow-up
- inferred task
- question
- risk
- note only

Only explicit commitments should be candidates for high-confidence task
creation. Inferred tasks should require review.

## Chapter 24: Approval Fatigue

If Pavo asks the user to approve everything, it will fail. If it approves too
much automatically, it will also fail. The product must manage the middle.

Strategies:

- batch approvals by record
- auto-archive low-risk records
- learn source-specific policies
- separate "review required" from "FYI"
- make rejection fast
- support "archive only"
- show confidence and evidence compactly
- avoid overproducing actions

Approval fatigue is a product design problem, not only a model-quality problem.

---

# Part 6: Marketing And Positioning

## Chapter 25: Category

Pavo should not launch as "another AI meeting notes tool." That category is
crowded and undersells the product.

Better category language:

```text
Approval-gated routing for spoken records.
```

or:

```text
The control layer between captured conversations and systems of work.
```

or:

```text
From recordings to approved, source-backed work.
```

The category needs to signal three differences:

1. Pavo starts from the source recording.
2. Pavo routes information, not just notes.
3. Pavo requires approval before external action.

## Chapter 26: Wedge

The wedge should be narrow:

```text
Capture Plaud or local recordings, preserve the source, generate a routing
packet, and approve one destination action.
```

That wedge is strong because it proves the full product loop without requiring
every source and destination.

Avoid broad launch promises:

- "Connect every meeting tool."
- "Automatically update all your systems."
- "Never take notes again."
- "AI runs your follow-up."

Better promises:

- "Never lose the source recording."
- "Know what level of trust the record has reached."
- "Review AI routing before anything writes externally."
- "Turn approved conversation evidence into work."

## Chapter 27: Comparison Language

Pavo should respect existing tools. The comparison is not "they are bad." The
comparison is "they stop at notes or at narrow integrations."

Example:

```text
Meeting AI gives you notes. Pavo gives you an approval queue for turning
captured conversations into durable records, tasks, and follow-up.
```

Plaud comparison:

```text
Plaud is excellent capture hardware and software. Pavo is the control layer
that preserves Plaud recordings, tunes the record, and routes approved outcomes
into the rest of your operating system.
```

Otter/Fireflies comparison:

```text
Transcript tools make conversations searchable. Pavo makes them governable:
source-backed, routed, approved, and auditable.
```

Granola comparison:

```text
Beautiful notes are useful. Pavo starts where notes end: deciding what should
happen next, with approval and proof.
```

---

# Part 7: Build Roadmap And Operating Model

## Chapter 28: The First Complete Loop

The first complete product loop should be small and real:

```text
Plaud or local audio
-> Nest source media and manifest
-> Tune transcript and speaker evidence
-> Scout one routing packet
-> approve one action
-> Land into one destination with proof
-> Home one policy suggestion
```

This loop proves the product. More sources and destinations can wait.

## Chapter 29: What Not To Build Yet

Pavo should avoid:

- every meeting platform at once
- too many destination adapters
- automatic sending
- opaque policy learning
- heavy UI before packet model is stable
- broad enterprise admin before single-user trust works
- replacing `eidos-transcribe`
- becoming a generic personal knowledge base

The dangerous temptation is breadth. The product needs depth in the control
loop first.

## Chapter 30: Milestones

Milestone 1: Nest is reliable.

- Plaud/local imports
- hashes
- source manifests
- ledger
- no secret leakage

Milestone 2: Tune is reviewable.

- transcripts
- speaker evidence
- uncertainty
- review bundles
- corrections

Milestone 3: Scout exists.

- routing packet schema
- destination recommendations
- evidence references
- sensitivity flags
- approval requirements

Milestone 4: Land is safe.

- one destination adapter
- approval queue
- write manifest
- retry safety
- destination proof

Milestone 5: Home is inspectable.

- policy candidates
- promoted policies
- source-aware rules
- approval thresholds
- privacy exceptions

## Chapter 31: Metrics

Useful product metrics:

- recordings nested
- records tuned
- records requiring review
- routing packets generated
- recommendations accepted
- recommendations rejected
- external actions landed
- duplicate writes avoided
- approval time
- auto-archive rate
- correction rate by source
- speaker uncertainty rate
- policy suggestions promoted

Bad metrics:

- number of integrations
- number of generated tasks without acceptance
- summary length
- automatic write count without user satisfaction
- "AI confidence" without evidence quality

## Chapter 32: The Product Standard

Pavo should be judged by whether it makes the requested final state more true:

```text
Captured conversations become trusted records and approved actions.
```

Every feature should map to the Flight Path:

- Does it help Nest?
- Does it help Tune?
- Does it help Scout?
- Does it help Land?
- Does it help Home?

If a feature does not improve one of those levels, it is probably noise.

---

# Appendix A: Worked Routing Scenarios

This appendix turns the product model into concrete product behavior. Each
scenario is intentionally specific: the source, Flight Path progression,
routing packet, approval options, gotchas, and product lesson are all visible.

The purpose is to make Pavo buildable. A product team should be able to read
these scenarios and know what screens, schemas, policies, and adapters the
system needs.

## Scenario A1: Customer Call With Product Blocker

### Situation

A founder records a Plaud call with a customer. The customer is trying to
expand usage but is blocked by an import failure. During the call, the customer
also mentions a renewal timeline and says the failure is affecting a pilot
team.

The raw capture looks like a normal customer call. The downstream reality is
more complex: part of the call belongs in CRM, part belongs in Linear, part
belongs in Drive, and part should not be shared widely because it contains
commercial risk.

### Nest

Pavo downloads the Plaud audio, records the source id, account reference,
duration, local path, and SHA-256 hash.

Nested record:

```json
{
  "recording_id": "plaud_customer_import_blocker_001",
  "source_system": "plaud",
  "source_recording_id": "c37...",
  "media_path": "~/Eidos/Pavo/cache/plaud/c37/audio.mp3",
  "media_sha256": "sha256:...",
  "flight_stage": "nested"
}
```

### Tune

Pavo transcribes the audio with customer and product vocabulary:

- customer name
- product module names
- "CSV import"
- "pilot team"
- "renewal"
- known participant names

Pavo identifies that the most important span is clear enough for routing, but
one speaker handoff is uncertain. It marks the uncertain span and keeps the raw
engine output.

Tuned evidence:

```json
{
  "transcript_status": "tuned",
  "speaker_status": "partially_reviewed",
  "uncertain_spans": [
    {
      "start": 812.4,
      "end": 820.9,
      "reason": "speaker handoff unclear"
    }
  ],
  "domain_terms": ["CSV import", "pilot team", "renewal"]
}
```

### Scout

Pavo produces a routing packet.

```json
{
  "recording_id": "plaud_customer_import_blocker_001",
  "flight_stage": "scouted",
  "summary": "Customer expansion is blocked by CSV import failures affecting the pilot team before renewal review.",
  "suggested_destinations": [
    {
      "destination": "drive",
      "action": "archive_source_record",
      "reason": "Preserve full customer source record.",
      "requires_approval": false
    },
    {
      "destination": "linear",
      "action": "create_issue",
      "reason": "Customer described a concrete import failure with expansion impact.",
      "requires_approval": true
    },
    {
      "destination": "crm",
      "action": "create_account_note",
      "reason": "Commercial renewal risk and expansion blocker should be visible on account.",
      "requires_approval": true
    }
  ],
  "proposed_actions": [
    {
      "kind": "create_issue",
      "title": "Investigate CSV import failure blocking customer pilot",
      "evidence_refs": [
        {
          "type": "transcript_span",
          "start": 733.2,
          "end": 781.8
        }
      ],
      "confidence": 0.87
    },
    {
      "kind": "crm_note",
      "title": "Expansion risk tied to import reliability",
      "evidence_refs": [
        {
          "type": "transcript_span",
          "start": 790.0,
          "end": 836.5
        }
      ],
      "confidence": 0.8
    }
  ],
  "sensitivity": {
    "contains_customer_data": true,
    "contains_commercial_risk": true,
    "broad_slack_summary_allowed": false
  }
}
```

### Approval

The user sees three decisions:

1. Archive the record to Drive.
2. Create a Linear issue.
3. Create a CRM account note.

The user approves Drive archive, edits the Linear issue title, and approves the
CRM note only after redacting one pricing sentence.

### Land

Pavo writes:

- Drive archive manifest
- Linear issue id
- CRM note id
- redaction manifest
- approval manifest

Landing proof:

```json
{
  "recording_id": "plaud_customer_import_blocker_001",
  "landed_actions": [
    {
      "destination": "drive",
      "destination_id": "drive:file:...",
      "status": "succeeded"
    },
    {
      "destination": "linear",
      "destination_id": "LIN-124",
      "status": "succeeded"
    },
    {
      "destination": "crm",
      "destination_id": "crm-note-889",
      "status": "succeeded",
      "redactions": 1
    }
  ]
}
```

### Home

Pavo proposes a policy:

```text
For customer calls with expansion risk:
  recommend CRM note and Drive archive.
  require approval before CRM write.
  recommend Linear issue only when a concrete product blocker is present.
  do not recommend broad Slack summary when commercial risk is detected.
```

### Gotchas

- If Pavo created the Linear issue automatically, it might create noisy work.
- If Pavo skipped CRM, account context would be lost.
- If Pavo posted a broad Slack summary, it might expose commercial risk.
- If Pavo failed to cite evidence, the product team would not trust the issue.

### Product Lesson

This scenario proves why Pavo is not a notes tool. The value is the controlled
split: one source conversation becomes several possible outcomes, each with
evidence and approval.

## Scenario A2: Personal Health Administration Call

### Situation

A user records a phone call with a health insurance administrator. The call
contains plan details, a claim reference, a name, a callback number, and a
deadline. The user needs the facts preserved and follow-up created, but the
record should remain private.

### Nest

Pavo imports a local audio file from the phone recording export. It records the
source as `local_import`, hashes the file, and marks the record as likely
personal.

Nested metadata:

```json
{
  "recording_id": "local_health_admin_2026_06_11",
  "source_system": "local_import",
  "media_sha256": "sha256:...",
  "sensitivity_class": "personal_health",
  "flight_stage": "nested"
}
```

### Tune

Pavo transcribes with a small context dictionary:

- claim
- policy
- administrator
- callback
- prior authorization
- deductible

Pavo marks the claim number as sensitive structured text. It does not include
the raw claim number in broad summaries. The tuned record has a private facts
section and a redacted summary.

### Scout

Routing packet:

```json
{
  "recording_id": "local_health_admin_2026_06_11",
  "flight_stage": "scouted",
  "summary": "Insurance administrator gave a follow-up deadline and callback path for an unresolved claim.",
  "suggested_destinations": [
    {
      "destination": "private_archive",
      "action": "archive_source_record",
      "requires_approval": false
    },
    {
      "destination": "personal_task",
      "action": "create_follow_up_task",
      "requires_approval": true
    }
  ],
  "blocked_destinations": [
    {
      "destination": "slack",
      "reason": "Personal health content."
    },
    {
      "destination": "crm",
      "reason": "Not a customer/business record."
    }
  ],
  "sensitivity": {
    "contains_health_information": true,
    "contains_claim_identifier": true,
    "external_routing_default": "deny"
  }
}
```

### Approval

The user approves a private archive and a personal reminder:

```text
Follow up with insurance administrator by Friday about unresolved claim.
```

The user rejects all other routing. Pavo does not suggest Slack, CRM, or Linear.

### Land

Pavo writes the private archive and personal task. The archive includes the
source media and a redacted summary. The private facts remain in the user's
private evidence folder.

### Home

Pavo proposes:

```text
For records classified as personal_health:
  auto-archive privately.
  allow personal task suggestions.
  block Slack, CRM, and shared project trackers by default.
  require explicit approval for every external destination.
```

### Gotchas

- The product must not leak health identifiers into logs.
- The product must not route personal health content to business tools.
- The product should support "private by default" without requiring repeated
  user correction.

### Product Lesson

Pavo's routing intelligence is valuable only if it can also decide not to
route. Privacy is not the absence of features. It is a routing policy.

## Scenario A3: User Interview With Ambiguous Feature Request

### Situation

A product manager records a user interview. The user complains about onboarding
but does not explicitly request a feature. They describe confusion, a failed
workflow, and a workaround.

The risk is hallucinated product work. A generic AI might create a feature
request that overstates what the user asked for.

### Nest

The interview video is imported from a local file and preserved.

### Tune

Pavo transcribes the interview and marks three spans:

- pain description
- failed workflow
- workaround

Speaker identity is reviewed because the interviewer and user alternate
quickly.

### Scout

Routing packet:

```json
{
  "recording_id": "user_interview_onboarding_004",
  "summary": "User struggled with onboarding import setup and used a manual workaround.",
  "suggested_destinations": [
    {
      "destination": "research_repository",
      "action": "archive_interview_note",
      "requires_approval": true
    },
    {
      "destination": "linear",
      "action": "create_discovery_followup",
      "requires_approval": true
    }
  ],
  "proposed_actions": [
    {
      "kind": "research_insight",
      "title": "Onboarding import setup is confusing for first-time users",
      "confidence": 0.83
    },
    {
      "kind": "inferred_task",
      "title": "Explore onboarding import guidance improvements",
      "confidence": 0.58,
      "requires_review_reason": "User did not explicitly request this feature."
    }
  ],
  "action_classification": {
    "explicit_commitments": [],
    "inferred_tasks": 1,
    "research_insights": 1
  }
}
```

### Approval

The product manager approves the research archive and edits the Linear item
from a build task into a discovery follow-up. The wording changes from:

```text
Build onboarding import guidance
```

to:

```text
Investigate whether onboarding import guidance would reduce setup confusion
```

### Land

Pavo creates a research note and a discovery issue. The issue includes evidence
spans but avoids claiming the user asked for the feature.

### Home

Pavo learns:

```text
For user interviews:
  prefer research insights over build tasks.
  classify inferred tasks separately from explicit requests.
  require product approval before creating roadmap or engineering work.
```

### Gotchas

- User pain is not always a feature request.
- A workaround is evidence, not necessarily a roadmap item.
- AI-generated action language can easily overstate certainty.

### Product Lesson

Pavo should preserve nuance between evidence and action. The routing packet
should help the product manager think, not force a premature roadmap decision.

## Scenario A4: Recruiting Screen

### Situation

A recruiter records a candidate screen. The conversation contains candidate
experience, compensation expectations, interview feedback, and private
evaluation notes from the interviewer after the call.

This is a high-risk routing scenario because the record contains sensitive
employment data and possibly legally sensitive evaluation content.

### Nest

Pavo preserves the recording and marks source type as `recruiting`.

### Tune

Pavo transcribes the call and separates candidate speech from interviewer
comments. Post-call interviewer notes are marked separately if they were
captured in the same recording.

### Scout

Routing packet:

```json
{
  "recording_id": "recruiting_screen_backend_012",
  "summary": "Candidate discussed backend systems experience and compensation expectations.",
  "suggested_destinations": [
    {
      "destination": "ats",
      "action": "draft_candidate_note",
      "requires_approval": true
    },
    {
      "destination": "private_archive",
      "action": "archive_source_record",
      "requires_approval": true
    }
  ],
  "blocked_destinations": [
    {
      "destination": "slack",
      "reason": "Recruiting and compensation-sensitive content."
    }
  ],
  "sensitivity": {
    "contains_employment_data": true,
    "contains_compensation": true,
    "contains_evaluation": true
  }
}
```

### Approval

The recruiter approves an ATS draft after editing. Pavo does not write directly
to a public channel. It distinguishes candidate-provided facts from interviewer
evaluation.

### Land

Pavo saves an ATS note draft and records a manifest. If the ATS does not
support drafts, Pavo produces a local approved packet for manual copy rather
than forcing an unsafe write.

### Home

Policy candidate:

```text
For recruiting records:
  block Slack summaries.
  require approval for ATS writes.
  separate candidate facts from interviewer evaluation.
  flag compensation spans.
```

### Gotchas

- Candidate evaluation must not be casually routed.
- Compensation details need careful handling.
- The candidate's words and the interviewer's judgment are different evidence
  types.

### Product Lesson

Pavo needs destination-specific policy. A note that is appropriate in an ATS
may be inappropriate in Slack.

## Scenario A5: Field Inspection Voice Memo

### Situation

A field operator records a noisy voice memo while inspecting an event setup.
The memo mentions a damaged cable, missing signage, a vendor arrival time, and
a safety concern.

The audio is imperfect. The record is still valuable.

### Nest

Pavo imports the voice memo and preserves timestamp and file hash. If location
metadata exists, it records it as non-secret operational metadata.

### Tune

Pavo transcribes with field vocabulary. It marks several uncertain words and
keeps low-confidence spans. The safety concern is clear enough for routing.

### Scout

Routing packet:

```json
{
  "recording_id": "field_memo_event_setup_009",
  "summary": "Inspection found a damaged cable, missing signage, delayed vendor, and one safety concern.",
  "suggested_destinations": [
    {
      "destination": "task_system",
      "action": "create_event_setup_tasks",
      "requires_approval": true
    },
    {
      "destination": "safety_log",
      "action": "create_safety_note",
      "requires_approval": true
    },
    {
      "destination": "drive",
      "action": "archive_source_record",
      "requires_approval": false
    }
  ],
  "proposed_actions": [
    {
      "kind": "task",
      "title": "Replace damaged cable near bar setup",
      "confidence": 0.74
    },
    {
      "kind": "task",
      "title": "Install missing entrance signage",
      "confidence": 0.71
    },
    {
      "kind": "safety_note",
      "title": "Review cable trip hazard before guest arrival",
      "confidence": 0.86
    }
  ]
}
```

### Approval

The operator approves the safety note and two tasks. The vendor arrival item is
left as a note because the transcript was uncertain.

### Land

Pavo writes tasks and safety note with the original memo attached or linked in
the archive.

### Home

Policy candidate:

```text
For field memos:
  auto-archive source.
  recommend tasks for clear operational issues.
  require approval for safety log entries.
  keep low-confidence spans as notes, not tasks.
```

### Gotchas

- Noisy audio should not block all value.
- Low confidence should shape the route, not discard the record.
- Safety-related items need careful escalation.

### Product Lesson

Pavo can be useful even when Tune is imperfect. Nest plus partial Tune plus
conservative Scout can still produce controlled action.

# Appendix B: Product Gotcha Catalog

This catalog should expand over time. Each gotcha should eventually have
examples, detection signals, UI implications, and test fixtures.

## Gotcha B1: The Same Sentence Has Multiple Destinations

"We can expand if SSO is fixed by renewal" might be:

- a CRM risk note
- a product blocker
- a customer success follow-up
- a Drive archive item
- not a Slack post

Pavo should not force a single destination. The routing packet should support
multiple recommendations with separate approvals.

## Gotcha B2: The Right Action Is No Action

Some recordings should only be preserved. Some should be private. Some should
be rejected. A product that measures success only by tasks created will
over-route.

Pavo should treat "archive only," "private," and "ignore" as successful
outcomes.

## Gotcha B3: Confidence Is Not The Same As Permission

The model may be confident that a CRM note is relevant. That does not mean it
has permission to write the CRM note. Confidence affects recommendation
quality. Policy controls action.

## Gotcha B4: Review Is A Data Source

User edits are not just friction. They are product data. If the user repeatedly
turns build tasks into research questions, Home should learn that policy.

## Gotcha B5: Destination APIs Shape Product Behavior

Some systems support drafts. Some do not. Some support idempotency keys. Some
do not. Some have rich permissions. Some are flat text dumps. Pavo should avoid
pretending all destination writes are equivalent.

## Gotcha B6: Speaker Names Need Evidence

Named speakers are seductive. The UI should resist overclaiming. Pavo should
show whether a speaker is unknown, diarized, inferred, mapped, or reviewed.

## Gotcha B7: The Archive Can Become A Dump

If every recording is archived without useful metadata, Drive becomes a dump.
Nest needs enough metadata to support later retrieval, but not so much that it
becomes a heavy knowledge system.

## Gotcha B8: Redaction Must Precede Routing

Redaction after posting is too late. Sensitive text should be detected and
redacted before the destination write preview is approved.

## Gotcha B9: Reprocessing Changes Evidence

Future models may produce better transcripts. Pavo should allow reprocessing
without erasing the old evidence. A record can have multiple Tune runs.

## Gotcha B10: Local-First And Cloud-Sync Need Different Promises

Some users will want local-only processing. Others will want cloud sync. Pavo
should be clear about which artifacts remain local, which are archived, and
which are routed externally.

# Appendix C: Marketing Narrative And Launch Assets

Pavo needs marketing language that is clear enough for a buyer and precise
enough for a builder. The product can easily be misunderstood as "meeting
notes," "transcription," "Plaud integration," or "AI task extraction." Each of
those is adjacent. None is the product.

The marketing narrative should make three claims:

1. Conversations are becoming operational source material.
2. Source material should not jump into systems of work without evidence and
   approval.
3. Pavo is the control layer that moves spoken records from capture to approved
   action.

## Category Statement

Primary:

```text
Pavo is approval-gated routing for spoken records.
```

Expanded:

```text
Pavo catches meetings, calls, voice notes, and field recordings before they
disappear, tunes them into trustworthy records, scouts where the information
belongs, and lands only the actions you approve.
```

Plain:

```text
Pavo turns captured conversations into approved, source-backed work.
```

Technical:

```text
Pavo is a recording lifecycle and routing control plane. It preserves source
media, attaches transcript and speaker evidence, generates routing packets,
holds external writes behind approval, and records destination proof.
```

## Homepage Draft

### Hero

```text
Turn conversations into approved work.
```

Subhead:

```text
Pavo catches meetings, calls, and voice notes, preserves the source recording,
cleans up the record, recommends where the information should go, and waits
for approval before writing to your tools.
```

Primary CTA:

```text
Start with a recording
```

Secondary CTA:

```text
See the Flight Path
```

Proof line:

```text
Nest the source. Tune the record. Scout the route. Land approved actions. Home
future decisions.
```

### Problem Section

```text
Meeting AI gives you notes. Your work still has to happen somewhere else.
```

Supporting copy:

```text
Important conversations scatter across Plaud, Zoom, Meet, voice memos, Slack
huddles, and call recorders. The transcript might be wrong. The speaker might
be mislabeled. The action item might be inferred. The destination might be
sensitive. Pavo gives those records a controlled path into the systems where
work actually happens.
```

### Product Section

```text
The Pavo Flight Path
```

Cards:

```text
Nest
Capture and preserve the source recording, metadata, and hash.

Tune
Make the record accurate with transcript, speaker, vocabulary, and review
evidence.

Scout
Generate routing packets with destination recommendations and source
references.

Land
Execute approved actions into Drive, Linear, CRM, email drafts, or other
systems.

Home
Learn routing policy from approvals, rejections, redactions, and corrections.
```

### Differentiation Section

```text
Built for control, not blind automation.
```

Bullets:

- Source media remains the record.
- Every recommendation can point back to evidence.
- External writes require approval unless policy allows them.
- Private records can stop at archive.
- Rejections and edits improve future routing.

### Closing CTA

```text
Give every captured conversation a safe path forward.
```

## Launch Post Draft

```text
Most meeting AI products stop at notes.

Pavo starts there, but the real question is what happens next.

Every important conversation creates operational residue: a customer blocker,
a follow-up task, a CRM note, a private record, a research insight, a draft
email, a project issue, or sometimes nothing at all.

The problem is not only transcription. The problem is controlled routing.

Pavo is an evidence-first approval queue for captured conversations. It moves
spoken records through a Flight Path:

Nest -> Tune -> Scout -> Land -> Home

Nest the source recording.
Tune the transcript and speaker evidence.
Scout where the information should go.
Land only the actions you approve.
Home future decisions into inspectable policy.

The first wedge is simple: preserve real Plaud or local audio, build a
source-backed record, generate a routing packet, and approve one destination
action with proof.

Meeting AI gives you notes. Pavo turns captured conversations into approved,
source-backed work.
```

## Demo Script

The best demo should not show a generic summary. It should show control.

### Demo 1: Customer Call To Approved Work

1. Start with a real or fixture recording.
2. Show Nest: source media path, hash, source metadata.
3. Show Tune: transcript evidence, speaker uncertainty, context terms.
4. Show Scout: routing packet with Drive, Linear, CRM recommendations.
5. Show approval: approve Drive, edit Linear issue, redact CRM note.
6. Show Land: destination ids and write manifest.
7. Show Home: proposed policy for similar customer calls.

Narration:

```text
The important part is not that Pavo summarized the call. The important part is
that Pavo knew what level of trust the record had reached, proposed routes
with evidence, and waited before writing externally.
```

### Demo 2: Private Record That Does Not Route

1. Import a personal health or finance call.
2. Show sensitivity classification.
3. Show blocked destinations.
4. Approve private archive and personal task only.
5. Show policy candidate: personal records stay private by default.

Narration:

```text
Good routing includes deciding not to route. Pavo treats private and archive
only as successful outcomes.
```

### Demo 3: Ambiguous User Research

1. Import a user interview.
2. Show Tune with product vocabulary.
3. Show Scout classifying one item as research insight and one as inferred
   task.
4. Edit the inferred task into a discovery follow-up.
5. Show Home learning that user interviews should not become build tasks by
   default.

Narration:

```text
Pavo should help the product manager preserve nuance between evidence and
action.
```

## Objection Handling

### "Is this just another meeting notes app?"

No. Meeting notes are one input. Pavo is about the path from source recording
to approved action. It preserves the original media, tracks evidence, generates
routing packets, and records proof for approved destination writes.

### "Why not just use the AI built into Zoom, Plaud, or CRM?"

Those tools are valuable at their native layer. Pavo does not need to replace
them. Pavo sits above capture and before destination systems. It can use their
outputs, but it preserves source evidence and manages routing policy across
tools.

### "Why require approval?"

Because routing is where mistakes become real. A wrong summary in a private
view is annoying. A wrong CRM update, Slack post, email, or engineering task
can create operational damage. Pavo makes approval specific and learnable so
the queue gets smarter without hiding risk.

### "Will this create more review work?"

Only if built poorly. Pavo should support auto-archive, batch review, fast
rejection, policy learning, low-risk routes, and "private" or "ignore" states.
The goal is fewer untrusted manual decisions, not more clicks.

### "What if the transcript is wrong?"

Pavo assumes transcripts can be wrong. That is why Nest preserves the source
recording and Tune stores evidence, uncertainty, review notes, and corrections.
Routing recommendations should cite evidence and mark confidence.

### "What if we already have a knowledge base?"

Pavo is not trying to be the whole knowledge base. It prepares source-backed
records and approved routing packets that can feed archives, search systems,
CRMs, task systems, or knowledge bases.

## Naming And Vocabulary

The bird language should be consistent but not cute at the expense of clarity.

Use:

- Flight Path
- Nest
- Tune
- Scout
- Land
- Home
- routing packet
- approval queue
- destination proof
- policy memory

Avoid:

- "autopilot" for external writes
- "magic notes"
- "fully automatic CRM"
- "never review meetings again"
- "perfect speaker identity"

The best tone is controlled confidence: Pavo helps users move faster because
it is careful about where automation ends.

## One-Liners

- Pavo turns spoken records into approved, source-backed work.
- Meeting AI gives you notes. Pavo gives those notes a safe path into action.
- Capture is easy. Controlled routing is the hard part.
- Pavo is the control layer between recorded conversations and systems of work.
- Nest the source. Tune the record. Scout the route. Land approved actions.
- Good routing includes knowing when not to route.
- Pavo does not replace your tools; it governs the path between them.
- External writes need evidence, approval, and proof.

## Positioning Matrix

| Product Type | What It Solves | Where Pavo Differs |
| --- | --- | --- |
| Meeting notes | Readable summaries and action items | Pavo manages source-backed routing and approval. |
| Recording hardware | High-quality capture | Pavo controls what happens after capture. |
| CRM call intelligence | Sales call analysis and CRM workflows | Pavo is source-agnostic and approval-first across destinations. |
| Project management AI | Task generation inside a work tracker | Pavo decides whether a conversation should become a task at all. |
| Knowledge base | Retrieval and documentation | Pavo prepares governed records and routing packets for knowledge systems. |
| Automation platform | Moving data between apps | Pavo adds evidence, review, sensitivity, and policy memory before movement. |

## Marketing Risks

Pavo can be marketed badly in several ways.

Risk 1: It sounds like a transcription tool.

Fix: Lead with approved work, not transcript quality. Mention transcription as
part of Tune.

Risk 2: It sounds like automation that writes everywhere.

Fix: Lead with approval-gated routing. Show edit/reject/private states in every
demo.

Risk 3: It sounds too abstract.

Fix: Use concrete scenarios. "Customer call becomes Drive archive, Linear
issue, and CRM note after approval" is better than "AI routing layer."

Risk 4: The bird metaphor sounds cute.

Fix: Always pair the bird term with the plain verb:

```text
Nest: capture
Tune: correct
Scout: recommend
Land: act
Home: learn
```

Risk 5: It overpromises privacy.

Fix: Be precise. Pavo can enforce product boundaries, local-first options,
approval gates, and redaction workflows. It should not make broad legal or
compliance claims without the implementation to support them.

# Appendix D: Implementation Implications

The product book should shape the codebase. If Pavo is an evidence-first
approval queue, the architecture should make that path obvious. The goal is not
to add abstractions for their own sake. The goal is to make the product
invariants hard to violate.

## Module Map

The future codebase should make the Flight Path visible:

```text
pavo/
  records.py        # recording ledger and lifecycle state
  intake.py         # Plaud/local/meeting imports
  evidence.py       # transcript, speaker, review, and uncertainty artifacts
  routes.py         # routing packet generation and validation
  policy.py         # approval rules and policy memory
  approvals.py      # approval queue state and decisions
  destinations/     # Drive, Linear, CRM, Slack, email, local archive
  audit.py          # write manifests and destination proof
```

The current modules can evolve toward this without a disruptive rewrite. The
existing `download`, `plaud`, `transcribe`, `review`, `overlap`, and `render`
modules already cover pieces of Nest and Tune. The missing product modules are
mostly Scout, Land, and Home.

## Data Objects

### Recording Record

The recording record should be the stable ledger row.

Required fields:

```json
{
  "recording_id": "string",
  "source_system": "plaud|local_import|zoom|meet|other",
  "source_account_ref": "string|null",
  "source_recording_id": "string|null",
  "title": "string|null",
  "created_at": "datetime|null",
  "captured_at": "datetime",
  "media_path": "path|null",
  "media_sha256": "string|null",
  "duration_seconds": "number|null",
  "flight_stage": "intake_pending|nested|tuning|tuned|scouted|approval_pending|approved|landed|archived|private|rejected",
  "sensitivity_class": "string|null"
}
```

Invariant:

```text
No record can advance past Nest without either source media or an explicit
source-unavailable status.
```

### Evidence Record

Evidence records should be append-only by default.

```json
{
  "evidence_id": "string",
  "recording_id": "string",
  "kind": "transcript|speaker|overlap|review|correction|summary|redaction",
  "input_refs": [],
  "output_path": "path|null",
  "created_at": "datetime",
  "engine": "string|null",
  "confidence": "number|null",
  "review_status": "unreviewed|reviewed|rejected|superseded"
}
```

Invariant:

```text
New evidence can supersede old evidence, but should not silently erase it.
```

### Routing Packet

The routing packet should be a first-class file or ledger object, not a prompt
response hidden in logs.

```json
{
  "packet_id": "string",
  "recording_id": "string",
  "created_at": "datetime",
  "flight_stage": "scouted",
  "summary": "string",
  "source_refs": [],
  "detected_entities": [],
  "suggested_destinations": [],
  "proposed_actions": [],
  "sensitivity": {},
  "approval_requirements": [],
  "status": "draft|ready_for_review|partially_approved|approved|rejected|landed"
}
```

Invariant:

```text
Destination adapters consume approved routing packet actions, not raw
transcripts.
```

### Approval Decision

Approval should be granular enough to approve one action and reject another.

```json
{
  "approval_id": "string",
  "packet_id": "string",
  "action_id": "string",
  "decision": "approved|rejected|edited|redact_first|deferred",
  "actor": "user|policy",
  "decided_at": "datetime",
  "edited_payload": {},
  "notes": "string|null"
}
```

Invariant:

```text
No external write occurs without an approval decision or an explicit policy
grant.
```

### Destination Write Manifest

Every Land action should produce proof.

```json
{
  "write_id": "string",
  "packet_id": "string",
  "action_id": "string",
  "destination": "linear|drive|crm|slack|email|local_archive",
  "destination_id": "string|null",
  "status": "succeeded|failed|partial|skipped",
  "idempotency_key": "string",
  "approved_by": "string",
  "written_at": "datetime|null",
  "redactions": [],
  "error": "string|null"
}
```

Invariant:

```text
Retries use stable idempotency keys and must not duplicate destination writes.
```

## CLI Shape

The CLI should expose the Flight Path directly.

Possible commands:

```bash
pavo records list
pavo records show <recording-id>
pavo nest plaud <recording-id>
pavo nest import <media-path> --source local
pavo tune <recording-id> --context-term ...
pavo scout <recording-id>
pavo approvals list
pavo approvals show <packet-id>
pavo approvals decide <action-id> --approve
pavo land <packet-id>
pavo home policies list
pavo home policies promote <policy-candidate-id>
```

The verbs should be product verbs, not implementation-only verbs. Existing
commands like `pavo plaud download` and `pavo transcribe` can remain as lower
level operations, but the product-level CLI should tell the Flight Path story.

## UI Implications

Pavo's first real UI should probably not be a meeting player. It should be an
approval queue and record detail view.

### Record List

Columns:

- title
- source
- created
- Flight Path stage
- sensitivity
- pending approvals
- last action

Useful filters:

- nested only
- needs Tune review
- scouted
- approval pending
- landed
- private
- failed write

### Record Detail

Sections:

- source media and hash
- transcript evidence
- speaker evidence
- uncertainty
- routing packet
- approval history
- destination proof
- policy suggestions

### Approval Review

The approval review should make it easy to answer:

- What will be written?
- Where will it go?
- Why is it recommended?
- What evidence supports it?
- What sensitive content is included?
- Can I edit it?
- Can I redact it?
- Can I reject it?
- Can I teach Pavo a rule?

## Storage Implications

Pavo can start local-first. A simple JSONL or SQLite ledger may be enough for
early development. The important part is not the database choice. The important
part is preserving product invariants.

Early storage should support:

- append-only evidence records
- stable recording ids
- source hashes
- routing packets as durable JSON
- approval decisions
- write manifests
- policy candidates

Avoid storing:

- raw OAuth tokens
- signed URLs as durable artifacts
- unredacted sensitive snippets in broad logs
- secret values in routing packets

## Test Implications

Current Pavo tests prove important Nest and Tune behaviors. The product book
implies new tests.

### Nest Tests

- imported media gets hashed
- Plaud download creates a recording record
- signed URL is not persisted as durable proof
- missing media blocks progression unless explicitly marked unavailable

### Tune Tests

- transcript evidence does not overwrite raw source
- speaker uncertainty is preserved
- review corrections are additive
- context terms are recorded

### Scout Tests

- routing packet schema validates
- destination recommendations include reasons
- proposed actions include evidence refs
- sensitivity flags can block destinations
- low-confidence items require approval

### Land Tests

- adapter refuses unapproved action
- destination write creates manifest
- retry uses idempotency key
- partial failure is visible
- redaction manifest is attached

### Home Tests

- approval creates policy candidate
- rejection creates negative signal
- private category blocks broad destinations
- promoted policy is inspectable
- policy does not silently grant broader permission than approved

## Integration Order

Recommended order:

1. Local archive adapter.
2. Drive archive adapter.
3. Linear task adapter.
4. Email draft adapter.
5. CRM note adapter.
6. Slack summary adapter.

Reasoning:

- Local archive proves Land without external auth risk.
- Drive archive proves durable external storage.
- Linear proves task creation from approved packets.
- Email draft proves "draft, not send."
- CRM proves sensitive business state updates.
- Slack should come late because broad sharing is high-risk.

## Product Review Gates

Every new Pavo feature should pass a Flight Path review:

1. Which stage does this feature improve?
2. What product state does it create or update?
3. What evidence proves the state?
4. What approval boundary applies?
5. What can go wrong?
6. What audit trail is produced?
7. What policy learning signal is generated?

If those questions cannot be answered, the feature is probably not ready.

# Appendix E: Routing Packet Schema And Policy Examples

The routing packet is the product hinge. Before a packet exists, Pavo has a
record. After a packet exists, Pavo has a decision surface. The packet should
be explicit enough that a human can review it, a destination adapter can act
on it, and a future policy engine can learn from the approval decision.

This appendix expands the packet from an implementation sketch into a product
contract. It should eventually become a formal schema with validators, test
fixtures, and example packets for every major scenario class.

## Why The Packet Matters

Without a routing packet, the product collapses into prompt output. A model can
say "create a Linear issue" or "send this to CRM," but the recommendation is
too soft to govern. It may not say what evidence supports the recommendation.
It may not say which fields are sensitive. It may not separate a proposed
draft from an external write. It may not preserve rejected choices. It may not
explain why a destination was blocked.

The routing packet turns the model recommendation into a durable object. That
object becomes the thing the user reviews, the thing adapters consume, the
thing tests validate, and the thing Home learns from.

Pavo should treat the packet as a contract between Scout and Land:

```text
Scout may recommend. Land may only execute approved packet actions.
```

This matters because it prevents direct prompt-to-destination behavior. A
destination adapter should not consume a transcript, summary, or chat response
directly. It should consume a packet action that has passed policy checks and
approval requirements.

## Packet Sections

A mature routing packet should contain at least nine sections:

1. Identity and provenance
2. Record summary
3. Source references
4. Entities and context
5. Sensitivity classification
6. Destination recommendations
7. Proposed actions
8. Approval requirements
9. Learning signals

The first version can be smaller, but the shape should point in this direction
from the beginning.

## Identity And Provenance

Identity fields answer "what is this packet and what record did it come from?"

Example:

```json
{
  "packet_id": "pkt_customer_acme_renewal_2026_06_11_001",
  "recording_id": "rec_customer_acme_renewal_2026_06_11",
  "created_at": "2026-06-11T15:22:00Z",
  "created_by": "scout.default.v1",
  "source_stage": "tuned",
  "packet_version": "0.1",
  "status": "ready_for_review"
}
```

Important product details:

- `packet_id` should be stable and unique.
- `recording_id` should link to the source record, not only a transcript.
- `created_by` should identify the Scout engine or rule set.
- `packet_version` should allow schema evolution.
- `status` should describe review state, not model confidence.

Gotcha:

```text
Do not use "approved" as a model output. Approval is a user or policy decision.
```

## Record Summary

The summary is for orientation, not proof. It should be short, plain, and
clearly marked as a derived artifact.

Example:

```json
{
  "summary": {
    "short": "Customer said renewal depends on SSO reliability and requested a follow-up plan.",
    "derived_from": ["ev_transcript_001", "ev_review_002"],
    "review_status": "unreviewed",
    "limits": [
      "Speaker identity for the customer champion was inferred, not manually reviewed.",
      "One product term was normalized from uncertain transcript text."
    ]
  }
}
```

The packet should avoid pretending that a summary is self-justifying. The
summary should point back to evidence and disclose uncertainty. If the summary
is later edited, the edited summary should become a review artifact rather
than overwriting the original generated summary.

## Source References

Source references are how Pavo earns trust. A proposed action should be able
to cite the part of the record that supports it.

Example:

```json
{
  "source_refs": [
    {
      "ref_id": "src_001",
      "kind": "audio_span",
      "recording_id": "rec_customer_acme_renewal_2026_06_11",
      "start_seconds": 312.4,
      "end_seconds": 337.8,
      "speaker_label": "customer_champion_inferred",
      "transcript_excerpt": "Renewal is hard to justify until SSO stops breaking for the team.",
      "confidence": 0.82
    },
    {
      "ref_id": "src_002",
      "kind": "review_note",
      "evidence_id": "ev_review_002",
      "note": "Reviewer confirmed SSO term and customer speaker."
    }
  ]
}
```

Pavo should be careful with transcript excerpts in packets. For sensitive
records, the packet may need redacted excerpts or references without raw text.
The product should support both:

```text
source ref with excerpt
source ref with redacted excerpt
source ref without excerpt
```

The key is that the system can return to the source under the right
permissions.

## Entities And Context

Entities help routing, but they are also a source of errors. The packet should
distinguish detected, inferred, mapped, and reviewed entities.

Example:

```json
{
  "entities": [
    {
      "entity_id": "ent_acme_corp",
      "name": "Acme Corp",
      "kind": "customer_account",
      "status": "mapped",
      "source": "crm_account_match",
      "confidence": 0.94
    },
    {
      "entity_id": "ent_sso",
      "name": "SSO",
      "kind": "product_area",
      "status": "reviewed",
      "source": "context_dictionary",
      "confidence": 0.98
    },
    {
      "entity_id": "ent_customer_champion",
      "name": "Jordan",
      "kind": "person",
      "status": "inferred",
      "source": "speaker_context",
      "confidence": 0.67
    }
  ]
}
```

The product should not make speaker naming feel more certain than it is. A
speaker can be:

```text
unknown
diarized
inferred
mapped
reviewed
```

That vocabulary is worth preserving in the UI and docs because it changes how
much trust a destination write should receive.

## Sensitivity Classification

Sensitivity should not be a single boolean. Pavo needs enough detail to block
or shape routing.

Example:

```json
{
  "sensitivity": {
    "class": "business_sensitive",
    "contains_personal_data": false,
    "contains_health_information": false,
    "contains_financial_terms": true,
    "contains_compensation": false,
    "contains_credentials": false,
    "contains_customer_commitment": true,
    "external_routing_default": "approval_required",
    "redaction_required_before": ["slack"],
    "blocked_destinations": []
  }
}
```

For personal health content:

```json
{
  "sensitivity": {
    "class": "personal_health",
    "contains_personal_data": true,
    "contains_health_information": true,
    "contains_financial_terms": false,
    "contains_compensation": false,
    "contains_credentials": false,
    "external_routing_default": "deny",
    "redaction_required_before": ["personal_task"],
    "blocked_destinations": ["slack", "crm", "linear_shared"]
  }
}
```

The default should be conservative. When the system is unsure whether a record
is sensitive, it should prefer review over broad routing.

## Destination Recommendations

Destination recommendations should explain why a destination is suggested,
what kind of write is proposed, and whether the recommendation depends on
review.

Example:

```json
{
  "suggested_destinations": [
    {
      "destination": "drive",
      "action": "archive_source_record",
      "reason": "Customer renewal call should be preserved with source media.",
      "requires_approval": false,
      "policy_basis": "customer_calls.auto_archive_drive",
      "risk": "low"
    },
    {
      "destination": "linear",
      "action": "create_issue",
      "reason": "Customer explicitly linked renewal risk to SSO reliability.",
      "requires_approval": true,
      "policy_basis": "customer_calls.product_blockers.require_pm_approval",
      "risk": "medium"
    },
    {
      "destination": "crm",
      "action": "draft_account_note",
      "reason": "Renewal dependency belongs with account context.",
      "requires_approval": true,
      "policy_basis": "customer_calls.crm_notes.require_account_owner_approval",
      "risk": "medium"
    }
  ]
}
```

Blocked destinations are just as important:

```json
{
  "blocked_destinations": [
    {
      "destination": "slack",
      "reason": "Conversation includes commercial renewal risk.",
      "policy_basis": "customer_calls.renewal_risk.block_broad_channels"
    }
  ]
}
```

The UI should show blocked destinations as product signal, not as a failure.
The user should see that Pavo considered a route and intentionally withheld it.

## Proposed Actions

Proposed actions are the units of approval. They should be small enough to
approve, edit, reject, redact, or defer separately.

Example:

```json
{
  "proposed_actions": [
    {
      "action_id": "act_archive_drive_001",
      "destination": "drive",
      "kind": "archive_source_record",
      "title": "Archive Acme renewal call",
      "payload": {
        "folder_hint": "Customers/Acme/Renewals",
        "include_media": true,
        "include_tuned_transcript": true,
        "include_routing_packet": true
      },
      "source_refs": ["src_001", "src_002"],
      "confidence": 0.91,
      "requires_approval": false
    },
    {
      "action_id": "act_linear_001",
      "destination": "linear",
      "kind": "create_issue",
      "title": "Investigate SSO reliability issue affecting Acme renewal",
      "payload": {
        "team": "Product",
        "labels": ["customer-evidence", "sso"],
        "body": "Acme said renewal is difficult to justify until SSO reliability improves. Source span attached."
      },
      "source_refs": ["src_001"],
      "confidence": 0.84,
      "requires_approval": true,
      "requires_review_reason": "Creates engineering/product work from a customer conversation."
    }
  ]
}
```

A proposed action should not hide its risk. The packet should make explicit
when an action:

- creates work for another person
- writes into a customer system
- sends or drafts outbound communication
- exposes private or sensitive content
- depends on uncertain speaker identity
- contains inferred rather than explicit commitments

## Approval Requirements

Approval requirements connect policy to action.

Example:

```json
{
  "approval_requirements": [
    {
      "action_id": "act_linear_001",
      "required_decision": "approve_or_edit",
      "eligible_actors": ["product_manager", "account_owner"],
      "reason": "Creates product work from customer evidence."
    },
    {
      "action_id": "act_crm_001",
      "required_decision": "approve_or_redact_or_reject",
      "eligible_actors": ["account_owner"],
      "reason": "Writes commercial account context."
    }
  ]
}
```

The product can start with a single-user approval model. The schema should not
preclude future team workflows. Eventually, some actions may need one approver,
some may need role-specific approval, and some may be granted by policy.

## Learning Signals

Home should learn from explicit review, not from hidden interpretation.

Example:

```json
{
  "learning_signals": [
    {
      "signal_id": "sig_001",
      "source": "approval_decision",
      "meaning": "User approved Drive archive without edit.",
      "policy_candidate": "customer_calls.auto_archive_drive"
    },
    {
      "signal_id": "sig_002",
      "source": "edited_action",
      "meaning": "User changed Linear issue from build task to investigation.",
      "policy_candidate": "customer_calls.product_blockers.prefer_investigation_language"
    },
    {
      "signal_id": "sig_003",
      "source": "rejected_destination",
      "meaning": "User rejected Slack summary due to commercial sensitivity.",
      "policy_candidate": "renewal_risk.block_broad_slack"
    }
  ]
}
```

Learning should be visible. A policy candidate should be inspectable before it
becomes durable behavior.

## Policy Examples

Policies should be written in plain language before they are encoded. The
human-readable form keeps the product honest.

### Customer Call Policy

```text
When a record is classified as a customer call:
  preserve the source recording.
  recommend Drive archive.
  recommend CRM note when account identity is mapped.
  recommend Linear only for concrete product blockers.
  require approval for CRM and Linear writes.
  block broad Slack posts when renewal risk or commercial terms appear.
  preserve rejected recommendations as learning signals.
```

### User Interview Policy

```text
When a record is classified as a user interview:
  preserve the source recording.
  recommend research archive.
  classify product feedback as insight, explicit request, or inferred task.
  require approval before creating engineering work.
  prefer discovery language unless the user made an explicit request.
  avoid CRM unless the interview is attached to a customer account.
```

### Personal Administration Policy

```text
When a record is classified as personal administration:
  preserve source privately.
  block shared work systems by default.
  allow personal task suggestions.
  redact identifiers in task titles.
  require explicit approval for every external destination.
  never include sensitive identifiers in broad logs.
```

### Recruiting Policy

```text
When a record is classified as recruiting:
  preserve source with restricted access.
  separate candidate-provided facts from interviewer evaluation.
  flag compensation and employment-sensitive spans.
  block broad Slack summaries.
  draft ATS notes only after approval.
  never route post-call interviewer commentary as candidate speech.
```

### Field Memo Policy

```text
When a record is classified as a field memo:
  preserve source.
  recommend tasks for clear operational issues.
  route safety concerns to a safety log after approval.
  keep uncertain transcript spans as notes, not tasks.
  allow low-risk archive without manual review.
```

## Packet Acceptance Criteria

A routing packet is acceptable when:

- it links to a recording record
- it identifies the evidence used
- it distinguishes summary from source
- it marks sensitive content
- it lists suggested and blocked destinations
- it expresses proposed actions as separately reviewable units
- it states approval requirements
- it can be validated without calling an AI model
- it can survive as an audit artifact after destination writes

If a packet fails those criteria, it is not ready for Land.

# Appendix F: Destination Adapter Playbooks

Destination adapters are where Pavo becomes real. They are also where product
risk increases. A recommendation inside Pavo can be inspected and rejected. A
write into another system changes the user's operational environment.

This appendix describes how major destination adapters should behave and what
they should refuse to do.

## Adapter Principles

Every adapter should follow five principles:

1. Consume approved packet actions, not raw transcripts.
2. Validate payload shape before writing.
3. Use idempotency keys where possible.
4. Return a destination write manifest.
5. Fail closed when approval, permission, or redaction is missing.

An adapter should be boring. The intelligence belongs in Scout and policy. The
adapter should execute a clearly approved action and record proof.

## Local Archive Adapter

The local archive adapter should be first because it proves Land without
external account risk.

Supported actions:

- archive source media
- archive tuned transcript
- archive routing packet
- archive approval decision
- write local manifest

Example output:

```json
{
  "write_id": "write_local_001",
  "destination": "local_archive",
  "status": "succeeded",
  "path": "/Users/dshanklin/Eidos/Pavo/archive/customer/acme/rec_customer_acme_renewal_2026_06_11",
  "idempotency_key": "rec_customer_acme_renewal_2026_06_11:local_archive:v1",
  "written_artifacts": [
    "source.m4a",
    "transcript.json",
    "routing-packet.json",
    "approval-decisions.json",
    "manifest.json"
  ]
}
```

Refusals:

- refuse to archive without a recording id
- refuse to mark a record landed if manifest write fails
- refuse to persist signed URLs as source proof
- refuse to overwrite a prior archive without a supersession manifest

Product note:

```text
Local archive is not glamorous, but it is the foundation of trust. It proves
that a record can land without depending on external APIs.
```

## Drive Adapter

Drive is a natural destination for source-backed archives. It is not the same
as search, memory, or task management. The Drive adapter should preserve
evidence packages, not spray summaries into folders.

Supported actions:

- create folder
- upload source media
- upload transcript
- upload routing packet
- upload human-readable summary
- upload manifest

Key design choice:

```text
Drive should receive evidence bundles, not unstructured note dumps.
```

Folder naming should include stable identifiers:

```text
2026-06-11 - Acme Renewal Call - rec_customer_acme_renewal_2026_06_11
```

Manifest example:

```json
{
  "write_id": "write_drive_001",
  "destination": "drive",
  "status": "succeeded",
  "folder_id": "drive-folder-id",
  "files": [
    {
      "name": "source.m4a",
      "drive_id": "drive-file-id-1",
      "sha256": "sha256:..."
    },
    {
      "name": "routing-packet.json",
      "drive_id": "drive-file-id-2",
      "sha256": "sha256:..."
    }
  ],
  "approved_by": "user",
  "written_at": "2026-06-11T16:03:00Z"
}
```

Gotchas:

- Drive permissions can leak records if folder inheritance is wrong.
- Large media uploads can fail halfway.
- Re-running a write can duplicate folders.
- Folder names can expose sensitive details.

Adapter requirements:

- preview folder name before write
- allow private or restricted folder targets
- support retry without duplicate upload where possible
- record partial failures
- avoid putting sensitive identifiers in default folder names

## Linear Adapter

Linear is useful when a conversation produces work. It is dangerous when a
conversation produces only vague interest. The adapter should make a hard
distinction between explicit tasks, inferred tasks, research insights, and
customer evidence.

Supported actions:

- create issue
- draft issue payload for manual copy
- attach source evidence link
- add labels
- add relation to customer evidence if local convention exists

The adapter should not create an issue when:

- the packet action is unapproved
- the action is classified as an insight only
- the title is an overstatement of evidence
- required team/project routing is unknown
- source evidence is missing and policy requires it

Good issue title:

```text
Investigate SSO reliability issue affecting Acme renewal
```

Risky issue title:

```text
Build new SSO system for Acme
```

The second may be correct eventually, but Pavo should not leap from one
conversation to a build mandate unless the approval explicitly says so.

Body template:

```text
Source: rec_customer_acme_renewal_2026_06_11
Packet: pkt_customer_acme_renewal_2026_06_11_001

Approved summary:
Acme said renewal is difficult to justify until SSO reliability improves.

Evidence:
- 05:12-05:38, customer champion inferred, transcript reviewed

Approval:
- Approved by user at 2026-06-11T16:08:00Z
- Edited from generated title to investigation language
```

Gotchas:

- Linear issues create work and attention load.
- Customer evidence can become product pressure without context.
- Duplicate issues are common if idempotency is weak.
- A sensitive transcript excerpt may not belong in the issue body.

Adapter requirements:

- require approved action
- use labels that mark source-backed evidence
- prefer links to private evidence over raw excerpts when sensitive
- store Linear issue id in write manifest
- detect likely duplicates when possible

## Email Draft Adapter

Email is high risk because sending is external communication. Pavo's first
email adapter should create drafts only. Sending should remain out of scope
until the product has a stronger approval and identity model.

Supported actions:

- create local draft
- create email-client draft if integration exists
- attach source-backed summary
- mark unresolved fields

The adapter should not:

- send email
- infer recipients without approval
- include sensitive source excerpts by default
- turn uncertain commitments into promises

Draft example:

```text
Subject: Follow-up on SSO reliability discussion

Hi Jordan,

Thanks for walking through the renewal concerns today. I captured that SSO
reliability is a key blocker for the team and that you would like a follow-up
plan before the renewal review.

Draft next step:
We will send a concrete update on SSO reliability status and mitigation plan
by [DATE].

Source-backed note:
This draft was prepared from rec_customer_acme_renewal_2026_06_11 and requires
human review before sending.
```

Gotchas:

- A draft can still be copied and sent by mistake.
- The user may assume Pavo verified commitments that were only inferred.
- Recipients may be ambiguous.
- Tone matters and is hard to validate from transcript alone.

Adapter requirements:

- label every output as draft
- require user-provided or approved recipient
- preserve unresolved placeholders
- avoid automatic send
- write manifest as `draft_created`, not `sent`

## CRM Adapter

CRM writes affect commercial truth. They should come after Drive and Linear in
the integration order because they require stronger account mapping and
permission controls.

Supported actions:

- draft account note
- write account note after approval
- attach source reference
- update follow-up field only when explicitly approved

The adapter should not:

- create or update deal amount based on transcript inference
- change stage without explicit approval
- overwrite account fields from a conversation
- write to an account with uncertain identity

Good CRM note:

```text
Source-backed call note, 2026-06-11:
Customer said renewal justification depends on improved SSO reliability. User
approved this note from Pavo packet pkt_customer_acme_renewal_2026_06_11_001.
```

Bad CRM note:

```text
Renewal blocked. Deal at risk. Product must fix SSO.
```

The bad version may be directionally true, but it compresses nuance and omits
approval proof.

Gotchas:

- CRM account matching can be wrong.
- Notes can be visible to broad sales teams.
- Commercial language can escalate a situation.
- Updating fields is riskier than adding notes.

Adapter requirements:

- require mapped account id
- require approval for every write
- use conservative language
- store CRM object id and note id
- distinguish note creation from field mutation

## Slack Adapter

Slack should come late. Broad messaging is easy to overuse and hard to undo.
Pavo should initially support Slack as a draft or private review output, not as
an automatic announcement channel.

Supported actions:

- create Slack draft text
- post to a configured private channel after approval
- attach source-backed link
- redact sensitive content

The adapter should not:

- post broad summaries by default
- post personal, health, recruiting, compensation, or commercial-risk content
  without strong policy
- mention people automatically
- post raw transcript excerpts unless approved

Slack message draft:

```text
Source-backed customer signal from Acme renewal call:
Acme linked renewal confidence to SSO reliability. Product follow-up issue was
approved in Linear. Evidence is archived in Drive.
```

Gotchas:

- Slack creates social pressure.
- A concise summary can sound more certain than the source.
- Channels have changing membership.
- Mentions can trigger unnecessary urgency.

Adapter requirements:

- require channel preview
- require redaction check
- require approval
- avoid mentions by default
- store channel id, timestamp, and permalink in manifest

## Adapter Comparison

| Destination | First Useful Mode | Primary Risk | Approval Default |
| --- | --- | --- | --- |
| Local archive | Write evidence bundle | Bad local metadata | Policy allowed |
| Drive | Write evidence bundle | Permission leak | Usually allowed or approval |
| Linear | Create issue | Noisy or overstated work | Required |
| Email | Create draft | Accidental external promise | Required |
| CRM | Draft/write note | Commercial truth mutation | Required |
| Slack | Draft/post message | Broad sensitive sharing | Required |

The adapter roadmap should move from low-risk evidence preservation to
high-risk external communication.

# Appendix G: Product Review Checklists

Pavo needs checklists because the product will otherwise drift toward the
easiest demo. The easiest demo is "AI turns transcript into tasks." The better
product is slower to explain and safer to build: evidence, routing, approval,
action, proof, and learning.

These checklists make the product bar explicit.

## Nest Review Checklist

Nest is complete for a record when:

- source system is recorded
- source media or source-unavailable status exists
- media hash exists when media is local
- capture timestamp is recorded
- source account reference is recorded when available
- original filename or title is preserved
- durable record id exists
- signed URLs are not treated as durable proof
- sensitivity defaults are conservative

Review questions:

1. Can we find the original record again?
2. Can we prove whether the local media changed?
3. Do we know which source system produced it?
4. Did we avoid storing temporary secrets as proof?
5. Is the record safe to show in a list?

Failure examples:

- The transcript exists but the source media path is lost.
- The file was imported but not hashed.
- A signed URL was saved and later expired.
- The title includes sensitive personal data and appears in broad logs.

## Tune Review Checklist

Tune is complete when:

- transcript exists or failure is recorded
- transcript engine/version is recorded
- speaker labels have status
- uncertain spans are preserved
- context terms are recorded
- review corrections are additive
- accepted and diagnostic artifacts are distinguished
- redaction candidates are marked before routing

Review questions:

1. What is the transcript based on?
2. Which speaker labels are reviewed versus inferred?
3. Where is uncertainty preserved?
4. Can a reviewer correct the record without destroying prior evidence?
5. Which spans should not be routed broadly?

Failure examples:

- Speaker names are shown as facts when they were inferred.
- Human review overwrites model output without trace.
- Low-confidence spans become confident action items.
- Sensitive identifiers are included in a broad summary.

## Scout Review Checklist

Scout is complete when:

- routing packet validates
- summary cites evidence
- suggested destinations include reasons
- blocked destinations include reasons
- proposed actions are separately reviewable
- sensitivity affects destination choice
- action type is classified
- approval requirements are explicit
- learning signals are proposed but not silently promoted

Review questions:

1. What is Pavo recommending?
2. Why is it recommending that?
3. What evidence supports each recommendation?
4. What destination did it choose not to use?
5. What requires approval?
6. What can the user edit?

Failure examples:

- One summary is sent everywhere.
- A user interview becomes an engineering task without nuance.
- A personal health record suggests Slack because Slack is connected.
- The packet says "high confidence" but omits permission state.

## Land Review Checklist

Land is complete when:

- approved action exists
- destination adapter validates payload
- redaction requirements are satisfied
- idempotency key exists
- write result is recorded
- destination id or failure is recorded
- partial failures are visible
- retry behavior is safe
- manifest links back to packet and approval

Review questions:

1. Who approved this action?
2. What exactly was written?
3. Where was it written?
4. What proof did the destination return?
5. Can retry duplicate the write?
6. Was sensitive content redacted before write?

Failure examples:

- Adapter writes from a transcript without packet approval.
- Retry creates duplicate Linear issues.
- CRM note is written to the wrong account.
- A Slack post succeeds but manifest is not saved.

## Home Review Checklist

Home is complete when:

- approval decisions are captured
- edits are compared to generated actions
- rejections become negative signals
- redactions become sensitivity signals
- policy candidates are inspectable
- promoted policies are scoped
- policy effects can be explained
- policy does not expand permissions silently

Review questions:

1. What did the user teach Pavo?
2. Is the proposed policy too broad?
3. Can the user see and undo it?
4. Does the policy affect private records?
5. Does the policy grant write permission or only change recommendations?

Failure examples:

- Pavo learns "always create Linear issues" from one approval.
- A rejection is ignored because it did not produce an action.
- A policy candidate silently starts posting to Slack.
- Home optimizes for fewer clicks by weakening approval boundaries.

## Milestone Acceptance Checklist

### Milestone 1: Source-Backed Local Record

Accept when:

- local or Plaud recording can be imported
- record has stable id and hash
- transcript can be attached
- source evidence can be rendered
- tests prove source media is preserved

Reject when:

- transcript exists without source linkage
- source proof depends on temporary URLs
- record ids change across runs

### Milestone 2: Tuned Review Artifact

Accept when:

- reviewer can inspect transcript and source
- corrections are saved as evidence
- speaker uncertainty is visible
- accepted artifacts are distinguished from diagnostics

Reject when:

- review destroys original output
- speaker labels overclaim certainty
- uncertainty is hidden for readability

### Milestone 3: Routing Packet

Accept when:

- Scout generates a durable packet
- packet validates locally
- actions are separately reviewable
- blocked destinations are represented
- packet can be rendered for humans

Reject when:

- recommendations exist only in model chat text
- actions cannot be approved separately
- sensitivity does not affect routes

### Milestone 4: Approval Queue

Accept when:

- user can approve, edit, reject, redact, or defer actions
- decisions are durable
- approval is linked to action id
- UI or CLI shows pending decisions

Reject when:

- approval is all-or-nothing for the whole record
- edited payload loses source evidence
- rejection is not saved

### Milestone 5: First Land Adapter

Accept when:

- adapter consumes approved packet action
- write manifest is produced
- retry is safe
- failure is visible
- tests prove unapproved writes are refused

Reject when:

- adapter reads transcript directly
- no manifest is produced
- duplicate writes are easy

### Milestone 6: Policy Memory

Accept when:

- approval/rejection/edit signals create policy candidates
- user can inspect candidate
- promoted policy is scoped
- policy effect is visible in future Scout output

Reject when:

- policy changes are hidden
- one decision creates broad automation
- approval requirements are weakened without explicit user intent

# Appendix H: Additional Worked Scenarios

The scenario library should become one of the longest parts of the book. Pavo
is easier to understand through concrete decisions than through category
language. Each scenario should prove a different edge of the product.

## Scenario H1: Consulting Discovery Call

### Situation

A consultant records a discovery call with a prospective client. The call
contains business context, possible project scope, budget hints, private
organizational tension, and a request for a follow-up proposal.

The value is obvious: Pavo can preserve the call, extract a proposal outline,
and create follow-up work. The risk is also obvious: a careless system might
write sensitive internal politics into a proposal or CRM note.

### Nest

Pavo imports the recording and classifies it as `professional_services`. It
preserves source media and marks the record as commercially sensitive.

### Tune

Tune identifies three kinds of content:

- client-stated goals
- consultant follow-up commitments
- sensitive internal context

The transcript is useful, but the routing depends on separating those
categories. Client-stated goals may belong in a proposal draft. Follow-up
commitments may belong in tasks. Internal tension may belong only in private
notes.

### Scout

Recommended routes:

- Drive archive for source evidence
- proposal outline draft
- personal or team task for follow-up
- CRM note with conservative language

Blocked or restricted routes:

- broad Slack summary
- raw transcript excerpt in proposal
- CRM note containing internal politics

Routing packet principle:

```text
Use the client's stated goals in external-facing drafts. Keep sensitive
organizational context in restricted evidence.
```

### Approval

The consultant approves:

- archive
- task to send proposal by Friday
- proposal outline draft

The consultant edits the CRM note to say:

```text
Discovery call completed. Client requested a proposal for improving onboarding
operations. Follow-up proposal due Friday.
```

The consultant rejects the generated note about internal stakeholder conflict.

### Land

Pavo writes the archive and task. It creates a proposal outline draft but does
not send it. It writes the approved CRM note if the account mapping is
confirmed.

### Home

Policy candidate:

```text
For consulting discovery calls:
  separate client-stated goals from sensitive internal context.
  allow proposal outline drafts.
  require approval for CRM notes.
  block broad team summaries unless the user explicitly approves.
```

### Product Lesson

Professional services work is full of useful context that should not all go to
the same place. Pavo's value is not extraction alone. It is controlled
separation.

## Scenario H2: Investor Update Call

### Situation

A founder records a call with an investor. The conversation includes
fundraising context, customer traction, hiring plans, runway, and a promised
follow-up.

This is high sensitivity. Pavo should help the founder preserve commitments
and follow up, but it should avoid broad routing.

### Nest

The recording is marked `investor_sensitive`. Source media is stored in a
restricted archive.

### Tune

Tune identifies:

- investor questions
- founder commitments
- financial references
- strategic claims

Financial and fundraising terms are marked sensitive. Speaker attribution
matters because investor questions and founder claims should not be mixed.

### Scout

Suggested destinations:

- restricted Drive archive
- founder task list
- draft follow-up email

Blocked destinations:

- Slack
- general knowledge base
- public CRM note

Proposed actions:

```json
[
  {
    "kind": "task",
    "title": "Send investor follow-up materials",
    "requires_approval": true
  },
  {
    "kind": "email_draft",
    "title": "Draft investor follow-up",
    "requires_approval": true
  }
]
```

### Approval

The founder approves a private task and an email draft. The draft includes
placeholders for numbers rather than copying financial details from the
transcript automatically.

### Land

Pavo creates the task and local draft. It records that no outbound email was
sent.

### Home

Policy candidate:

```text
For investor-sensitive records:
  restrict archive.
  allow private tasks and drafts.
  block broad sharing by default.
  never auto-fill financial figures into outbound drafts without explicit
  review.
```

### Product Lesson

Some of the most valuable recordings are the least appropriate for broad
automation. Pavo should make private follow-through easy without weakening
confidentiality.

## Scenario H3: Customer Support Escalation

### Situation

A support lead records a call with an upset customer. The customer reports a
bug, describes business impact, and receives an apology plus a follow-up
commitment.

The product must preserve urgency without turning emotion into imprecise
operational claims.

### Nest

Pavo captures the call from a support call recorder and maps the customer
account.

### Tune

Tune marks:

- reported bug
- business impact
- support commitment
- emotional tone

Tone is useful context, but it should not become a task by itself.

### Scout

Suggested routes:

- support ticket update
- Linear issue if bug is concrete
- CRM account note
- Drive archive

Blocked:

- public Slack escalation unless approved

The bug action must cite the exact customer description. The business impact
should be included only if the customer stated it clearly.

### Approval

The support lead approves:

- support ticket note
- Linear bug issue
- CRM note

They edit the Linear issue to remove exaggerated language. The generated title
changes from:

```text
Critical outage for Acme users
```

to:

```text
Investigate Acme report of failed SSO login for three users
```

### Land

Pavo updates the support ticket, creates the Linear issue, and writes a CRM
note. Each write includes source-backed proof.

### Home

Policy candidate:

```text
For support escalations:
  preserve customer impact language when directly stated.
  avoid severity labels unless approved.
  create Linear issues only for concrete reproducible reports.
  require approval for broad escalation posts.
```

### Product Lesson

Pavo should help teams respond faster without amplifying imprecision. The
approval queue is a pressure valve between urgency and accuracy.

## Scenario H4: Legal Or Compliance-Adjacent Interview

### Situation

A manager records an internal interview about a policy incident. The record
contains employee names, timeline details, disputed facts, and possible legal
or compliance implications.

This is not a place for automation-first behavior.

### Nest

Pavo classifies the record as `restricted_compliance_adjacent`. It preserves
source media in a restricted local archive and does not recommend broad
destinations.

### Tune

Tune focuses on evidence preservation:

- transcript
- speaker labels
- timestamps
- uncertainty
- review notes

The tuned record should avoid interpretive summaries that sound like findings.

### Scout

Recommended route:

- restricted archive
- optional private review packet

Blocked:

- Slack
- CRM
- general tasks
- public project trackers
- broad knowledge base

The packet should state:

```text
This record may be compliance-adjacent. Pavo recommends restricted archive and
manual review before any downstream action.
```

### Approval

The reviewer approves restricted archive only. No action items are created.

### Land

Pavo writes the restricted archive and manifest.

### Home

Policy candidate:

```text
For compliance-adjacent records:
  preserve source.
  default to restricted archive only.
  block broad routing.
  require manual classification before tasks or summaries.
```

### Product Lesson

The right routing result can be restraint. Pavo should be proud of safe
non-action where action would be reckless.

## Scenario H5: Family School Meeting

### Situation

A parent records a school meeting about a child's support plan. The discussion
contains names, dates, commitments, sensitive educational information, and
follow-up tasks.

The record is personally important and privacy-sensitive.

### Nest

Pavo imports the recording locally and classifies it as `family_education`.
The source media is preserved in a private archive.

### Tune

Tune identifies:

- school commitments
- parent commitments
- dates
- contact names
- sensitive child information

Sensitive child information should be redacted from task titles and broad
summaries.

### Scout

Suggested destinations:

- private archive
- personal task list
- private follow-up note

Blocked destinations:

- business workspaces
- Slack
- CRM
- public project trackers

Proposed task:

```text
Follow up with school by Friday about agreed support-plan next steps.
```

The task intentionally avoids including the child's private details in the
title.

### Approval

The parent approves private archive and personal reminder. They reject any
shared destination.

### Land

Pavo writes the private archive and task. The manifest records that all shared
destinations were blocked.

### Home

Policy candidate:

```text
For family education records:
  keep private by default.
  allow personal reminders with redacted titles.
  block business destinations.
  require explicit approval for any shared route.
```

### Product Lesson

Pavo's consumer value may come from exactly the same principles as its business
value: source, accuracy, routing, approval, action, and privacy.

## Scenario H6: Internal Strategy Jam

### Situation

A leadership team records a strategy discussion. The conversation includes
product bets, people concerns, competitive observations, and undecided ideas.

The risk is premature crystallization. A generic AI might turn every idea into
a plan.

### Nest

Pavo preserves the recording and marks it as `internal_strategy`.

### Tune

Tune separates:

- decided commitments
- open questions
- speculative ideas
- sensitive people or company references

The tuned record should preserve uncertainty and disagreement.

### Scout

Suggested routes:

- restricted archive
- decision log draft for explicit decisions
- follow-up questions list

Blocked:

- broad roadmap updates
- automatic task creation for speculative ideas
- Slack summary unless heavily edited

### Approval

The team approves a decision log draft containing only explicit decisions. The
open questions are saved separately. Speculative ideas are archived but not
converted into roadmap items.

### Land

Pavo writes the decision log draft and follow-up questions. It does not create
tasks for every brainstorm item.

### Home

Policy candidate:

```text
For internal strategy records:
  distinguish decisions from speculation.
  prefer decision logs and question lists over task generation.
  block people-sensitive content from broad summaries.
```

### Product Lesson

Pavo should not turn thinking into false certainty. The product needs states
for "open question," "speculation," and "decision" because they route
differently.

# Appendix I: User And Buyer Personas

Pavo is easier to build when the team is specific about who is using it. The
product can serve many people eventually, but an early product should not blur
all users into one generic "knowledge worker." Different users have different
capture habits, different routing destinations, different approval burdens,
and different definitions of success.

This appendix defines the first persona set. It should be read as product
pressure, not market segmentation theater. Each persona exists because they
stress a different part of the Flight Path.

## Persona I1: The Founder Operator

The founder operator lives in conversations. They talk to customers,
investors, candidates, contractors, family members, vendors, and internal
collaborators. Their day produces a stream of small commitments and decisions
that rarely land cleanly in the right system.

The founder's problem is not lack of notes. The founder's problem is that
important spoken information decays before it becomes durable work.

Common inputs:

- customer calls
- investor calls
- recruiting screens
- voice memos during walks
- vendor calls
- internal strategy sessions
- personal administration calls

Common destinations:

- Drive
- Linear
- CRM
- email drafts
- personal task lists
- restricted local archive

What they need from Pavo:

- a reliable catch fence for conversations
- quick triage across business and personal contexts
- approval before anything touches external systems
- aggressive privacy boundaries for sensitive records
- a way to turn repeated approval choices into policy

Why Pavo is necessary for this user:

```text
The founder is not trying to create more documents. They are trying to keep
spoken commitments, evidence, and follow-through from escaping the operating
system of the company.
```

Completion level that matters most:

- Nest is mandatory because the founder needs source proof.
- Scout is the product unlock because the founder has many destination types.
- Land is valuable only if approval is fast.
- Home matters because repeated founder decisions should become less manual.

Failure mode:

Pavo becomes another inbox. If the founder has to review every captured record
from scratch, the product adds load. The system must learn low-risk policies
like "archive customer calls" while preserving hard approval for external
writes.

## Persona I2: The Product Manager

The product manager records user interviews, sales calls, support escalations,
and internal planning meetings. They need evidence, but they also need
restraint. Product teams are especially vulnerable to AI turning ambiguous
user pain into overconfident roadmap work.

Common inputs:

- user interviews
- customer calls
- support calls
- usability sessions
- product review meetings
- internal planning meetings

Common destinations:

- research repository
- Linear
- product briefs
- customer evidence archive
- roadmap review docs

What they need from Pavo:

- separation between evidence and interpretation
- source-backed research notes
- clear classification of explicit request, inferred task, and insight
- issue drafts that do not overstate the source
- review trails for why something became product work

Why Pavo is necessary for this user:

```text
Product evidence is valuable because it is specific. Generic AI summaries can
destroy that specificity by smoothing uncertainty into confident bullets.
```

Completion level that matters most:

- Tune is critical because speaker, wording, and uncertainty matter.
- Scout is critical because user pain should not always become a task.
- Home is powerful because the product manager's edits teach category policy.

Failure mode:

Pavo creates a large number of plausible but weak product tasks. The product
manager stops trusting the queue and returns to manual note-taking. The fix is
to make "research insight" a first-class action type, not a lesser task.

## Persona I3: The Customer Success Lead

The customer success lead handles renewals, adoption problems, escalations,
and relationship context. Their calls often include commercial risk and
product evidence at the same time.

Common inputs:

- renewal calls
- executive business reviews
- onboarding calls
- support escalations
- risk reviews
- check-in calls

Common destinations:

- CRM
- customer success platform
- Drive evidence archive
- Linear
- Slack escalation channels
- account plans

What they need from Pavo:

- account mapping
- conservative CRM notes
- customer evidence linked to product issues
- clear separation between commercial risk and product blocker
- approval gates for broad internal sharing

Why Pavo is necessary for this user:

```text
Customer calls often contain three records at once: account truth, product
evidence, and relationship nuance. Sending the same summary everywhere is
wrong.
```

Completion level that matters most:

- Scout matters because the call must split into multiple possible routes.
- Land matters because CRM and Linear writes need proof.
- Home matters because customer-success teams repeat similar routing choices.

Failure mode:

Pavo writes account notes that sound more certain than the customer was, or it
creates product issues that omit commercial context. The product must preserve
source nuance and let the account owner approve final language.

## Persona I4: The Sales Or Account Executive

The account executive needs capture without administrative drag. They want
next steps, CRM hygiene, and follow-up drafts, but they cannot afford
automation that misstates a customer's buying intent.

Common inputs:

- discovery calls
- demos
- procurement calls
- renewal calls
- negotiation calls

Common destinations:

- CRM
- follow-up email drafts
- sales notes
- task list
- restricted deal folder

What they need from Pavo:

- draft CRM notes
- follow-up commitments
- deal-risk capture
- competitor and objection tracking
- strict approval before field updates

Why Pavo is necessary for this user:

```text
Sales systems are only useful when the data is right. AI that creates noisy or
overconfident CRM updates makes the system less trusted.
```

Completion level that matters most:

- Tune matters because names, dates, pricing terms, and commitments need
  accuracy.
- Land matters because CRM writes are operational truth.
- Approval must be fast enough that sales users actually use it.

Failure mode:

The product markets "automatic CRM updates" and wins demos but loses trust in
real use. Pavo should instead market approved CRM hygiene: faster than manual,
safer than blind automation.

## Persona I5: The Recruiter Or Hiring Manager

Recruiting records are high value and high sensitivity. They contain candidate
facts, interviewer judgments, compensation, protected or sensitive
information, and sometimes post-call private commentary.

Common inputs:

- recruiter screens
- hiring manager interviews
- debrief voice notes
- reference calls
- compensation discussions

Common destinations:

- ATS
- restricted hiring folder
- private interviewer notes
- follow-up tasks

What they need from Pavo:

- separation of candidate-provided facts from evaluation
- compensation-sensitive handling
- ATS note drafts
- approval before hiring-system writes
- default block on broad sharing

Why Pavo is necessary for this user:

```text
Recruiting records are not casual meeting notes. The destination, wording, and
permission model matter as much as the transcript.
```

Completion level that matters most:

- Tune matters because speaker attribution changes meaning.
- Scout matters because not all content belongs in the ATS.
- Land should be conservative and draft-first.

Failure mode:

Pavo routes evaluation notes into the wrong place or attributes interviewer
judgment to the candidate. The product must handle recruiting as a restricted
class from the start if it claims to support it.

## Persona I6: The Field Operator

The field operator captures messy, time-sensitive records outside a clean
meeting environment. Audio may be noisy. The recording may be a one-minute
memo during an inspection. The value is often in practical follow-through.

Common inputs:

- inspection memos
- event setup notes
- maintenance observations
- vendor arrival updates
- safety concerns

Common destinations:

- task system
- safety log
- event folder
- team update
- local archive

What they need from Pavo:

- useful partial transcription
- task extraction with confidence
- safety escalation handling
- ability to preserve uncertain spans as notes
- mobile-friendly approval

Why Pavo is necessary for this user:

```text
Field records are often too messy for polished meeting-note tools, but they
contain exactly the kind of operational facts that should not be forgotten.
```

Completion level that matters most:

- Nest matters because even imperfect records are evidence.
- Scout matters because partial confidence should route differently.
- Land matters when safety or operations teams need proof of follow-up.

Failure mode:

Pavo treats low-quality audio as either useless or fully reliable. The right
middle is partial value with explicit uncertainty.

## Persona I7: The Personal Chief-Of-Staff User

This user records life administration: health calls, school meetings,
insurance calls, vendor calls, elder-care coordination, financial admin, and
personal reminders. The value is significant, but the privacy bar is higher
than many business workflows.

Common inputs:

- health administration calls
- school meetings
- home vendor calls
- finance or insurance calls
- personal voice notes

Common destinations:

- private archive
- personal task list
- private notes
- family folder

What they need from Pavo:

- private by default
- redacted task titles
- no business-tool routing unless explicitly approved
- ability to find source evidence later
- clean follow-up reminders

Why Pavo is necessary for this user:

```text
Personal administration often depends on what someone said on a call. The
record needs to be preserved, but the wrong route can be more harmful than no
route.
```

Completion level that matters most:

- Nest is mandatory.
- Tune needs sensitive entity handling.
- Scout should recommend private outcomes.
- Land should avoid public or work systems.

Failure mode:

The product assumes productivity means external action. For this persona,
success is often private preservation plus one clean reminder.

## Persona I8: The Team Administrator

The team administrator cares less about any single recording and more about
consistent routing behavior. They want to know which destinations are allowed,
which records require review, what retention means, and where proof lives.

Common inputs:

- all team recordings
- policy exceptions
- failed writes
- approval history
- destination manifests

Common destinations:

- admin dashboard
- audit archive
- policy registry
- compliance exports

What they need from Pavo:

- inspectable policy
- role-based approval later
- retention controls
- destination inventory
- audit manifests
- ability to disable risky routes

Why Pavo is necessary for this user:

```text
Once Pavo moves from personal tool to team workflow, routing becomes
governance. The administrator needs proof that the product is not silently
writing sensitive records into the wrong systems.
```

Completion level that matters most:

- Home matters because policies must be visible.
- Land matters because manifests prove action.
- Scout matters because blocked routes are governance evidence.

Failure mode:

Pavo has clever routing but no administrative control. A team cannot adopt it
without knowing where records go and why.

## Persona Prioritization

The recommended early ordering is:

1. Founder operator
2. Product manager
3. Customer success lead
4. Personal chief-of-staff user
5. Field operator
6. Sales/account executive
7. Recruiter/hiring manager
8. Team administrator

This ordering is not purely market size. It is a build sequence. The founder
operator stresses cross-context routing. The product manager stresses evidence
versus action. Customer success stresses multi-destination business routing.
Personal chief-of-staff stresses privacy. Field work stresses imperfect audio.
Sales and recruiting add higher-stakes destination rules. Team administration
adds governance once repeated usage exists.

## Persona-Invariant Product Promises

Across personas, the product should keep the same promises:

- source media remains the record
- summaries are derived artifacts
- uncertainty is product data
- routes are recommendations until approved
- private and archive-only are successful outcomes
- destination writes produce proof
- user edits and rejections teach policy
- policy is inspectable

If a feature violates those promises for one persona, it is probably not a
Pavo feature. It may be a useful automation, but it does not belong inside the
approval-gated routing model without redesign.

# Appendix J: Trust, Safety, Consent, Retention, And Redaction

Pavo's trust model cannot be pasted on after the product works. It is the
product. A system that captures spoken records, extracts meaning, recommends
routes, and writes into other tools has to know when to stop.

This appendix defines the trust vocabulary Pavo should use in product docs,
implementation, and marketing.

## Consent States

Consent is not one state. Pavo should represent it explicitly.

Suggested states:

```text
unknown
not_required_by_user_context
capturer_confirmed
meeting_platform_disclosed
all_parties_confirmed
restricted_use_only
do_not_process
```

The product should not pretend to resolve legal consent for every
jurisdiction. It can, however, make the user's capture and processing state
explicit.

Example:

```json
{
  "consent_state": "capturer_confirmed",
  "consent_note": "User confirmed they had permission to record this call.",
  "processing_limit": "routing_allowed_after_review"
}
```

Product implication:

- `unknown` should allow private Nest but may block external Land.
- `do_not_process` should preserve only the minimum permitted record or delete
  according to policy.
- `restricted_use_only` should block broad summaries and external destinations.

Marketing implication:

Pavo should not say "we handle consent" in a broad legal sense. It should say
the product records consent state and can enforce routing restrictions based
on that state.

## Privacy Classes

Pavo needs a small, understandable privacy taxonomy.

Suggested classes:

```text
public_or_low_sensitivity
business_internal
business_sensitive
customer_sensitive
personal_private
personal_health
financial_private
employment_sensitive
recruiting_sensitive
compliance_adjacent
unknown_sensitive
```

The class should affect default routing. It should not merely label the
record.

Example defaults:

| Privacy Class | Archive | Tasks | CRM | Slack | Email Draft |
| --- | --- | --- | --- | --- | --- |
| business_internal | allowed | approval | approval | approval | approval |
| customer_sensitive | allowed | approval | approval | restricted | approval |
| personal_health | private only | approval, redacted | blocked | blocked | restricted |
| recruiting_sensitive | restricted | approval | blocked | blocked | restricted |
| compliance_adjacent | restricted | blocked by default | blocked | blocked | blocked |

The key product idea is that routing policy starts before the user reviews the
packet. The queue should already be safer because Pavo recognized the class.

## Retention States

Retention should be separate from routing. A record can be archived privately
but never routed. A record can be routed and then retained only for a short
time. A record can be deleted after a destination write if policy requires it.

Suggested retention states:

```text
retain_source
retain_source_restricted
retain_derived_only
retain_manifest_only
delete_after_review
delete_after_landing
legal_hold
user_deleted
```

Product implications:

- A destination write manifest may outlive the source media.
- Deleting source media should not erase the fact that a write occurred.
- Reprocessing should be impossible after source deletion unless derived
  artifacts remain.
- The UI should make destructive retention choices explicit.

Example:

```json
{
  "retention": {
    "source": "retain_source_restricted",
    "transcript": "retain_derived_only",
    "routing_packet": "retain_manifest_only",
    "review_after_days": 365
  }
}
```

Gotcha:

```text
Retention is not just storage cleanup. It changes what Pavo can prove later.
```

## Redaction Modes

Redaction needs more nuance than "remove sensitive data." Pavo should know
what is being redacted and for which destination.

Suggested modes:

```text
mask_identifier
remove_excerpt
generalize_fact
link_private_source
omit_from_destination
replace_with_placeholder
```

Examples:

- `mask_identifier`: replace claim number with `claim ending 4821`
- `remove_excerpt`: omit transcript quote from Slack draft
- `generalize_fact`: say "compensation expectations discussed" rather than
  listing the number
- `link_private_source`: include evidence link without raw text
- `omit_from_destination`: keep private note out of CRM
- `replace_with_placeholder`: draft email with `[DATE]` or `[AMOUNT]`

Redaction should happen before Land. Redaction after external write is failure
recovery, not product design.

## Approval Risk Levels

Approval should not feel the same for every action. Pavo can use risk levels
to decide review density and UI friction.

Suggested levels:

```text
low
medium
high
blocked
```

Examples:

- Low: local archive of non-sensitive record
- Medium: Linear issue draft from reviewed customer evidence
- High: CRM write involving renewal risk
- Blocked: Slack post with personal health information

The UI should not bury high-risk actions among low-risk archive tasks. A good
approval queue makes risk visible and reviewable.

## Sensitive Routing Policies

Pavo should ship with conservative defaults. Users can loosen them later, but
the product should not begin by spraying summaries into all connected tools.

Default policy examples:

```text
If privacy_class is personal_health:
  block Slack, CRM, shared Linear, and public Drive.
  allow private archive.
  allow redacted personal task after approval.
```

```text
If privacy_class is recruiting_sensitive:
  block Slack.
  allow restricted archive.
  allow ATS draft after approval.
  separate candidate facts from interviewer evaluation.
```

```text
If privacy_class is customer_sensitive:
  allow restricted archive.
  require approval for CRM and Linear.
  block broad Slack when commercial risk is present.
```

```text
If consent_state is unknown:
  allow Nest.
  allow Tune only under user-confirmed processing policy.
  block external Land until consent state is resolved or policy grants a
  restricted exception.
```

## Audit Trail Requirements

Every important product action should leave evidence:

- capture event
- transcript generation
- review correction
- routing packet creation
- approval decision
- redaction operation
- destination write
- failed write
- policy promotion
- deletion or retention change

The audit trail does not need to be heavyweight at first. It does need to be
append-only enough that the product can answer "what happened?"

Basic event shape:

```json
{
  "event_id": "evt_001",
  "recording_id": "rec_001",
  "kind": "approval_decision",
  "actor": "user",
  "created_at": "2026-06-11T16:12:00Z",
  "input_refs": ["pkt_001", "act_linear_001"],
  "output_refs": ["approval_001"]
}
```

The product should be able to reconstruct the path:

```text
recording -> evidence -> packet -> approval -> redaction -> write -> manifest
```

## User-Facing Trust Language

Trust features should be named plainly.

Use:

- source recording
- evidence
- reviewed
- inferred
- approval required
- blocked by policy
- redacted
- private archive
- destination proof

Avoid:

- guaranteed compliance
- perfect transcript
- safe by AI
- automatic truth
- zero review

The product should earn trust by showing its work.

## Trust Acceptance Criteria

Pavo is not ready for broad use until:

- sensitive classes change routing defaults
- unapproved external writes are blocked
- redaction happens before destination preview
- destination manifests are durable
- source and derived artifacts are distinguishable
- consent state can be represented
- retention choices are explicit
- user can see why a route was blocked

These are not enterprise polish. They are the minimum product structure for
approval-gated routing.

# Appendix K: Go-To-Market And Product Narrative Field Guide

Pavo needs a sharp story because the obvious comparison set is crowded.
Everyone understands meeting notes. Fewer people immediately understand
approval-gated routing for spoken records. The marketing has to bridge that
gap without making the product sound abstract.

## The Category Wedge

The wedge should be:

```text
Your recorded conversations are becoming operational source material. Pavo
gives them a safe path into work.
```

This is better than "AI meeting notes" because it names the shift:

- capture is everywhere
- recordings are evidence
- work happens in other systems
- AI recommendations need approval
- routing should learn

The wedge should not be:

```text
The best meeting summarizer.
```

That market is noisy and forces Pavo into feature comparison on transcript
quality, note templates, and meeting bots. Pavo may need good transcripts, but
the differentiated product is the control path after capture.

## Ideal First Market

The first market should have:

- frequent recorded conversations
- high cost of lost follow-up
- multiple destination systems
- sensitivity that makes blind automation risky
- users willing to approve AI recommendations
- value from source-backed evidence

Strong candidates:

- founder-led B2B teams
- product teams doing customer discovery
- customer success teams with renewal risk
- professional services teams with client calls
- operators handling business and personal administration

Weak initial markets:

- casual personal journaling
- generic meeting summaries for low-stakes teams
- fully automated sales engagement
- compliance-heavy enterprise as first customer

The weak markets may become useful later. They are not the best first wedge
because they either underuse the routing model or require too much governance
before product value is proven.

## The First Demo Story

The first demo should show one recording splitting into controlled outcomes.

Demo outline:

1. Import a real customer call.
2. Show source media, hash, and metadata.
3. Show transcript with one uncertainty marker.
4. Show Scout recommending three routes:
   - archive in Drive
   - create Linear investigation issue
   - draft CRM note
5. Show Slack blocked due to commercial risk.
6. Approve Drive.
7. Edit Linear issue title.
8. Redact CRM note.
9. Land approved actions.
10. Show destination manifests.
11. Show Home proposing a scoped policy.

The key moment is not the generated summary. The key moment is the user's
realization that Pavo can split one conversation into different destinations
with different approval rules.

## Website Information Architecture

Recommended home page sections:

1. Hero: "Turn conversations into approved work."
2. Problem: recordings and meeting notes still leave routing undone.
3. Flight Path: Nest, Tune, Scout, Land, Home.
4. Scenario: customer call to archive, issue, CRM note, blocked Slack.
5. Trust: source-backed, approval-gated, destination proof.
6. Integrations: Plaud/local first, then Drive/Linear/email/CRM/Slack.
7. CTA: start with one recording.

Avoid a hero that only shows abstract AI language. The first viewport should
signal the actual product: a recorded conversation becoming an approval queue.

## Sales Narrative

The sales narrative should follow a simple sequence:

```text
You are already capturing conversations.
The valuable part is not the file; it is what should happen next.
Today that next step is manual, inconsistent, or too risky to automate.
Pavo creates a source-backed routing packet.
You approve what lands.
Pavo records proof and learns your policy.
```

Discovery questions:

- Where do important conversations get recorded today?
- What usually happens after the recording?
- Which follow-ups get lost?
- Which systems should the information land in?
- Which destinations would be risky without approval?
- Who needs to approve customer, recruiting, or personal records?
- What would you trust Pavo to do automatically after repeated review?

Qualification signals:

- user has multiple capture sources
- user has multiple destination systems
- user already manually copies notes into tools
- user has sensitive routing concerns
- user wants source evidence, not only summaries

Disqualification signals:

- user only wants a cheaper transcript
- user wants fully automatic outbound communication immediately
- user refuses any review step for high-risk writes
- user has no destination systems or workflow pain

## Competitive Framing

Pavo should respect adjacent tools. The product does not need to pretend Plaud,
Zoom, Otter, Fireflies, Granola, or CRMs are bad. They each solve a layer.

Framing:

| Adjacent Layer | What It Does Well | Pavo's Position |
| --- | --- | --- |
| Recording devices | Capture clean audio | Pavo governs what happens after capture. |
| Meeting bots | Join meetings and generate notes | Pavo turns records into approved routes. |
| Transcription APIs | Convert audio to text | Pavo preserves evidence and approval state. |
| CRM call intelligence | Sales workflows | Pavo is source-agnostic and approval-first. |
| Task systems | Manage work | Pavo decides whether spoken evidence should become work. |
| Automation tools | Connect apps | Pavo adds source, sensitivity, approval, and proof. |

The line to repeat:

```text
Pavo does not compete with capture. It makes capture operationally safe.
```

## Packaging Hypothesis

Early packaging should follow value and trust maturity.

Personal or founder plan:

- local import
- Plaud import
- local archive
- routing packets
- manual approval
- limited destination adapters

Team plan:

- shared archive
- Drive/Linear/CRM adapters
- approval queue
- policy candidates
- destination manifests
- role-aware review later

Governed plan:

- retention policy
- admin dashboard
- consent state tracking
- advanced redaction
- audit exports
- destination restrictions

The product should not sell governed features before it can prove the audit
trail. It is better to be precise than to create enterprise promises too early.

## Messaging By Persona

Founder operator:

```text
Stop losing what was decided in calls. Pavo turns captured conversations into
approved follow-through.
```

Product manager:

```text
Keep user evidence tied to the source. Route insights and tasks without
turning ambiguity into roadmap noise.
```

Customer success:

```text
Move renewal risks and product blockers into the right systems with account
context, approval, and proof.
```

Sales:

```text
Draft CRM notes and follow-ups from calls without trusting blind automation
with commercial truth.
```

Recruiting:

```text
Prepare hiring notes from interviews while keeping sensitive evaluation
content controlled.
```

Personal administration:

```text
Preserve important calls privately and turn only the approved follow-ups into
reminders.
```

## Launch Sequence

Recommended launch sequence:

1. Publish the product book spine and Flight Path.
2. Demo local/Plaud record to routing packet.
3. Add local archive Land.
4. Add Drive archive Land.
5. Add Linear approved issue Land.
6. Publish scenario library.
7. Add email draft adapter.
8. Add CRM note draft/write.
9. Add policy memory.
10. Add team approval concepts.

The sequence should show increasing trust. Pavo should not launch by promising
every integration. It should launch by proving the model with one or two
high-quality routes.

## Marketing Gotchas

Gotcha: "Approved work" sounds slower than automation.

Response:

```text
Approval is not the opposite of automation. Approval is how automation becomes
safe enough to use where mistakes matter.
```

Gotcha: "Routing" sounds technical.

Response:

Use concrete examples:

```text
This customer call became a Drive archive, a Linear investigation, and a CRM
note. Slack was blocked. You approved each step.
```

Gotcha: The bird terms could confuse users.

Response:

Always pair bird vocabulary with plain verbs:

```text
Nest: capture. Tune: correct. Scout: recommend. Land: act. Home: learn.
```

Gotcha: Buyers may ask whether Pavo is a system of record.

Response:

```text
Pavo is the control plane for spoken records. It preserves source evidence and
routes approved outputs into systems of record.
```

Gotcha: Teams may fear another inbox.

Response:

Show policy learning and batch approval. The product must demonstrate that the
queue gets smaller and smarter over time.

# Appendix L: Metrics, Roadmap, And Operating Cadence

Pavo should measure progress by whether spoken records become trusted,
approved work. Generic activity metrics can mislead the team. "Tasks created"
is not automatically good. "Summaries generated" is not enough. "Automation
rate" can be dangerous if it hides approval quality.

This appendix defines product metrics and roadmap discipline.

## North Star

Recommended north star:

```text
Approved source-backed outcomes per active user.
```

An approved source-backed outcome is a landed or intentionally resolved result
from a recording:

- private archive
- Drive evidence bundle
- approved Linear issue
- approved CRM note
- approved email draft
- approved personal task
- approved restricted archive
- explicit reject/private/no-action decision

The inclusion of reject/private/no-action is important. Pavo should not
optimize only for external writes. Correct restraint is a product success.

## Supporting Metrics

Capture metrics:

- records nested per week
- capture source mix
- records with durable media hash
- records missing source proof

Tune metrics:

- transcript success rate
- records with reviewed corrections
- speaker uncertainty rate
- redaction candidate rate

Scout metrics:

- packets generated
- packet validation success
- suggested destinations per packet
- blocked destinations per packet
- actions per packet

Approval metrics:

- approval rate by action type
- edit rate by action type
- rejection rate by destination
- defer rate
- time to decision
- batch approval usage

Land metrics:

- successful writes by destination
- failed writes by destination
- retry success
- duplicate prevention events
- manifest completeness

Home metrics:

- policy candidates generated
- policy candidates promoted
- policy candidates rejected
- policy-triggered route changes
- policy-caused approval reduction

Trust metrics:

- unapproved write attempts blocked
- sensitive route blocks
- redactions before Land
- records with explicit consent state
- retention changes

## Bad Metrics

The team should be suspicious of:

- raw number of summaries generated
- raw number of tasks created
- percentage of actions automated without approval
- number of integrations connected
- total transcript length processed
- time spent in app without outcome quality

These can be useful diagnostic signals, but they are not product success.

Example:

```text
If Pavo doubles tasks created but half are rejected as noisy, the product got
worse.
```

## Roadmap Principle

The roadmap should follow trust maturity:

```text
preserve -> understand -> recommend -> approve -> write -> learn -> govern
```

Do not reverse this sequence for demo appeal. A Slack posting demo before
source evidence, redaction, and approval are mature would teach the wrong
product behavior.

## Roadmap Phase 1: Source-Backed Local Loop

Goal:

```text
One local or Plaud recording becomes a source-backed record with transcript
evidence and review output.
```

Build:

- stable recording ledger
- local import/Plaud import
- media hash
- transcript attachment
- review artifact
- source-backed render

Do not build yet:

- broad integrations
- team policy
- complex admin roles
- automatic external writes

Exit criteria:

- user can import a recording
- user can inspect source and transcript
- user can save review corrections
- tests prove source preservation

## Roadmap Phase 2: Scout Packet

Goal:

```text
One tuned record becomes a durable routing packet with suggested and blocked
destinations.
```

Build:

- packet schema
- packet validator
- source refs
- sensitivity flags
- action classification
- human-readable packet render

Do not build yet:

- destination writes
- policy auto-promotion
- team approvals

Exit criteria:

- packet validates without model call
- packet can be rendered
- actions are separately reviewable
- blocked destinations appear

## Roadmap Phase 3: Approval Queue

Goal:

```text
The user can approve, edit, reject, redact, or defer packet actions.
```

Build:

- approval decision object
- CLI or simple UI queue
- edited payload storage
- rejection reasons
- redaction requirement states

Do not build yet:

- broad automation
- complex multi-user approval
- Slack posting

Exit criteria:

- unapproved actions cannot Land
- edited actions retain source refs
- rejected actions become learning signals

## Roadmap Phase 4: First Land Adapters

Goal:

```text
Approved actions land in local archive, Drive, and Linear with manifests.
```

Build:

- local archive adapter
- Drive evidence bundle adapter
- Linear approved issue adapter
- write manifests
- idempotency keys
- failure state

Do not build yet:

- send email
- automatic CRM field mutation
- Slack broad posting

Exit criteria:

- adapter consumes approved packet action
- write manifest is saved
- retries do not duplicate writes
- failures are visible

## Roadmap Phase 5: Draft And Sensitive Adapters

Goal:

```text
Pavo supports draft-first workflows for email and CRM while preserving
approval and redaction.
```

Build:

- email draft adapter
- CRM note draft/write adapter
- recipient/account confirmation
- redaction preview
- conservative payload templates

Do not build yet:

- automatic send
- automatic deal-stage changes
- broad Slack by default

Exit criteria:

- email output is clearly draft
- CRM account identity is required
- sensitive fields are redacted or blocked
- manifests distinguish draft from sent/written

## Roadmap Phase 6: Home And Policy Memory

Goal:

```text
Pavo learns from approvals, edits, rejections, and redactions without silently
expanding permissions.
```

Build:

- policy candidate object
- policy review surface
- scoped promotion
- policy effect preview
- negative signal handling

Do not build yet:

- opaque autonomous policy changes
- organization-wide rules without admin controls

Exit criteria:

- user can see proposed policy
- policy can be accepted or rejected
- promoted policy affects future Scout output
- policy cannot grant broader write permission than approved

## Roadmap Phase 7: Team Governance

Goal:

```text
Teams can govern capture, routing, approval, retention, and destination access.
```

Build:

- admin policy view
- role-aware approvals
- retention controls
- audit export
- destination restrictions
- consent state reporting

Exit criteria:

- admin can answer where records go
- sensitive classes have enforceable defaults
- audit trail covers capture through Land
- retention changes are recorded

## Operating Cadence

Every product review should include:

1. One real or fixture recording.
2. The current Flight Path stage.
3. What evidence exists.
4. What routing packet says.
5. What approval decision is needed.
6. What Land proof exists.
7. What Home learned.
8. What went wrong.

The team should maintain a scenario ledger. Each scenario should have:

- source record
- expected packet
- expected approval choices
- expected destination manifests
- gotchas
- regression tests

If a scenario is important enough to market, it is important enough to test.

## Definition Of Done For Pavo As A Product

Pavo becomes a complete product when a user can repeatedly:

1. Capture or import a spoken record.
2. Preserve the source.
3. Improve and review the record.
4. See where the information should and should not go.
5. Approve, edit, reject, redact, or defer each action.
6. Land approved actions with proof.
7. Teach Pavo scoped policy from those decisions.
8. Trust that sensitive records will not route broadly by accident.

That is the product. Everything else is implementation detail, integration
surface, or packaging.

# Appendix M: Flight Path Glossary And Status Vocabulary

Pavo needs a vocabulary that works in three places at once:

1. A user should understand it in the product.
2. A builder should be able to encode it in data structures.
3. A future agent should be able to follow it without rereading the whole
   product book.

The vocabulary should be plain enough for users and precise enough for
implementation. Bird language is useful only when it carries real product
meaning. Every bird term should have a direct operational translation.

## Core Product Sentence

Canonical sentence:

```text
Pavo turns spoken records into approved, source-backed work.
```

Do not replace this with "Pavo records meetings" or "Pavo creates notes." The
recording and notes are parts of the system. They are not the point of the
product.

Expanded sentence:

```text
Pavo catches spoken records, preserves the source, tunes the record into
trustworthy evidence, scouts where the information should go, lands only the
approved actions, and learns scoped routing policy from review.
```

Use this expanded form when introducing Pavo to builders or reviewers who need
to understand why the product has more stages than a note-taking app.

## Flight Path Terms

### Flight Path

The end-to-end lifecycle of a spoken record in Pavo:

```text
Nest -> Tune -> Scout -> Land -> Home
```

Plain meaning:

```text
capture -> correct -> recommend -> act -> learn
```

Product rule:

```text
No stage should erase the evidence produced by earlier stages.
```

The Flight Path is not a marketing flourish. It is the product architecture.
When a feature does not clearly improve one stage or the transition between
stages, it should be treated with skepticism.

### Nest

Nest means capture and preserve the source record.

User-facing explanation:

```text
Pavo keeps the original recording and enough metadata to prove where it came
from.
```

Implementation meaning:

- create or update a recording record
- store source system
- store source id when available
- store local media path when available
- hash local media
- record capture/import time
- record source-unavailable state when the media cannot be kept

Common statuses:

```text
intake_pending
nested
source_unavailable
nest_failed
```

Success state:

```text
The record can be found again, and Pavo can explain whether it has durable
source media.
```

Failure examples:

- transcript exists but source media path is missing
- media exists but was not hashed
- source system is unknown
- signed URL is treated as durable evidence

### Tune

Tune means make the record accurate and trustworthy enough for routing.

User-facing explanation:

```text
Pavo improves the transcript, speaker evidence, uncertainty markers, and
review notes without pretending the record is perfect.
```

Implementation meaning:

- attach transcript evidence
- attach speaker evidence
- preserve confidence and uncertainty
- record engine and command metadata
- record review corrections
- mark redaction candidates
- keep diagnostic artifacts separate from accepted artifacts

Common statuses:

```text
tuning
tuned_unreviewed
tuned_reviewed
tune_failed
needs_review
superseded
```

Success state:

```text
Pavo can tell the user what it knows, what it inferred, what was reviewed, and
what remains uncertain.
```

Failure examples:

- speaker labels appear as facts when they were inferred
- review overwrites generated evidence without a trace
- low-confidence transcript spans become confident tasks
- redaction candidates are found only after routing

### Scout

Scout means recommend where the information should go and what should happen.

User-facing explanation:

```text
Pavo proposes routes and actions, shows why it recommends them, and also shows
where it chose not to route.
```

Implementation meaning:

- create routing packet
- classify entities and sensitivity
- suggest destinations
- block destinations by policy
- propose actions
- attach source references
- state approval requirements
- produce learning signals

Common statuses:

```text
scout_pending
scouted
packet_ready
packet_invalid
route_blocked
needs_policy_review
```

Success state:

```text
The user can review a durable packet that separates suggested destinations,
blocked destinations, proposed actions, evidence, sensitivity, and approval
requirements.
```

Failure examples:

- recommendations live only in an AI chat response
- one summary is sprayed into multiple destinations
- blocked destinations are invisible
- confidence is shown but permission is not

### Land

Land means execute approved actions and record proof.

User-facing explanation:

```text
Pavo writes only the approved actions into destination systems and records
what happened.
```

Implementation meaning:

- consume approved packet action
- validate destination payload
- apply redaction before write
- write to local or external destination
- record write manifest
- record destination id or failure
- support idempotent retry

Common statuses:

```text
approval_pending
approved
landing
landed
land_failed
partial_land
skipped
```

Success state:

```text
Pavo can answer who approved the action, what was written, where it went, and
what proof the destination returned.
```

Failure examples:

- adapter writes from transcript without packet approval
- retry creates duplicate issues
- CRM write goes to wrong account
- manifest is missing after destination write

### Home

Home means learn scoped routing policy from review.

User-facing explanation:

```text
Pavo learns from approvals, edits, rejections, redactions, and private
decisions so similar records become easier to route next time.
```

Implementation meaning:

- collect review signals
- create policy candidates
- show candidate scope
- allow promotion or rejection
- apply promoted policy to future Scout output
- avoid silently widening write permission

Common statuses:

```text
policy_candidate
policy_review_pending
policy_promoted
policy_rejected
policy_disabled
policy_conflict
```

Success state:

```text
Pavo gets faster without becoming less inspectable.
```

Failure examples:

- one approval becomes a broad automation rule
- rejection is not captured as a learning signal
- policy silently grants external write permission
- user cannot see why future routing changed

## Record Lifecycle Statuses

The product can show a friendly stage while storing a precise status.

| Machine Status | Stage | User Label | Meaning |
| --- | --- | --- | --- |
| `intake_pending` | Nest | Waiting for source | Pavo knows a record exists but has not preserved it. |
| `nested` | Nest | Source preserved | Source media or source-unavailable proof exists. |
| `source_unavailable` | Nest | Source unavailable | Pavo could not preserve media but recorded why. |
| `tuning` | Tune | Tuning record | Transcript or evidence processing is running. |
| `tuned_unreviewed` | Tune | Needs review | Derived evidence exists but has not been reviewed. |
| `tuned_reviewed` | Tune | Reviewed record | Human or policy review confirmed key evidence. |
| `scout_pending` | Scout | Ready to route | Record can be evaluated for routes. |
| `packet_ready` | Scout | Routes proposed | Routing packet is ready for review. |
| `packet_invalid` | Scout | Routing error | Packet failed validation. |
| `approval_pending` | Land | Waiting for approval | At least one action needs decision. |
| `approved` | Land | Approved | At least one action is approved and ready to land. |
| `landing` | Land | Writing approved action | Destination adapter is executing. |
| `landed` | Land | Landed | Approved action has write proof. |
| `partial_land` | Land | Partially landed | Some approved actions succeeded and others failed. |
| `private` | Land | Private | User chose private/archive-only handling. |
| `rejected` | Land | No action | User rejected proposed actions. |
| `policy_candidate` | Home | Learning proposed | Review generated a possible future rule. |
| `policy_promoted` | Home | Learned rule | User promoted a scoped policy. |

The UI does not need to show every machine status everywhere. It should,
however, preserve enough fidelity that users understand whether Pavo is
waiting for source, waiting for review, waiting for approval, writing, or
learning.

## Evidence Types

Evidence is any durable artifact that helps explain a record, recommendation,
approval decision, or destination write.

Suggested evidence types:

```text
source_media
source_metadata
media_hash
transcript
speaker_diarization
speaker_mapping
overlap_analysis
separation_diagnostic
accepted_stem_transcript
review_note
correction
summary
redaction_candidate
redacted_payload
routing_packet
approval_decision
destination_manifest
policy_candidate
retention_event
```

Important distinction:

```text
Evidence can be derived without being authoritative.
```

A transcript is evidence. It is not the source of truth. A summary is
evidence. It is not the source of truth. A review note can be stronger
evidence than a model output if it is attached to the relevant source span.

## Speaker Confidence Vocabulary

Pavo should avoid pretending it knows speaker identity when it does not.

Suggested speaker states:

```text
unknown
diarized
inferred
mapped
reviewed
conflicted
```

Definitions:

- `unknown`: Pavo does not know who spoke.
- `diarized`: Pavo separated speakers but did not identify them.
- `inferred`: Pavo guessed identity from context.
- `mapped`: Pavo matched speaker to a known person or role using available
  evidence.
- `reviewed`: a human confirmed the mapping.
- `conflicted`: evidence disagrees or the mapping is unsafe.

Product rule:

```text
Speaker names should not appear as plain facts until they are mapped or
reviewed. Inferred names should be visibly qualified.
```

## Action Types

Pavo should not treat all proposed actions as tasks.

Suggested action types:

```text
archive_source
create_task
create_issue
draft_email
draft_crm_note
write_crm_note
create_research_insight
create_decision_log
create_followup_question
create_safety_note
mark_private
reject_all
defer_review
```

Why this matters:

- A research insight is not a build task.
- A draft email is not a sent email.
- A CRM note is different from a CRM field mutation.
- A decision log is different from a brainstorm note.
- A private/archive-only result is a successful action.

The action type should shape approval requirements, UI language, destination
adapter behavior, and metrics.

## Approval Decisions

Approval is not binary.

Suggested decisions:

```text
approve
approve_with_edits
reject
redact_first
defer
mark_private
archive_only
needs_more_evidence
escalate_review
```

Definitions:

- `approve`: action can Land as proposed.
- `approve_with_edits`: edited payload can Land.
- `reject`: action should not Land.
- `redact_first`: action may be appropriate after sensitive content changes.
- `defer`: no decision yet.
- `mark_private`: record should remain private.
- `archive_only`: preserve evidence but do not create external work.
- `needs_more_evidence`: Tune or review should improve before routing.
- `escalate_review`: another person or role should decide.

Product rule:

```text
Every approval decision should be durable enough for Home to learn from it.
```

## Sensitivity Classes

Sensitivity class should shape default routes.

Suggested classes:

```text
public_or_low_sensitivity
business_internal
business_sensitive
customer_sensitive
personal_private
personal_health
financial_private
employment_sensitive
recruiting_sensitive
compliance_adjacent
unknown_sensitive
```

Default stance:

```text
When unsure, classify toward review and restricted routing.
```

The sensitivity class should appear in the routing packet and approval queue.
It should not be hidden in logs.

## Destination States

Destinations need their own state vocabulary because a route can be suggested,
blocked, approved, written, failed, or intentionally skipped.

Suggested destination states:

```text
not_considered
suggested
blocked_by_policy
requires_approval
approved
redaction_required
ready_to_land
landing
succeeded
failed
partial
skipped
manual_copy_required
```

Examples:

- Slack may be `blocked_by_policy`.
- CRM may be `requires_approval`.
- Email may be `manual_copy_required` if the first adapter only creates local
  drafts.
- Drive may be `succeeded` with a folder id.
- Linear may be `failed` because the team id was missing.

The UI should show these states as route outcomes, not just errors.

## Retention Vocabulary

Retention describes what Pavo keeps after review or Land.

Suggested states:

```text
retain_source
retain_source_restricted
retain_derived_only
retain_manifest_only
delete_after_review
delete_after_landing
legal_hold
user_deleted
```

Product rule:

```text
Retention choices change what Pavo can prove later, so they should be
explicit and auditable.
```

## Policy Vocabulary

Policy is how Home turns repeated decisions into future behavior.

Suggested policy terms:

- policy candidate
- promoted policy
- rejected policy
- disabled policy
- policy scope
- policy basis
- policy exception
- policy conflict
- permission grant
- recommendation rule

Important distinction:

```text
A recommendation rule is not a permission grant.
```

Pavo may learn that customer calls should usually suggest Drive archive. That
does not automatically mean Pavo may write CRM notes without approval.

## Terms To Avoid

Avoid language that undermines the product model:

- autopilot for external writes
- fully automatic CRM
- perfect transcript
- AI truth
- no review needed
- one-click compliance
- meeting bot as the primary category
- task extractor as the primary category

Preferred replacements:

| Avoid | Use |
| --- | --- |
| automatic CRM | approved CRM note |
| perfect notes | source-backed record |
| AI decides | Pavo recommends |
| autopilot | policy-assisted routing |
| meeting bot | spoken-record control layer |
| action extraction | approval-gated routing |

## Canonical Short Glossary

| Term | Short Definition |
| --- | --- |
| Spoken record | A meeting, call, voice memo, or field recording that may contain operational evidence. |
| Source media | The original audio or video artifact, treated as the record of highest authority. |
| Recording record | Ledger entry that identifies the source, media, metadata, and Flight Path state. |
| Evidence record | Durable artifact derived from or attached to the source record. |
| Routing packet | Durable Scout output describing suggested routes, blocked routes, actions, evidence, sensitivity, and approvals. |
| Proposed action | A separately reviewable action that may become a destination write or private resolution. |
| Approval decision | User or policy decision about a proposed action. |
| Destination adapter | Code path that executes an approved action into a destination system. |
| Destination manifest | Proof of what a destination adapter wrote, skipped, or failed to write. |
| Redaction | Pre-Land transformation that removes, masks, generalizes, or withholds sensitive content. |
| Blocked route | A destination Pavo intentionally does not recommend because policy or sensitivity says no. |
| Policy candidate | Proposed Home learning derived from approvals, edits, rejections, or redactions. |
| Policy memory | Inspectable set of promoted routing preferences and constraints. |
| Approved outcome | A landed, private, rejected, archived, or deferred result that reflects user or policy decision. |

This glossary should remain synchronized with `docs/product.md`, the README,
and the Codex-facing Pavo skill. If the vocabulary changes here, those shorter
docs should either change too or explicitly point back to this book as the
canonical source.

# Appendix N: UI Product Specs For Approval-Gated Routing

Pavo's first UI should not be a decorative meeting-notes page. It should be a
work surface for moving spoken records through the Flight Path. The UI must
make evidence, uncertainty, sensitivity, routing, approval, and proof visible
without burying the user in implementation details.

This appendix describes the core product surfaces. These are not wireframes,
but they should be detailed enough to drive wireframes, implementation issues,
and acceptance tests.

## UI Principle: The Queue Is The Product

The central surface is the approval queue. A player and transcript viewer are
necessary, but they are supporting surfaces. The product value appears when
Pavo says:

```text
Here is what this spoken record probably means.
Here is where it should and should not go.
Here is the evidence.
Here is what needs approval.
Here is what happened after approval.
```

The UI should avoid the common meeting-notes trap: a pretty summary with a
long transcript underneath and integrations as afterthoughts. Pavo is not
trying to make recordings feel finished. It is trying to move them safely.

## Surface N1: Record List

Purpose:

```text
Show every captured record and its current Flight Path state.
```

Primary user questions:

- What records have been captured?
- Which records need review?
- Which records are ready for routing?
- Which records have pending approvals?
- Which writes failed?
- Which records are private or restricted?

Visible fields:

- title
- source system
- captured/imported date
- duration
- Flight Path stage
- machine status
- sensitivity class
- speaker-review state
- pending approval count
- last destination result
- policy flags

Default filters:

- needs review
- approval pending
- failed Land
- private/restricted
- recently landed
- source missing

Row actions:

- open record
- open approvals
- mark private
- defer
- show proof

Empty state:

```text
No records yet. Import a recording or connect a capture source to start the
Flight Path.
```

Error state:

```text
Some records could not load. Pavo should show partial results and a diagnostic
link rather than blanking the entire list.
```

Gotchas:

- Do not show sensitive titles broadly by default.
- Do not collapse `private`, `rejected`, and `failed` into the same "done"
  state.
- Do not make pending approvals invisible behind each record row.

Acceptance criteria:

- User can see which records need action in under ten seconds.
- Sensitive classes are visible without exposing sensitive details.
- The list can be filtered to only approval work.
- A failed destination write is visible from the list.

## Surface N2: Record Detail

Purpose:

```text
Let the user inspect one record from source through proof.
```

Primary user questions:

- What is the source?
- What did Pavo derive from it?
- How trustworthy is the transcript?
- Who spoke, and how confident is that identity?
- What is Pavo recommending?
- What has already happened?

Sections:

1. Source header
2. Evidence summary
3. Transcript and speaker view
4. Uncertainty and review notes
5. Routing packet
6. Approval decisions
7. Destination manifests
8. Policy learning

Source header fields:

- recording id
- source system
- source id
- media path or source-unavailable reason
- media hash
- duration
- captured/imported date
- consent state
- retention state

Evidence summary fields:

- transcript status
- engine/version
- speaker state
- review status
- redaction candidates
- accepted diagnostic artifacts
- superseded artifacts

Primary actions:

- play source
- open transcript
- add review correction
- create or regenerate routing packet
- open approval queue
- show manifests
- mark private

Empty state:

```text
Source is preserved, but no transcript evidence exists yet.
```

Error state:

```text
Transcript failed. Preserve the source record and show the failure reason,
then offer retry or manual note attachment.
```

Gotchas:

- The transcript should not visually dominate the source proof.
- Speaker labels should include confidence state.
- Superseded evidence should remain inspectable but not confuse the primary
  view.

Acceptance criteria:

- User can find source proof and routing state on the same page.
- User can tell whether speaker names were reviewed.
- User can distinguish generated summary from source evidence.

## Surface N3: Source And Evidence Viewer

Purpose:

```text
Give users confidence that recommendations are grounded in the original
record.
```

Primary user questions:

- What source span supports this recommendation?
- Was the speaker identified or inferred?
- Was the transcript reviewed?
- Did a later Tune run supersede this evidence?

Visible fields:

- audio/video player
- transcript span
- timestamp range
- speaker label and state
- confidence
- evidence id
- evidence kind
- review status
- linked proposed actions

Primary actions:

- play span
- copy source reference
- mark transcript correction
- mark speaker correction
- flag sensitive excerpt
- reject evidence for routing

Empty state:

```text
No source references are attached to this recommendation.
```

This should be a warning, not a quiet absence.

Error state:

```text
Source media unavailable. Pavo can show derived evidence, but routing should
respect the weaker proof state.
```

Gotchas:

- A transcript excerpt alone is not source playback.
- Sensitive excerpts should not be copied casually.
- Review corrections should create new evidence, not mutate old evidence.

Acceptance criteria:

- Every important proposed action can link to source evidence or explain why
  source is unavailable.
- User can correct evidence without losing prior artifact history.

## Surface N4: Routing Packet Review

Purpose:

```text
Show what Scout believes should happen before the approval decision.
```

Primary user questions:

- What destinations are recommended?
- What destinations are blocked?
- What actions are proposed?
- Why does Pavo think this route is appropriate?
- What evidence and sensitivity flags affect the recommendation?

Sections:

1. Packet summary
2. Suggested destinations
3. Blocked destinations
4. Proposed actions
5. Sensitivity and consent
6. Approval requirements
7. Learning signals

Suggested destination card fields:

- destination
- action type
- reason
- risk level
- policy basis
- required approval
- source refs

Blocked destination card fields:

- destination
- block reason
- policy basis
- what would need to change

Proposed action fields:

- action id
- destination
- title
- payload preview
- source refs
- confidence
- risk level
- approval options

Primary actions:

- approve
- edit then approve
- reject
- redact first
- mark private
- defer
- ask for more evidence

Empty state:

```text
No routing packet exists yet. Scout this record when Tune evidence is ready.
```

Error state:

```text
Routing packet failed validation. Show schema error and do not allow Land.
```

Gotchas:

- Do not hide blocked destinations. They teach the user why Pavo is careful.
- Do not use green styling for "high confidence" if approval is still
  required.
- Do not merge multiple actions into one all-or-nothing approval.

Acceptance criteria:

- User can approve one action and reject another.
- User can see why Slack or another broad destination was blocked.
- Packet validation failure blocks Land.

## Surface N5: Approval Queue

Purpose:

```text
Give the user a fast, focused place to make routing decisions.
```

Primary user questions:

- What needs my decision now?
- Which actions are high risk?
- What can be approved in batch?
- What needs editing or redaction?
- What can be safely rejected or archived?

Queue grouping:

- high-risk external writes
- redaction required
- low-risk archive approvals
- failed/retry decisions
- deferred items

Action row fields:

- record title or redacted title
- action type
- destination
- risk level
- sensitivity class
- short reason
- source refs count
- last reviewed time

Primary actions:

- approve
- edit
- reject
- redact
- defer
- mark private
- batch approve low-risk archives

Keyboard or command-flow considerations:

- approve selected low-risk archive
- reject selected recommendation
- open evidence
- edit payload
- defer with reason

Empty state:

```text
No approvals pending. New routed records will appear here before any external
write.
```

Error state:

```text
Some approvals could not be loaded. External writes remain blocked until the
queue is available.
```

Gotchas:

- Approval fatigue is a product failure.
- Batch approval should be limited to low-risk, policy-eligible actions.
- High-risk actions should not be visually adjacent to low-risk archive
  approvals without separation.

Acceptance criteria:

- User can clear simple approvals quickly.
- User cannot accidentally approve high-risk actions in a low-risk batch.
- Every decision becomes durable approval data.

## Surface N6: Edit And Redaction Preview

Purpose:

```text
Let the user modify what will be written before Land.
```

Primary user questions:

- What exact payload will be written?
- What sensitive content is included?
- What redactions are required?
- What changed from the generated proposal?
- Does the edited payload still cite evidence?

Visible fields:

- original generated payload
- editable approved payload
- destination
- destination-specific required fields
- sensitive spans
- redaction mode
- source refs
- unresolved placeholders

Primary actions:

- save edit
- apply redaction
- replace with placeholder
- remove excerpt
- link private source
- approve edited payload
- cancel and reject

Empty state:

```text
No editable payload exists for this action.
```

Error state:

```text
Payload does not satisfy destination requirements. Pavo should show the field
that failed and keep Land blocked.
```

Gotchas:

- Editing should not break evidence links silently.
- Redaction preview should happen before destination write.
- Destination-specific fields should be validated before approval when
  possible.

Acceptance criteria:

- Edited payload is stored as part of the approval decision.
- Redaction manifest records what changed and why.
- Land consumes the edited approved payload, not the original generated one.

## Surface N7: Destination Manifest And Proof View

Purpose:

```text
Show what happened after approved actions landed.
```

Primary user questions:

- What was written?
- Where did it go?
- Did it succeed?
- What destination id or link proves it?
- Was anything skipped or failed?
- Can retry duplicate the write?

Visible fields:

- write id
- packet id
- action id
- destination
- status
- destination object id
- destination URL when safe
- idempotency key
- approved by
- written at
- redactions applied
- error message
- retry state

Primary actions:

- open destination
- copy manifest id
- retry failed write
- mark manual copy complete
- attach note
- open source packet

Empty state:

```text
No destination writes have landed for this record.
```

Error state:

```text
Write failed. Pavo should show whether anything was partially created before
offering retry.
```

Gotchas:

- A successful API response is not always a useful user-facing proof.
- Partial failures must be visible.
- Retry should use idempotency keys and warn about uncertain duplicate risk.

Acceptance criteria:

- User can trace every landed action back to approval and source packet.
- Failed writes are inspectable and do not look like successful completion.
- Manifest is durable even when destination link becomes unavailable.

## Surface N8: Policy Candidate And Home Review

Purpose:

```text
Let the user decide what Pavo should learn from repeated approvals,
rejections, edits, and redactions.
```

Primary user questions:

- What pattern did Pavo notice?
- What rule is it proposing?
- What records would the rule affect?
- Does the rule recommend or grant permission?
- Can I narrow, reject, or disable it?

Visible fields:

- policy candidate id
- source decisions
- proposed rule
- scope
- affected record classes
- affected destinations
- permission effect
- examples
- conflicts
- rollback option

Primary actions:

- promote policy
- edit scope
- reject policy
- disable existing policy
- preview effect on recent records
- open source decisions

Empty state:

```text
No policy candidates yet. Pavo learns after approvals, edits, rejections, and
redactions.
```

Error state:

```text
Policy candidate conflicts with an existing rule. Pavo should show both rules
and keep the candidate unpromoted.
```

Gotchas:

- A policy that changes recommendations is safer than one that grants write
  permission.
- One decision should not create an organization-wide rule.
- Users need to see negative learning from rejections, not only positive
  learning from approvals.

Acceptance criteria:

- User can inspect why a policy was proposed.
- Policy scope is visible before promotion.
- Promotion does not silently weaken approval gates.

## Surface N9: Admin And Governance View

Purpose:

```text
Help a team administrator understand routing, retention, and destination risk.
```

This is not an early single-user requirement, but the product book should
define it because team adoption depends on governance.

Primary user questions:

- Which capture sources are connected?
- Which destinations can Pavo write to?
- Which classes are blocked by default?
- Which policies exist?
- Which records are restricted?
- What retention rules apply?
- What writes happened recently?

Visible sections:

- capture source inventory
- destination inventory
- sensitivity defaults
- approval policy
- retention policy
- recent write manifests
- failed writes
- policy changes

Primary actions:

- disable destination
- require approval for destination
- restrict sensitivity class
- export audit trail
- change retention policy
- review policy changes

Gotchas:

- Admin UI should not expose sensitive transcript content unnecessarily.
- Governance controls should not silently mutate existing records.
- Exported audit should include enough proof without leaking secrets.

Acceptance criteria:

- Admin can answer where records may go.
- Admin can block risky destinations.
- Audit export can reconstruct capture through Land.

## Cross-Surface Empty States

Pavo's empty states should teach the Flight Path without turning into
marketing copy.

Examples:

- Nest empty: "Import a recording to preserve the source."
- Tune empty: "No transcript evidence yet."
- Scout empty: "No routing packet yet."
- Land empty: "No approved writes have landed."
- Home empty: "No policy candidates yet."

Avoid:

```text
Nothing here. Try again later.
```

The state should say what is missing and what stage it belongs to.

## Cross-Surface Error States

Errors should fail closed around external writes.

Rules:

- source missing blocks source-backed claims
- packet invalid blocks approval
- approval unavailable blocks Land
- redaction failure blocks external write
- destination uncertainty blocks success state
- manifest failure makes Land incomplete

User-facing error language should be specific:

```text
Pavo did not write the CRM note because approval data could not be loaded.
```

not:

```text
Something went wrong.
```

## UI Metrics

The UI should make the product measurable:

- time from nested to routed
- time from routed to approved
- approval edit rate
- rejection rate
- redaction rate
- failed Land rate
- policy candidate promotion rate
- low-risk batch approval usage

But these metrics should not pressure the user into unsafe speed. The product
should optimize for trusted throughput, not raw automation.

## First UI Build Recommendation

The first real UI should include:

1. Record list
2. Record detail
3. Routing packet review
4. Approval queue
5. Destination manifest view

The first UI can defer:

- full admin governance
- complex team roles
- rich policy simulation
- broad dashboard analytics
- advanced transcript editing

This order matches the product thesis. Pavo is not ready as a product when it
can merely play a recording and show a transcript. It becomes a product when a
user can review a route, approve or reject actions, and see proof of what
landed.

# Appendix O: End-To-End Evidence Bundle Example

This appendix makes Pavo concrete. It shows one record moving through the
Flight Path from source capture to approved action and destination proof. The
example is synthetic, but the objects are intentionally realistic. A future
implementation should be able to produce artifacts with this shape or a
clearly versioned successor.

The scenario:

```text
Acme renewal call. The customer says renewal confidence depends on SSO
reliability. The account owner wants the source preserved, a product follow-up
created, a conservative CRM note drafted, and a broad Slack summary blocked.
```

The example demonstrates:

- one durable recording record
- multiple evidence records
- one routing packet
- one approved action
- one edited action
- one blocked route
- one redaction manifest
- multiple destination write manifests
- one policy candidate

## Bundle Directory

An evidence bundle should be inspectable as files, not only as UI state.

Example local archive:

```text
archive/customer/acme/rec_acme_renewal_2026_06_11/
  recording.json
  source/
    audio.m4a
    source-metadata.json
    sha256.txt
  evidence/
    ev_transcript_001.json
    ev_speaker_001.json
    ev_review_001.json
    ev_summary_001.json
  routing/
    pkt_acme_renewal_001.json
  approvals/
    approvals.json
    redaction_manifest.json
  writes/
    write_drive_001.json
    write_linear_001.json
    write_crm_001.json
    write_slack_blocked_001.json
  home/
    policy_candidate_001.json
  manifest.json
```

The exact file layout can evolve. The product invariant should not:

```text
A reviewer can reconstruct source -> evidence -> packet -> approval -> write
without trusting a hidden chat transcript.
```

## Recording Record

The recording record is the stable ledger entry. It should not contain raw
secrets or temporary signed URLs.

```json
{
  "recording_id": "rec_acme_renewal_2026_06_11",
  "source_system": "local_import",
  "source_account_ref": null,
  "source_recording_id": null,
  "title": "Acme renewal call",
  "owner": "account_owner",
  "captured_at": "2026-06-11T15:00:00Z",
  "imported_at": "2026-06-11T15:18:42Z",
  "media_path": "source/audio.m4a",
  "media_sha256": "sha256:9d9a1f4a7f6f0c0d85f3c0c66a5d9f1a0e4d5db9d1c612b3efacmeexample001",
  "duration_seconds": 2842.6,
  "flight_stage": "landed",
  "status": "partial_land",
  "sensitivity_class": "customer_sensitive",
  "consent_state": "meeting_platform_disclosed",
  "retention": {
    "source": "retain_source_restricted",
    "transcript": "retain_derived_only",
    "routing_packet": "retain_manifest_only",
    "review_after_days": 365
  }
}
```

What this proves:

- Pavo preserved the source.
- The record is customer-sensitive.
- The product knows the consent state.
- The final status is partial, not blindly "done," because one proposed route
  was intentionally blocked and only approved actions landed.

## Source Metadata

Source metadata should explain where the record came from without storing
temporary access tokens.

```json
{
  "recording_id": "rec_acme_renewal_2026_06_11",
  "source_system": "local_import",
  "original_filename": "2026-06-11-acme-renewal-call.m4a",
  "import_command": "pavo nest import ./2026-06-11-acme-renewal-call.m4a --source local_import",
  "imported_by": "user",
  "captured_timezone": "America/Chicago",
  "source_notes": "Exported from meeting platform after customer call.",
  "temporary_urls_persisted": false
}
```

Product rule:

```text
Temporary source URLs may be used during import. They should not become the
durable record.
```

## Evidence Record: Transcript

Transcript evidence should identify how it was produced and what it depends
on.

```json
{
  "evidence_id": "ev_transcript_001",
  "recording_id": "rec_acme_renewal_2026_06_11",
  "kind": "transcript",
  "created_at": "2026-06-11T15:25:04Z",
  "engine": "eidos-transcribe",
  "engine_version": "0.4.0",
  "input_refs": ["source/audio.m4a"],
  "output_path": "evidence/transcript.json",
  "confidence": 0.87,
  "review_status": "unreviewed",
  "context_terms": ["Acme", "SSO", "renewal", "identity provider"],
  "uncertain_spans": [
    {
      "span_id": "span_uncertain_001",
      "start_seconds": 1042.2,
      "end_seconds": 1049.7,
      "reason": "overlap",
      "text": "renewal is hard to justify until SSO stops breaking"
    }
  ]
}
```

Product rule:

```text
The transcript is evidence, not source truth.
```

## Evidence Record: Speaker Mapping

Speaker identity should carry state.

```json
{
  "evidence_id": "ev_speaker_001",
  "recording_id": "rec_acme_renewal_2026_06_11",
  "kind": "speaker_mapping",
  "created_at": "2026-06-11T15:27:19Z",
  "input_refs": ["ev_transcript_001"],
  "speakers": [
    {
      "speaker_label": "speaker_0",
      "display_name": "Account owner",
      "state": "reviewed",
      "confidence": 0.98
    },
    {
      "speaker_label": "speaker_1",
      "display_name": "Jordan, Acme champion",
      "state": "inferred",
      "confidence": 0.72
    }
  ],
  "review_status": "partially_reviewed"
}
```

Product implication:

```text
The customer name can appear in internal evidence, but Pavo should qualify it
as inferred until reviewed.
```

## Evidence Record: Human Review

Human review should add evidence rather than overwrite generated evidence.

```json
{
  "evidence_id": "ev_review_001",
  "recording_id": "rec_acme_renewal_2026_06_11",
  "kind": "review_note",
  "created_at": "2026-06-11T15:42:33Z",
  "actor": "account_owner",
  "input_refs": ["ev_transcript_001", "ev_speaker_001"],
  "review_status": "reviewed",
  "corrections": [
    {
      "target": "span_uncertain_001",
      "before": "until SSO stops breaking",
      "after": "until SSO reliability improves",
      "reason": "Reviewer corrected wording after listening to source span."
    },
    {
      "target": "speaker_1",
      "before_state": "inferred",
      "after_state": "reviewed",
      "reason": "Reviewer confirmed customer champion voice from call context."
    }
  ]
}
```

Product rule:

```text
Review is product data. It should improve future routing and future evidence
quality.
```

## Evidence Record: Summary

Summary should cite evidence and disclose limits.

```json
{
  "evidence_id": "ev_summary_001",
  "recording_id": "rec_acme_renewal_2026_06_11",
  "kind": "summary",
  "created_at": "2026-06-11T15:46:10Z",
  "input_refs": ["ev_transcript_001", "ev_review_001"],
  "summary": "Acme said renewal confidence depends on SSO reliability and asked for a concrete follow-up plan before renewal review.",
  "limits": [
    "Commercial impact should be phrased conservatively in broad channels.",
    "CRM note should avoid raw transcript quote unless approved."
  ],
  "review_status": "reviewed"
}
```

The summary is useful because it is attached to evidence. It should not be the
only artifact carried into Scout.

## Routing Packet

The routing packet is the Scout artifact. It is the decision surface between
understanding and action.

```json
{
  "packet_id": "pkt_acme_renewal_001",
  "recording_id": "rec_acme_renewal_2026_06_11",
  "created_at": "2026-06-11T15:50:00Z",
  "created_by": "scout.default.v1",
  "packet_version": "0.1",
  "status": "ready_for_review",
  "summary": {
    "short": "Acme renewal confidence depends on SSO reliability.",
    "derived_from": ["ev_summary_001"],
    "review_status": "reviewed"
  },
  "source_refs": [
    {
      "ref_id": "src_001",
      "kind": "audio_span",
      "recording_id": "rec_acme_renewal_2026_06_11",
      "start_seconds": 1042.2,
      "end_seconds": 1049.7,
      "speaker_label": "speaker_1",
      "speaker_state": "reviewed",
      "transcript_excerpt": "Renewal is hard to justify until SSO reliability improves.",
      "confidence": 0.91
    }
  ],
  "entities": [
    {
      "entity_id": "ent_acme",
      "name": "Acme",
      "kind": "customer_account",
      "status": "mapped",
      "confidence": 0.95
    },
    {
      "entity_id": "ent_sso",
      "name": "SSO",
      "kind": "product_area",
      "status": "reviewed",
      "confidence": 0.98
    }
  ],
  "sensitivity": {
    "class": "customer_sensitive",
    "contains_customer_data": true,
    "contains_financial_terms": true,
    "contains_personal_data": false,
    "contains_credentials": false,
    "external_routing_default": "approval_required",
    "redaction_required_before": ["crm", "slack"],
    "blocked_destinations": ["slack"]
  },
  "suggested_destinations": [
    {
      "destination": "drive",
      "action": "archive_source_record",
      "reason": "Customer renewal evidence should be preserved with source media.",
      "requires_approval": false,
      "risk": "low",
      "policy_basis": "customer_calls.auto_archive_drive"
    },
    {
      "destination": "linear",
      "action": "create_issue",
      "reason": "Customer explicitly linked renewal confidence to SSO reliability.",
      "requires_approval": true,
      "risk": "medium",
      "policy_basis": "customer_calls.product_blockers.require_pm_approval"
    },
    {
      "destination": "crm",
      "action": "draft_account_note",
      "reason": "Renewal dependency belongs with account context.",
      "requires_approval": true,
      "risk": "medium",
      "policy_basis": "customer_calls.crm_notes.require_account_owner_approval"
    }
  ],
  "blocked_destinations": [
    {
      "destination": "slack",
      "reason": "Conversation includes commercial renewal risk.",
      "policy_basis": "customer_calls.renewal_risk.block_broad_channels"
    }
  ],
  "proposed_actions": [
    {
      "action_id": "act_drive_001",
      "destination": "drive",
      "kind": "archive_source",
      "title": "Archive Acme renewal call",
      "payload": {
        "folder_hint": "Customers/Acme/Renewals",
        "include_media": true,
        "include_tuned_transcript": true,
        "include_routing_packet": true
      },
      "source_refs": ["src_001"],
      "confidence": 0.94,
      "requires_approval": false
    },
    {
      "action_id": "act_linear_001",
      "destination": "linear",
      "kind": "create_issue",
      "title": "Investigate SSO reliability issue affecting Acme renewal",
      "payload": {
        "team": "Product",
        "labels": ["customer-evidence", "sso"],
        "body": "Acme said renewal confidence depends on SSO reliability. Source span attached."
      },
      "source_refs": ["src_001"],
      "confidence": 0.86,
      "requires_approval": true
    },
    {
      "action_id": "act_crm_001",
      "destination": "crm",
      "kind": "draft_crm_note",
      "title": "Draft Acme renewal note",
      "payload": {
        "account_id": "crm_acme_001",
        "body": "Acme linked renewal confidence to SSO reliability and requested a concrete follow-up plan."
      },
      "source_refs": ["src_001"],
      "confidence": 0.84,
      "requires_approval": true,
      "redaction_required": true
    },
    {
      "action_id": "act_slack_001",
      "destination": "slack",
      "kind": "post_summary",
      "title": "Post Acme renewal risk summary",
      "payload": {},
      "source_refs": ["src_001"],
      "confidence": 0.73,
      "requires_approval": true,
      "blocked": true,
      "blocked_reason": "Commercial renewal risk should not be posted broadly."
    }
  ],
  "approval_requirements": [
    {
      "action_id": "act_linear_001",
      "required_decision": "approve_or_edit",
      "reason": "Creates product work from customer evidence."
    },
    {
      "action_id": "act_crm_001",
      "required_decision": "approve_or_redact_or_reject",
      "reason": "Writes commercial account context."
    }
  ]
}
```

What this packet demonstrates:

- Drive archive is low risk and policy-allowed.
- Linear and CRM require approval.
- Slack is visible as blocked, not silently omitted.
- Source references support the proposed actions.

## Approval Decisions

Approval decisions are granular.

```json
{
  "packet_id": "pkt_acme_renewal_001",
  "decisions": [
    {
      "approval_id": "approval_drive_001",
      "action_id": "act_drive_001",
      "decision": "approve",
      "actor": "policy",
      "decided_at": "2026-06-11T15:51:03Z",
      "policy_basis": "customer_calls.auto_archive_drive",
      "edited_payload": null,
      "notes": "Auto-archive allowed for customer calls."
    },
    {
      "approval_id": "approval_linear_001",
      "action_id": "act_linear_001",
      "decision": "approve_with_edits",
      "actor": "account_owner",
      "decided_at": "2026-06-11T15:55:44Z",
      "edited_payload": {
        "team": "Product",
        "labels": ["customer-evidence", "sso", "renewal-risk"],
        "title": "Investigate SSO reliability concern raised by Acme",
        "body": "Acme said renewal confidence depends on improved SSO reliability. Treat this as customer evidence for investigation, not a committed roadmap item. Source: src_001."
      },
      "notes": "Changed title from direct renewal blocker to investigation language."
    },
    {
      "approval_id": "approval_crm_001",
      "action_id": "act_crm_001",
      "decision": "redact_first",
      "actor": "account_owner",
      "decided_at": "2026-06-11T15:57:11Z",
      "edited_payload": {
        "account_id": "crm_acme_001",
        "body": "Customer discussed SSO reliability as an important factor for renewal confidence. Follow-up plan requested before renewal review."
      },
      "notes": "Removed raw quote and softened commercial-risk language."
    },
    {
      "approval_id": "approval_slack_001",
      "action_id": "act_slack_001",
      "decision": "reject",
      "actor": "account_owner",
      "decided_at": "2026-06-11T15:58:02Z",
      "edited_payload": null,
      "notes": "Do not post renewal risk in broad Slack."
    }
  ]
}
```

This is why approval is not a single checkbox. The same record produced an
auto-approved archive, an edited product issue, a redacted CRM note, and a
rejected Slack route.

## Redaction Manifest

Redaction should be explicit and pre-Land.

```json
{
  "redaction_manifest_id": "redact_acme_001",
  "packet_id": "pkt_acme_renewal_001",
  "created_at": "2026-06-11T15:58:44Z",
  "actor": "account_owner",
  "items": [
    {
      "action_id": "act_crm_001",
      "mode": "generalize_fact",
      "before": "Acme linked renewal confidence to SSO reliability and requested a concrete follow-up plan.",
      "after": "Customer discussed SSO reliability as an important factor for renewal confidence. Follow-up plan requested before renewal review.",
      "reason": "CRM note should be conservative and avoid raw quote."
    },
    {
      "action_id": "act_slack_001",
      "mode": "omit_from_destination",
      "before": "Post Acme renewal risk summary",
      "after": null,
      "reason": "Route rejected due to commercial sensitivity."
    }
  ]
}
```

Product rule:

```text
Redaction is part of approval. It is not a cleanup operation after posting.
```

## Destination Write Manifest: Drive

Drive receives the source-backed evidence bundle.

```json
{
  "write_id": "write_drive_001",
  "packet_id": "pkt_acme_renewal_001",
  "action_id": "act_drive_001",
  "destination": "drive",
  "destination_id": "drive_folder_acme_renewal_001",
  "status": "succeeded",
  "idempotency_key": "rec_acme_renewal_2026_06_11:drive:archive:v1",
  "approved_by": "policy",
  "written_at": "2026-06-11T16:02:00Z",
  "files": [
    {
      "name": "source/audio.m4a",
      "destination_file_id": "drive_file_audio_001",
      "sha256": "sha256:9d9a1f4a7f6f0c0d85f3c0c66a5d9f1a0e4d5db9d1c612b3efacmeexample001"
    },
    {
      "name": "routing/pkt_acme_renewal_001.json",
      "destination_file_id": "drive_file_packet_001",
      "sha256": "sha256:packetexample001"
    },
    {
      "name": "writes/write_drive_001.json",
      "destination_file_id": "drive_file_manifest_001",
      "sha256": "sha256:manifestexample001"
    }
  ],
  "error": null
}
```

Drive success does not mean all actions landed. It means the archive action
landed.

## Destination Write Manifest: Linear

Linear receives the edited approved payload.

```json
{
  "write_id": "write_linear_001",
  "packet_id": "pkt_acme_renewal_001",
  "action_id": "act_linear_001",
  "destination": "linear",
  "destination_id": "LIN-1842",
  "destination_url": "https://linear.example/acme-sso-reliability",
  "status": "succeeded",
  "idempotency_key": "rec_acme_renewal_2026_06_11:linear:act_linear_001:v1",
  "approved_by": "account_owner",
  "approval_id": "approval_linear_001",
  "written_at": "2026-06-11T16:04:12Z",
  "payload_source": "edited_payload",
  "redactions": [],
  "error": null
}
```

Product rule:

```text
Land should consume the edited approved payload, not the original generated
payload.
```

## Destination Write Manifest: CRM

CRM receives the redacted note.

```json
{
  "write_id": "write_crm_001",
  "packet_id": "pkt_acme_renewal_001",
  "action_id": "act_crm_001",
  "destination": "crm",
  "destination_id": "crm_note_9981",
  "status": "succeeded",
  "idempotency_key": "rec_acme_renewal_2026_06_11:crm:act_crm_001:v1",
  "approved_by": "account_owner",
  "approval_id": "approval_crm_001",
  "written_at": "2026-06-11T16:06:21Z",
  "payload_source": "redacted_edited_payload",
  "redactions": ["redact_acme_001"],
  "error": null
}
```

The CRM manifest distinguishes note creation from field mutation. This example
does not change deal stage, amount, close date, or forecast. Those would need
separate approval.

## Destination Manifest: Blocked Slack Route

Blocked routes should be durable proof too.

```json
{
  "write_id": "write_slack_blocked_001",
  "packet_id": "pkt_acme_renewal_001",
  "action_id": "act_slack_001",
  "destination": "slack",
  "destination_id": null,
  "status": "skipped",
  "skip_reason": "blocked_by_policy_and_rejected_by_user",
  "policy_basis": "customer_calls.renewal_risk.block_broad_channels",
  "approved_by": null,
  "approval_id": "approval_slack_001",
  "written_at": null,
  "error": null
}
```

This matters because "nothing was written" is part of the trust story. The
user should be able to prove that Pavo considered Slack and did not post.

## Policy Candidate

Home proposes scoped learning from the user's decisions.

```json
{
  "policy_candidate_id": "policy_candidate_acme_001",
  "created_at": "2026-06-11T16:08:42Z",
  "source_recording_id": "rec_acme_renewal_2026_06_11",
  "source_packet_id": "pkt_acme_renewal_001",
  "signals": [
    {
      "source": "approval_drive_001",
      "meaning": "Customer calls may be archived to restricted Drive automatically."
    },
    {
      "source": "approval_linear_001",
      "meaning": "Customer product blockers should use investigation language unless explicitly committed."
    },
    {
      "source": "approval_crm_001",
      "meaning": "CRM notes for renewal-sensitive calls should avoid raw quotes."
    },
    {
      "source": "approval_slack_001",
      "meaning": "Broad Slack posts should be blocked for renewal-risk content."
    }
  ],
  "proposed_policy": {
    "name": "customer_renewal_risk_conservative_routing",
    "scope": {
      "record_class": "customer_call",
      "sensitivity_class": "customer_sensitive",
      "contains_financial_terms": true
    },
    "rules": [
      "suggest restricted Drive archive",
      "require approval for Linear and CRM",
      "prefer investigation language for product issues",
      "redact raw customer quote from CRM by default",
      "block broad Slack posts"
    ],
    "permission_effect": "recommendation_only",
    "external_write_permission_granted": false
  },
  "status": "policy_review_pending"
}
```

Product rule:

```text
Home may propose routing policy. It should not silently grant broader write
permission.
```

## Bundle Manifest

The top-level bundle manifest should summarize the path.

```json
{
  "bundle_id": "bundle_acme_renewal_001",
  "recording_id": "rec_acme_renewal_2026_06_11",
  "created_at": "2026-06-11T16:09:30Z",
  "flight_path": {
    "nest": "nested",
    "tune": "tuned_reviewed",
    "scout": "packet_ready",
    "land": "partial_land",
    "home": "policy_candidate"
  },
  "artifacts": {
    "recording": "recording.json",
    "source": ["source/audio.m4a", "source/source-metadata.json", "source/sha256.txt"],
    "evidence": ["ev_transcript_001", "ev_speaker_001", "ev_review_001", "ev_summary_001"],
    "routing_packet": "pkt_acme_renewal_001",
    "approvals": ["approval_drive_001", "approval_linear_001", "approval_crm_001", "approval_slack_001"],
    "redactions": ["redact_acme_001"],
    "writes": ["write_drive_001", "write_linear_001", "write_crm_001", "write_slack_blocked_001"],
    "policy_candidates": ["policy_candidate_acme_001"]
  },
  "outcome_summary": "Source archived, Linear issue created from edited approval, CRM note written from redacted approval, Slack route blocked and skipped, policy candidate proposed.",
  "completion_state": "approved_source_backed_outcomes_created"
}
```

The bundle manifest is what allows a reviewer, agent, or test fixture to
evaluate whether Pavo did the right thing without replaying the whole product.

## Human-Readable Explanation

In prose, the bundle says:

```text
Pavo preserved the Acme renewal call, transcribed it with context terms,
reviewed a key span and speaker mapping, generated a routing packet, archived
the evidence bundle to Drive, created an edited Linear investigation issue,
wrote a redacted CRM note, blocked a broad Slack route, and proposed a scoped
policy for future customer renewal-risk calls.
```

This is the complete product loop. A summary-only meeting tool might stop
after "Acme has SSO concerns." Pavo should continue until the user can see
what happened, where it happened, who approved it, what evidence supports it,
what did not happen, and what the system learned.

## Evidence Bundle Acceptance Criteria

An end-to-end bundle is acceptable when:

- the recording record links to durable source or explicit source-unavailable
  status
- evidence records are append-only or supersession-aware
- transcript, speaker, review, and summary artifacts cite inputs
- routing packet includes suggested and blocked destinations
- proposed actions are separately reviewable
- approvals are granular
- redaction is recorded before destination write
- every Land attempt produces a manifest
- blocked or skipped destinations are represented
- policy learning is a candidate, not hidden behavior

This example should become a fixture. The product should eventually be able to
generate a bundle like this from a real or synthetic recording and validate it
with deterministic tests.

# Appendix P: Gotcha And Test-Fixture Matrix

Pavo's gotchas should become tests. Otherwise the product will slowly drift
toward the easiest demo: transcript in, tasks out. This matrix turns product
risks into detection signals, expected behavior, UI implications, and fixture
ideas.

The goal is not to test every AI output deterministically. The goal is to test
the product invariants around evidence, approval, redaction, routing, and
proof.

## Matrix Format

Each gotcha should eventually have:

- risk
- detection signals
- expected product behavior
- UI implication
- fixture idea
- acceptance test

The first test matrix is below.

## Gotcha P1: Transcript Error Becomes Action

Risk:

```text
Pavo creates a task or CRM note from a misheard word.
```

Detection signals:

- low transcript confidence
- context term mismatch
- uncertain span near proposed action
- reviewer correction exists

Expected behavior:

- mark proposed action as `needs_more_evidence`
- require review before Land
- cite the uncertain source span
- avoid external write until corrected or approved

UI implication:

The approval queue should show an uncertainty warning on the action row and a
link to the source span.

Fixture idea:

Synthetic transcript where "SSO reliability" is misheard as "SEO reliability"
and Scout proposes a product issue.

Acceptance test:

```text
Given a proposed action based on a low-confidence span,
when the packet is validated,
then the action requires review and cannot Land by policy alone.
```

## Gotcha P2: Speaker Identity Is Overclaimed

Risk:

```text
Pavo attributes a commitment to the wrong person.
```

Detection signals:

- speaker state is `inferred` or `conflicted`
- multiple speakers overlap
- proposed action depends on who said a phrase
- no human review exists

Expected behavior:

- qualify speaker name in UI
- require review for external write
- avoid naming the speaker in broad destination payloads unless reviewed

UI implication:

Speaker labels should show state: unknown, diarized, inferred, mapped,
reviewed, or conflicted.

Fixture idea:

Two-speaker call where the account owner and customer talk over each other
near a commitment phrase.

Acceptance test:

```text
Given speaker state is inferred,
when a CRM note payload names the speaker,
then validation requires approval or reviewed speaker evidence.
```

## Gotcha P3: User Pain Becomes Roadmap Commitment

Risk:

```text
Pavo turns an ambiguous user interview into an engineering task.
```

Detection signals:

- record class is user interview
- language contains pain/workaround but no explicit request
- proposed action type is `create_issue`
- confidence is moderate but evidence is inferential

Expected behavior:

- classify as research insight or discovery follow-up
- require product approval before engineering issue
- prefer investigation language

UI implication:

Packet review should show action classification: explicit request, inferred
task, research insight, decision, or open question.

Fixture idea:

User interview with onboarding confusion but no feature request.

Acceptance test:

```text
Given a user interview with inferred task classification,
when Scout proposes a Linear issue,
then the issue title must use discovery/investigation language or require edit.
```

## Gotcha P4: Correct Action Is No Action

Risk:

```text
Pavo optimizes for writes and treats private, archive-only, reject, or ignore
as failures.
```

Detection signals:

- user rejects all external routes
- sensitivity class is personal or compliance-adjacent
- blocked destinations outnumber suggested destinations
- approval decision is `archive_only` or `mark_private`

Expected behavior:

- record outcome as successful resolution
- preserve rejection/private signal for Home
- do not nag user to create tasks

UI implication:

Record list should show `private`, `archive_only`, or `rejected` as resolved
states, not errors.

Fixture idea:

Personal health call where only private archive and redacted reminder are
allowed.

Acceptance test:

```text
Given all external routes are rejected,
when the user marks archive_only,
then the record is resolved and no external Land adapters run.
```

## Gotcha P5: Redaction Happens Too Late

Risk:

```text
Sensitive content is posted or written before redaction.
```

Detection signals:

- sensitivity class requires redaction
- destination is broad or commercial
- payload includes raw transcript excerpt
- redaction manifest missing

Expected behavior:

- block Land until redaction is applied or explicitly waived
- store redaction manifest
- write redacted payload only

UI implication:

Approval screen should show "redaction required" as a blocking state, not a
warning after approval.

Fixture idea:

CRM note includes raw customer quote with commercial renewal risk.

Acceptance test:

```text
Given destination requires redaction,
when an approved payload contains unredacted sensitive text,
then Land refuses the write and records a blocked validation result.
```

## Gotcha P6: Destination Outage Creates Ambiguous State

Risk:

```text
Pavo fails to write to a destination but shows the action as complete.
```

Detection signals:

- adapter timeout
- API error
- no destination id
- manifest status missing

Expected behavior:

- create failed write manifest
- keep record in `partial_land` or `land_failed`
- expose retry state
- avoid duplicate risk on retry

UI implication:

Manifest view should separate succeeded, failed, partial, skipped, and manual
copy states.

Fixture idea:

Mock Linear adapter returns timeout after receiving request but before
returning issue id.

Acceptance test:

```text
Given a destination adapter fails without a destination id,
when Land completes,
then the write manifest status is failed and the record is not marked landed.
```

## Gotcha P7: Retry Duplicates Work

Risk:

```text
Pavo creates duplicate Linear issues, Drive folders, or CRM notes on retry.
```

Detection signals:

- retry uses new idempotency key
- prior write manifest exists
- destination has possible partial object
- same action id is retried

Expected behavior:

- use stable idempotency key
- inspect prior manifest
- detect likely duplicate where possible
- require user review for uncertain retry

UI implication:

Retry control should show prior attempt and duplicate risk.

Fixture idea:

First Linear write succeeds but manifest save fails; retry attempts same
action.

Acceptance test:

```text
Given an action has a prior uncertain write attempt,
when the user retries,
then Pavo reuses the idempotency key and shows duplicate-risk state before
creating a new object.
```

## Gotcha P8: Wrong Account Mapping

Risk:

```text
Pavo writes CRM notes to the wrong customer account.
```

Detection signals:

- account match confidence below threshold
- multiple account candidates
- entity status is inferred, not mapped
- CRM action depends on account id

Expected behavior:

- require account confirmation
- block CRM Land until mapped
- preserve candidate accounts as evidence

UI implication:

CRM action should show account identity prominently before approval.

Fixture idea:

Transcript mentions "Acme" but CRM has "Acme Corp" and "Acme Logistics."

Acceptance test:

```text
Given CRM account mapping is ambiguous,
when Scout proposes a CRM note,
then the action requires account confirmation before approval or Land.
```

## Gotcha P9: Consent State Is Missing

Risk:

```text
Pavo processes or routes a record when consent state should restrict action.
```

Detection signals:

- consent state is `unknown`
- record class involves external party
- destination is external
- user has not confirmed processing basis

Expected behavior:

- allow private Nest
- restrict Tune/Scout/Land according to policy
- block external writes until consent state is resolved or policy exception is
  explicit

UI implication:

Record detail should show consent state near source metadata, not buried in
settings.

Fixture idea:

Imported customer call with no meeting-platform disclosure metadata.

Acceptance test:

```text
Given consent_state is unknown and destination is external,
when approval is attempted,
then Pavo requires consent resolution or explicit restricted-use exception.
```

## Gotcha P10: Personal Content Routes To Business Tool

Risk:

```text
Personal health, finance, family, or school content routes into Linear, CRM,
or Slack.
```

Detection signals:

- privacy class is personal health, financial private, or family education
- proposed destination is business system
- record source is local personal import
- sensitive identifiers detected

Expected behavior:

- block business destinations by default
- allow private archive
- allow redacted personal reminder after approval
- avoid sensitive identifiers in task titles

UI implication:

Approval queue should group personal/private records separately and make
blocked business routes visible.

Fixture idea:

Insurance call with claim number and callback deadline.

Acceptance test:

```text
Given privacy class is personal_health,
when Scout considers Slack, CRM, or shared Linear,
then those destinations are blocked and represented in the packet.
```

## Gotcha P11: Compliance-Adjacent Record Gets Summarized As Findings

Risk:

```text
Pavo turns disputed facts into confident compliance findings.
```

Detection signals:

- sensitivity class is compliance_adjacent
- transcript contains disputed claims
- speaker confidence varies
- proposed action uses finding/conclusion language

Expected behavior:

- recommend restricted archive
- avoid findings language
- require manual review before any summary or task
- preserve uncertainty and speaker attribution

UI implication:

Scout output should show "restricted archive only" as a valid outcome.

Fixture idea:

Internal policy incident interview with conflicting accounts.

Acceptance test:

```text
Given record class is compliance_adjacent,
when Scout creates a packet,
then broad destinations are blocked and generated summaries avoid findings
language unless manually approved.
```

## Gotcha P12: Meeting Notes Become Source Of Truth

Risk:

```text
Downstream systems cite the summary without source evidence.
```

Detection signals:

- proposed action has no source refs
- destination payload contains summary-only claim
- source media unavailable without explicit status
- packet lacks evidence ids

Expected behavior:

- mark action as weakly sourced
- require review or attach source refs
- avoid source-backed label unless evidence exists

UI implication:

Actions without source refs should show a visible evidence gap.

Fixture idea:

Routing packet generated from imported text notes without audio.

Acceptance test:

```text
Given a proposed action has no source_refs,
when the action claims source-backed status,
then packet validation fails.
```

## Gotcha P13: Policy Learns Too Broadly

Risk:

```text
One approval creates a broad future automation rule.
```

Detection signals:

- policy candidate has broad scope
- permission effect includes external write grant
- source signal count is one
- candidate affects unrelated sensitivity classes

Expected behavior:

- keep candidate recommendation-only by default
- require explicit promotion
- show scope and examples
- block silent permission expansion

UI implication:

Home review should distinguish "recommend this route" from "write without
approval."

Fixture idea:

User approves one CRM note for one customer call.

Acceptance test:

```text
Given a policy candidate is based on one approval,
when Home proposes it,
then permission_effect remains recommendation_only and external_write_permission_granted is false.
```

## Gotcha P14: Approval Fatigue

Risk:

```text
Pavo asks for too many decisions and becomes another inbox.
```

Detection signals:

- high defer rate
- repeated low-risk approvals
- high time-to-decision
- repeated rejections of same route

Expected behavior:

- batch low-risk archive approvals
- promote scoped policy candidates
- suppress repeatedly rejected recommendations
- keep high-risk writes separate

UI implication:

Approval queue should group by risk and offer low-risk batch actions only when
policy allows.

Fixture idea:

Ten customer calls all requiring manual Drive archive approval.

Acceptance test:

```text
Given repeated low-risk archive approvals,
when Home proposes a scoped auto-archive policy,
then future Scout packets can mark Drive archive policy-allowed while CRM and
Slack still require approval or remain blocked.
```

## Gotcha P15: User Reverses Approval

Risk:

```text
A user approves an action, then realizes it should not have landed.
```

Detection signals:

- reversal requested after Land
- destination supports delete/edit
- destination already consumed by other users
- manifest exists

Expected behavior:

- preserve original approval and write manifest
- create reversal event
- offer destination-specific remediation if safe
- do not erase history

UI implication:

Manifest view should support "record reversal" or "remediate" without
pretending the original write never happened.

Fixture idea:

Approved Slack post later deemed too sensitive.

Acceptance test:

```text
Given a landed action is reversed,
when remediation is recorded,
then Pavo preserves original write manifest and appends a reversal event.
```

## Gotcha P16: Reprocessing Erases Prior Evidence

Risk:

```text
A newer transcription run silently replaces the old one, breaking audit.
```

Detection signals:

- new engine version
- force retranscribe
- prior transcript exists
- prior routing packet cited old evidence

Expected behavior:

- create new evidence record
- mark prior evidence superseded
- preserve old evidence refs for old packets
- flag packets that may be stale

UI implication:

Record detail should show evidence versions and packet staleness.

Fixture idea:

Transcript v1 routed an action; transcript v2 changes key phrase.

Acceptance test:

```text
Given a transcript is reprocessed,
when a new evidence record is created,
then old routing packets still resolve their original evidence refs and new
packets cite the new evidence.
```

## Gotcha P17: Destination API Forces Unsafe Shape

Risk:

```text
A destination lacks drafts, permissions, idempotency, or field-level control,
and Pavo pretends it is equivalent to safer destinations.
```

Detection signals:

- adapter lacks draft mode
- adapter lacks idempotency support
- adapter cannot restrict visibility
- adapter requires broad text blob

Expected behavior:

- downgrade to manual copy or local draft
- increase risk level
- require explicit approval
- record destination capability limits

UI implication:

Destination cards should show capability warnings.

Fixture idea:

CRM adapter can write notes but cannot create drafts.

Acceptance test:

```text
Given destination lacks draft support,
when action kind is draft_crm_note,
then Pavo either produces manual_copy_required or requires explicit write
approval before adapter execution.
```

## Gotcha P18: Broad Channel Membership Changes

Risk:

```text
Slack channel looked safe when policy was created but later includes broader
membership.
```

Detection signals:

- destination is broad channel
- channel membership changed
- policy older than channel membership snapshot
- sensitivity class is customer_sensitive or higher

Expected behavior:

- require fresh approval for broad posts
- snapshot channel id and membership metadata when available
- avoid auto-posting sensitive content to channels

UI implication:

Slack approval should show channel identity and visibility warning.

Fixture idea:

Private channel becomes larger team channel between policy creation and post.

Acceptance test:

```text
Given channel visibility changed after policy promotion,
when Slack Land is requested,
then Pavo requires renewed approval before posting.
```

## Gotcha P19: Archive Becomes Dump

Risk:

```text
Pavo archives everything but makes records impossible to find or evaluate.
```

Detection signals:

- missing titles
- missing source metadata
- no sensitivity class
- no routing packet or manifest
- folder names inconsistent

Expected behavior:

- require minimum archive metadata
- write bundle manifest
- use stable ids and predictable folder names
- avoid sensitive details in folder names

UI implication:

Record list should expose missing archive metadata as a quality issue.

Fixture idea:

Bulk import of unnamed voice memos.

Acceptance test:

```text
Given a record is archived,
when required archive metadata is missing,
then the archive manifest is marked incomplete and the record remains visible
for cleanup.
```

## Gotcha P20: Product Metrics Encourage Unsafe Automation

Risk:

```text
The team optimizes for tasks created, posts sent, or automation rate instead
of approved source-backed outcomes.
```

Detection signals:

- dashboard emphasizes raw writes
- reject/private outcomes excluded
- high automation rate with rising reversals
- approval edit rate ignored

Expected behavior:

- track approved source-backed outcomes
- include private/archive/reject as valid outcomes
- track reversal and edit rates
- treat high automation with high reversal as risk

UI implication:

Metrics views should separate throughput from trust quality.

Fixture idea:

Analytics sample where task count rises but rejection/reversal rate rises too.

Acceptance test:

```text
Given outcome metrics are calculated,
when records are marked private, archive_only, or rejected,
then they count as resolved outcomes rather than failures to automate.
```

## Fixture Library Plan

The test fixture library should include:

1. Customer renewal call with SSO blocker.
2. User interview with inferred feature request.
3. Personal health administration call.
4. Recruiting screen with compensation discussion.
5. Field memo with poor audio and safety issue.
6. Compliance-adjacent interview with disputed facts.
7. Multi-speaker overlap near commitment.
8. Duplicate destination write retry.
9. Wrong CRM account mapping.
10. Consent-unknown external call.
11. Destination outage during Land.
12. Reprocessing with changed transcript evidence.

Each fixture should define:

- source metadata
- transcript/evidence inputs
- expected sensitivity class
- expected routing packet
- expected approval requirements
- blocked destinations
- expected Land behavior
- expected Home signals

## Matrix Acceptance Criteria

The gotcha matrix is useful when:

- every gotcha maps to at least one product invariant
- every high-risk route has a failure mode
- tests cover correct non-action, not only successful writes
- redaction and approval are tested before Land
- destination manifests are tested for success, failure, partial, skipped, and
  reversal states
- policy learning is tested as inspectable and scoped

The matrix should evolve with the product. Whenever Pavo gains a new
destination adapter, the matrix should gain new destination-specific gotchas.
Whenever Pavo gains a new record class, the matrix should gain class-specific
privacy and routing fixtures.

# Appendix Q: Edge-Case Scenario Chapters

The first scenario library proves the normal product loop. This appendix
pushes harder. It covers the kinds of records that will break a shallow
meeting-notes product: overlap, language shifts, poor audio, missing consent,
duplicate records, destination failures, wrong account mapping, reversal after
approval, and reprocessing.

These scenarios should eventually become fixtures. For now, they serve as
product chapters: what the user brings to Pavo, what the system should notice,
where approval matters, what should land, what should not land, and how Home
should learn.

## Scenario Q1: Multi-Speaker Overlap Near A Commitment

### Situation

A customer success manager records a renewal call. Near the end, the customer
and account owner talk over each other. The transcript appears to say:

```text
We'll send the migration plan by Friday.
```

But the overlap makes it unclear who said it. If the account owner said it,
that is a company commitment. If the customer said it, it may be the
customer's own internal plan. A generic AI summary might turn the line into an
outbound follow-up commitment without checking speaker evidence.

### Before Pavo

The account owner skims a transcript, copies the apparent commitment into CRM,
and creates a follow-up task. Later, the customer asks why the team promised a
migration plan by Friday. The source recording has to be replayed manually to
understand the mistake.

### Nest

Pavo preserves the full recording, timestamp, source metadata, and media hash.
The record is classified as `customer_sensitive` because it includes renewal
discussion and possible commitments.

### Tune

Tune detects overlap around the commitment span. Speaker state remains
`conflicted` for the key phrase. The evidence record keeps both the raw
transcript and an overlap flag.

Example evidence note:

```text
Span 41:18-41:25 contains overlapping speech. Commitment wording is plausible,
but speaker attribution is unsafe.
```

### Scout

Scout recommends:

- Drive archive
- CRM note draft that avoids attributing the commitment
- follow-up question for account owner review

Scout blocks:

- automatic follow-up email
- CRM field update
- Linear issue that assumes an owner commitment

Routing packet action:

```json
{
  "kind": "followup_question",
  "title": "Confirm who committed to sending migration plan by Friday",
  "source_refs": ["overlap_span_4118_4125"],
  "requires_approval": true,
  "requires_review_reason": "Speaker attribution is conflicted."
}
```

### Approval

The account owner listens to the span and confirms the customer was asking for
a plan, not promising one. They approve a task:

```text
Clarify migration-plan timing with Acme before Friday.
```

They reject the generated CRM note that used commitment language.

### Land

Pavo archives the source, creates the clarified follow-up task, and records
that the CRM route was rejected. No outbound email is sent.

### Home

Policy candidate:

```text
When commitment language appears in overlapped customer-call speech:
  require speaker review.
  prefer follow-up question over commitment task.
  block outbound drafts until speaker state is reviewed.
```

### Gotchas

- Commitments are speaker-dependent.
- Overlap is not only a transcription problem; it is a routing problem.
- A confident summary can create a false obligation.

### Success Metrics

- overlapped commitment spans require review
- false commitment writes prevented
- clarified follow-up task created
- CRM note rejected without losing the learning signal

## Scenario Q2: Multilingual Call With Code Switching

### Situation

A product manager records a user interview where the user switches between
English and Spanish. The user describes onboarding confusion in English, then
uses Spanish to describe the emotional frustration and a workaround. The
interviewer understands the gist but not every phrase.

The risk is that Pavo routes only the English portions and loses the most
important user evidence.

### Before Pavo

The transcript engine produces partial English notes. The Spanish sections are
marked vaguely as unclear. A product insight is created from only half the
conversation.

### Nest

Pavo preserves the original audio and records that the call contains
multilingual content. If language detection is uncertain, it marks the record
as `needs_language_review`.

### Tune

Tune produces segment-level language tags:

```text
00:00-08:42 English
08:43-10:12 Spanish
10:13-14:55 English
```

The Spanish segment is transcribed and translated as separate evidence. Pavo
keeps the original-language text, translation, confidence, and review state.

### Scout

Scout recommends:

- research archive
- discovery follow-up issue
- no engineering build task yet

It marks the Spanish evidence as important because the workaround was
described there. The packet includes both original and translated source refs.

### Approval

The product manager approves the research insight and edits the Linear issue
title from:

```text
Improve onboarding import flow
```

to:

```text
Investigate onboarding import confusion for bilingual users
```

They request language review before any public product brief uses the quote.

### Land

Pavo writes a research note with original-language excerpts and translations.
It creates a discovery issue with a clear evidence caveat:

```text
Spanish segment translated by model; quote needs native-speaker review before
external use.
```

### Home

Policy candidate:

```text
For multilingual user interviews:
  preserve original-language excerpts.
  keep translation confidence visible.
  require review before using translated quotes externally.
  prefer discovery issues over build tasks.
```

### Gotchas

- Translation can hide nuance.
- Code switching often marks important emotion or workaround detail.
- Translated quotes should not be treated as reviewed customer language.

### Success Metrics

- multilingual spans detected
- original and translated evidence preserved
- no quote routed externally without review
- discovery issue created with translation caveat

## Scenario Q3: Poor Audio Field Memo With Safety Concern

### Situation

A field operator records a 90-second memo outside an event venue. There is
wind, traffic, and background music. The memo mentions missing signage, a
delayed vendor, and a cable crossing a walkway.

The audio quality is poor, but the safety concern is actionable.

### Before Pavo

The memo stays in a phone voice-recorder app. The operator later remembers the
signage but forgets the cable hazard until setup is nearly complete.

### Nest

Pavo imports the voice memo, stores the hash, and records likely field context
from filename, timestamp, or user selection. It does not require a perfect
transcript before preserving the record.

### Tune

Tune generates a partial transcript and marks uncertain spans. It classifies
the cable hazard as high-confidence enough for review, while the vendor arrival
time remains low-confidence.

### Scout

Scout recommends:

- safety log note for the cable hazard
- task for missing signage
- note-only record for vendor timing
- archive of the original memo

Routing packet classification:

```text
clear_operational_issue: missing signage
clear_safety_issue: cable across walkway
uncertain_note: vendor arrival time
```

### Approval

The operator approves the safety note and signage task. They defer the vendor
timing because the transcript is unclear.

### Land

Pavo writes:

- safety log entry with source timestamp
- task to move or cover cable
- signage task
- archive manifest

It does not create a vendor escalation.

### Home

Policy candidate:

```text
For poor-audio field memos:
  preserve source.
  route high-confidence safety concerns after approval.
  keep low-confidence operational details as notes.
  do not block all value because one span is uncertain.
```

### Gotchas

- Poor audio should not mean no action.
- Low confidence should shape the route.
- Safety issues need conservative escalation with evidence.

### Success Metrics

- safety concern not lost
- low-confidence vendor item not over-routed
- source memo preserved
- approved tasks carry evidence refs

## Scenario Q4: Missing Consent State On External Call

### Situation

A founder imports an audio file from a call with an external advisor. The file
has no meeting-platform metadata and no obvious consent record. The call
contains useful product and fundraising advice.

The risk is that Pavo treats a useful imported file like any other record and
routes it into shared systems before the capture basis is clear.

### Before Pavo

The founder pastes a transcript into a shared doc and asks an AI to extract
action items. The advisor did not expect broad internal distribution.

### Nest

Pavo imports the source but marks consent state as `unknown`. The source can be
preserved privately, but external routing is restricted.

### Tune

Tune can be deferred or run under restricted-use policy depending on user
settings. The record remains marked `restricted_use_only` until the founder
confirms consent or chooses private processing.

### Scout

Scout recommends:

- private archive
- private follow-up notes
- consent-state review

Scout blocks:

- Slack
- CRM
- shared Drive
- Linear

### Approval

The founder confirms the advisor gave permission for private notes but not
broad sharing. They approve private archive and a private task list only.

### Land

Pavo writes a private archive and private tasks. It records blocked shared
destinations in the manifest.

### Home

Policy candidate:

```text
For external calls with unknown consent:
  allow private Nest.
  require consent review before external Land.
  block broad sharing by default.
```

### Gotchas

- Consent state is product data.
- Useful content does not override routing restrictions.
- Private archive can be the right outcome.

### Success Metrics

- unknown consent blocks external writes
- private archive succeeds
- consent decision is durable
- shared routes are represented as blocked

## Scenario Q5: Duplicate Recording From Two Sources

### Situation

A meeting is captured by both Plaud and Zoom. Pavo imports the Plaud audio and
later sees a Zoom recording with the same meeting title and similar duration.
Both contain useful artifacts. The Plaud audio is cleaner; Zoom has participant
metadata and chat.

The risk is duplicate archives, duplicate tasks, and conflicting transcripts.

### Before Pavo

Two separate notes are created. One creates a Linear task. The other creates a
CRM note. Later, nobody can tell whether both came from the same meeting.

### Nest

Pavo detects a possible duplicate using timestamp, duration, title similarity,
participant overlap, and audio fingerprint. It creates two source records but
links them under a duplicate candidate group.

### Tune

Tune preserves both transcripts as separate evidence. It marks the Plaud audio
as primary for speech quality and Zoom metadata as supporting context.

### Scout

Scout recommends:

- merge evidence into one routing packet
- archive both source artifacts under one bundle
- block duplicate destination writes until a primary record is selected

Routing packet note:

```text
Possible duplicate source records: rec_plaud_001 and rec_zoom_001. Use merged
packet for routing; do not create duplicate Linear or CRM writes.
```

### Approval

The user confirms they are the same meeting. They approve a single Drive
archive with both sources and one Linear issue. They reject the duplicate CRM
note proposed from the second source.

### Land

Pavo writes one evidence bundle and one Linear issue. Destination manifests
include source refs from both recordings but use one idempotency key for the
approved action.

### Home

Policy candidate:

```text
When recordings share meeting title, timestamp, participants, and duration:
  create duplicate candidate.
  require merge review before external writes.
  preserve all source artifacts.
```

### Gotchas

- Duplicate detection should prevent duplicate action, not delete evidence.
- Different sources may each contain useful evidence.
- Merge review is part of routing safety.

### Success Metrics

- duplicate candidate detected
- source artifacts preserved
- one routing packet created
- duplicate destination writes prevented

## Scenario Q6: Destination Outage During Land

### Situation

A support lead approves a Linear issue and a CRM note from a customer
escalation call. Drive archive succeeds. Linear times out during issue
creation. CRM succeeds.

The risk is that Pavo marks the record complete even though one approved write
failed or might have partially succeeded.

### Before Pavo

The user sees a generic "sync failed" toast and does not know whether the
Linear issue exists. They manually create another issue, possibly duplicating
work.

### Nest

The source call is already preserved and tuned. The key point in this scenario
is not capture but Land proof.

### Tune

The record has reviewed evidence and a ready packet. No additional Tune work
is needed.

### Scout

Scout recommended Drive archive, Linear issue, and CRM note. All three were
approved.

### Approval

The user approved all three actions before Land. Pavo stores approval ids for
each action.

### Land

Drive succeeds. CRM succeeds. Linear returns a timeout before destination id is
known.

Pavo writes:

```text
write_drive_001: succeeded
write_crm_001: succeeded
write_linear_001: failed_unknown_destination_state
record status: partial_land
```

It does not mark the record fully landed. Retry is offered with duplicate-risk
warning and the same idempotency key.

### Home

No broad policy is learned from the outage. The failure is operational proof,
not a user preference. Home may record an adapter reliability signal.

### Gotchas

- Partial success is not complete success.
- Retry can create duplicates if idempotency is weak.
- Failed writes need manifests too.

### Success Metrics

- partial land state visible
- failed manifest written
- successful writes preserved
- retry uses stable idempotency key

## Scenario Q7: Wrong CRM Account Mapping

### Situation

A sales call mentions "Acme," but the CRM has `Acme Corp`, `Acme Logistics`,
and `Acme EMEA`. The transcript also mentions "logistics," but in the context
of the customer's operations, not the company name.

The risk is writing a commercially sensitive note to the wrong account.

### Before Pavo

The sales rep asks an AI assistant to update CRM. The assistant chooses the
first account match and writes the note. The actual account team never sees
the risk.

### Nest

Pavo preserves the recording and marks account mapping as unresolved.

### Tune

Tune extracts entities:

```text
Acme
logistics operation
renewal review
SSO
```

It does not collapse "logistics operation" into `Acme Logistics` without
evidence.

### Scout

Scout recommends:

- Drive archive
- account mapping review
- CRM note draft blocked until account confirmation
- Linear issue if product blocker is clear

The CRM action has state:

```text
requires_account_confirmation
```

### Approval

The user confirms the correct CRM account is `Acme Corp`. They approve a
redacted CRM note and reject the `Acme Logistics` candidate.

### Land

Pavo writes the CRM note to `Acme Corp` only after account confirmation. The
manifest records candidate account ids and the approved mapping.

### Home

Policy candidate:

```text
When CRM account match has multiple candidates:
  block CRM Land.
  require account confirmation.
  preserve rejected account candidates as negative mapping signals.
```

### Gotchas

- Entity detection is not account mapping.
- A wrong CRM write changes commercial truth.
- Rejected mappings are learning data.

### Success Metrics

- ambiguous account blocks CRM write
- correct account confirmed before Land
- rejected account candidate stored
- no note written to wrong account

## Scenario Q8: User Reverses Approval After Landing

### Situation

A team lead approves a Slack summary for an internal strategy meeting. Ten
minutes later, they realize the summary includes sensitive people-related
context and should not have been posted broadly.

The risk is that Pavo either hides the mistake or deletes proof in an attempt
to clean up the record.

### Before Pavo

The user deletes the Slack message manually. The transcript and original
approval history no longer match the actual operational history.

### Nest

The original meeting source remains preserved.

### Tune

Tune includes people-sensitive spans that should have triggered redaction. The
reversal becomes evidence that the sensitivity classifier or approval UI missed
something.

### Scout

Scout had recommended Slack with approval. In retrospect, the route should
have been blocked or redacted. The packet remains part of the audit trail.

### Approval

The original approval remains durable. The user creates a reversal decision:

```text
reverse act_slack_001 because people-sensitive context was included.
```

### Land

Pavo records:

- original Slack write manifest
- reversal event
- remediation action if Slack deletion/edit succeeds
- note that deletion does not erase the original write history

### Home

Policy candidate:

```text
For internal strategy meetings:
  block Slack summaries when people-sensitive spans exist.
  require redaction preview for broad destinations.
  treat reversal as a negative routing signal.
```

### Gotchas

- Reversal is not erasure.
- Product audit must preserve mistakes.
- Reversal signals should improve future policy.

### Success Metrics

- reversal event appended
- original write manifest preserved
- remediation manifest created
- policy candidate narrows future Slack routing

## Scenario Q9: Reprocessing Changes A Key Phrase

### Situation

A month after a customer call was routed, a better transcription engine becomes
available. The old transcript said:

```text
We can renew if onboarding is improved.
```

The new transcript says:

```text
We cannot renew unless onboarding is improved.
```

The difference is material. A stale CRM note and Linear issue may now
understate risk.

### Before Pavo

The old transcript is overwritten. Nobody knows which downstream actions were
based on which wording.

### Nest

The source media remains unchanged and hashed. This makes reprocessing
possible.

### Tune

Pavo creates `ev_transcript_002` instead of overwriting
`ev_transcript_001`. The old transcript is marked superseded but remains
available because old routing packets cited it.

### Scout

Pavo marks prior packet `pkt_customer_001` as potentially stale and creates a
new review packet. It does not automatically mutate old destination writes.

### Approval

The account owner reviews the changed span and approves:

- updated CRM note
- Linear comment on existing issue
- no new duplicate issue

### Land

Pavo writes a CRM update and Linear comment that reference the new evidence.
It records the relationship to the old manifests:

```text
supersedes interpretation used by write_crm_001
does not delete write_crm_001
```

### Home

Policy candidate:

```text
When reprocessing changes a routed high-impact phrase:
  mark prior packets stale.
  require review before destination correction.
  prefer comments/updates over duplicate issues.
```

### Gotchas

- Reprocessing is evidence evolution, not history rewrite.
- Old packets must keep resolving.
- Corrections should update downstream context without hiding prior actions.

### Success Metrics

- new evidence created
- old evidence preserved
- stale packet detected
- downstream correction landed with proof

## Scenario Library Coverage Summary

After this appendix, the book contains twenty worked scenario chapters:

1. Customer call with product blocker.
2. Personal health administration call.
3. User interview with ambiguous feature request.
4. Recruiting screen.
5. Field inspection voice memo.
6. Consulting discovery call.
7. Investor update call.
8. Customer support escalation.
9. Legal or compliance-adjacent interview.
10. Family school meeting.
11. Internal strategy jam.
12. Multi-speaker overlap near a commitment.
13. Multilingual call with code switching.
14. Poor audio field memo with safety concern.
15. Missing consent state on external call.
16. Duplicate recording from two sources.
17. Destination outage during Land.
18. Wrong CRM account mapping.
19. User reverses approval after Landing.
20. Reprocessing changes a key phrase.

The scenarios now cover every major persona from Appendix I and include both
successful action and correct non-action. They also give Pavo a product test
surface: each scenario can later become a fixture with expected packet,
approval, manifest, and Home outputs.

# Appendix R: Launch, Sales, And Buyer Narrative Assets

Pavo needs marketing assets that are specific enough to sell the product and
careful enough not to overpromise it. This appendix turns the product canon
into buyer-facing language, demo paths, sales discovery, packaging, and launch
material. The goal is not to make Pavo sound bigger than it is. The goal is to
make the real product legible.

The core claim remains:

```text
Pavo turns spoken records into approved, source-backed work.
```

Everything else should explain that claim. Pavo should not lead with "AI
meeting notes," "automatic CRM updates," "memory for your calls," or "never
take notes again." Those phrases are familiar, but they compress the product
into the wrong category. Pavo starts where those products often stop: a real
record exists, and someone needs to decide what it means, where it belongs,
what can be acted on, what must be withheld, and what proof should travel with
the action.

The marketing burden is unusually high because the product is about trust more
than convenience. A generic note taker can sell speed. Pavo must sell a more
serious promise: speed with review, routing with evidence, and action with a
human approval boundary. That is a harder story, but it is also more durable.
People already know how often recorded conversations create loose ends. They
also know that blind automation creates cleanup work when it writes the wrong
thing to the wrong place. Pavo lives in that tension.

## R1: Homepage Copy System

The homepage should make the category clear in the first screen. The user
should immediately understand that Pavo starts with a recording and ends with
approved downstream work. The page should not make the visitor decode a vague
AI productivity claim.

Recommended hero:

```text
Turn recorded conversations into approved work.

Pavo catches calls, memos, and meeting records, tunes them into trustworthy
evidence, recommends where the information should go, and waits for approval
before anything lands.
```

Primary CTA:

```text
Review a recording
```

Secondary CTA:

```text
See the Flight Path
```

Trust line under CTA:

```text
Source-backed routing. Human approval. Destination proof.
```

The hero should show a concrete product surface: a recorded call on the left,
a source-backed routing packet in the center, and an approval queue on the
right. The best homepage image is not a decorative bird, a waveform alone, or
a chat interface. It is a visible path from source to approved destination.

Alternate founder-operator hero:

```text
Stop losing what calls decided.

Pavo catches your important recordings and turns them into routed follow-up:
archives, issues, CRM notes, reminders, and drafts, all reviewed before they
land.
```

Alternate product-team hero:

```text
Keep user evidence attached to the work it creates.

Pavo turns customer calls and interviews into source-backed routing packets so
insights, bugs, and follow-ups move without turning uncertainty into roadmap
noise.
```

Alternate personal-administration hero:

```text
Keep important calls private until you choose what should happen next.

Pavo preserves the source, identifies likely follow-ups, and asks before
turning a recording into reminders, documents, or messages.
```

Problem section copy:

```text
Recording is easy now. Routing is still messy.

Teams record sales calls, support calls, user interviews, hiring screens, and
internal meetings. Individuals record doctor calls, school meetings, vendor
calls, and field notes. The record exists, but the work still has to be copied,
summarized, redacted, assigned, filed, and proven.

Generic notes help with recall. They do not decide where information belongs.
Generic automation helps move data. It does not know whether a sentence is
safe to write to a CRM, whether a speaker was uncertain, whether consent was
missing, or whether a follow-up should remain a draft.

Pavo fills that gap.
```

Flight Path section copy:

```text
Nest preserves the record.
Tune makes the record trustworthy.
Scout recommends routes.
Land executes only approved actions.
Home learns scoped policies from reviewed decisions.
```

Scenario section copy:

```text
A customer call can become three different outcomes.

The recording is archived with source proof. A product blocker becomes a
Linear issue after review. A CRM note is drafted, redacted, and approved. A
Slack route is blocked because the claim is commercially sensitive.

That is the Pavo difference: one source, multiple possible routes, explicit
approval, and proof of what landed.
```

Trust section copy:

```text
Pavo is built for the moment before automation becomes risky.

Every route has a source. Every action has a review state. Every landing has a
manifest. Every learned policy starts as a candidate, not a hidden behavior
change.
```

Integration section copy:

```text
Pavo should meet records where they start and work where it already happens.

Early sources: local files, Plaud exports, meeting recordings, voice memos.
Early destinations: local archive, Drive, Linear, CRM notes, email drafts, and
Slack drafts or blocked routes.
```

Closing CTA:

```text
Start with one important recording.
```

Homepage gotchas:

- Do not claim that Pavo replaces judgment.
- Do not imply that Pavo can infer consent without evidence.
- Do not describe Home as autonomous memory that rewrites policy silently.
- Do not show destinations landing before an approval surface.
- Do not bury the recording source; the source is the product's trust anchor.
- Do not make privacy claims that depend on future infrastructure.

The homepage should make a visitor say: "I have exactly this problem. I have
records, but I do not have a safe path from records to work."

## R2: Category And Positioning Copy

Pavo needs a category that is close enough to known buying behavior but distinct
enough to avoid being trapped as a note taker. The strongest category phrase is:

```text
Approval-gated routing for spoken records.
```

This phrase is accurate, but it is too dense for every buyer-facing surface.
The website can use:

```text
The safe path from recordings to work.
```

Sales decks can use:

```text
Pavo is a control layer between captured conversations and downstream systems.
```

Product docs can use:

```text
Pavo is an approval-gated recording-routing control plane.
```

The category should be explained with contrast:

```text
Recording tools capture what happened.
Transcription tools turn audio into text.
Meeting-note tools summarize the conversation.
Automation tools move data between apps.
Pavo decides, with review, what a spoken record is allowed to become.
```

The word "decides" must be handled carefully. Pavo recommends; users approve.
The more precise version is:

```text
Pavo recommends what a spoken record should become, shows the evidence, and
waits for approval before routing work downstream.
```

Short positioning by context:

For founders:

```text
Pavo is the approval queue for everything your recorded conversations should
turn into.
```

For product teams:

```text
Pavo routes user evidence into research, roadmap, and engineering systems
without losing the source.
```

For customer success:

```text
Pavo turns customer calls into reviewed account notes, risks, tasks, and
escalations.
```

For sales:

```text
Pavo drafts CRM updates from calls while keeping commercial claims under human
review.
```

For personal administration:

```text
Pavo catches important calls and routes only the approved follow-up into your
personal systems.
```

The category should not be described as:

- AI secretary
- meeting bot
- call summarizer
- personal memory
- autonomous CRM writer
- compliance archive
- Zapier for calls

Each phrase may contain a partial truth, but each pulls Pavo toward the wrong
expectation. "AI secretary" implies broad agency. "Meeting bot" implies capture
is the main product. "Call summarizer" implies text output is the destination.
"Personal memory" implies a recall layer rather than a routing layer.
"Autonomous CRM writer" makes approval sound optional. "Compliance archive"
creates enterprise obligations before the product is ready. "Zapier for calls"
understates evidence, review, and policy.

## R3: Demo Path 1 - Customer Call To Approved Work

This should be the default demo. It shows the complete Flight Path in a context
most business users understand.

Demo setup:

- Source: 22-minute customer call.
- Participants: account owner, customer operator, product manager.
- Content: customer reports a workflow blocker, mentions renewal concern,
  asks for follow-up, and shares one sensitive detail.
- Destinations: Drive, Linear, CRM, Slack.

Talk track:

```text
We start in Nest. Pavo has the source recording, metadata, and source hash. The
important point is that this is not a floating summary. Everything downstream
has to point back to the record.
```

Show:

- recording record
- source file path or source connector
- timestamp range
- capture time
- hash
- consent or consent-unknown state

Talk track:

```text
Now Tune has created a transcript, but it does not pretend every word is
equally certain. It marks uncertain spans, speaker confidence, and review
status. Pavo can route from an imperfect record, but only if uncertainty is
visible.
```

Show:

- transcript with confidence markers
- speaker labels
- correction from reviewer
- selected evidence spans

Talk track:

```text
Scout turns the record into possible routes. This is where Pavo stops being a
note taker. It is asking: what should this conversation become?
```

Show four route recommendations:

1. Archive the recording and transcript to Drive.
2. Create a Linear issue for the product blocker.
3. Draft a CRM note for the account record.
4. Block a Slack update because the proposed message includes a sensitive
   commercial claim.

Talk track:

```text
Notice that Scout can recommend action and non-action. A blocked route is not a
failure. It is part of the product doing its job.
```

Show approval:

- Drive archive approved as-is.
- Linear issue title edited.
- CRM note redacted.
- Slack route rejected.

Talk track:

```text
Land executes only the approved pieces. Each destination gets a manifest. If
the CRM write fails, Drive and Linear do not become ambiguous. Pavo knows what
landed, what failed, and what needs review.
```

Show:

- Drive destination manifest
- Linear issue URL
- CRM draft or note proof
- Slack blocked route record

Talk track:

```text
Home does not silently automate future behavior. It proposes a policy
candidate: calls with this account and this type of blocker can usually create
a Linear draft, but commercial claims still require review.
```

Close:

```text
That is the product: source, trustworthy record, recommended routes, approval,
destination proof, and scoped learning.
```

What the demo must prove:

- Pavo can preserve source context.
- Pavo can expose uncertainty.
- Pavo can split one record into multiple routes.
- Pavo can block unsafe routes.
- Pavo can execute approved routes.
- Pavo can show proof after execution.
- Pavo can learn without hiding policy changes.

What the demo should not imply:

- Pavo knows the truth without source evidence.
- Pavo can safely write everywhere by default.
- Pavo has enterprise compliance guarantees before the infrastructure exists.
- Pavo replaces customer success, product, or sales judgment.

## R4: Demo Path 2 - Private Record That Should Mostly Stay Private

This demo matters because it proves Pavo is not only a business workflow tool.
It also proves restraint.

Demo setup:

- Source: personal administration call with a school, doctor office, insurer,
  or vendor.
- Content: appointment timing, documentation request, a personal detail, and a
  possible follow-up.
- Destinations: local archive, reminder, email draft.

Talk track:

```text
This call is useful, but it is not something the user wants sprayed across
tools. Pavo starts by preserving the record privately.
```

Show Nest:

- local file
- private sensitivity class
- retention option
- no default team visibility

Talk track:

```text
Tune makes the actionable pieces clear. It separates what was said from what
the user might do about it.
```

Show:

- appointment date
- requested document
- uncertain spelling of a name
- sensitive detail marked as not routable

Talk track:

```text
Scout recommends a reminder and an email draft, but it does not recommend
exporting the whole transcript. It also marks a personal detail as archive-only.
```

Show:

- route to local archive
- route to reminder
- route to email draft
- blocked route to shared workspace

Talk track:

```text
The user approves the reminder, edits the email draft, and keeps everything
else private. Land creates only those outputs.
```

Close:

```text
This is one of the hardest things for AI products to learn: sometimes the best
action is a narrow action.
```

This demo is useful for buyers who worry that routing means oversharing. It
also creates a bridge to personal operating systems, private memory products,
and family administration workflows without collapsing Pavo into a general
assistant.

## R5: Demo Path 3 - Ambiguous User Research

This demo is for product teams. It should make Pavo feel safer than generic AI
insight extraction.

Demo setup:

- Source: user interview.
- Content: user complains about onboarding, asks for a shortcut, contradicts
  themselves once, and mentions a workaround.
- Destinations: research repository, product issue draft, roadmap note blocked.

Talk track:

```text
User research is where bad routing is especially dangerous. A complaint can be
real without being a roadmap commitment. Pavo keeps that distinction visible.
```

Show:

- transcript evidence spans
- user quote with uncertainty marker
- extracted pain point
- extracted workaround

Scout recommendations:

1. Archive interview and evidence spans to research repository.
2. Draft product-discovery note.
3. Draft Linear investigation issue.
4. Block roadmap-commitment language.

Talk track:

```text
Pavo is willing to say this should not become a commitment yet. That is product
value. It helps the team move evidence without turning one conversation into a
false decision.
```

Approval:

- approve research archive
- edit Linear issue to "Investigate onboarding import confusion"
- reject roadmap note
- create Home candidate that similar interviews can draft investigation issues
  but cannot set roadmap priority without review

Close:

```text
For product teams, Pavo is not a faster way to make a roadmap. It is a safer
way to keep source evidence connected to product work.
```

## R6: Demo Path 4 - Sales Call With Commercial Risk

This demo is for revenue teams. It should acknowledge why sales automation is
tempting and risky.

Demo setup:

- Source: sales discovery call.
- Content: prospect states budget range, asks about a capability, receives a
  tentative answer, and requests follow-up.
- Destinations: CRM note, task, email draft, blocked commitment.

Talk track:

```text
Sales calls contain facts, intent, and pressure. Pavo can draft useful CRM
notes, but it should not turn tentative language into commitments.
```

Show:

- buyer budget evidence
- capability request
- uncertain answer from seller
- follow-up request

Scout recommendations:

1. Draft CRM note with budget and buying process.
2. Create follow-up task.
3. Draft email with approved factual summary.
4. Block promise language around the tentative capability.

Approval:

- approve CRM note after editing "likely budget" to "stated budget range"
- approve follow-up task
- edit email draft
- reject unsupported commitment

Close:

```text
Pavo helps revenue teams move faster without letting the model become the
source of commercial truth.
```

This demo should never position Pavo as a tool that automatically updates CRM
with no review. The wedge is stronger when Pavo says: "We know why you want
automation here. That is exactly why approval and proof matter."

## R7: Sales Discovery Guide

Discovery should uncover whether the buyer has routing pain, not only note
pain. If the buyer only wants transcripts, Pavo may not be the right sale yet.

Opening question:

```text
After an important conversation is recorded, what has to happen for that
record to become useful work?
```

Capture questions:

- What kinds of conversations do you record today?
- Which tools create those recordings?
- Are any important conversations recorded outside scheduled meetings?
- Do you have local files, Plaud exports, Zoom recordings, voice memos, or
  call-center records?
- How often do recordings go unused after capture?
- Who is responsible for reviewing recordings today?

Tune questions:

- How much do you trust your current transcripts or summaries?
- What errors create real downstream problems?
- Do speaker labels matter for your work?
- Do you need to preserve exact quotes?
- Do you need human correction before the record becomes operational?
- What does "accurate enough" mean for each destination?

Scout questions:

- Where should useful information from calls usually go?
- Which destinations are straightforward?
- Which destinations are risky?
- Which routes should Pavo recommend but not execute?
- Which routes should Pavo block outright?
- What would make a recommendation trustworthy?

Land questions:

- What systems should Pavo write to first?
- Do you want direct writes, drafts, or export files?
- Who approves writes today?
- What proof do you need after a write lands?
- How do you handle failed writes or duplicate writes?
- What is worse: missing a follow-up or writing the wrong thing?

Home questions:

- Which decisions repeat often enough that Pavo should learn from them?
- Which policies should remain manual forever?
- Who can approve policy changes?
- How should Pavo explain why it recommended a route?
- What would cause you to revoke an automation?

Risk questions:

- What information must never leave the archive?
- What records have consent requirements?
- What systems are regulated or sensitive?
- What outbound messages require explicit approval?
- What would be embarrassing or costly if routed incorrectly?
- What audit trail would you need to trust the product?

Budget and urgency questions:

- How many recorded conversations per week have follow-up value?
- How much time is spent turning them into work?
- How often are follow-ups missed?
- How much cleanup happens after bad notes or bad CRM updates?
- Which team feels the pain most?
- What happens if nothing changes for six months?

Qualification rubric:

Strong fit:

- multiple recording sources
- multiple destinations
- high follow-up cost
- existing manual review or copy-paste workflow
- sensitivity around what should be routed
- buyer values evidence and proof

Moderate fit:

- one dominant recording source
- two or three destinations
- some manual follow-up pain
- buyer sees approval as acceptable

Weak fit:

- only wants raw transcription
- only wants fully autonomous writes
- no meaningful destination systems
- no review owner
- no sensitivity or follow-up cost

Sales should not force a weak-fit buyer into Pavo's story. The product becomes
easier to build and sell if early buyers actually have routing pain.

## R8: Objection Handling

Objection:

```text
We already have meeting notes.
```

Response:

```text
That is a good starting point. Pavo is for the next step: deciding which parts
of a recorded conversation should become work, which systems they belong in,
what evidence supports the route, and what needs approval before it lands.
```

Discovery follow-up:

```text
After the notes are created, who moves the follow-ups into the right systems?
```

Objection:

```text
Why not just automate this with Zapier or a workflow builder?
```

Response:

```text
Workflow builders are useful once the input is clean and the rule is known.
Spoken records are messier. Pavo handles source evidence, transcript
uncertainty, sensitivity, review state, and destination proof before routing.
```

Discovery follow-up:

```text
Which fields or messages would be unsafe to automate from a call without human
review?
```

Objection:

```text
Approval sounds like extra work.
```

Response:

```text
Approval is only extra work if the alternative is already safe. In many
recording workflows the alternative is manual copy-paste, missed follow-up, or
unsafe blind writes. Pavo narrows approval to the decision that matters: what
should land, where, and with what edits.
```

Discovery follow-up:

```text
Which actions would you approve quickly if the source evidence and destination
preview were already prepared?
```

Objection:

```text
Can Pavo just do it automatically?
```

Response:

```text
Some routes can become low-review over time, but Pavo should earn that through
reviewed history. The first version should recommend, preview, and prove. Home
can later propose scoped policies for repeated patterns.
```

Discovery follow-up:

```text
Which actions would you trust after ten correct reviewed examples, and which
would always require approval?
```

Objection:

```text
This sounds like compliance software.
```

Response:

```text
Pavo borrows some trust patterns from compliance systems, but the first product
is operational: getting useful records into useful work with approval and
proof. It should not claim enterprise compliance before the required controls
exist.
```

Discovery follow-up:

```text
Do you need formal compliance controls today, or do you mainly need better
source-backed routing and review?
```

Objection:

```text
Our conversations are too sensitive.
```

Response:

```text
That is exactly why routing needs a review boundary. Pavo can archive sensitive
records, recommend narrow actions, block unsafe routes, and keep destination
writes separate from the full transcript.
```

Discovery follow-up:

```text
What should be archive-only, and what types of follow-up are still useful if
properly redacted?
```

Objection:

```text
The transcript will be wrong.
```

Response:

```text
Transcripts are sometimes wrong. Pavo's job is not to pretend otherwise. It
should expose uncertainty, preserve the audio source, allow correction, and
limit actions when the evidence is weak.
```

Discovery follow-up:

```text
Which transcript errors would matter most for your downstream workflows?
```

Objection:

```text
We do not want another inbox.
```

Response:

```text
Pavo should not become a permanent dumping ground. Its queue exists to turn
records into approved outcomes, blocked outcomes, or retained evidence. A good
Pavo queue gets cleared into destination proof.
```

Discovery follow-up:

```text
Who would review the first few routing packets, and what would make that queue
fast enough to use?
```

Objection:

```text
What if Pavo routes to the wrong customer, project, or person?
```

Response:

```text
That is a first-class risk. Pavo needs account matching evidence, destination
preview, duplicate checks, and approval before landing. Wrong mapping should be
a blocked or review-required state, not an invisible failure.
```

Discovery follow-up:

```text
Which identifiers would Pavo need to match a recording to the right record in
your systems?
```

## R9: Competitive Battlecards

These battlecards should be used with respect. Adjacent tools solve real
problems. Pavo wins by owning the control path after capture.

Battlecard: Recording devices

Buyer view:

```text
We already use a recorder.
```

Pavo view:

```text
Great. Pavo does not need to replace the recorder. It makes the captured record
useful by preserving source evidence, recommending routes, and requiring
approval before downstream action.
```

Differentiators:

- source-to-destination workflow
- routing packet
- approval queue
- destination manifest
- policy learning

Do not say:

```text
Your recorder is not smart enough.
```

Say:

```text
Capture is the first step. Pavo handles what should happen next.
```

Battlecard: Meeting bots

Buyer view:

```text
We already use a meeting bot.
```

Pavo view:

```text
Meeting bots are strong at joining calls and producing notes. Pavo is useful
when those notes need to become reviewed work across systems.
```

Differentiators:

- works with recordings that did not come from scheduled meetings
- handles multiple destinations
- blocks unsafe routes
- keeps source proof connected to actions
- treats approval as a product surface

Do not say:

```text
Meeting notes are useless.
```

Say:

```text
Notes are useful. Pavo turns the right parts into approved outcomes.
```

Battlecard: CRM call intelligence

Buyer view:

```text
Our CRM already analyzes calls.
```

Pavo view:

```text
CRM call intelligence is valuable inside the revenue workflow. Pavo is broader:
it can route one recording into CRM, product, archive, task, and blocked
outcomes with different approval rules.
```

Differentiators:

- source-agnostic capture
- non-CRM destinations
- product/customer-success/personal use cases
- sensitivity-aware route decisions
- proof outside CRM

Do not say:

```text
The CRM is wrong.
```

Say:

```text
CRM is one destination. Pavo governs whether and how a record should land
there.
```

Battlecard: Automation platforms

Buyer view:

```text
Can we build this with an automation tool?
```

Pavo view:

```text
Automation platforms are powerful after the rule is stable. Pavo is the review
and evidence layer that decides whether a spoken record is safe to route at
all.
```

Differentiators:

- audio source evidence
- transcript uncertainty
- human approval state
- redaction before write
- route blocking
- destination manifests

Do not say:

```text
Workflow builders cannot do AI.
```

Say:

```text
Pavo prepares and governs the action. Automation can still be a destination or
execution partner later.
```

Battlecard: Generic AI assistants

Buyer view:

```text
Can ChatGPT or another assistant summarize and route this?
```

Pavo view:

```text
A general assistant can help with ad hoc reasoning. Pavo turns the workflow
into durable product state: source records, routing packets, approvals,
destination manifests, and learned policies.
```

Differentiators:

- durable evidence model
- repeatable approval workflow
- destination-specific previews
- audit trail
- policy candidates
- productized queues

Do not say:

```text
General assistants are unsafe.
```

Say:

```text
Ad hoc assistance is useful. Pavo makes the path repeatable and reviewable.
```

## R10: Packaging And Pricing Hypotheses

Pavo should package around trust maturity, not only seat count. A buyer's
valuable question is not "how many users can log in?" It is "how much of our
spoken work can safely move through this system?"

Package 1: Personal Flight

Target user:

- founder operator
- consultant
- individual professional
- personal administration user

Core value:

- catch important recordings
- preserve source evidence
- review routing packets
- land narrow approved actions

Included:

- local import
- Plaud/local file import
- basic Nest archive
- Tune transcript and correction
- Scout routing packet
- manual Land to local archive and export
- limited Drive or file destination
- private Home suggestions

Not included:

- team approval roles
- governed retention policy
- admin dashboard
- automatic direct writes to high-risk systems

Why this matters:

Personal Flight lets Pavo prove the product loop without overbuilding team
governance. It also gives founder users a natural way to feel the product
before selling it to a team.

Package 2: Team Flight

Target user:

- product team
- customer success team
- small revenue team
- professional services pod

Core value:

- turn recorded conversations into shared, approved work
- keep evidence attached to downstream tasks and notes
- reduce missed follow-up

Included:

- shared source archive
- team review queue
- Drive adapter
- Linear adapter
- CRM note drafts
- email draft adapter
- destination manifests
- approval roles
- route history
- scenario templates

Not included:

- broad enterprise compliance claims
- fully autonomous policy execution
- complex legal hold
- formal regulated-retention guarantees

Why this matters:

Team Flight is likely the first commercial wedge. The team pain is visible, the
approval model is useful, and the integration set can stay narrow while still
creating value.

Package 3: Governed Flight

Target user:

- larger teams
- regulated-adjacent teams
- companies with audit and retention requirements

Core value:

- make recording-to-work workflows governable
- manage retention, sensitivity, approvals, and proof
- restrict unsafe routes

Included:

- admin policy console
- retention controls
- consent-state tracking
- advanced redaction
- audit exports
- destination restrictions
- policy approval workflows
- role-based review
- evidence bundle exports

Not included until proven:

- legal compliance certifications
- claims of regulatory completeness
- autonomous high-risk routing
- unsupported data residency claims

Why this matters:

Governed Flight is attractive but dangerous too early. It should be a roadmap
direction that grows from proven audit primitives, not a launch promise that
the product cannot yet support.

Pricing axes to test:

- number of recordings processed
- storage volume
- number of destination adapters
- team seats
- approval queue seats
- governed policy features
- retention/audit exports
- Home policy automation level

Pricing warnings:

- Do not price only per transcript minute if the value is routing and proof.
- Do not make approval users expensive enough that teams avoid review.
- Do not hide destination manifests behind a high tier; proof is central.
- Do not sell automatic writes as a premium feature before safety is earned.
- Do not bundle personal and governed use cases so tightly that neither feels
  clear.

The simplest early pricing message:

```text
Start with the recordings that already create follow-up work. Pay when Pavo
turns them into reviewed, source-backed outcomes.
```

## R11: Buyer Personas And Buying Triggers

Founder operator

Trigger:

- too many calls create loose ends
- important conversations are captured but not acted on
- founder wants one queue for follow-up without hiring operations help

Desired outcome:

- "My recordings become reviewed follow-through."

Emotional pull:

- relief from remembering every call
- confidence that nothing sensitive lands without review
- desire for follow-through without loss of control

Proof needed:

- one real call routed to archive, task, and draft
- clear approval screen
- no surprise outbound action

Likely objection:

- "I do not want another system to manage."

Response:

- Pavo should clear records into outcomes and proof. The queue is a review
  surface, not a new permanent workspace.

Product manager

Trigger:

- customer evidence gets scattered
- user quotes turn into loose roadmap claims
- research calls do not connect to engineering work

Desired outcome:

- "Evidence moves into product work without losing context."

Emotional pull:

- fewer ambiguous product requests
- better source-backed prioritization
- less pressure to overstate one interview

Proof needed:

- interview archive with evidence spans
- issue draft with uncertainty preserved
- blocked roadmap commitment

Likely objection:

- "We already have research notes."

Response:

- Pavo should route evidence and preserve source links; it does not replace
  research judgment.

Customer success leader

Trigger:

- renewal risk appears in calls but not in systems
- customer blockers are reported but not escalated
- account notes are inconsistent

Desired outcome:

- "Important customer signals become reviewed account work."

Emotional pull:

- fewer missed renewal risks
- stronger evidence for escalations
- cleaner account history

Proof needed:

- risk route
- product blocker issue
- CRM note draft
- blocked oversharing

Likely objection:

- "My team will not review another queue."

Response:

- Pavo should prepare the decision so review is faster than manual CRM and
  task entry.

Sales leader

Trigger:

- CRM quality is poor
- reps resist data entry
- call recordings contain useful detail but blind AI notes create risk

Desired outcome:

- "Calls produce better CRM notes without losing human control."

Emotional pull:

- cleaner pipeline visibility
- less rep admin
- fewer unsupported commitments

Proof needed:

- CRM note preview
- claim evidence
- task creation
- blocked unsupported promise

Likely objection:

- "We need automation, not review."

Response:

- Review is the path to trustworthy automation. Low-risk patterns can earn
  lighter review through Home.

Professional services operator

Trigger:

- client calls contain action items, decisions, and scope questions
- follow-up quality depends on manual note discipline
- client-sensitive details need careful handling

Desired outcome:

- "Client conversations become approved deliverables, tasks, and archives."

Emotional pull:

- fewer missed commitments
- better project continuity
- less risk from accidental oversharing

Proof needed:

- project task route
- client recap draft
- internal-only note
- archive proof

Likely objection:

- "Client context is too nuanced."

Response:

- Pavo should expose nuance and require approval; it should not flatten client
  conversations into automatic tasks.

Personal administration user

Trigger:

- important calls with schools, insurers, doctors, vendors, banks, or landlords
  create follow-ups
- user records for recall but still loses next steps
- privacy is critical

Desired outcome:

- "My important calls stay preserved and only approved follow-up leaves the
  archive."

Emotional pull:

- reduced cognitive load
- privacy
- confidence around dates, names, and promises

Proof needed:

- private archive
- narrow reminder
- edited email draft
- blocked shared route

Likely objection:

- "I do not want personal recordings in a business tool."

Response:

- Pavo should support private mode and narrow export. Personal records should
  not default into team systems.

## R12: Launch Asset Kit

Launch should make one idea unavoidable: Pavo is the control path from spoken
source to approved work.

One-line launch copy:

```text
Pavo turns recorded conversations into approved, source-backed work.
```

Two-sentence launch copy:

```text
Recording tools capture what happened, but the work still has to be routed.
Pavo preserves the source, tunes the record, recommends destinations, waits
for approval, and proves what landed.
```

Short launch post:

```text
We are building Pavo because recording has become easy, but trustworthy
follow-through has not.

Calls, meetings, voice memos, interviews, and admin conversations all create
work. Some should become issues. Some should become CRM notes. Some should be
archived. Some should stay private. Some should be blocked.

Pavo is an approval-gated path from spoken records to downstream action:
Nest the source, Tune the record, Scout routes, Land approved actions, and Home
learns from reviewed decisions.

The product starts with a simple promise: no downstream action without source,
preview, and approval.
```

Longer launch post:

```text
The world is recording more conversations than ever. Sales calls, product
interviews, customer escalations, internal meetings, field notes, school calls,
doctor calls, and vendor calls all become files somewhere.

But most recordings do not become useful work on their own. Someone still has
to listen, correct, summarize, redact, file, copy, assign, draft, and verify.
When teams skip that step, the record goes stale. When they automate it
blindly, the wrong thing can land in the wrong place.

Pavo is built for the space between capture and action.

It catches the record. It makes the record trustworthy enough to use. It
recommends routes. It asks before anything lands. Then it records proof of what
actually happened downstream.

We call the model the Flight Path:

Nest: preserve the source.
Tune: make the record accurate.
Scout: recommend where information belongs.
Land: execute approved actions.
Home: learn scoped policies from review.

Pavo is not trying to replace judgment. It is trying to make judgment easier to
apply at the exact moment when AI recommendations become operational action.
```

Launch email:

```text
Subject: Pavo turns recordings into approved work

Hi,

I am building Pavo for a problem that keeps showing up: recording is easy, but
follow-through is still manual, inconsistent, and risky to automate blindly.

Pavo catches spoken records, tunes them into usable evidence, recommends where
the information should go, and waits for approval before anything lands.

One customer call might become a Drive archive, a Linear investigation, and a
CRM note, while a Slack update is blocked because the claim is too sensitive.
One personal administration call might become a private archive and one edited
reminder, with everything else staying put.

The product is built around a simple rule: source-backed routing first,
approval before action, proof after landing.

I would like to show you the first demo if recorded conversations already
create follow-up work in your world.
```

Founder DM:

```text
Quick question: after important calls are recorded, where do the follow-ups
actually go?

I am building Pavo for the gap between "we have the recording" and "the right
work landed in the right system." It recommends routes from calls and waits for
approval before writing anything downstream.
```

Product-team DM:

```text
I am working on Pavo, a source-backed routing layer for recorded user
interviews and customer calls. The idea is to move evidence into research,
issues, and follow-ups without letting AI turn ambiguity into roadmap claims.
Worth showing you?
```

Customer-success DM:

```text
I am building Pavo for customer calls where renewal risks and product blockers
show up in conversation but do not reliably land in account systems. It drafts
routes with evidence and approval instead of blindly writing notes. Could I
show you the workflow?
```

Demo invitation:

```text
Bring one recorded conversation that should have become follow-up work. The
demo is simple: we will preserve the source, tune the record, review route
recommendations, approve or block destinations, and inspect the proof.
```

Launch checklist:

- product book spine published internally
- Flight Path vocabulary stable
- one default demo recording prepared
- one personal/privacy demo prepared
- one product-research demo prepared
- homepage copy reviewed against overclaim checklist
- demo script includes blocked route and correction
- sales discovery guide ready
- objection handling ready
- known limitations visible
- no unsupported compliance claims
- no blind automation claims
- first integration promises limited to proven adapters

## R13: Sales Deck Outline

Slide 1: Title

```text
Pavo
The safe path from recorded conversations to approved work
```

Visual:

- recording source
- routing packet
- approval queue
- destination proof

Slide 2: The shift

```text
Recording has become ambient.
Follow-through has not.
```

Speaker notes:

```text
Teams and individuals are capturing more spoken records than ever. The problem
is no longer only memory. It is operational routing.
```

Slide 3: The broken path

```text
Recordings become notes.
Notes become manual copy-paste.
Copy-paste becomes missed work or unsafe automation.
```

Speaker notes:

```text
The current path is either too manual or too automatic. Pavo creates the review
layer in the middle.
```

Slide 4: Pavo's answer

```text
Source-backed routing with approval before action.
```

Show:

- source
- evidence
- route
- approval
- manifest

Slide 5: Flight Path

```text
Nest -> Tune -> Scout -> Land -> Home
```

Speaker notes:

```text
These are not brand decorations. They are the product maturity model.
```

Slide 6: Demo scenario

```text
One customer call. Four possible outcomes.
```

Show:

- archive approved
- Linear issue edited and approved
- CRM note redacted and approved
- Slack route blocked

Slide 7: Trust model

```text
Pavo makes uncertainty visible.
```

Show:

- transcript confidence
- speaker confidence
- source spans
- sensitivity
- approval state

Slide 8: Why now

```text
Capture is everywhere. AI can recommend routes. Teams still need control.
```

Speaker notes:

```text
The timing is right because capture volume is rising and AI can reason over
records, but buyers are also more aware of the cost of wrong automation.
```

Slide 9: Where Pavo starts

```text
Founder-led teams, product teams, customer success, professional services, and
personal administration.
```

Slide 10: What Pavo is not

```text
Not just notes.
Not blind automation.
Not a compliance promise before controls exist.
Not a replacement for human judgment.
```

Slide 11: Packaging

```text
Personal Flight
Team Flight
Governed Flight
```

Slide 12: Call to action

```text
Bring one recording that should have become work.
```

The deck should be short. The demo should do the convincing. Pavo's concept is
much easier to understand when a buyer sees a route get edited, approved,
blocked, and proven.

## R14: Product Marketing Guardrails

Pavo needs explicit marketing guardrails because the product sits near several
high-risk claims.

Do say:

- source-backed
- approval-gated
- routing recommendations
- destination previews
- reviewed actions
- proof after landing
- scoped policy candidates
- private archive
- blocked route
- uncertainty markers
- human review

Do not say:

- fully autonomous
- compliance-ready unless proven
- zero-review
- guaranteed accuracy
- understands every meeting
- replaces your CRM admin
- never miss anything
- records everything safely
- automatic outbound follow-up
- private by default unless architecture proves it
- learns your policy silently

Careful phrase:

```text
Pavo learns your preferences.
```

Safer version:

```text
Pavo proposes scoped policies from reviewed routing decisions.
```

Careful phrase:

```text
Pavo knows where everything belongs.
```

Safer version:

```text
Pavo recommends routes with evidence, confidence, and review requirements.
```

Careful phrase:

```text
Pavo automates your follow-up.
```

Safer version:

```text
Pavo prepares follow-up for approval and executes only what you approve.
```

Careful phrase:

```text
Pavo makes recordings searchable memory.
```

Safer version:

```text
Pavo preserves spoken records and routes approved outcomes into the systems
where work happens.
```

Careful phrase:

```text
Pavo handles compliance.
```

Safer version:

```text
Pavo can preserve approval and destination proof. Formal compliance controls
must be implemented and verified for each governed use case.
```

The marketing rule:

```text
Never make the product sound safer than the proof surface.
```

This rule should apply to website copy, sales calls, investor decks, demos,
docs, onboarding, and marketplace descriptions. Pavo can be ambitious without
being loose.

## R15: Marketplace Listing Draft

Short description:

```text
Pavo turns spoken records into approved, source-backed work.
```

Long description:

```text
Pavo is a recording-routing control layer for calls, meetings, memos, and other
spoken records. It preserves the source, improves record quality, recommends
where information should go, requires approval before downstream action, and
records proof of what landed.

Use Pavo when a recording should become more than a note: an archive, issue,
CRM draft, email draft, reminder, blocked route, or policy candidate.
```

Use cases:

- import local or Plaud recordings
- preserve source evidence
- review transcript and speaker uncertainty
- generate routing packets
- approve, edit, or block destination actions
- create destination manifests
- develop scenario fixtures for future Scout and Land behavior

Trust statement:

```text
Pavo is designed around approval before action. It should not write to
downstream systems without a reviewable route, destination preview, and user
approval unless a scoped policy has been explicitly approved.
```

Limitations:

- Pavo is not a generic meeting bot.
- Pavo is not a compliance archive by default.
- Pavo should not be used for blind outbound communication.
- Pavo's transcript and route confidence must be reviewed for high-risk uses.
- Destination adapters should be enabled only when their proof and retry
  behavior is understood.

Install-page CTA:

```text
Start by reviewing one recording and one route.
```

Marketplace screenshot priorities:

1. Flight Path overview.
2. Record detail with source evidence.
3. Routing packet review.
4. Approval queue.
5. Destination manifest.

The marketplace listing should feel more like an operational tool than a
generic AI app. The buyer should understand that Pavo is opinionated about
state, proof, and approval.

## R16: First 30 Customer Conversations

The first 30 conversations should test the product thesis, not merely collect
compliments. Each call should be treated as a Pavo scenario candidate.

Conversation goal:

```text
Find out whether the buyer has valuable recordings that do not reliably become
the right work.
```

Questions to ask every prospect:

1. What conversations do you record?
2. What should happen after those conversations?
3. What happens today?
4. What gets missed?
5. What gets routed to the wrong place?
6. What would be unsafe to automate?
7. Who approves follow-up?
8. What evidence would make a recommendation trustworthy?
9. Which destination would you want first?
10. What would make you stop using the product?

Call notes should classify the prospect:

- capture-heavy but routing-light
- routing-heavy but low sensitivity
- high sensitivity and high routing value
- personal administration use case
- team workflow use case
- governed workflow use case
- weak-fit transcription-only use case

Each call should produce:

- one scenario title
- one source type
- one likely destination
- one risky destination
- one approval owner
- one evidence requirement
- one gotcha
- one next demo artifact

Example classification:

```text
Prospect: founder-led B2B team
Source: customer calls and founder voice memos
Likely destination: Linear, CRM, Drive
Risky destination: Slack and outbound customer email
Approval owner: founder first, later CS lead
Evidence requirement: quote spans and account mapping
Gotcha: customer complaint becomes overbroad roadmap commitment
Next artifact: customer-call demo with blocked Slack route
```

The first 30 conversations should update the product book. Pavo's product canon
should grow from real scenario pressure. If buyers repeatedly ask for the same
route, that route deserves an adapter plan. If buyers repeatedly fear the same
failure, that failure deserves a gotcha fixture. If buyers do not understand a
term, the term should be renamed or explained differently.

## R17: Marketing Metrics

Marketing metrics should measure whether the category is becoming clearer and
whether buyers understand approval-gated routing.

Top-of-funnel metrics:

- homepage visitor to "review a recording" CTA click
- percentage of visitors who view Flight Path
- percentage of visitors who view demo scenario
- demo-request conversion by persona
- reply rate to "bring one recording" outreach

Message clarity metrics:

- buyer can explain Pavo back as more than notes
- buyer names a real destination during discovery
- buyer names a risky route without prompting
- buyer understands approval before action
- buyer asks about destination proof

Sales quality metrics:

- percentage of calls with multiple destination systems
- percentage of prospects with review owner identified
- percentage of prospects with concrete first recording
- percentage of prospects disqualified as transcription-only
- percentage of demos that produce a real scenario

Product-learning metrics:

- new gotchas discovered per ten calls
- repeated route requests by destination
- repeated source types by persona
- blocked route acceptance rate
- Home policy interest by buyer type

Bad marketing metrics:

- raw signups without scenario quality
- transcript-minute volume without downstream routing
- number of integrations promised
- demos won by implying blind automation
- conversion driven by unsupported compliance claims

The most important early marketing metric:

```text
Can the buyer bring one recording and name where it should have gone?
```

If the answer is yes, Pavo has a live wedge. If the answer is no, the buyer may
like the idea but not have immediate pull.

## R18: Launch Risks And Countermeasures

Risk: buyers hear "meeting notes."

Countermeasure:

- lead every demo with the downstream approval queue
- show multiple destinations
- show a blocked route
- ask discovery questions about what happens after notes

Risk: buyers hear "automation" and expect zero review.

Countermeasure:

- make approval visible in the first screen
- describe Home as policy proposals, not silent automation
- show how reviewed history can reduce review over time

Risk: buyers worry about privacy.

Countermeasure:

- show private archive mode
- show narrow routes from sensitive records
- show redaction before destination preview
- avoid privacy claims beyond implemented architecture

Risk: buyers ask for every integration immediately.

Countermeasure:

- sell the source-to-approved-outcome loop first
- prioritize the first destination that proves value
- use export and draft modes before direct writes when needed

Risk: Pavo becomes an archive dump.

Countermeasure:

- measure records cleared to outcomes
- distinguish retained evidence from unresolved queue items
- use review aging and route status

Risk: Pavo creates approval fatigue.

Countermeasure:

- group low-risk approvals
- explain confidence and evidence clearly
- let users reject routes quickly
- promote reviewed patterns into Home candidates only when scoped

Risk: Pavo overlearns from early users.

Countermeasure:

- require explicit policy approval
- keep policy scope narrow
- preserve rejected examples
- show why a future recommendation used a prior decision

Risk: demos overstate current implementation.

Countermeasure:

- label roadmap surfaces clearly
- separate product vision from shipped capability
- use marketplace checks and test evidence as proof
- maintain the product book as the canonical ambition, not a fake ship claim

## R19: Better Challenge To The Product Narrative

The strongest version of Pavo should survive hard criticism. The product should
challenge itself before customers do.

Challenge:

```text
Is Pavo just a complicated way to make tasks from calls?
```

Better answer:

```text
If Pavo only makes tasks, it is too small. The product is about deciding what a
spoken record is allowed to become: evidence, task, note, draft, blocked route,
policy candidate, or retained archive. Task creation is one Land outcome, not
the product.
```

Challenge:

```text
Will users really approve routes?
```

Better answer:

```text
Users already approve implicitly by manually copying, editing, sending, and
filing. Pavo makes that approval explicit and faster. The product must earn use
by making review easier than manual follow-up.
```

Challenge:

```text
Why would this not be built into every recorder?
```

Better answer:

```text
Some capture tools will add routing features. Pavo's opportunity is to be
source-agnostic and destination-aware. People will have recordings from many
places, and the harder problem is not capture. It is governed routing across
work systems.
```

Challenge:

```text
Why would this not be built into every CRM?
```

Better answer:

```text
CRM is one important destination, especially for sales and customer success.
But many spoken records should also become product issues, research evidence,
private reminders, archives, email drafts, or blocked actions. Pavo sits before
the destination decision.
```

Challenge:

```text
Does approval slow down the magic?
```

Better answer:

```text
For low-risk notes, maybe. For high-value records, approval is what makes the
magic usable. The product should reduce approval effort, not pretend judgment
is unnecessary.
```

Challenge:

```text
Can Pavo avoid becoming a half-built integration platform?
```

Better answer:

```text
Only if the product treats destination adapters as proof surfaces, not feature
checklist items. Each adapter needs preview, approval, idempotency, failure
state, and manifest. A shallow integration that cannot prove what happened is
not a real Pavo Land path.
```

Challenge:

```text
What if users want search and memory more than routing?
```

Better answer:

```text
Search and memory are useful, but Pavo should not collapse into Omni. Pavo
owns the path from source to approved work. Memory systems can be destinations
or complements. The routing boundary keeps Pavo focused.
```

Challenge:

```text
What if the product is too subtle to market?
```

Better answer:

```text
Then demos must carry the story. A buyer may not understand approval-gated
routing from words alone, but they can understand one call becoming an archive,
an issue, a CRM draft, and a blocked Slack route.
```

Challenge:

```text
What would make Pavo fail?
```

Better answer:

```text
Pavo fails if it becomes a note app, if it writes without enough proof, if it
creates another queue nobody clears, if it promises compliance before controls,
if destination adapters are shallow, or if Home learns too broadly. The product
should keep these failure modes visible in docs, tests, and demos.
```

This challenge section should remain part of the marketing canon because it
prevents the story from becoming soft. Pavo's pitch is stronger when it admits
the product's hard parts and then shows the control surfaces that answer them.

# Appendix S: Implementation Roadmap Mapping

This appendix connects the product book to the actual Pavo codebase and Linear
roadmap. The product canon is larger than the current implementation. That is
expected. The important thing is to keep the gap explicit, so future work can
move from working audio/proof tools toward the full Flight Path without
pretending the Scout, Land, and Home layers already exist.

Current source of truth:

- Repo: `/Users/dshanklin/repos-eidos-agi/pavo`
- Product spine: `/Users/dshanklin/repos-eidos-agi/pavo/docs/product.md`
- Product book: `/Users/dshanklin/repos-eidos-agi/pavo/docs/pavo-product-book.md`
- Codex skill: `/Users/dshanklin/repos-eidos-agi/pavo/skills/use-pavo/SKILL.md`
- Marketplace plugin: `/Users/dshanklin/repos-eidos-agi/eidos-marketplace/plugins/pavo`
- Marketplace audit: `/Users/dshanklin/repos-eidos-agi/eidos-marketplace/AUDITS/pavo.md`

The current codebase is strongest in Nest and Tune. It has early worker and
plugin surfaces. It has product docs for Scout, Land, and Home, but those layers
still need real modules, contracts, persistence, UI, and adapter behavior.

## S1: Current Module Map

Current Pavo modules:

| Path | Current Responsibility | Flight Path Fit |
| --- | --- | --- |
| `pavo/config.py` | Local Pavo home, config path, state path, directory creation | Nest foundation |
| `pavo/plaud.py` | Plaud CLI wrapper, account/audio URL/list surfaces | Nest source adapter |
| `pavo/download.py` | Save remote audio locally with hashes/manifests | Nest source preservation |
| `pavo/audio.py` | Audio readiness checks for local tools | Tune readiness |
| `pavo/transcribe.py` | Plaud/local audio transcription, processing, decomposition, manifest writing | Tune core |
| `pavo/overlap.py` | Mixed speaker region separation and fingerprint evidence | Tune evidence |
| `pavo/review.py` | Human review sheets, browser review bundles, corrections, gates, rerun commands | Tune review and early approval mechanics |
| `pavo/render.py` | Captioned video rendering from processed transcript artifacts | Tune inspection artifact |
| `pavo/proof.py` | Proof reports and fixture status across real media and tests | Cross-stage evidence |
| `pavo/worker.py` | Private worker health/status/tick API | Future always-on Nest/Tune runner |
| `pavo/cli.py` | Command-line control surface over local Pavo workflows | Operator interface |
| `tests/` | Unit and proof tests for current local behavior | Regression surface |

The product book should treat those paths as current implementation evidence,
not as final product architecture. The current code can preserve source media,
invoke transcription and decomposition, generate human review bundles, and
produce proof reports. It does not yet have a durable routing packet store, a
proper approval queue for destination writes, destination adapters, or Home
policy memory.

## S2: Nest Implementation Map

Nest is the closest to real implementation today.

Current Nest pieces:

- `pavo/config.py` creates the local Pavo home and state directories.
- `pavo/plaud.py` wraps Plaud CLI discovery and audio URL retrieval.
- `pavo/download.py` saves audio and computes source proof.
- `pavo/cli.py` exposes `pavo plaud me`, `pavo plaud files`, `pavo plaud
  audio-url`, and `pavo plaud download`.
- `README.md` and `skills/use-pavo/SKILL.md` document the local-first, secrets
  out-of-config operating model.

Existing Linear anchors:

- `EID-380`: harden Plaud recording discovery and download ledger.
- `EID-381`: expand doctor coverage across Plaud CLI, Plaud MCP, and local
  config.
- `EID-382`: implement sync index for known Plaud recordings.
- `EID-383`: design and implement Google Drive artifact layout.
- `EID-384`: add duplicate-safe Google Drive upload manifest.
- `EID-385`: implement one-command Plaud to Drive sync.

Missing Nest contracts:

- `RecordingRecord`: stable object for source system, source id, title, owner,
  participants, capture time, import time, audio artifact, hash, byte size,
  retention class, sensitivity class, and source permissions.
- `SourceArtifact`: durable object for original media and non-secret source
  metadata.
- `SourceAdapter`: interface implemented by Plaud, local files, meeting exports,
  Fireflies or other future sources.
- `SourceLedger`: local or server-side index of known recordings, hashes,
  download status, transcript status, and archive status.
- `ConsentState`: explicit field, not inferred from wishful thinking.

Recommended next implementation order:

1. Finish the local sync index (`EID-382`) so Nest has durable inventory.
2. Harden Plaud discovery and download ledger (`EID-380`) so every Plaud source
   has repeatable proof.
3. Add Drive artifact layout and idempotent upload manifest (`EID-383` and
   `EID-384`) so Nest can create durable archives.
4. Add `pavo sync --dry-run` and bounded runs (`EID-385`) so capture becomes a
   daily command instead of a manual recipe.

Nest should not wait for Scout. A safely nested record is useful even if the
product never routes it. That is why Nest can ship as a valuable foundation:
real recordings stop disappearing.

## S3: Tune Implementation Map

Tune is the current technical center of gravity. The repo already has a real
audio intelligence loop and review loop.

Current Tune pieces:

- `pavo/transcribe.py` invokes `eidos-transcribe` for Plaud and imported media.
- `pavo/transcribe.py` writes `pavo-transcribe-manifest.json`,
  `pavo-process-manifest.json`, and `pavo-decompose-manifest.json` style proof.
- `pavo/overlap.py` creates separated-overlap evidence for mixed speaker
  regions.
- `pavo/review.py` creates review sheets, browser-safe bundles, review pages,
  import validation, corrections, gate reports, and rerun commands.
- `pavo/proof.py` and `tests/test_proof.py` maintain real-media proof reports
  for Plaud, Conan, overlap, accepted stems, and review gates.
- `pavo/render.py` turns tuned transcript evidence into visual inspection
  artifacts.

Existing Linear anchors:

- `EID-389`: add retranscription policy when `eidos-transcribe` improves.
- `EID-390`: wire dictionaries and context profiles into transcription runs.
- `EID-391`: evaluate speaker fingerprints and noise cleanup for Plaud audio.
- `EID-393`: transcribe accepted separated stems and merge evidence.

Missing Tune contracts:

- `EvidenceRecord`: normalized transcript, speaker, source-span, correction,
  stem, review-note, and confidence objects.
- `TranscriptVersion`: immutable version object with engine, command, context,
  model, preprocessing, created time, and stale reason.
- `SpeakerIdentityEvidence`: separate from a speaker label; should record why a
  label is believed and whether it has been reviewed.
- `ReviewDecision`: reusable object for approval, rejection, correction, and
  uncertainty notes, not only anchor review rows.
- `TuneStatus`: machine-readable status that can say `tuned`, `needs_review`,
  `reviewed`, `stale`, `partial`, or `unsafe_for_routing`.

Recommended next implementation order:

1. Add context profiles (`EID-390`) so terms and dictionaries are not passed by
   hand for every recording.
2. Add retranscription staleness (`EID-389`) so improved models or dictionaries
   do not silently conflict with older evidence.
3. Convert review decisions into a generic evidence object that Scout can cite.
4. Promote selected proof reports into fixtures that future Scout tests can
   consume.

Tune should keep one discipline: better transcription is not the final product
unless it changes routing safety. A perfect transcript that cannot support a
reviewable routing packet is still incomplete Pavo work.

## S4: Scout Implementation Map

Scout is mostly product canon today. The book has routing-packet schemas,
scenario chapters, UI specs, gotcha fixtures, and evidence-bundle examples, but
the repo does not yet expose a `pavo/scout.py` module or persisted routing
packet store.

Current Scout-adjacent pieces:

- `docs/product.md` defines the routing packet as the central product object.
- Appendix E defines packet schema and policy examples.
- Appendix O defines an end-to-end evidence bundle with routing packet and
  approval decisions.
- Appendix P defines gotchas that should become routing fixtures.
- Appendix Q adds edge-case scenario chapters for route safety.
- `pavo/review.py` proves Pavo can build human review surfaces, but those are
  Tune review surfaces, not destination-routing review yet.

Existing Linear anchors:

- `EID-406`: define Pavo normalized recording and Omni routing API.
- `EID-407`: scaffold Eidos Pavo web app with Supabase storage model.
- `EID-411`: UI product specs for approval-gated routing.
- `EID-412`: end-to-end evidence bundle example.
- `EID-413`: gotcha and test-fixture matrix.

Missing Scout modules:

- `pavo/records.py`: normalized recording and evidence object models.
- `pavo/packets.py`: routing packet schema, validation, versioning, and
  serialization.
- `pavo/scout.py`: recommendation engine boundary that consumes tuned evidence
  and emits packet candidates.
- `pavo/policy.py`: rule and policy-candidate evaluation, separate from hidden
  automation.
- `pavo/approval.py`: approval state machine for packet actions.
- `pavo/fixtures.py`: scenario fixtures generated from Appendix A, H, Q, and P.

Minimum Scout contract:

```json
{
  "packet_id": "routepkt_...",
  "recording_id": "rec_...",
  "packet_version": 1,
  "source_refs": [],
  "evidence_refs": [],
  "summary": "",
  "suggested_routes": [],
  "blocked_routes": [],
  "approval_requirements": [],
  "sensitivity": {},
  "created_at": "",
  "created_by": "pavo.scout"
}
```

Minimum Scout behavior:

- never emit a route without source or evidence references
- mark low-confidence speaker or transcript regions as review-required
- recommend "no action" or "private archive" as first-class outcomes
- separate destination choice from destination write
- produce deterministic packet JSON for fixtures
- preserve the reason a route was blocked

Recommended next implementation order:

1. Implement `pavo/records.py` and `pavo/packets.py` with tests only; do not
   write to destinations yet.
2. Convert Appendix O into a checked fixture.
3. Convert the top five gotchas from Appendix P into Scout tests.
4. Implement a rules-only Scout prototype that can emit simple archive,
   Linear-draft, CRM-draft, private, and blocked route candidates from fixture
   inputs.
5. Connect `EID-406` to the normalized recording and route-decision API.

Scout should ship before Land. If Pavo cannot create a trustworthy packet, it
has no business writing to external systems.

## S5: Land Implementation Map

Land is the destination-write layer. It should execute approved actions and
return proof. The current repo does not yet have a destination adapter module.
Drive sync is planned in M2, worker status exists in `pavo/worker.py`, and
Linear/API routing is represented in docs and Linear backlog.

Current Land-adjacent pieces:

- `pavo/worker.py` exposes private `/v1/status` and `/v1/tick`.
- `EID-405` shipped the private Railway Pavo worker.
- `EID-383`, `EID-384`, and `EID-385` define Drive archive and sync work.
- Appendix F defines destination adapter playbooks.
- Appendix O defines destination write manifests.
- Appendix N defines the manifest/proof UI surface.

Missing Land modules:

- `pavo/destinations/base.py`: adapter protocol.
- `pavo/destinations/drive.py`: archive/media/transcript/manifest writes.
- `pavo/destinations/linear.py`: approved issue creation or draft creation.
- `pavo/destinations/crm.py`: CRM draft/write boundary, initially probably
  draft-only.
- `pavo/destinations/email.py`: email draft boundary, never send without
  explicit approval.
- `pavo/destinations/slack.py`: draft or blocked route boundary before any
  channel write.
- `pavo/land.py`: executor that consumes approved packet actions and writes
  destination manifests.
- `pavo/idempotency.py`: duplicate-safe write keys.

Minimum Land contract:

```json
{
  "manifest_id": "land_...",
  "packet_id": "routepkt_...",
  "route_id": "route_...",
  "destination": "linear",
  "action": "create_issue",
  "approval_id": "approval_...",
  "idempotency_key": "recording_hash:route_id:packet_version",
  "status": "landed",
  "destination_refs": [],
  "request_preview": {},
  "response_summary": {},
  "created_at": ""
}
```

Minimum Land behavior:

- refuse unapproved routes
- refuse stale packets unless reapproved
- write idempotently
- return destination ids and URLs when available
- preserve failed, partial, skipped, and blocked states
- support dry-run previews
- redact secrets and temporary signed URLs from manifests
- make outbound communication draft-only until explicitly approved

Recommended next implementation order:

1. Finish Drive archive Land because it is the safest first destination.
2. Add Linear draft/create from an approved packet.
3. Add a manifest viewer and proof report for Land.
4. Add retries and idempotency before adding more destinations.
5. Add CRM and email as draft-first adapters.
6. Treat Slack as a high-risk destination that starts with blocked/draft
   behavior.

Land is where product risk becomes real. The implementation should be narrower
than the story until manifests, idempotency, and approval checks are boring.

## S6: Home Implementation Map

Home is the least implemented and should remain conservative. It should learn
from approvals, rejections, corrections, and exceptions, but it should not hide
policy changes or silently broaden automation.

Current Home-adjacent pieces:

- Product canon in `docs/product.md` and this book.
- Appendix M status vocabulary.
- Appendix E policy examples.
- Appendix O policy candidate example.
- Appendix N Home review UI spec.
- Appendix P gotcha matrix, especially policy overlearning and approval
  fatigue.

Missing Home modules:

- `pavo/home.py`: policy candidate generation and review boundary.
- `pavo/policies.py`: approved policy storage, scope, versioning, and
  explanation.
- `pavo/learning.py`: pattern extraction from reviewed routing history.
- `pavo/audit.py`: policy change log and explanation history.

Minimum Home contract:

```json
{
  "policy_candidate_id": "polcand_...",
  "derived_from": ["approval_...", "rejection_..."],
  "scope": {
    "source_type": "customer_call",
    "destination": "linear",
    "account_id": "acct_..."
  },
  "proposal": "Create Linear draft for product blockers after review.",
  "limits": ["no outbound messages", "commercial claims still require review"],
  "status": "candidate",
  "requires_approval": true
}
```

Minimum Home behavior:

- propose policies, never silently activate them
- scope policies narrowly
- preserve rejected examples
- include examples that support and limit the policy
- allow revocation
- explain why a later recommendation used a policy
- keep personal/private records from training broad team behavior unless
  explicitly allowed

Recommended next implementation order:

1. Store approval and rejection history in a durable shape.
2. Generate read-only policy candidates from repeated route decisions.
3. Build Home review UI before policy execution.
4. Enable policy-assisted Scout recommendations before policy-executed Land.
5. Add policy revocation and stale-policy detection.

Home should be marketed as learning only after the UI and audit model exist.
Until then, Home is a product direction and schema, not shipped behavior.

## S7: Web App And Worker Architecture

The current local CLI is valuable, but the full product needs a web approval
queue and server-side state.

Existing anchors:

- `EID-405`: private Railway worker shipped.
- `EID-407`: scaffold Eidos Pavo web app with Supabase storage model.
- `pavo/worker.py`: current private worker with health, status, and manual tick.

Recommended architecture:

```text
Local/source adapter
-> Nest source ledger
-> Tune worker jobs
-> evidence store
-> Scout packet generation
-> web approval queue
-> Land adapter jobs
-> destination manifests
-> Home policy candidates
```

Vercel/Supabase/Railway split:

- Vercel: web app, approval UI, dashboard, public product surfaces.
- Supabase Postgres: recordings, artifacts, evidence, routing packets,
  approvals, destination manifests, policies.
- Supabase Storage: source media only when user-approved and architecture is
  ready; local-first remains valid for sensitive personal records.
- Railway workers: long-running media import, transcription, decomposition,
  routing jobs, destination adapter execution.
- Local CLI: trusted operator path, private imports, proof generation, and
  fallback workflow.

Initial Supabase tables:

- `recordings`
- `source_artifacts`
- `evidence_records`
- `transcript_versions`
- `review_decisions`
- `routing_packets`
- `route_candidates`
- `approval_decisions`
- `destination_manifests`
- `policy_candidates`
- `approved_policies`
- `audit_events`

Architecture warning:

Pavo should not move sensitive local recordings into cloud storage merely to
make the web app easier. The product needs explicit storage mode: local-only,
cloud archive, team shared, governed. Storage mode is part of the routing and
approval model.

## S8: Docs And Marketplace Migration Notes

The docs and marketplace bundle should track the same vocabulary.

Current docs that must stay aligned:

- `README.md`: short public/product repo framing.
- `docs/product.md`: compact product spine and Flight Path contract.
- `docs/pavo-product-book.md`: long-form canon.
- `docs/proof.md`: current implementation proof and real-media status.
- `docs/proof-matrix.md`: current proof plan.
- `docs/media-tests.md`: real media fixtures.
- `docs/backstory.md`: origin and motivation.
- `skills/use-pavo/SKILL.md`: agent operating instructions.

Marketplace migration rules:

- The marketplace plugin should stay thin and point to the Pavo CLI/package.
- Marketplace docs should not claim Scout/Land/Home shipped until implemented.
- Plugin audit should prove manifest id, copied bundle, source path, and tests.
- Python 3.14 should remain the verified runtime on the Mac mini until the
  codebase stops using syntax unsupported by the default Python 3.9.
- Any docs change that changes Flight Path vocabulary should update README,
  `docs/product.md`, skill instructions, and marketplace copy together.

Recommended final-docs task:

- Use `EID-417` to do the final alignment pass after the manuscript reaches
  editorial depth.
- Rerun Pavo tests, marketplace publish/check, and marketplace tests.
- Record final word count and source paths in Linear.

## S9: Implementation Gap Register

Gap: normalized recording model.

Risk:

- Scout and Land will each invent their own source object.

Needed:

- `RecordingRecord`, `SourceArtifact`, `EvidenceRecord`, and fixture tests.

Linear anchor:

- `EID-406`.

Gap: routing packet validator.

Risk:

- AI recommendations become loose prose instead of durable product state.

Needed:

- schema, validator, deterministic JSON serialization, packet versioning.

Linear anchor:

- new implementation issue after `EID-415`, likely under the Pavo project.

Gap: approval state machine.

Risk:

- Land cannot reliably distinguish draft, approved, rejected, stale, reversed,
  and blocked routes.

Needed:

- `ApprovalDecision`, `ApprovalRequirement`, state transitions, reversal
  behavior, stale packet handling.

Linear anchor:

- can be paired with `EID-407` web app scaffold or created as a separate
  implementation issue.

Gap: destination adapter protocol.

Risk:

- every integration implements approval, idempotency, error handling, and
  proof differently.

Needed:

- base adapter contract, dry-run preview, idempotency key, manifest return,
  retry taxonomy.

Linear anchor:

- `EID-383`, `EID-384`, `EID-385` for Drive; future issues for Linear, CRM,
  email, and Slack.

Gap: route fixture ledger.

Risk:

- scenario docs stay prose and do not protect behavior.

Needed:

- convert Appendices A, H, Q, and P into JSON fixtures with expected packet,
  approval, Land, and Home outputs.

Linear anchor:

- `EID-409`, `EID-412`, `EID-413` provide the doc basis; implementation issue
  still needed.

Gap: Home policy audit.

Risk:

- learning becomes invisible automation.

Needed:

- policy candidates, explicit approval, examples, limits, revocation, audit
  events.

Linear anchor:

- new implementation issue after Scout/Land primitives exist.

## S10: Build Sequence From Here

The next implementation sequence should be:

1. Finish Nest local inventory and Drive archive work: `EID-380` through
   `EID-385`.
2. Finish Tune repeatability: `EID-389`, `EID-390`, `EID-391`.
3. Define normalized recording and routing API: `EID-406`.
4. Add packet and evidence schemas in the repo with fixture tests.
5. Scaffold the web approval queue and storage model: `EID-407`.
6. Implement rules-only Scout against fixtures.
7. Implement Drive Land as the first safe destination.
8. Implement Linear Land for approved issue creation or draft creation.
9. Add Home policy candidates as read-only suggestions.
10. Only then add higher-risk destinations such as CRM writes, email, and Slack.

This ordering keeps Pavo honest. The product book can describe the full Flight
Path, but the implementation should move in trust order: source, evidence,
packet, approval, proof, policy.

# Part 8: Expanded Book Chapters

The earlier sections define Pavo's vocabulary, mechanics, scenarios, risks, and
roadmap. This part turns those pieces into fuller book chapters. These chapters
are written for a reader who may not already share the Pavo assumptions: a
founder, operator, product lead, engineer, investor, design partner, or future
teammate who needs to understand not only what Pavo does, but why it deserves
to exist as a product category.

The central argument is simple:

```text
The world is capturing more spoken records. The missing product layer is the
approved path from those records to durable work.
```

That argument has consequences. Pavo cannot be a generic note taker. It cannot
be a black-box transcription wrapper. It cannot be an automation tool that
writes wherever the model points. It has to be a control surface for judgment:
preserve the source, improve the record, recommend routes, ask for approval,
prove what landed, and learn only through reviewable policy.

## Chapter T1: The Catch Fence Problem

Every organization already has a catch fence. Most of them do not call it that.
The catch fence is the messy boundary where real-world information first enters
the work system. A customer calls. A founder records a voice memo. A product
manager interviews a user. A support lead joins an escalation. A school
administrator explains a child's plan. A field operator records a safety note.
A salesperson hears a buying signal. A doctor office gives instructions. A
team holds a strategy discussion that determines what happens next.

The modern problem is not that these conversations vanish instantly. Many of
them are recorded. Devices record. Meeting platforms record. Phones record.
Call tools record. Wearable and pocket devices record. AI tools can summarize.
The problem is that capture does not create completion. It creates a source
that still needs interpretation, routing, permission, and proof.

The naive version of the future says that once everything is recorded, the work
is solved. The recording exists, therefore the memory exists. The transcript
exists, therefore the action exists. The summary exists, therefore the decision
exists. That story is attractive because it turns a hard operating problem into
a file-generation problem. It is also false.

A recording can exist and still be useless. A transcript can exist and still be
wrong. A summary can exist and still be too vague to route. A task can be
created and still be assigned to the wrong team. A CRM note can be written and
still overstate what the customer said. A Slack message can be posted and still
share sensitive information with the wrong audience. A personal call can be
summarized and still leak context that should have stayed private. Capture is
not completion.

Pavo starts with that truth. It treats recording as the beginning of an
operational path, not the end. The catch fence is where a spoken record enters
Pavo. The Flight Path is how that record becomes useful without becoming
unsafe.

Nest answers the first question: do we have the source? Not a temporary link,
not only a vendor summary, not a screenshot of notes, but the real durable
source or a durable enough local copy. If the answer is no, nothing downstream
is stable. Pavo should not reason over evidence that it cannot preserve.

Tune answers the second question: is the record trustworthy enough to use? This
does not mean perfect. It means the product exposes uncertainty. It knows when
a speaker label is weak. It knows when a word was uncertain. It knows when
overlap made the sentence hard to attribute. It knows when a human correction
changed the record. It does not flatten messy audio into false confidence.

Scout answers the third question: what could this record become? This is the
moment where Pavo stops being a transcription tool. A record might become an
archive, a task, an issue, a CRM note, an email draft, a reminder, a research
evidence object, a blocked route, a policy candidate, or nothing at all. Scout
does not write. It prepares a decision.

Land answers the fourth question: what did the user approve, and what actually
happened? A route without proof is an aspiration. A landed route has a
destination manifest. Pavo knows whether Drive received the archive, whether
Linear created the issue, whether CRM accepted the draft, whether Slack was
blocked, whether a retry happened, and whether the packet became stale.

Home answers the fifth question: what should Pavo learn from the reviewed
decision? It does not silently convert one approval into broad automation. It
proposes scoped policy. It remembers that this kind of customer blocker often
creates a Linear draft, that personal records stay private by default, that
commercial claims require review, and that some destinations are never safe
without explicit approval.

The catch fence problem is easy to underestimate because it hides inside
ordinary administrative work. People call it follow-up. They call it note
taking. They call it remembering. They call it updating the CRM. They call it
filing the recording. They call it sending the recap. They call it creating the
ticket. They call it "I need to get back to that call." The naming varies, but
the structure is the same: spoken information has entered the world, and now it
needs to become the right kind of work.

Pavo's opportunity is to make that structure visible. Once visible, it can be
designed. Once designed, it can be tested. Once tested, it can be trusted.

## Chapter T2: Why Notes Are Not Enough

Meeting notes solve a real problem. A good note helps a person remember what
happened. It gives shape to a discussion that would otherwise be scattered
across memory, chat, and calendar context. Pavo should not dismiss notes. Pavo
depends on the same desire that made notes valuable: people want conversations
to survive the moment in which they happened.

But the note is not the whole job. In important workflows, the note is usually
an intermediate artifact. It is useful because it helps someone do something
else.

A customer-success note is useful if it updates account understanding, reveals
renewal risk, triggers an escalation, or preserves a customer quote. A product
interview note is useful if it strengthens evidence, clarifies a pain point,
supports a discovery issue, or prevents a roadmap mistake. A sales note is
useful if it updates qualification, captures buyer language, schedules a
follow-up, or avoids an unsupported promise. A personal administration note is
useful if it preserves dates, names, documents, obligations, and next steps
without exposing private context. The note is not the destination. The work is
the destination.

This is why generic AI notes often feel impressive and incomplete at the same
time. They can produce a coherent summary. They can list action items. They can
extract decisions. They can sound polished. But after the wow moment, the user
still asks:

- Which action items are real commitments?
- Which statements need source evidence?
- Which system should receive this?
- Which details should be redacted first?
- Which claims are too uncertain?
- Which routes are safe to automate?
- Which routes require approval?
- What proof exists after the write?

Those questions are not note-taking questions. They are routing questions. They
belong to Pavo.

The difference matters because products optimize around the object they think
is central. If the central object is the note, the product optimizes for note
quality: concise summaries, templates, action items, themes, speaker bullets,
share links, meeting recaps, and search. Those are useful features. They do not
force the product to answer where the information belongs.

If the central object is the routing packet, the product optimizes differently.
It asks what evidence supports the route. It tracks sensitivity. It previews
destination writes. It blocks unsafe actions. It records approvals and
rejections. It writes manifests. It learns scoped policy. It makes "do not
route" a valid outcome. It treats the source as the truth anchor and the note
as one evidence artifact among many.

This is why Pavo's product object should not be a transcript or a summary. It
should be a packet that can cite the transcript, cite the audio, cite review
notes, cite speaker evidence, cite redaction choices, and then propose what
should happen. The packet is where judgment lives.

The distinction also changes the user interface. A note product can put the
summary at the center and hide the rest behind tabs. Pavo should put the
approval decision at the center. The user should see: source, evidence,
recommendation, destination preview, sensitivity, approval state, and proof.
The summary can help, but it should not dominate the decision.

The note product asks:

```text
What happened in the meeting?
```

Pavo asks:

```text
What is this record allowed to become?
```

That second question is more demanding. It is also more valuable when mistakes
matter.

## Chapter T3: The Approval Boundary

Approval is often described as friction. In consumer products, friction is
usually bad. In serious operational products, friction can be the difference
between usable automation and cleanup work. Pavo has to be precise about this:
approval is not valuable because it slows the product down. Approval is
valuable because it concentrates human judgment at the point where a
recommendation becomes a real-world write.

The approval boundary is the line between "Pavo thinks this should happen" and
"Pavo did this." Everything before the boundary can be generous: Pavo can
generate options, compare destinations, cite evidence, propose drafts, detect
risks, and explain alternatives. Everything after the boundary must be
disciplined: the approved route is the only route that lands, the write is
idempotent, the destination response is captured, and the manifest proves the
result.

This boundary is especially important because spoken records are full of soft
edges. People hedge. They joke. They change their minds. They interrupt. They
refer to context outside the call. They say "we should probably" when they mean
"maybe." They say "I think" when they are uncertain. They use names that sound
alike. They mention confidential details in passing. They ask questions that
sound like commitments. They brainstorm ideas that should not become roadmap
items. They complain in ways that deserve empathy but not immediate product
promises.

An AI system can help interpret those records, but it should not pretend that
interpretation is identical to permission. The model may recommend that a
customer complaint become a Linear issue. That can be useful. It should not
therefore write an overconfident issue title that says "Customer requires
feature X for renewal" unless the evidence supports it and a user approves it.

The approval boundary also protects the user from the product's own ambition.
Pavo will naturally want to become more helpful. It will want to route faster.
It will want to learn patterns. It will want to reduce review. Those are good
directions if earned. They are dangerous if hidden. Home must therefore remain
reviewable: Pavo proposes policies before it applies them. The user can see
examples, limits, scope, and exceptions. A policy can say: "For customer calls
with product blockers, create a Linear draft with evidence spans." It should
not silently become: "Write product commitments from any customer call."

Approval has levels. Not every route requires the same review.

Low-risk approval might be a one-click archive to a private Drive folder. The
source is preserved, the destination is expected, and the action does not
publish sensitive claims broadly. Medium-risk approval might be a Linear draft
that a product manager edits before creating. High-risk approval might be a CRM
write, legal-adjacent summary, customer-facing email, Slack post, or anything
that can change another person's understanding or obligations.

Pavo should make those levels visible. A route can be approved as-is, edited
then approved, approved as draft-only, rejected, blocked by policy, returned to
Tune, marked private, or deferred. Each decision teaches Pavo something. A
rejection is not a failure; it is training data for the routing layer. A block
is not a failure; it is proof that Pavo can withhold action.

The approval boundary becomes more powerful when the review surface is good.
Bad approval UI creates fatigue. Good approval UI narrows the decision. The
user should not have to reread the whole transcript to approve a route. The
packet should show the evidence span, the proposed write, the sensitive fields,
the confidence markers, the destination, the policy reason, and the expected
manifest. The best review question is not "Do you trust the AI?" It is "Is this
specific action allowed to land in this specific place in this specific form?"

That question is the heart of Pavo.

## Chapter T4: The Source Is The Trust Anchor

Every Pavo route should be able to answer a basic question:

```text
Where did this claim come from?
```

If the answer is "the model said it," Pavo is not doing its job. A model can
help generate the route, but it is not the source. The source is the recording,
the transcript span, the speaker evidence, the review note, the correction, the
manifest, or the destination response. Pavo's trust model is source-backed
because spoken records are too easy to summarize into something smoother than
truth.

This is not only a technical preference. It is a product stance. Pavo should be
designed for users who care about evidence. A founder may need to know why a
follow-up was created. A product manager may need to replay the user quote. A
customer success lead may need to show the account owner what the customer
actually said. A salesperson may need to avoid turning a tentative answer into
a promise. A parent may need to remember the exact date a school administrator
gave. A field operator may need to preserve a safety concern without turning it
into an unsupported incident report.

Source-backed work means the downstream artifact can carry its lineage. A
Linear issue can link to an evidence bundle. A CRM note can include source span
references. A Drive archive can include the original media, transcript,
manifest, and review record. A blocked Slack route can explain which sentence
was too sensitive to share. A Home policy candidate can show the approvals and
rejections that produced it.

The source also protects against future improvement. Pavo will improve. Audio
models will improve. Speaker attribution will improve. Context dictionaries
will improve. If Pavo preserves the source and the manifest, old records can be
reprocessed with better tools. If Pavo only preserves a vendor summary, the
future cannot recover what was lost.

This is why Nest is not glamorous but essential. Nest is the product's memory
of reality. It captures the thing that later stages depend on. A nested record
has value even if it never reaches Scout. It is safe from link expiry. It has a
hash. It has metadata. It has a place. It can be revisited.

Tune then makes the source usable. Tuning is not only transcription. It is the
act of turning raw media into inspectable evidence. It includes speaker labels,
confidence, human corrections, overlap analysis, source-separation diagnostics,
review pages, and proof reports. A tuned record can still be partial. It can
say: "This span is uncertain." That is better than false certainty.

Scout should cite Tune. Land should cite Scout. Home should cite approvals and
rejections. The chain matters:

```text
source -> evidence -> route -> approval -> manifest -> policy candidate
```

Break the chain and Pavo becomes another AI text generator. Preserve the chain
and Pavo becomes a system of operational trust.

## Chapter T5: Why Routing Is The Product

Routing sounds technical until it is made concrete. A recorded customer call
may contain:

- a product bug
- a renewal risk
- a customer quote
- a support follow-up
- a private detail
- a vague feature idea
- a moment of confusion
- a request for an email recap
- an unsupported commercial claim

A note can summarize all of that. Routing decides what each piece is allowed
to become.

The product bug might become a Linear issue. The renewal risk might become a
CRM note. The customer quote might become research evidence. The support
follow-up might become a task. The private detail might remain archive-only.
The vague feature idea might be blocked from the roadmap. The confusion might
be tagged for discovery. The email recap might become a draft. The unsupported
claim might be rejected.

That is routing.

Routing is not merely choosing an integration. It is deciding the operational
meaning of a spoken record. The same source can produce several destinations,
each with its own risk and approval level. This is why Pavo should resist
simple integration-count marketing. A shallow product can say it connects to
twenty apps. Pavo should care whether it can safely decide what belongs in one
app.

Good routing has several properties.

It is evidence-backed. The route cites source spans, transcript rows, review
notes, speaker evidence, and manifests. If the evidence is weak, the route says
so.

It is destination-aware. A Linear issue, CRM note, Drive archive, email draft,
Slack post, and policy candidate have different shapes and risks. The route
cannot treat them as generic text sinks.

It is sensitivity-aware. Some information should not leave the archive. Some
information can be shared internally but not externally. Some information can
be summarized but not quoted. Some information can become a task but not a
customer-facing message.

It is approval-aware. The route knows whether it is ready to land, needs
review, should be draft-only, should be blocked, or should return to Tune.

It is reversible enough. If a user later reverses approval, Pavo should know
what landed and what correction is needed. It cannot erase the past, but it can
create a correction trail.

It is learnable. Repeated approvals and rejections should shape future
recommendations, but only through scoped policy. Home learns from routing
history; it does not become hidden automation.

Routing is the product because it is where Pavo turns evidence into controlled
movement. Capture creates inventory. Tune creates trust. Routing creates the
decision. Land completes the approved action. Home remembers the pattern.

## Chapter T6: The Product Must Respect Non-Action

Many AI products overvalue action. They imply that a good system should always
summarize, always assign, always draft, always send, always file, always
produce. Pavo needs a more mature posture. Sometimes the correct result is
non-action.

Non-action can mean archive-only. A sensitive personal call may need to be
preserved but not routed. A legal-adjacent interview may need evidence retained
without generating conclusions. A customer complaint may need to stay in
research until a pattern exists. A sales call may include a speculative
statement that should not enter CRM. A meeting may contain brainstorming that
should not become commitments. A field memo may be too noisy to route without
review.

If Pavo cannot represent non-action, it will create pressure toward unsafe
automation. Every record will look like it needs an output. Every output will
look like success. Metrics will drift toward "routes landed" instead of
"records handled correctly." That would be a product failure.

Correct non-action should have state. It should not disappear. Pavo should be
able to say:

- private
- archive-only
- blocked by policy
- insufficient evidence
- consent missing
- duplicate
- stale packet
- awaiting review
- returned to Tune
- rejected route
- no action needed

Each state should explain why. A blocked route with a reason is useful. A
silent absence is not.

Non-action also matters for user trust. Users will not trust Pavo because it
routes everything. They will trust Pavo when it demonstrates restraint. The
moment a user sees Pavo block a risky Slack post, refuse to write a CRM note
from uncertain evidence, or keep a personal detail private, the product becomes
more credible. Restraint is a feature.

This should shape metrics. Pavo should measure records cleared to appropriate
outcomes, not just downstream writes. An archive-only decision can be complete.
A rejected route can be complete. A blocked route can be complete. A returned
Tune request can be correct progress. The product should reward safety and
truth, not volume.

## Chapter T7: Personal And Team Records Need Different Defaults

Pavo crosses an unusual boundary. It can help with team workflows and personal
administration. That is powerful, but it creates design risk. A product that
treats every record like team work will violate personal privacy. A product
that treats every record like private memory will fail operational teams.

The answer is not to choose one forever. The answer is to make storage mode,
visibility, destination rules, and approval requirements explicit.

A personal record should default toward privacy. It may contain family,
health, school, finance, vendor, or household context. The right action might
be a reminder, an email draft, a document checklist, or no action. Pavo should
not assume that the transcript belongs in a team archive, shared search index,
or broad memory system. It should avoid turning private administrative work
into organizational data.

A team record should default toward role-appropriate sharing. A customer call
may belong to the account team, product team, and support team in different
forms. The source recording may have restricted access. A redacted quote may be
useful in research. A product blocker may become a Linear issue. A renewal risk
may belong in CRM. Team value comes from routing the right subset to the right
system.

The same person may use both modes. A founder might record a customer call at
10 a.m. and a doctor office call at 2 p.m. Pavo should not blend those worlds
because the same user owns both records. Source type, sensitivity, account,
participants, and user-selected mode matter.

This is where Pavo's Flight Path helps. Nest can preserve both personal and
team records, but with different storage classes. Tune can improve both, but
with different visibility. Scout can recommend different destinations. Land can
refuse team writes for personal records. Home can keep policy learning scoped
so personal decisions do not train team automation.

The product should make this visible in the UI:

- storage mode
- visibility
- sensitivity
- allowed destinations
- blocked destinations
- policy scope
- approval owner

Without those fields, Pavo will eventually make a trust-damaging mistake. With
those fields, Pavo can become one system that respects multiple contexts.

## Chapter T8: The First Product Should Be Narrower Than The Vision

The full Pavo vision is broad: sources, transcripts, evidence, routing,
approval, destinations, manifests, policies, web app, worker, marketplace,
personal use, team use, governed use. That breadth is useful for product
direction, but dangerous for first implementation. The first product should be
narrower than the book.

The first complete product loop should prove:

```text
one source -> one durable record -> one tuned evidence bundle -> one routing
packet -> one approved destination -> one manifest
```

That loop is enough to test the core thesis. If it works, Pavo is real. If it
does not work, adding ten destinations will not help.

The best first loop is probably:

```text
Plaud or local recording
-> local Nest with source hash
-> Tune transcript with review evidence
-> Scout packet with archive and Linear draft routes
-> approval queue
-> Drive archive Land
-> Linear draft or issue Land
-> destination manifests
```

This loop is narrow but not trivial. It touches the hardest product questions:
source preservation, transcript uncertainty, route recommendation, approval,
destination write, and proof. It also supports a strong demo: one customer call
becomes an archive, an issue draft, and a blocked route.

The first product should avoid:

- broad CRM writes
- automatic outbound email
- Slack posting
- compliance claims
- broad policy automation
- multi-tenant enterprise admin
- every capture source
- every transcription engine
- every memory/search destination

Those can come later. The first job is to make the product's trust chain work.

This restraint also helps marketing. A narrow demo is easier to believe. A
buyer can bring one recording. Pavo can show the path. The product can prove
that it did not write without approval. That proof is more valuable than a
slide with many integrations.

The vision can be large. The first ship should be sharp.

## Chapter T9: What Pavo Should Be Famous For

If Pavo succeeds, it should not be famous for having the prettiest summaries.
It should not be famous for having the most integrations. It should not be
famous for being the most aggressive automation tool. It should be famous for
making spoken records safe to use.

That reputation should be built around a few durable product promises.

First, Pavo preserves the source. The recording is not treated as a disposable
input to a summary. It is the trust anchor.

Second, Pavo exposes uncertainty. It does not hide weak speaker attribution,
low-confidence transcript spans, missing consent state, stale processing, or
destination ambiguity.

Third, Pavo recommends routes. It understands that a record can become several
different outcomes, including non-action.

Fourth, Pavo asks before action. Approval is not cosmetic. It is the product
boundary between recommendation and write.

Fifth, Pavo proves what landed. Destination manifests are not afterthoughts.
They are how Pavo earns trust.

Sixth, Pavo learns with limits. Home is policy memory, not silent automation.

These promises are understandable. They are also hard. That is good. Products
with easy promises are easy to copy. Pavo's advantage should come from taking
the hard trust work seriously and turning it into product surfaces that users
can feel.

The phrase "approved, source-backed work" should remain the north star because
it compresses those promises. Approved means the user or policy boundary
matters. Source-backed means evidence matters. Work means the product does not
stop at notes.

## Chapter T10: The Long-Term Product Shape

Over time, Pavo can become a system that handles spoken records across many
contexts. The long-term shape is not one monolithic assistant. It is a layered
control plane.

At the bottom is source capture and preservation. Pavo should ingest from local
files, Plaud, meeting platforms, call systems, voice memos, and future capture
tools. Each source adapter should produce a normalized recording record and
source artifact. The original source should remain inspectable.

Above that is evidence processing. Pavo should orchestrate transcription,
speaker analysis, overlap handling, context dictionaries, human corrections,
review notes, and stale reprocessing. The output is not just text. It is an
evidence graph.

Above that is routing intelligence. Pavo should create packets that cite the
evidence graph and propose routes. Some routes are destination writes. Some are
drafts. Some are archives. Some are blocked. Some are policy candidates.

Above that is approval. Users and teams need review queues, roles, defaults,
bulk actions, redaction previews, and policy review. Approval should be
ergonomic enough that it beats manual follow-up.

Above that is destination execution. Pavo should land approved actions into
Drive, Linear, CRM, email drafts, Slack drafts, personal reminders, research
repositories, and other systems. Each destination must return proof.

Above that is policy memory. Home should propose rules from reviewed history.
It should know which records usually archive, which routes need review, which
destinations are blocked, which users can approve, and which policies have been
revoked.

Across all layers is audit. Pavo needs to answer what happened, why it was
recommended, who approved it, what landed, what failed, what changed, and what
was learned.

This shape gives Pavo a path from a single-user local tool to a team product
and eventually a governed workflow platform. The path only works if each layer
keeps its contract. Capture should not pretend to be action. Transcription
should not pretend to be truth. Routing should not pretend to be permission.
Approval should not pretend to be proof. Policy should not pretend to be
automatic correctness.

The product book exists to keep those contracts visible.

# Part 9: Expanded Scenario Narratives

The scenario library already defines many cases. This part adds more narrative
depth to the most important ones so the book can teach the product through
story, not only schema. Each scenario follows the same discipline: the source is
preserved, uncertainty is visible, routes are recommended, approval controls
what lands, and proof remains after the action.

## Chapter U1: Founder Customer Call With Product Blocker

The founder does not start the call thinking about Pavo. The call is just one
more customer conversation in a crowded week. There are already notes in the
CRM, a few Slack threads, a half-updated roadmap, and a mental list of promises
the founder hopes not to forget. The customer is important enough that the call
is recorded. That is the first good decision. It is not enough.

The conversation begins with normal context. The customer explains their team,
their workflow, the project timeline, and the reason they agreed to talk. For
the first ten minutes, nothing sounds urgent. Then a detail appears. The
customer says their operations team has stopped using the import workflow
because it fails silently when files contain certain account names. They have a
manual workaround. The workaround takes an hour each week. The founder asks
whether this is a blocker. The customer says, "It is not the only thing, but if
we cannot trust imports, expansion is hard to justify."

A meeting-note product might summarize:

```text
Customer has issues with import workflow and expansion may depend on fixing
trust in imports.
```

That is useful. It is also insufficient. Pavo needs to decide what this record
should become.

Nest:

Pavo preserves the source recording, call metadata, participants, account name,
capture time, and file hash. The record is associated with the customer account
but not yet routed. The source is stable before any interpretation begins.

Tune:

The transcript is mostly clear, but the product name and account name are
misheard twice. Pavo marks the relevant spans as needing review. The founder
corrects the account name and approves the span where the customer describes
the import failure. The renewal language is marked as commercially sensitive
because it could be overstated.

Scout:

Pavo recommends four routes.

Route one is a Drive archive. The full recording, transcript, manifest, and
review corrections should be archived under the account folder. This is low
risk and can be approved quickly.

Route two is a Linear issue draft:

```text
Investigate silent import failure for customer account-name edge cases
```

The evidence includes the customer's description, the manual workaround, and
the founder's clarification question. The route is review-required because the
issue should not include renewal pressure as a product fact.

Route three is a CRM note draft. It includes the customer-reported workflow
pain and the next follow-up, but redacts internal product speculation.

Route four is a blocked Slack post. The model initially suggests:

```text
Customer says expansion depends on fixing imports.
```

Pavo blocks this because the actual phrase was softer: "expansion is hard to
justify." The difference matters. A Slack post can create internal panic or
false priority. The blocked route shows why it was blocked.

Approval:

The founder approves the Drive archive. The founder edits the Linear issue to
remove renewal speculation and add a source link. The CRM note is approved
after changing "blocking expansion" to "customer raised expansion concern if
import trust does not improve." The Slack route stays rejected.

Land:

Pavo writes the Drive archive, creates the Linear issue, saves the CRM note,
and records a blocked Slack manifest. The Linear issue contains evidence spans,
not the full transcript. The CRM note contains a clean account summary. The
Slack block remains visible in the packet.

Home:

Pavo proposes a scoped policy:

```text
For reviewed customer calls with product blockers, draft a Linear investigation
issue with evidence spans. Do not include renewal or expansion claims unless
explicitly approved.
```

This policy is useful because it captures the repeated pattern without
automating the risky part. The founder can approve it later, narrow it, or
reject it.

What Pavo prevented:

- the call becoming only a summary
- the blocker staying in memory
- the CRM note overstating the customer
- the roadmap receiving a false commitment
- Slack amplifying commercial pressure
- the evidence being separated from the issue

What Pavo created:

- durable source archive
- corrected transcript evidence
- product investigation issue
- CRM account note
- blocked unsafe route
- policy candidate for future calls

This scenario is the core Pavo demo because it shows the product's complete
reason to exist. It is not about taking notes. It is about turning a customer
conversation into approved, source-backed work.

## Chapter U2: Personal Administration Call That Stays Mostly Private

The user records a call with an insurance office. The call includes ordinary
details: policy number, claim status, document request, appointment window,
agent name, and a promise that a form will be emailed by Friday. It also
includes sensitive personal context. The user wants help remembering what to do
next. They do not want the whole call in a shared workspace. They do not want a
model to send messages on their behalf. They do not want private context used
to train broad team policy.

This is where Pavo's restraint matters.

Nest:

The recording is stored in private mode. Pavo records source metadata, file
hash, call date, and owner. Visibility is set to personal. Team destinations
are disabled by default. The retention setting is visible. The source is
preserved, but preservation does not imply sharing.

Tune:

The transcript extracts the agent name, document deadline, and form name. The
policy number is detected as sensitive. A family-health detail is marked
archive-only. The agent name has low confidence because the audio clipped when
the name was spoken. Pavo flags it for review. The user listens to the span and
corrects the spelling.

Scout:

Pavo recommends three narrow actions and one blocked route.

The first action is private archive. The full source and transcript remain in
the user's private Pavo storage.

The second action is a reminder:

```text
Check whether insurance form arrives by Friday at 4 p.m.
```

The reminder does not include the policy number or sensitive detail.

The third action is an email draft:

```text
Hi [Agent Name],

Thank you for speaking with me today. I am confirming that the requested form
will be emailed by Friday. Please let me know if you need any additional
documents from me.
```

The draft is not sent. It is only prepared.

The blocked route is a shared Drive upload. Pavo blocks it because the record
is personal and no user-approved shared destination exists.

Approval:

The user approves the private archive. They approve the reminder. They edit
the email draft and save it. They keep the shared route blocked.

Land:

Pavo writes the private archive manifest, creates the reminder, saves the email
draft if the user's mail system supports draft creation, and records that the
shared Drive route was blocked.

Home:

Pavo proposes:

```text
For personal insurance calls, default to private archive, suggest reminders
for dated obligations, and require explicit approval for any shared export.
```

The user may approve that policy. It remains personal in scope.

The important product lesson is that Pavo can create value without maximizing
sharing. The user did not need a team note. They needed private recall, narrow
follow-up, and confidence that the sensitive parts stayed contained.

This scenario also shapes the product's architecture. Personal mode cannot be
a marketing label only. It must affect storage, destinations, policy learning,
approval defaults, and UI. If the product cannot enforce those differences, it
should not claim them.

## Chapter U3: Product Interview With Ambiguous Evidence

A product manager interviews a user about onboarding. The user is thoughtful,
but not perfectly consistent. Early in the call, they say the import process is
confusing. Later, they say the import worked after a teammate showed them the
right template. They ask for a one-click shortcut, but they also admit they
would not want the system to make assumptions about their data. They describe a
workaround. They mention that another tool "kind of does this," but cannot
remember the name.

This is not a simple feature request. It is evidence.

Nest:

Pavo preserves the recording, source metadata, participant role, research
project, and consent state. The record is tagged as user-research material.

Tune:

The transcript captures the main quotes, but the competitor name is uncertain.
Pavo marks that span as low confidence. The product manager adds a review note:

```text
Do not treat competitor name as verified. User was unsure.
```

The user's request for a shortcut is marked as a quote, not as a product
commitment. The workaround is extracted as a separate evidence span.

Scout:

Pavo recommends a research repository archive with source spans. It recommends
a Linear discovery issue:

```text
Investigate onboarding import confusion around template selection
```

It recommends blocking a roadmap item titled:

```text
Build one-click import shortcut
```

The blocked route matters. A less careful AI product might turn the most
concrete phrase into the most concrete task. Pavo sees that the user's real
pain may be template selection, confidence, or education, not necessarily a
shortcut.

Pavo also recommends a Home policy candidate for research calls:

```text
User feature requests should default to discovery drafts, not roadmap
commitments, unless manually approved.
```

Approval:

The product manager approves the research archive. They edit the Linear issue
to include two evidence spans: one quote about confusion and one quote about
not wanting the system to assume too much. They reject the roadmap item. They
approve the policy candidate as a draft for later team review.

Land:

The research repository receives the archive. Linear receives the discovery
issue. The roadmap route remains blocked. The destination manifest records
what landed and what did not.

Home:

Pavo remembers that this product team treats interview requests as discovery
evidence first. It can use that to recommend better routes next time, but it
cannot silently create roadmap commitments.

This scenario proves that Pavo is not just an action-item extractor. Action
items are easy to overproduce. Product judgment is harder. Pavo's value is in
preserving ambiguity until a human decides what the ambiguity means.

## Chapter U4: Recruiting Screen With Sensitive Evaluation

A hiring manager records a recruiting screen. The conversation includes basic
candidate details, availability, compensation expectations, role preferences,
and a few sensitive evaluation notes. Some information belongs in the applicant
tracking system. Some belongs only in private hiring notes. Some should not be
written at all. A generic summary can easily blur those boundaries.

Nest:

Pavo preserves the recording with hiring sensitivity. Access is restricted. The
candidate's consent state is recorded. The source is associated with a role and
candidate id, but not broadly indexed.

Tune:

The transcript identifies compensation numbers, availability dates, and
candidate questions. It also marks uncertain phrases around a prior employer's
name. The hiring manager corrects the employer name and adds a note that one
evaluation impression should not be routed because it was tentative.

Scout:

Pavo recommends an ATS note draft with factual candidate-provided information.
It recommends a private hiring note with interviewer's observations. It blocks
a Slack route because it includes compensation and evaluation content. It
recommends a follow-up task to send the candidate the role overview.

The ATS draft is constrained:

```text
Candidate is available to start in mid-August. Candidate asked about remote
expectations and team structure. Candidate stated compensation expectations in
the range discussed on the call.
```

It does not include speculative evaluation language. It does not include
sensitive personal details. It cites evidence spans.

Approval:

The hiring manager approves the ATS draft after editing compensation language
to match company policy. They approve the follow-up task. They keep the private
note private. They reject the Slack route.

Land:

Pavo creates the ATS draft or note, creates the follow-up task, preserves the
private note in the restricted evidence bundle, and records the blocked Slack
route.

Home:

Pavo proposes:

```text
For recruiting screens, route factual candidate-provided logistics to ATS,
keep evaluative notes restricted, and block Slack routes containing
compensation or sensitive evaluation content.
```

This is a strong Home candidate because the pattern is repeated and the risk is
clear. It should still require hiring-team approval.

This scenario shows why Pavo should not market blind automation. Recruiting is
full of information that looks operational but needs careful boundaries.
Approved, source-backed routing is useful precisely because the work is
sensitive.

## Chapter U5: Customer Support Escalation With Anger And Facts

A support escalation call is emotionally charged. The customer is frustrated.
They describe a real outage, but also make broad claims about reliability. The
support lead wants to move quickly. Engineering needs facts. Customer success
needs account context. Leadership may need a summary. The wrong route can make
the situation worse.

Nest:

Pavo preserves the source, account, incident date, support ticket id, and call
participants. The source is marked customer-sensitive. Broad sharing is not
allowed by default.

Tune:

The transcript distinguishes between verifiable facts and emotional language.
Pavo marks exact timestamps where the customer describes error messages,
affected workflows, and business impact. It also marks generalized statements
like "this always happens" as claims requiring caution.

Scout:

Pavo recommends an engineering incident investigation draft with concrete
facts:

- error message
- time window
- affected workflow
- customer environment
- reproduction clue

It recommends a customer-success account note with impact and follow-up owner.
It recommends a leadership brief draft that is internal-only and excludes
unsupported claims. It blocks a public-status update because the source is one
customer report, not confirmed incident scope.

Approval:

The support lead approves the engineering draft after adding the ticket id.
The customer success manager approves the account note. The leadership brief is
edited to say "customer reported" rather than "system failed." The public route
is rejected.

Land:

Pavo creates the engineering issue, updates the account note, saves the
leadership brief draft, and records the blocked public route.

Home:

Pavo proposes a policy:

```text
For escalation calls, route concrete reproduction evidence to engineering,
route account impact to CS, and block public or broad internal claims until
confirmed by incident evidence.
```

This policy is exactly the kind Pavo should learn over time: narrow, useful,
and risk-aware.

## Chapter U6: Legal-Adjacent Interview Where Summary Is Dangerous

Some conversations are dangerous to summarize casually. A legal-adjacent
interview, compliance investigation, HR matter, or dispute call may contain
facts, allegations, uncertainty, emotion, privileged context, and procedural
requirements. Pavo should not pretend to be a legal system. It should help
preserve source material and prevent unsafe routing.

Nest:

The record is preserved with restricted access and legal-adjacent sensitivity.
The consent and authorization state are explicit. Retention policy is visible.
No default downstream destinations are enabled.

Tune:

Pavo creates an evidence transcript but marks the record as high-risk. Speaker
identity and exact quotes matter. Uncertain spans require review. Pavo avoids
generating a confident narrative conclusion.

Scout:

The primary recommendation is restricted archive. Pavo may recommend a review
task for an authorized person. It may recommend an evidence index that points
to timestamps. It blocks broad summaries, Slack posts, CRM notes, roadmap
issues, and any route that turns allegations into established findings.

Approval:

The authorized reviewer approves archive and review task only. They reject all
interpretive routes.

Land:

Pavo writes the restricted archive and review task manifest. Nothing else
lands.

Home:

Pavo proposes:

```text
For legal-adjacent records, default to restricted archive and authorized review
task. Block interpretive summaries and broad sharing unless manually approved
by the authorized owner.
```

This scenario is important because it defines a boundary. Pavo is not useful
only when it creates tasks. It is useful when it prevents a record from
becoming the wrong kind of artifact.

## Chapter U7: Internal Strategy Jam That Should Not Become Commitments

Teams brainstorm loosely. They say things they do not mean yet. They test
ideas. They exaggerate to explore. They ask "what if" questions. A generic AI
summary can turn that into a false plan.

Nest:

Pavo preserves the meeting recording with internal strategy sensitivity. The
record is associated with a project, but not routed to execution systems by
default.

Tune:

Pavo identifies topics, open questions, explicit decisions, and speculative
ideas. It marks phrases like "maybe," "what if," "we could," and "not a
commitment" as important uncertainty signals.

Scout:

Pavo recommends an internal archive. It recommends a decision log draft for the
few decisions that were explicit. It recommends an open-questions list. It
blocks task creation for speculative ideas. It blocks customer-facing or
public-facing drafts.

Approval:

The team lead approves the archive. They approve two decision log entries.
They edit the open-question list. They reject six proposed tasks that came from
brainstorming.

Land:

Pavo writes the decision log and open-question list. The rejected task routes
remain in the packet with reasons.

Home:

Pavo proposes:

```text
For internal strategy jams, default to archive, decision log, and open
questions. Require explicit approval before creating execution tasks from
speculative language.
```

This scenario teaches one of Pavo's deepest lessons: a conversation can be
valuable without being executable. Preserving strategy thinking is not the same
as turning it into work.

## Chapter U8: Field Inspection Memo With Poor Audio

A field operator records a voice memo after inspecting equipment. The audio is
windy. There is background noise. The operator uses shorthand. A safety concern
may be present, but one phrase is hard to hear. The wrong product behavior
would turn uncertainty into a confident incident report.

Nest:

Pavo preserves the original audio, GPS or site metadata if available, capture
time, operator, and device source. It marks the audio as field memo with
possible safety relevance.

Tune:

Pavo transcribes what it can, marks low-confidence spans, and detects a
possible phrase related to a safety latch. The phrase is not clear enough for
automatic routing. Pavo creates a review clip around the uncertain region.

Scout:

Pavo recommends archive. It recommends a review task for the safety officer. It
recommends a draft maintenance note that excludes the uncertain safety phrase.
It blocks an incident report until the uncertain phrase is reviewed.

Approval:

The operator approves archive. The safety officer reviews the clip and confirms
the phrase. Only after that correction does Pavo recommend a maintenance issue
with safety flag.

Land:

Pavo writes the archive, creates the review task, then creates the maintenance
issue after review. The incident-report route remains manual because the
organization's policy requires a separate workflow.

Home:

Pavo proposes:

```text
For poor-audio field memos with possible safety language, create review tasks
before incident or maintenance routing. Do not route low-confidence safety
phrases as facts.
```

This scenario is an implementation test. It requires Tune and Scout to work
together. Low confidence from Tune must change routing behavior in Scout. If
Pavo cannot propagate that uncertainty, it is unsafe.

# Part 10: Operating Doctrine

Pavo is not only a product surface. It is an operating doctrine for turning
spoken records into work without losing trust. This part defines the practices
that should guide product reviews, engineering work, customer discovery,
support, and release gates.

## Chapter V1: Product Review Doctrine

Every major Pavo product review should start with the same question:

```text
What spoken record are we helping the user complete?
```

If the review starts with a feature instead of a record, the product can drift.
For example, "add Slack integration" is not a complete product review. The
better review is: "When a customer call contains a product blocker and
commercially sensitive renewal language, what Slack route, if any, should Pavo
recommend?" That framing forces the team to inspect source, evidence,
sensitivity, approval, and proof.

Product reviews should use a fixed checklist.

Record:

- What is the source type?
- Who owns it?
- What is the sensitivity?
- What consent state exists?
- Where is the original media?
- What is the storage mode?

Evidence:

- What transcript or evidence exists?
- What is uncertain?
- What has been reviewed?
- What speaker identity claims are supported?
- What corrections changed the record?

Routing:

- What routes are recommended?
- What routes are blocked?
- What routes are private or archive-only?
- What destinations are allowed?
- What evidence supports each route?

Approval:

- Who approves?
- What exactly are they approving?
- Can they edit before approval?
- Can they approve draft-only?
- What happens if they reject?
- What happens if they reverse approval?

Landing:

- What writes occur?
- Are they idempotent?
- What proof returns?
- What failure states exist?
- What is the retry behavior?

Home:

- What should Pavo learn?
- What should Pavo not learn?
- What scope limits apply?
- Who approves policy?
- How can policy be revoked?

This checklist may feel heavy. That is the point. Pavo is a trust product. It
should not review features as if they were isolated UI additions.

## Chapter V2: Engineering Doctrine

Pavo engineering should prefer durable contracts over clever flows. The system
will touch recordings, transcripts, evidence, approvals, destinations, and
policy. If the contracts are loose, the product will become impossible to
trust.

Engineering rules:

1. Preserve source before inference.
2. Preserve manifests before summaries.
3. Treat transcript confidence as data, not decoration.
4. Treat speaker identity as evidence, not a label.
5. Never let Scout write directly to a destination.
6. Never let Land execute without approval or explicit approved policy.
7. Make blocked routes first-class objects.
8. Make non-action inspectable.
9. Make retry behavior idempotent.
10. Make Home policy explicit and revocable.

The codebase should reflect these rules. `pavo/transcribe.py` can create Tune
evidence, but it should not decide destination writes. A future
`pavo/scout.py` can create routing packets, but it should not call destination
APIs. A future `pavo/land.py` can execute approved actions, but it should not
invent new routes. A future `pavo/home.py` can propose policies, but it should
not silently activate them.

Testing should follow product risk. Unit tests are enough for small parsing
helpers. Routing and landing need fixtures. Destination adapters need dry-run,
success, failure, retry, duplicate, stale-packet, and reversal tests. Home
needs policy-scope and overlearning tests. UI needs proof that the user can see
source, evidence, preview, approval state, and manifest.

The most important test shape is scenario-to-packet. Given a source record and
evidence bundle, Scout should produce an expected packet. Given an approved
packet, Land should produce an expected manifest. Given approvals and
rejections, Home should produce or refuse a policy candidate. This is how the
book becomes executable.

## Chapter V3: Customer Discovery Doctrine

Pavo discovery should not ask whether people want AI notes. Many do. That does
not prove Pavo. Discovery should ask whether recorded conversations fail to
become the right work.

The best discovery prompt is:

```text
Bring one recording that should have become follow-up work.
```

That prompt reveals the real workflow. If the prospect cannot name one
recording, the pain may be abstract. If they can name one, the conversation
becomes concrete. Pavo can ask where the recording came from, what should have
happened, what did happen, what was missed, what would have been unsafe, and
who should have approved it.

Discovery notes should become scenario records. Each interview should produce:

- source type
- persona
- current workflow
- missed route
- risky route
- desired destination
- approval owner
- evidence requirement
- gotcha
- product implication

The product team should review discovery through the Flight Path:

- Did the prospect have a Nest problem?
- Did they have a Tune problem?
- Did they have a Scout problem?
- Did they have a Land problem?
- Did they describe Home-like learning?

This prevents overbuilding. A buyer with only a Nest problem may need archive
and sync first. A buyer with Tune pain may need dictionaries and review. A
buyer with Scout pain may need routing packets. A buyer with Land pain may need
destination manifests. A buyer asking for Home may actually be asking for
policy, not magic.

## Chapter V4: Release Gate Doctrine

Pavo release gates should be tied to trust.

A Nest release is ready when:

- source files are preserved
- hashes are recorded
- metadata is non-secret and durable
- duplicate downloads are handled
- source adapters do not leak credentials
- local and archive paths are inspectable

A Tune release is ready when:

- transcript artifacts have manifests
- context terms and profiles are recorded
- uncertain spans are visible
- review corrections are durable
- stale processing can be detected
- proof reports explain what changed

A Scout release is ready when:

- packets are schema-validated
- every route cites evidence
- blocked routes are represented
- sensitivity changes approval requirements
- fixture scenarios pass
- no destination writes occur from Scout

A Land release is ready when:

- only approved actions execute
- dry-run previews exist
- idempotency keys prevent duplicates
- destination manifests are written
- partial failure is visible
- secrets are redacted
- retries are safe

A Home release is ready when:

- policy candidates cite reviewed decisions
- scope is explicit
- activation requires approval
- revocation exists
- rejected examples are preserved
- explanations are visible

These gates are stricter than ordinary feature gates because Pavo's product
surface is trust. A feature that appears to work but cannot prove its state is
not done.

## Chapter V5: Support Doctrine

When Pavo fails, support should diagnose by Flight Path stage. The user should
not hear a generic answer like "the AI got it wrong." The product should know
where the failure happened.

Nest failures:

- recording not imported
- source link expired
- hash mismatch
- duplicate source
- wrong account
- missing consent state

Tune failures:

- bad transcript
- wrong speaker
- missing term
- overlap not handled
- review correction not applied
- stale transcript used

Scout failures:

- wrong route recommended
- risky route not blocked
- evidence missing
- sensitivity misclassified
- private record treated as team work
- no-action not offered

Land failures:

- unapproved write
- duplicate write
- destination outage
- wrong destination record
- partial failure hidden
- manifest missing

Home failures:

- overbroad policy
- silent behavior change
- rejected example ignored
- personal record affected team policy
- policy not revocable

Support should collect artifacts, not vague descriptions. A useful support
packet includes source id, packet id, approval id, manifest id, destination id,
timestamps, and redacted screenshots if needed. It should not include secrets
or raw private content unless explicitly approved and necessary.

Support should also feed the gotcha matrix. Every real failure should either
match an existing gotcha or create a new one. Pavo's product quality should
improve by turning support incidents into fixtures.

## Chapter V6: Marketplace Doctrine

Pavo's marketplace presence should be honest about shipped capability. The
plugin should help agents use Pavo safely; it should not market future product
layers as already complete.

Marketplace copy should say:

- Pavo preserves spoken records.
- Pavo improves transcript and speaker evidence.
- Pavo uses manifests and proof.
- Pavo is being built toward approval-gated routing.
- External writes require approval.

Marketplace copy should not say:

- Pavo fully automates all follow-up.
- Pavo is compliance-ready.
- Pavo sends messages automatically.
- Pavo supports every destination.
- Pavo has shipped Home policy automation if it has not.

The marketplace audit should verify:

- plugin id
- source path
- copied bundle
- manifest wiring
- skill instructions
- tests
- Python runtime
- no stale user path

This matters because agents will read marketplace copy as operational truth.
If the plugin overclaims, agents may take unsafe actions. The marketplace is
part of the product boundary.

## Chapter V7: The Book As A Product Artifact

This book is not a pitch deck. It is also not only documentation. It is a
product artifact that should shape implementation. The point of writing a long
book before the full product exists is not to create theater. It is to force
the product's hard distinctions into language before code hides them.

The book should do several jobs:

- explain why Pavo exists
- define the Flight Path
- name product levels of completion
- preserve the bird-theme vocabulary that users liked
- explain why Tune matters
- describe scenarios deeply enough to guide design
- define schemas and status vocabulary
- identify gotchas before they become incidents
- guide marketing without overclaiming
- map product vision to implementation work
- create fixture candidates for tests
- define release gates

As the product matures, parts of the book should become more formal. Glossary
terms should become enums. Evidence examples should become fixtures. UI specs
should become tickets. Gotchas should become regression tests. Roadmap chapters
should become milestones. Marketing guardrails should become launch review
criteria.

The book should remain alive, but not loose. Changes to core vocabulary should
be deliberate. If the team changes a Flight Path term, it should update the
README, product spine, skill, marketplace copy, and book together. If a
scenario reveals a new risk, the gotcha matrix should change. If an
implementation makes a product claim real, the docs should distinguish shipped
behavior from aspiration.

The book is long because the product is subtle. Pavo is easy to explain badly:
"AI notes that create tasks." It takes more space to explain it correctly:
spoken records become approved, source-backed work through a reviewable Flight
Path.

That is the product.

# Part 11: Product Requirements For The First Real Pavo

This part translates the book into buildable product requirements. It does not
replace engineering tickets or schemas, but it gives the product team a clear
standard for what the first real Pavo should do. The emphasis remains narrow:
prove the Flight Path with a small set of sources and destinations before
trying to support every recording workflow.

The first real Pavo should feel like a working control plane, not a demo glued
to a transcript. A user should be able to bring a recording, see the source
preserved, inspect the tuned record, review routing recommendations, approve or
block actions, and then see proof of what landed. If the product cannot show
that loop, the rest of the vision is still speculative.

## Chapter W1: The First Complete User Story

The first complete user story should be written in plain language:

```text
As a founder or operator with important recorded conversations, I want Pavo to
preserve the source, make the record trustworthy, recommend where follow-up
belongs, ask before writing, and prove what landed, so that conversations
become controlled work instead of loose memory.
```

That user story contains several product requirements.

Requirement one: the user can import or select a real recording. The recording
may come from Plaud or a local file. The product should not require the user to
paste a summary. It starts with the source.

Requirement two: Pavo creates a durable source record. The user can see where
the source came from, when it was captured, where it is stored, what its hash
is, and what storage mode applies. If the file is missing, the product should
say so. If the source link is temporary, the product should not pretend the
link is the durable record.

Requirement three: Pavo creates or imports transcript evidence with visible
confidence and provenance. The transcript does not need to be perfect. It needs
to be inspectable. The user should see uncertain spans, speaker labels, and
review status.

Requirement four: Pavo creates a routing packet. The packet should not be a
paragraph of advice. It should be structured enough to render in the UI and
test in code: routes, reasons, evidence, sensitivity, approval requirements,
blocked routes, and non-action outcomes.

Requirement five: the user can approve, edit, reject, or block each route. The
approval surface should be faster than manual follow-up. The user should not
have to understand the whole data model to make a safe decision.

Requirement six: Pavo lands approved actions and only approved actions. If the
route is a Drive archive, it writes the archive. If the route is a Linear
issue, it creates or drafts the issue. If the route is blocked, it records the
block. If the destination fails, it shows the failure.

Requirement seven: Pavo writes destination manifests. The user can inspect what
happened after approval. Proof is not optional.

Requirement eight: Pavo proposes learning only after reviewed history exists.
The first version may show Home candidates as read-only or draft-only. It
should not silently automate.

This story should remain the test for the product. If a feature helps this
story, it is likely aligned. If a feature distracts from this story, it should
wait.

## Chapter W2: First Source Requirements

The first sources should be Plaud and local files. That is enough.

Plaud matters because it represents the new capture reality: a device can make
recording easy, but the downstream workflow still needs control. Local files
matter because they provide a universal fallback and avoid overdependence on
one vendor.

Plaud source requirements:

- show the connected account without exposing secrets
- list recordings with ids, titles, timestamps, and duration when available
- download audio to a durable local path
- record source adapter, source id, fetch time, file path, byte size, and hash
- avoid duplicate downloads when the same source and hash already exist
- handle expired or missing audio URLs as source failures, not transcript
  failures
- preserve Plaud credentials in Plaud's own store
- support a dry-run listing path

Local file requirements:

- import audio or video file
- compute hash and byte size
- assign stable source id
- accept title, owner, sensitivity, storage mode, and optional context terms
- preserve original file or record controlled reference to it
- detect duplicate imports by hash
- support private-mode import

Both sources should produce the same normalized object:

```text
RecordingRecord
SourceArtifact
SourceMetadata
SourceManifest
```

The UI should not care whether the source was Plaud or local file once the
record is nested. The source adapter matters for provenance and refresh, but
the rest of the Flight Path should consume normalized records.

Source anti-requirements:

- do not require cloud upload for local/private records
- do not store vendor tokens in Pavo config
- do not treat temporary URLs as durable records
- do not route records before Nest completes
- do not let the user confuse source deletion with destination deletion

The first source experience should feel quiet and reliable. It should not
impress the user with AI. It should reassure the user that the record is under
control.

## Chapter W3: First Tune Requirements

Tune should make the record trustworthy enough to route. The first Tune layer
does not need every audio feature the product may eventually support. It needs
enough evidence and reviewability for Scout to make safe recommendations.

Required Tune artifacts:

- transcript text
- transcript JSON or structured segments
- transcript manifest
- engine and command metadata
- context terms or context profile
- speaker labels
- speaker confidence or review state
- uncertain spans
- human corrections
- review notes
- stale processing metadata

The transcript should be versioned. If Pavo reprocesses a record with a new
engine, new dictionary, new speaker correction, or new preprocessing setting,
the old transcript should not disappear. A route that was approved from an old
transcript may become stale, but the evidence trail remains.

Tune should expose uncertainty in at least four places.

First, word or span uncertainty. If a key term is low confidence, Scout should
know that a route citing it requires review.

Second, speaker uncertainty. If Pavo does not know who said a phrase, it should
not route that phrase as a commitment by a named person.

Third, source quality uncertainty. If the audio is noisy, clipped, incomplete,
or contains overlap, Scout should see that.

Fourth, review uncertainty. If a human review is pending, partial, rejected, or
contradictory, the packet should say so.

Tune UI requirements:

- show transcript with timestamped segments
- show source audio controls
- show confidence markers without overwhelming the user
- allow correction of key terms and speakers
- preserve reviewer notes
- show what changed after correction
- allow a route to return to Tune when evidence is insufficient

Tune anti-requirements:

- do not present a polished summary as if it were the source
- do not hide low-confidence spans
- do not overwrite old transcript versions without trace
- do not let corrected snippets detach from their source timestamps
- do not require every transcript to be perfect before allowing safe archive
  routes

Tune is done when the product can explain why the record is trustworthy enough
for a specific route. It is not done merely because text exists.

## Chapter W4: First Scout Requirements

Scout is the first place where Pavo becomes truly differentiated. It should
recommend what the record can become, but it should not write anything.

The first Scout implementation can be rules-first. It does not need a complex
AI planner. It needs deterministic packet structure, evidence citation, and
safe recommendation behavior.

Initial route types:

- archive source and transcript
- create Linear draft issue
- create CRM note draft
- create email draft
- create reminder or task
- mark private
- block route
- no action needed
- return to Tune

Initial destination set:

- local archive
- Drive archive
- Linear draft or issue
- CRM draft only
- email draft only
- Slack blocked or draft only

Scout packet requirements:

- packet id
- recording id
- source refs
- evidence refs
- route candidates
- blocked routes
- recommended non-action
- sensitivity flags
- approval requirements
- destination previews
- confidence and uncertainty
- stale status
- created time
- packet version

Scout behavior requirements:

- every route must cite evidence
- every blocked route must explain why
- every high-risk destination must require approval
- every route from uncertain evidence must require review
- every personal/private record must restrict team destinations by default
- every route should be previewable before approval
- Scout must support "no action"
- Scout must support "return to Tune"

Scout should use the scenario library as its first evaluation set. The first
fixtures should include:

- customer blocker call
- personal administration call
- ambiguous product interview
- recruiting screen
- support escalation
- legal-adjacent interview
- internal strategy jam
- poor audio field memo
- destination outage
- wrong account mapping

Each fixture should have expected routes, blocked routes, approval
requirements, and gotchas. The goal is not to make Scout brilliant. The goal is
to make it safe and testable.

Scout anti-requirements:

- do not call destination APIs
- do not invent facts without source refs
- do not collapse blocked routes into absence
- do not treat all destinations as generic text
- do not route personal records into team tools by default
- do not turn Home policy into silent execution

Scout is done when a user can look at a packet and understand what Pavo thinks,
why it thinks it, what is risky, and what requires approval.

## Chapter W5: First Approval Queue Requirements

The approval queue is the product's central working surface. It should feel
less like an inbox and more like a decision table. The user is not there to
read everything. The user is there to decide what is allowed to happen.

Queue item fields:

- recording title
- source type
- owner
- sensitivity
- current Flight Path stage
- recommended route count
- blocked route count
- approval required count
- age
- highest-risk destination
- evidence quality status
- next recommended decision

Record detail fields:

- source metadata
- source audio
- transcript evidence
- route candidates
- destination previews
- sensitivity warnings
- approval controls
- manifest history
- Home candidates

Approval actions:

- approve as-is
- edit then approve
- approve as draft-only
- reject
- block by policy
- mark private
- return to Tune
- defer
- split route
- request more evidence

The queue should support batch behavior only for low-risk actions. For example,
approving several private archives may be safe. Batch-approving CRM writes,
Slack posts, or customer-facing drafts should not be allowed in the first
version.

Approval UI should always show the thing being approved. If the user approves
a Linear issue, they should see the exact title, body, evidence links, labels,
and destination project. If they approve a CRM note, they should see the exact
account, note text, and redacted fields. If they approve an email draft, they
should see recipients, subject, body, attachments, and send state. Pavo should
never ask for abstract approval of "the recommendation."

Approval anti-requirements:

- do not hide destination preview behind the approval button
- do not approve all routes as one undifferentiated bundle
- do not make rejection feel like an error
- do not make blocked routes disappear
- do not allow approval of stale packets without warning
- do not make Home policy changes look like ordinary route approval

The best approval queue creates confidence by narrowing the user's burden.
Instead of asking the user to reconstruct the call, it asks them to decide on a
well-supported action.

## Chapter W6: First Land Requirements

Land should be small and strict. It is better to support two destinations well
than six destinations weakly.

The first Land destinations should be:

1. local archive
2. Drive archive
3. Linear draft or issue

CRM, email, and Slack should begin as draft or blocked routes until the product
has strong preview, approval, and manifest behavior.

Land executor requirements:

- consume approved route only
- validate packet version
- validate approval id
- validate destination preview hash if applicable
- compute idempotency key
- perform dry-run when requested
- execute destination write
- capture destination response
- write destination manifest
- mark route status
- handle partial failure
- support retry safely

Destination manifest fields:

- manifest id
- packet id
- route id
- approval id
- destination type
- destination object id
- destination URL when available
- idempotency key
- request preview
- response summary
- status
- error class if failed
- retry state
- created time
- actor

Drive Land requirements:

- create or find destination folder
- upload source artifact when approved
- upload transcript/evidence bundle when approved
- upload manifest
- avoid duplicates by hash and recording id
- record Drive ids
- support dry-run
- preserve privacy mode

Linear Land requirements:

- create draft or issue from approved route
- include evidence references
- avoid unsupported claims
- set project/team/labels from approved preview
- return issue id and URL
- support duplicate detection
- support failure manifest

Land anti-requirements:

- do not execute unapproved routes
- do not execute stale packet routes silently
- do not retry by creating duplicates
- do not hide partial failure
- do not store secrets in manifests
- do not send outbound messages in first version

Land is the product's proof layer. If a user cannot tell what Pavo wrote, Pavo
has not landed.

## Chapter W7: First Home Requirements

Home should start as read-only policy candidates. That is the safest way to
test learning without letting the system surprise users.

Home input:

- approved routes
- edited routes
- rejected routes
- blocked routes
- returned-to-Tune routes
- destination manifests
- reversal events
- user notes

Home output:

- policy candidate
- scope
- examples
- counterexamples
- proposed default
- approval requirement
- risk level
- revocation path

Example candidate:

```text
For customer calls in account segment A, when the customer describes a product
blocker with reviewed evidence, draft a Linear investigation issue. Keep CRM
notes draft-only. Block Slack routes containing renewal language.
```

Home UI requirements:

- show why the candidate exists
- show supporting approvals
- show rejected or blocked examples
- show scope clearly
- show what would change if approved
- allow edit
- allow reject
- allow approve as suggestion-only
- allow revoke later

Home anti-requirements:

- do not silently activate policy
- do not infer broad policy from one approval
- do not mix personal and team records
- do not hide counterexamples
- do not make policy impossible to revoke
- do not execute Land directly from new policy in the first version

Home is where Pavo compounds. It should move slowly because policy mistakes can
be worse than one-off route mistakes.

# Part 12: Buyer, Market, And Category Chapters

Pavo's market story should be honest about the product's difficulty. The buyer
does not need another vague AI productivity claim. The buyer needs to recognize
their own operational pain: important conversations are captured but still do
not reliably become the right work.

## Chapter X1: The Buyer Is Not Buying Transcription

Some buyers will enter through transcription pain. Their current transcripts
may be wrong. Speaker labels may be unreliable. Names may be misheard. Vendor
links may expire. These problems matter, but they are not the final buying
reason for Pavo.

The buyer is buying controlled follow-through.

They are buying fewer lost customer blockers. They are buying cleaner account
notes. They are buying better product evidence. They are buying less manual
copy-paste. They are buying private handling of sensitive calls. They are
buying proof that approved actions landed. They are buying the ability to use
AI recommendations without surrendering judgment.

This difference should shape pricing, demos, sales calls, and onboarding. If
Pavo sells by the transcript minute, it competes with transcription vendors. If
Pavo sells by approved outcomes, it competes in the operational value layer.
The product may still need usage limits around audio minutes and storage, but
the value story is routing and proof.

The buyer's pain statements sound like:

- "We record calls, but follow-up still depends on memory."
- "The transcript exists, but nobody knows what to do with it."
- "Our CRM notes are inconsistent."
- "Product evidence is scattered."
- "We cannot let AI write to Slack or customers without review."
- "Important personal calls disappear into my phone."
- "We need source proof, not just a summary."

The weak-fit statements sound like:

- "We just need cheaper transcription."
- "We want zero review for all CRM updates immediately."
- "We do not care where the notes go."
- "We have no follow-up pain."
- "We want compliance guarantees before any product proof."

Pavo should sell to the first group. The second group may become future buyers,
but they are not the best early design partners.

## Chapter X2: The First Design Partners

The best design partners will have real recordings and real routing pain. They
will not need to be convinced that conversations create work. They will already
feel it.

Founder-led B2B teams are strong design partners because founders sit across
sales, product, support, hiring, fundraising, and operations. They have many
recorded conversations and not enough operating bandwidth. They are also
comfortable approving AI recommendations if the value is obvious. A founder
can use Pavo personally before turning it into a team workflow.

Product teams are strong design partners because user evidence is valuable and
dangerous. The danger is not privacy alone; it is interpretation. A user quote
can become an overbroad roadmap claim. Pavo can help route evidence without
flattening ambiguity.

Customer success teams are strong design partners because calls contain
renewal risk, blockers, promises, sentiment, and account context. The
destination systems are obvious: CRM, Linear, support tool, Drive, and internal
briefs. The risks are also obvious: overclaiming, oversharing, wrong account
mapping, and missed follow-up.

Professional services teams are strong design partners because client
conversations become tasks, deliverables, scope changes, and internal notes.
The cost of missing a commitment is high. The cost of oversharing is also high.

Personal administration users are useful design partners because they force
privacy discipline. If Pavo can safely handle school, health, insurance,
vendor, and household calls, it will develop strong primitives for sensitivity,
storage mode, and narrow action.

Weak early design partners include teams that only want meeting notes, teams
that refuse review, teams with no destination systems, and teams whose first
requirement is broad regulated compliance. Pavo can learn from them, but it
should not let them define the first product.

## Chapter X3: The Demo That Teaches The Category

The category will not be understood by explanation alone. The demo must teach
it.

The demo should begin with a recording, not a dashboard. The user should see
that Pavo starts with source material. The product then shows the Flight Path:
Nest, Tune, Scout, Land, Home. Each step should be visible but not theatrical.
The demo should feel like a real workflow.

The default demo should use a customer call because it crosses enough
destinations to show the category:

- archive to Drive
- issue to Linear
- draft CRM note
- blocked Slack route
- Home policy candidate

The decisive moment is the blocked route. Many products can show a summary and
a task. Pavo should show that it can say no. The buyer sees that Pavo is not
just trying to generate more output. It is trying to route correctly.

The second decisive moment is the manifest. After approval, the user sees what
landed. This turns the demo from AI magic into operational software. A route
was recommended, approved, executed, and proven.

The third decisive moment is Home. Pavo proposes a policy but does not activate
it silently. The buyer sees how automation can become safer over time without
becoming hidden.

The demo script should avoid abstract claims. Instead of saying "Pavo
understands your meetings," say:

```text
This sentence is the source span for the Linear issue. This phrase is why the
CRM note requires review. This proposed Slack route is blocked because the
claim is commercially sensitive. This manifest proves the Drive archive landed.
```

That is how Pavo teaches the category.

## Chapter X4: The Category Name Should Stay Practical

"Approval-gated routing for spoken records" is precise, but dense. It belongs
in product docs and sales enablement. The public category language should be
simpler:

```text
The safe path from recordings to work.
```

This phrase has three advantages. It names the source, names the destination,
and implies trust. It does not trap Pavo as notes. It does not overpromise
automation. It makes the buyer curious about the path.

The category story can unfold in layers:

One-line:

```text
Pavo turns recorded conversations into approved, source-backed work.
```

Short explanation:

```text
Recording tools capture what happened. Pavo helps decide what should happen
next, asks before writing, and proves what landed.
```

Technical explanation:

```text
Pavo is an approval-gated routing control plane for spoken records.
```

Investor explanation:

```text
As capture becomes ambient, the missing layer is governed conversion from
spoken source material into operational systems. Pavo owns that conversion.
```

User explanation:

```text
Bring a recording. Pavo shows what it could become and waits for your approval.
```

The product can use all of these, but it should not mix them randomly. The
public site should be concrete. The product docs should be precise. The sales
deck should show the workflow. The investor narrative can explain category
timing.

## Chapter X5: Why Now

Pavo is timely because several changes are converging.

First, capture is becoming easier. People have more recordings because devices,
meeting tools, call systems, and AI products normalize recording. The volume of
spoken source material is rising.

Second, AI can reason over recordings better than before. Transcription,
speaker analysis, summarization, classification, and routing recommendations
are more feasible. The product can now generate useful packet candidates.

Third, teams are more aware of automation risk. People have seen AI generate
polished but wrong text. They know blind writes can create cleanup work. A
product that includes approval and proof is easier to trust.

Fourth, work is fragmented across systems. A conversation rarely belongs in
one place. It may touch CRM, Linear, Drive, Slack, email, personal reminders,
and archives. The need for routing is increasing.

Fifth, personal and professional administration are both overloaded. People
are recording more because they cannot remember everything. They still need a
system that turns important records into controlled follow-up.

The timing is not simply "AI is better now." The timing is:

```text
More recordings + better AI + fragmented work systems + higher automation risk
= need for approval-gated routing.
```

That is the market opening.

## Chapter X6: The Competitive Frame

Pavo should not attack adjacent products. The better stance is to acknowledge
what each layer does and then show the missing path.

Recording devices capture. Pavo routes after capture.

Meeting bots attend and summarize. Pavo turns records into approved downstream
outcomes.

Transcription APIs produce text. Pavo treats text as evidence, not completion.

CRM call intelligence helps revenue teams. Pavo is source-agnostic and can
route to product, archive, tasks, drafts, and blocked outcomes.

Automation platforms connect apps. Pavo decides whether a spoken record is
safe to route and what proof should travel with it.

General AI assistants reason flexibly. Pavo turns reasoning into durable state:
records, packets, approvals, manifests, and policy candidates.

This frame keeps Pavo from sounding defensive. It also makes partnership
possible. Capture tools can feed Pavo. CRMs can be destinations. Automation
tools can become execution partners. Memory/search tools can consume approved
archives. Pavo's category is not "replace everything." It is "control the path
between capture and action."

## Chapter X7: Pricing Around Trust Maturity

Pavo pricing should reflect how much of the Flight Path a buyer uses and how
much trust infrastructure they need.

A simple early pricing model could have three tiers:

Personal Flight:

- local/Plaud import
- private archive
- transcript and review
- routing packets
- manual approvals
- limited exports

Team Flight:

- shared archive
- approval queue
- Drive and Linear destinations
- CRM/email draft routes
- destination manifests
- team roles
- scenario templates

Governed Flight:

- retention policy
- consent tracking
- admin restrictions
- audit exports
- policy approval workflows
- advanced redaction
- governed destination controls

The product should be careful not to put proof behind an expensive tier. Proof
is core. Even a personal user needs manifests. Even a small team needs approval
state. Higher tiers can add governance breadth, not basic trust.

Pricing metrics to test:

- active recordings processed
- storage volume
- destination adapters
- approval seats
- team workspaces
- governed policy features
- audit export volume
- Home policy automation level

Pricing should avoid rewarding unsafe behavior. For example, charging heavily
for approval seats may cause teams to reduce review. Charging only for
transcript minutes may pull the product toward commodity transcription.
Charging for integrations may encourage shallow adapter sprawl. The best
pricing will align with approved outcomes and trust maturity.

## Chapter X8: Onboarding The First User

Onboarding should begin with one recording. Not a workspace setup wizard. Not
a complex integration checklist. One recording.

Step one:

```text
Choose a recording that should have become follow-up work.
```

Step two:

```text
Tell Pavo what kind of record it is: customer call, product interview, personal
administration, sales call, recruiting screen, support escalation, internal
meeting, field memo, or other.
```

Step three:

```text
Choose storage mode: private local, cloud archive, team shared, or governed.
```

Step four:

```text
Tune the record: review key terms, speakers, and uncertain spans.
```

Step five:

```text
Review routes: approve archive, edit task, block unsafe destination, or keep
private.
```

Step six:

```text
Inspect proof after landing.
```

The onboarding win is not "your transcript is ready." The win is:

```text
This recording became the right approved outcome.
```

Onboarding should avoid asking for broad integrations too early. A user who has
not seen one packet land safely may not trust a CRM connection. The product can
offer integrations after the user understands the control model.

## Chapter X9: Investor Narrative

The investor narrative should not oversell Pavo as generic AI productivity. It
should explain the structural shift.

Thesis:

```text
Spoken records are becoming a major source of operational data, but the
conversion layer from recording to work is underbuilt. Pavo is building the
approval-gated routing control plane for that conversion.
```

Market timing:

- capture volume is rising
- AI reasoning over audio is improving
- teams distrust blind automation
- work systems remain fragmented
- source-backed evidence is increasingly valuable

Why Pavo:

- starts with source preservation
- owns the routing packet
- treats approval as a product surface
- writes destination proof
- learns through scoped policy
- can serve personal, team, and governed workflows through the same Flight Path

Initial wedge:

- founder-led teams and product/customer workflows with recorded calls
- Plaud/local import and Drive/Linear first destinations
- narrow loop that proves source to approved work

Expansion:

- more sources
- more destinations
- web approval queue
- team governance
- policy memory
- governed retention and audit

Defensibility:

- durable evidence model
- scenario fixtures
- approval history
- destination manifests
- policy memory
- trust-oriented product design

The investor should leave understanding that Pavo is not chasing note-taking
features. It is building the operational layer that makes recorded speech safe
to use.

# Part 13: Editorial Continuity And Final Book Shape

This part describes how the manuscript should be finished into a coherent
150-page book. The current draft contains the substance: vision, scenarios,
schemas, gotchas, marketing, implementation, and operating doctrine. The final
editorial pass should reduce the feeling of appendices and make the book read
as one argument.

## Chapter Y1: Recommended Final Table Of Contents

The final book should be organized like this:

Part 1: Why Pavo Exists

- The catch fence problem
- Why notes are not enough
- The approval boundary
- The source as trust anchor
- Why routing is the product

Part 2: The Flight Path

- Nest
- Tune
- Scout
- Land
- Home
- Completion states
- Non-action as completion

Part 3: The Product Object Model

- Recording record
- Evidence record
- Routing packet
- Approval decision
- Destination manifest
- Policy candidate
- Status vocabulary

Part 4: Core Scenarios

- customer blocker call
- personal administration call
- product interview
- recruiting screen
- support escalation
- legal-adjacent interview
- internal strategy jam
- field memo

Part 5: Edge Cases And Gotchas

- transcript error
- speaker identity
- consent missing
- duplicate record
- destination outage
- wrong account
- reversal after landing
- stale reprocessing
- policy overlearning
- approval fatigue

Part 6: The Approval Product

- queue design
- record detail
- source viewer
- route preview
- redaction
- destination proof
- Home review

Part 7: Go To Market

- category
- demo
- buyer personas
- sales discovery
- objections
- packaging
- launch assets

Part 8: Implementation Roadmap

- current repo map
- Nest/Tune/Scout/Land/Home modules
- web app and worker architecture
- marketplace migration
- gap register
- build sequence

Part 9: Operating Doctrine

- product reviews
- engineering
- discovery
- release gates
- support
- marketplace
- book maintenance

This structure would turn the existing draft into a book rather than a large
reference document. The content already exists in draft form; the final pass
should move sections into this order, add transitions, and remove repeated
claims.

## Chapter Y2: Repetition To Keep And Repetition To Cut

Some repetition is useful. The book should repeatedly say:

```text
Pavo turns spoken records into approved, source-backed work.
```

That sentence is the spine. It should appear in the introduction, product
spine, marketing section, and conclusion.

The book should also repeat:

- source before summary
- routing before writing
- approval before action
- proof after landing
- policy through review

These are not filler. They are product invariants.

Other repetition should be reduced in the final pass:

- repeated definitions of Nest/Tune/Scout/Land/Home
- repeated warnings about not being a meeting note app
- repeated examples of customer call to Linear/CRM/Drive
- repeated lists of destinations
- repeated marketplace verification language

The final editorial rule:

```text
Repeat invariants. Consolidate explanations.
```

This keeps the book coherent without making it sterile.

## Chapter Y3: Tone And Voice

The book should sound practical, not breathless. Pavo is ambitious, but the
voice should not be hype. The product earns trust by being precise.

Good tone:

- direct
- concrete
- operational
- honest about risk
- clear about what is shipped and what is future
- respectful of adjacent tools
- careful with privacy and compliance claims

Bad tone:

- magical
- generic AI enthusiasm
- "never miss anything"
- "automate everything"
- "replace your team"
- "compliance-ready" without proof
- "private by default" without architecture

The book should make readers feel that Pavo is serious. Serious does not mean
dull. It means the product understands the consequences of being wrong.

## Chapter Y4: Page-Budget Proof

A rough page budget for a 150-page product book can use 450-500 words per page
for dense Markdown prose. At 70,000 words, the manuscript supports roughly
140-155 dense pages before diagrams, tables, and code blocks. With tables,
schemas, screenshots, and spacing, 65,000-70,000 words can credibly become 150
formatted pages.

The current manuscript should therefore target:

```text
minimum credible depth: 65,000 words
strong target depth: 70,000-80,000 words
```

Word count alone is not enough. The book also needs coverage:

- product vision
- Flight Path model
- user scenarios
- product docs
- marketing narrative
- edge cases
- gotchas
- implementation implications
- why Pavo exists

Once the manuscript exceeds the word target and covers those areas, the final
work becomes editorial: ordering, transitions, deduplication, and verification.

## Chapter Y5: Final Verification Checklist

Before closing the full product-book goal, verify:

- `docs/pavo-product-book.md` exists
- word count meets page-budget target
- product thesis is clear
- Flight Path terms are present
- scenarios cover business and personal use
- gotcha matrix exists
- routing packet examples exist
- UI specs exist
- marketing assets exist
- implementation roadmap exists
- operating doctrine exists
- expansion backlog is removed or converted to final next steps
- README points to product book
- `docs/product.md` points to product book
- `skills/use-pavo/SKILL.md` uses current vocabulary
- marketplace plugin is republished
- Pavo tests pass
- marketplace check passes
- marketplace tests pass
- Linear parent and subtasks have proof comments

This checklist is stricter than "the file is long." The goal is a usable
product canon, not a word pile.

## Chapter Y6: Final Conclusion Draft

The final book should end plainly.

Pavo exists because recorded speech is becoming a major source of operational
truth, but capture alone does not create completion. The recording must be
preserved. The record must be made trustworthy. The information must be routed
with context. The user must approve the actions that matter. The destination
must prove what happened. The system may learn, but only through scoped,
reviewed policy.

That is the Flight Path:

```text
Nest -> Tune -> Scout -> Land -> Home
```

The path matters because the stakes vary. A customer call can become a product
issue, CRM note, archive, and blocked Slack message. A personal call can become
a private archive and one reminder. A research interview can become evidence
without becoming a roadmap promise. A recruiting screen can become factual ATS
notes without leaking sensitive evaluation. A legal-adjacent record can remain
restricted. A field memo can wait for review before becoming a safety action.

Pavo's job is not to turn every conversation into more output. Pavo's job is
to help each spoken record become the right outcome.

The product should be built with restraint because restraint is part of the
value. Approval is not a lack of ambition. It is how AI becomes usable in
workflows where mistakes matter. Proof is not bureaucracy. It is how users know
what happened. Source evidence is not a backend detail. It is the difference
between trust and generated text.

If Pavo succeeds, people will record important conversations with more
confidence because they will know there is a safe path after capture. They will
not have to choose between forgetting and blind automation. They will have a
reviewable system that catches, tunes, scouts, lands, and learns.

Pavo turns spoken records into approved, source-backed work.

# Part 14: Fixture Ledger, Scorecards, And Review Artifacts

The book should not end only as prose. Pavo is a product that should convert
written doctrine into executable checks. This part defines the fixture ledger,
scorecards, and review artifacts that should carry the book into product work.
It is intentionally concrete. The future team should be able to open these
chapters and create issues, tests, schemas, UI review rubrics, and customer
discovery forms.

## Chapter Z1: Scenario Fixture Ledger

Every major scenario in the book should eventually become a fixture. A fixture
is not just a story. It is a structured input and expected output that protects
product behavior.

Minimum fixture fields:

- fixture id
- scenario title
- persona
- source type
- sensitivity class
- storage mode
- transcript quality
- key evidence spans
- uncertain spans
- expected route candidates
- expected blocked routes
- expected approval requirements
- expected Land manifests
- expected Home candidate
- gotchas covered
- regression priority

Fixture F1: Customer blocker call

Purpose:

- prove that a customer complaint can become an archive, Linear issue, CRM
  draft, and blocked Slack route without overstating commercial pressure

Inputs:

- customer call
- account id
- transcript span for product blocker
- transcript span for expansion concern
- reviewed correction for product name

Expected Scout output:

- Drive archive route
- Linear investigation draft
- CRM note draft
- blocked Slack route for expansion claim
- commercial sensitivity flag

Expected Land output:

- Drive archive manifest
- Linear issue or draft manifest
- CRM draft manifest if enabled
- blocked Slack manifest

Gotchas covered:

- user pain becomes roadmap commitment
- commercial claim overstatement
- wrong CRM account mapping
- broad channel oversharing

Fixture F2: Personal administration call

Purpose:

- prove that Pavo can create narrow personal follow-up without leaking private
  context into team systems

Inputs:

- personal phone call
- private storage mode
- document deadline
- uncertain agent name
- sensitive policy or health detail

Expected Scout output:

- private archive route
- reminder route
- email draft route
- blocked shared Drive/team route
- sensitive fields redacted from drafts

Expected Land output:

- private archive manifest
- reminder manifest
- email draft manifest if enabled
- blocked team route manifest

Gotchas covered:

- personal content routes to business tool
- redaction happens too late
- no-action and narrow-action behavior
- policy learns too broadly

Fixture F3: Ambiguous product interview

Purpose:

- prove that Pavo preserves ambiguity and does not turn one user request into
  an unsupported roadmap commitment

Inputs:

- user interview
- quote about confusion
- quote asking for shortcut
- quote expressing caution
- uncertain competitor mention

Expected Scout output:

- research archive route
- Linear discovery draft
- blocked roadmap commitment
- review note preserving ambiguity

Expected Land output:

- research archive manifest
- Linear discovery issue or draft manifest
- blocked roadmap route manifest

Gotchas covered:

- user pain becomes roadmap commitment
- transcript uncertainty
- unsupported competitor claim
- action pressure from product teams

Fixture F4: Recruiting screen

Purpose:

- prove that Pavo separates factual candidate-provided information from
  sensitive evaluation and compensation content

Inputs:

- recruiting call
- candidate logistics
- compensation range
- availability
- evaluation note
- consent state

Expected Scout output:

- ATS factual note draft
- private hiring note
- follow-up task
- blocked Slack route
- compensation sensitivity flag

Expected Land output:

- ATS draft manifest
- follow-up task manifest
- private note retention manifest
- blocked Slack manifest

Gotchas covered:

- sensitive evaluation oversharing
- wrong destination audience
- redaction timing
- review owner requirements

Fixture F5: Support escalation

Purpose:

- prove that Pavo routes facts to engineering and account impact to CS while
  blocking unsupported broad claims

Inputs:

- support escalation call
- error details
- customer emotional statements
- account id
- support ticket id
- incident uncertainty

Expected Scout output:

- engineering investigation draft
- CS account note draft
- leadership brief draft
- blocked public status route

Expected Land output:

- Linear engineering issue manifest
- CRM/account note manifest
- brief draft manifest
- blocked public route manifest

Gotchas covered:

- angry language treated as fact
- unsupported incident scope
- wrong account mapping
- broad internal amplification

Fixture F6: Legal-adjacent interview

Purpose:

- prove that Pavo can preserve restricted evidence and refuse interpretive
  routes

Inputs:

- legal-adjacent interview
- restricted storage mode
- allegation-like statements
- uncertain facts
- authorized reviewer

Expected Scout output:

- restricted archive route
- authorized review task
- blocked interpretive summary
- blocked broad sharing routes

Expected Land output:

- restricted archive manifest
- review task manifest
- blocked summary manifest

Gotchas covered:

- meeting notes become source of truth
- compliance-adjacent summary as findings
- missing authorization
- overconfident narrative generation

Fixture F7: Internal strategy jam

Purpose:

- prove that brainstorming can become archive, decisions, and open questions
  without becoming false commitments

Inputs:

- internal strategy meeting
- speculative ideas
- explicit decisions
- open questions
- "not a commitment" language

Expected Scout output:

- internal archive
- decision log draft
- open question list
- blocked execution tasks from speculative language

Expected Land output:

- archive manifest
- decision log manifest
- open questions manifest
- blocked task manifests

Gotchas covered:

- brainstorm becomes task
- strategy note becomes external claim
- action bias
- no-action as completion

Fixture F8: Poor audio field memo

Purpose:

- prove that low-confidence safety language triggers review before routing

Inputs:

- noisy field memo
- site metadata
- uncertain safety phrase
- maintenance clue
- operator id

Expected Scout output:

- archive route
- safety review task
- maintenance draft excluding uncertain phrase
- blocked incident report until review

Expected Land output:

- archive manifest
- safety review task manifest
- maintenance draft manifest after review
- blocked incident report manifest

Gotchas covered:

- transcript error becomes action
- low-confidence safety routing
- source quality propagation
- review before high-risk Land

Fixture F9: Destination outage during Land

Purpose:

- prove that Pavo handles partial landing without ambiguity or duplicate
  retries

Inputs:

- approved packet with Drive and Linear routes
- simulated Drive success
- simulated Linear outage
- idempotency key

Expected Scout output:

- approved routes ready for Land

Expected Land output:

- Drive landed manifest
- Linear failed manifest with retry state
- no duplicate Drive write on retry
- packet remains partially landed

Gotchas covered:

- destination outage creates ambiguous state
- retry duplicates work
- partial failure hidden
- stale packet retry

Fixture F10: Wrong account mapping

Purpose:

- prove that uncertain destination identity blocks or requires review before
  CRM/Linear writes

Inputs:

- customer call
- ambiguous account name
- two possible CRM accounts
- transcript evidence
- reviewer correction

Expected Scout output:

- archive route
- blocked CRM route until account review
- Linear draft with account ambiguity warning

Expected Land output:

- archive manifest
- no CRM write before account approval
- corrected destination manifest after review

Gotchas covered:

- wrong CRM account mapping
- speaker/company name confusion
- unsafe direct write
- review-required identity resolution

The first fixture ledger should start with these ten. They cover enough product
surface to protect the core thesis. More scenarios can be added later, but a
small reliable fixture suite is better than a large unmaintained one.

## Chapter Z2: Pavo Product Scorecard

Every release should be scored against the Flight Path. The scorecard should be
simple enough to use and strict enough to catch drift.

Nest score:

0 means Pavo does not preserve the source.

1 means Pavo can reference the source but not reliably preserve it.

2 means Pavo preserves the source locally with basic metadata.

3 means Pavo preserves source, hash, metadata, owner, sensitivity, and storage
mode.

4 means Pavo has source ledger, duplicate detection, and archive proof.

5 means Pavo has validated source adapters, idempotent archive behavior, and
auditable source lifecycle.

Tune score:

0 means no transcript or evidence.

1 means transcript exists but lacks provenance.

2 means transcript has manifest and source link.

3 means transcript includes uncertainty, speaker evidence, and review state.

4 means review corrections, stale detection, and evidence versions exist.

5 means Tune evidence is fixture-tested and drives Scout behavior.

Scout score:

0 means no routing packet.

1 means freeform recommendations only.

2 means structured packet without full evidence refs.

3 means packet includes evidence, sensitivity, blocked routes, and approval
requirements.

4 means scenario fixtures prove expected routing behavior.

5 means Scout is destination-aware, policy-aware, and regression-tested across
major gotchas.

Land score:

0 means no destination writes.

1 means manual exports only.

2 means one destination can land with proof.

3 means approved-only Land, idempotency, dry-run, and manifests exist.

4 means failure, retry, duplicate, and partial states are tested.

5 means multiple adapters share one proof contract and safe approval boundary.

Home score:

0 means no learning.

1 means preferences are informal.

2 means route history is visible.

3 means policy candidates are generated from reviewed history.

4 means policies require approval, have scope, and can be revoked.

5 means Home safely influences Scout and Land through audited, tested policy.

Overall product score:

The overall score is not the average. Pavo is limited by the weakest stage in
the path a feature depends on. A beautiful Home policy UI cannot compensate for
missing Land manifests. A strong transcript cannot compensate for missing
approval. A broad destination list cannot compensate for weak Scout packets.

Release interpretation:

- 0-1: prototype or raw capability
- 2: useful local tool
- 3: credible alpha workflow
- 4: trustworthy beta workflow
- 5: mature product path

The first commercial Pavo should aim for 3 across Nest, Tune, Scout, and one
Land destination. Home can start at 2 or 3 as policy candidates.

## Chapter Z3: Design Review Scorecard

Pavo UI should be reviewed through user questions, not visual preference alone.
Each core surface should answer specific questions.

Record list:

- What records need my attention?
- Which records are safely archived?
- Which records are waiting on Tune?
- Which records have route approvals pending?
- Which records have failed Land attempts?
- Which records are private?

Record detail:

- What is the source?
- Can I play or inspect it?
- What evidence exists?
- What is uncertain?
- What routes are proposed?
- What is blocked?
- What has already landed?

Evidence viewer:

- Which transcript span supports this route?
- Who said it?
- How confident is Pavo?
- Has a human reviewed it?
- What changed after correction?

Routing packet review:

- What action is being proposed?
- Why?
- What destination will receive it?
- What exact content will be written?
- What approval is required?
- What happens if I reject?

Approval queue:

- What decisions are waiting?
- Which are high risk?
- Which can be approved quickly?
- Which need more evidence?
- Which are stale?

Destination manifest:

- What landed?
- Where?
- When?
- Who approved it?
- What idempotency key was used?
- What failed?

Home review:

- What policy is Pavo proposing?
- Which decisions support it?
- What are the limits?
- What would change?
- How do I revoke it?

Design review should fail any surface that hides the source, hides the
destination preview, hides approval state, hides proof, or makes blocked routes
look like errors.

## Chapter Z4: Engineering Ticket Template

Future implementation tickets should use a Pavo-specific template. Generic
feature tickets will miss the trust requirements.

Ticket title:

```text
Pavo: [Flight Path stage] [specific behavior]
```

Problem:

- What record workflow fails today?
- Which user is affected?
- What current workaround exists?

Flight Path stage:

- Nest
- Tune
- Scout
- Land
- Home
- cross-stage

Source/evidence:

- What source object is used?
- What evidence object is created or consumed?
- What uncertainty matters?

Approval:

- Is approval required?
- Who approves?
- What exactly is approved?
- Can the user edit before approval?

Destination/proof:

- Does anything land?
- What manifest proves it?
- What failure states exist?
- What idempotency behavior is needed?

Privacy/sensitivity:

- What data is sensitive?
- What must be redacted?
- What destinations are forbidden?
- What secrets must not be logged?

Tests:

- unit test
- fixture test
- dry-run test
- failure test
- duplicate/retry test
- stale/reversal test if relevant

Docs:

- README
- product spine
- product book
- skill
- marketplace
- proof report

Definition of done:

- code implemented
- tests pass
- proof artifact written
- docs updated
- Linear proof comment added

This template keeps engineering tied to the book. It also prevents shallow
destination work from bypassing approval and proof.

## Chapter Z5: Customer Pilot Checklist

Before a pilot, Pavo should know exactly what it is proving.

Pilot setup:

- named pilot owner
- user persona
- source type
- destination systems
- approval owner
- sensitivity boundaries
- storage mode
- success metric
- explicit non-goals

Pilot source checklist:

- source recordings available
- permission to process
- retention expectation
- private/team mode selected
- sample recording chosen
- source adapter tested

Pilot Tune checklist:

- transcript pipeline works
- context terms available
- speaker expectations known
- review workflow explained
- uncertainty shown

Pilot Scout checklist:

- first route types selected
- blocked routes defined
- approval requirements defined
- destination previews understood
- no-action state explained

Pilot Land checklist:

- first destination selected
- dry-run tested
- approval tested
- manifest inspected
- failure behavior explained
- no outbound send unless explicitly in scope

Pilot Home checklist:

- policy learning is opt-in
- candidates are reviewable
- no silent automation
- revocation explained

Pilot success should be measured by completed records, not signups. A completed
record is one that reached the right state: archived, tuned, approved, landed,
blocked, private, or no-action with proof. The pilot should ask:

```text
Did Pavo help this recording become the right outcome faster and safer than the
old workflow?
```

If the answer is yes, the pilot is meaningful even if only a few records were
processed. If the answer is no, processing more recordings will not fix the
product.

## Chapter Z6: Risk Register

Pavo's risk register should stay visible because the product operates near
sensitive workflows.

Risk: source loss.

Impact:

- downstream evidence cannot be trusted

Mitigation:

- source hashing, durable local copy, archive manifests, duplicate detection

Risk: transcript overconfidence.

Impact:

- wrong words become tasks, notes, or claims

Mitigation:

- uncertainty markers, human review, stale detection, source replay

Risk: speaker misattribution.

Impact:

- wrong person appears to make a commitment

Mitigation:

- speaker confidence, review bundles, evidence separation, no high-risk routes
  from weak attribution

Risk: wrong destination.

Impact:

- sensitive or false information lands in the wrong system

Mitigation:

- destination preview, identity evidence, approval, blocked routes, manifests

Risk: approval fatigue.

Impact:

- users stop reviewing carefully or abandon the product

Mitigation:

- better packet design, grouped low-risk approvals, Home candidates, clear
  evidence, fast reject

Risk: blind automation pressure.

Impact:

- product overroutes to satisfy perceived customer demand

Mitigation:

- approval boundary, marketing guardrails, release gates, policy review

Risk: compliance overclaim.

Impact:

- customer trust and legal exposure

Mitigation:

- precise copy, shipped-control evidence, governed features only when built

Risk: personal/team boundary failure.

Impact:

- private records leak into team systems or policy

Mitigation:

- storage mode, visibility, policy scope, blocked destinations, separate Home
  learning

Risk: destination side effects.

Impact:

- duplicate writes, wrong messages, stale updates

Mitigation:

- dry-run, idempotency, approval ids, stale packet checks, failure manifests

Risk: product becomes archive dump.

Impact:

- records accumulate without becoming useful outcomes

Mitigation:

- completion states, queue aging, no-action states, review cadence, metrics

The risk register should be reviewed before major releases and after support
incidents. Each new risk should become either a product constraint, a fixture,
a release gate, or a customer-facing limitation.

## Chapter Z7: Metrics That Matter

Pavo should avoid vanity metrics. The product should not optimize for raw
recording volume, transcript minutes, or number of AI summaries generated. The
right metrics measure whether records become correct outcomes.

North-star metric:

```text
approved, source-backed outcomes per active user
```

Supporting metrics:

- records nested
- records tuned
- routing packets generated
- approvals completed
- routes edited before approval
- blocked routes accepted
- routes landed
- destination manifests created
- no-action completions
- Home candidates reviewed
- policies approved
- reversals handled

Quality metrics:

- route rejection rate by reason
- blocked route false-positive rate
- blocked route false-negative incidents
- transcript uncertainty causing route review
- destination failure rate
- duplicate write prevention
- stale packet detection
- wrong destination incidents
- personal/team boundary incidents

Speed metrics:

- time from source capture to Nest
- time from Nest to Tune
- time from Tune to Scout
- time from Scout to approval
- time from approval to Land
- time to clear queue

Trust metrics:

- percentage of routes with evidence refs
- percentage of Land manifests with destination ids
- percentage of policies with supporting examples and counterexamples
- percentage of high-risk routes requiring review
- percentage of support incidents with complete proof packet

Bad metrics:

- summaries generated
- integrations connected
- routes auto-landed without risk weighting
- transcript minutes processed without outcomes
- messages sent
- number of policies created without approval

Pavo's metrics should reward correctness. A blocked unsafe route should count
as a successful outcome when blocking was appropriate. A no-action decision
should count as completion when the record truly needed no downstream work.

## Chapter Z8: Future Work Register

Once the book is converted into final structure, future work should move into
implementation systems rather than staying as prose.

Future implementation issue: normalized records.

Scope:

- `RecordingRecord`
- `SourceArtifact`
- `EvidenceRecord`
- serialization
- tests

Future implementation issue: routing packet validator.

Scope:

- schema
- packet version
- evidence refs
- blocked routes
- approval requirements
- fixture tests

Future implementation issue: approval state machine.

Scope:

- approve
- edit
- reject
- block
- return to Tune
- stale packet
- reversal

Future implementation issue: Drive Land adapter.

Scope:

- dry-run
- archive write
- idempotency
- manifest
- failure behavior

Future implementation issue: Linear Land adapter.

Scope:

- draft or issue creation
- evidence refs
- destination preview
- idempotency
- manifest

Future implementation issue: Home policy candidates.

Scope:

- approval history
- candidate generation
- scope
- examples
- review UI
- revocation

Future design issue: approval queue wireframes.

Scope:

- record list
- detail
- packet review
- redaction
- destination manifest
- Home review

Future GTM issue: design partner packet.

Scope:

- demo script
- discovery guide
- pilot checklist
- buyer one-pager
- limitations note

Future docs issue: fixture ledger extraction.

Scope:

- convert Chapter Z1 to JSON fixtures
- link fixtures to gotchas
- add expected packet outputs
- add expected manifest outputs

This register should prevent the book from becoming a parking lot. The book
sets direction; Linear and the repo should carry execution.

## Chapter Z9: Meeting-Bot Complaint Response Pack

The detailed implementation spec lives in
[pavo-meeting-bot-complaint-response.md](pavo-meeting-bot-complaint-response.md).
The fixture ledger lives in
[pavo-complaint-fixture-ledger.md](pavo-complaint-fixture-ledger.md). The gate
contracts live in [pavo-gate-contracts.md](pavo-gate-contracts.md).
The one-button UX acceptance spec lives in
[pavo-one-button-ux-acceptance.md](pavo-one-button-ux-acceptance.md). The
proof-first demo script lives in
[pavo-proof-first-demo-script.md](pavo-proof-first-demo-script.md). The
packaging doctrine lives in
[pavo-packaging-trust-promises.md](pavo-packaging-trust-promises.md). The
anti-slop audit lives in [pavo-anti-slop-audit.md](pavo-anti-slop-audit.md).
The completion audit lives in [pavo-completion-audit.md](pavo-completion-audit.md).
This chapter records the book-level standard it introduces.

Pavo should be judged against the complaints users already have about meeting
bots and transcription assistants:

- transcripts are wrong on accents, jargon, noise, and multiple speakers
- speaker attribution is unreliable
- summaries change the meaning of the conversation
- bots join, record, or share in ways that feel surprising
- users cannot tell where data goes
- setup and navigation are too heavy
- pricing and credits feel slippery
- notes stop at recall instead of becoming approved work

The answer is not to claim "better AI." The answer is a product contract:

```text
preserve source -> tune evidence -> recommend routes -> approve -> land -> prove
```

Every claim in this complaint-response pack must have four parts:

1. the user complaint
2. the Pavo mechanism
3. the plain-user behavior
4. the acceptance test

If a sentence cannot point to all four, it is probably marketing filler.

The core mechanisms are:

- transcript bundle, not single transcript
- uncertainty spans, not blind confidence
- speaker identity as evidence, not a label
- summary separated from route
- route packet before destination write
- consent and visibility fields before sharing
- one primary next action per record
- proof manifest after Land

The plain-user product standard is intentionally strict. A user should be able
to add a recording, fix the important parts, approve the safe actions, and see
proof without understanding diarization, source separation, embeddings,
manifests, or destination adapters.

The expert product standard is equally strict. An operator should be able to
inspect source hash, transcript versions, context terms, speaker anchors,
voiceprint scores, overlap regions, separated stems, route packet JSON, and the
landing manifest without guessing what the system did.

The first release should include a real blocked route in the demo. That blocked
route is not a failure. It is the product teaching the buyer that Pavo prevents
unsafe automation.

Required acceptance fixtures from the complaint-response design:

- `CFX-001`: custom vocabulary drift
- `CFX-002`: accent and slang preservation
- `CFX-003`: three speakers and short interjections
- `CFX-004`: overlap during a decision
- `CFX-005`: summary meaning drift
- `CFX-006`: stale processing before Landing

The release gate is simple:

```text
No evidence span, no action.
No approval, no landing.
No known visibility, no external route.
No speaker evidence, no named commitment.
```

This chapter should be kept short in the book because the standalone spec is
the implementation artifact. The book's job is to make the standard unavoidable.

Final complaint-response product artifacts:

- one-button UX acceptance: one primary next action per record, data card on
  every critical surface, risky spans before full transcript, proof after Land
- fixture ledger: `CFX-001` through `CFX-006`
- gate contracts: source through landing gates with route-packet and landing
  manifest minimums
- proof-first demo: real or fixture-backed recording, one corrected risky span,
  one blocked route, one approved action, one proof manifest
- packaging doctrine: proof is not an add-on
- anti-slop audit: claims must point to a screen, fixture, gate, route packet,
  or proof manifest

# Final Pass Backlog

This manuscript is now at credible formatted-book depth for the 150-page goal:
65,000+ words plus tables, schemas, code blocks, checklists, and structured
artifacts. It has a real spine, core vocabulary, implementation implications,
packet schema, adapter playbooks, trust vocabulary, go-to-market framing,
metrics, scenario chapters, operating doctrine, buyer narrative, fixture
ledger, scorecards, and final editorial structure. The remaining work should be
final alignment and verification rather than broad content expansion.

Recommended final passes:

1. Reorder the manuscript into the final table of contents from Chapter Y1.
2. Remove duplicate explanations while preserving the core invariants.
3. Convert the expansion backlog into a short "future work" note or remove it
   entirely after final verification.
4. Promote the scenario chapters into a fixture ledger once Scout/Land
   validation exists.
5. Turn UI specs into implementation tickets for the approval queue.
6. Turn schema examples into machine-readable contract tests.
7. Align README, product spine, skill instructions, and marketplace copy.
8. Run Pavo and marketplace verification.
9. Add final Linear proof with word count, paths, and test evidence.

The finished book should be long because the product is subtle. Pavo is not
only capture. It is not only transcription. It is not only routing. It is the
controlled path from spoken source to approved work.
