# Pavo Packaging And Trust Promises

Pavo cannot fix meeting-bot trust complaints if its packaging hides trust
primitives behind credits, unclear tiers, or surprise limits.

The product promise is:

```text
Proof is not an add-on.
```

## Packaging Principle

Pavo may charge for capacity, collaboration, adapters, retention, and managed
infrastructure. It should not charge extra for the safety primitives that make
the product trustworthy.

Trust primitives must be included in every usable tier:

- source preservation
- source manifest
- transcript manifest
- uncertainty markers
- approval state
- blocked routes
- destination preview
- landing manifest
- redacted proof summary
- no-action decision

## Always Included

These features are part of Pavo's definition, not premium upsells.

| Feature | Why it must be included |
| --- | --- |
| Source preservation | Without source, transcript and route proof are weak |
| Source hash and provenance | Needed for audit and stale detection |
| Transcript manifest | Needed to know engine, terms, and processing state |
| Uncertainty markers | Needed to prevent confident wrong routes |
| Speaker evidence state | Needed before named commitments |
| Route packet | Pavo routes before it writes |
| Approval state | Approval is the product boundary |
| Blocked routes | Blocking unsafe action is a successful outcome |
| Destination preview | User must see what will be written |
| Landing manifest | Proof after action is required |

Packaging copy must not imply that a lower tier gets unsafe automation or
unprovable notes.

## Paid Expansion Areas

Paid tiers can expand:

- storage volume
- processing volume
- team seats
- shared workspaces
- destination adapters
- governed retention
- audit exports
- SSO and admin controls
- policy libraries
- managed workers
- higher-throughput reprocessing

These are capacity and governance expansions. They do not remove the baseline
proof requirement.

## Prohibited Packaging Moves

Do not:

- charge extra for seeing why a route was blocked
- hide transcript uncertainty on lower tiers
- let low tiers create actions without manifests
- make approval history a premium-only feature
- make destination preview a premium-only feature
- sell "autopilot follow-up" as the default product
- meter basic blocked-route proof as a credit burn
- make pricing copy imply perfect transcription

## Credit Language Rules

Credits are acceptable only when they map to capacity.

Allowed:

```text
Includes 100 processed recording hours per month.
Additional processing hours are billed at...
```

Avoid:

```text
Spend credits to unlock advanced proof.
Spend credits to see why Pavo blocked a route.
Spend credits to approve actions.
```

If credits are used, every billable action should answer:

- what was processed
- what artifact was produced
- whether the action was reversible
- whether it caused an external write

## Candidate Tiers

These are hypotheses, not final prices.

### Local

For one person trying Pavo with local recordings.

Includes:

- local source preservation
- local transcript bundles
- uncertainty spans
- one-button review queue
- route packet preview
- local proof manifests
- no external writes without approval

Limits:

- local storage only
- manual export
- no managed team workspace
- limited adapter automation

### Pro

For an operator using Pavo repeatedly.

Adds:

- larger processing volume
- Drive archive adapter
- Linear draft adapter
- reusable context profiles
- fixture-backed demo templates
- policy candidates
- audit export

### Team

For a team that shares records.

Adds:

- team workspace
- role-based visibility
- shared policy review
- governed retention
- SSO/admin controls
- destination adapter controls
- team audit exports

### Enterprise

For regulated or high-volume environments.

Adds:

- dedicated storage controls
- private deployment options
- custom retention
- custom destination adapters
- legal/security review package
- managed worker capacity

## Claims By Tier

Every tier can say:

```text
Pavo preserves the source, shows uncertainty, recommends routes, asks before
Land, and records proof.
```

No tier should say:

```text
Pavo guarantees perfect transcripts.
Pavo sends follow-up automatically.
Pavo replaces consent review.
Pavo removes the need for human approval.
```

## Public Promise Boundary

Good public claim:

```text
Pavo produces the best transcript it can prove for the route being approved.
```

Bad public claim:

```text
Pavo is the most accurate transcription tool.
```

Good public claim:

```text
Pavo blocks external routes when consent, visibility, evidence, or approval is
missing.
```

Bad public claim:

```text
Pavo automates every meeting follow-up.
```

## Buyer-Facing Pricing FAQ

Question:

```text
Will I pay extra to see why Pavo blocked something?
```

Answer:

```text
No. Blocked-route proof is part of the product. You may pay for more storage,
processing, adapters, seats, or governance, but not for the basic proof that a
route was unsafe.
```

Question:

```text
Do lower tiers get lower trust?
```

Answer:

```text
No. Lower tiers may have lower capacity and fewer adapters. They still preserve
source, show uncertainty, require approval, and produce proof.
```

Question:

```text
What happens if I run out of processing volume?
```

Answer:

```text
Pavo should preserve existing source artifacts and proofs. It may pause new
processing or reprocessing until capacity is available, but it should not hide
existing proof.
```

## Packaging Acceptance Criteria

Packaging is acceptable when:

- every tier includes the trust primitives
- paid tiers expand capacity, adapters, collaboration, or governance
- pricing copy does not imply proof is optional
- blocked-route proof is visible without an upsell
- route approval is not metered as a premium action
- public claims separate current capability from future roadmap
- no copy promises perfect transcription or fully automatic follow-up

Packaging fails when:

- proof is positioned as a premium feature
- low tiers can write externally without full manifests
- credit language hides what caused an external write
- pricing creates surprise around review or approval
- marketing copy suggests unsafe automation is a benefit
