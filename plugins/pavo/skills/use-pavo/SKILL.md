---
name: use-pavo
description: Use when the user asks about Pavo, Plaud recordings, Plaud CLI, Plaud MCP, real audio files, speaker identification, custom dictionaries, Pavo manifests, Google Drive sync planning, routing, or task creation from recordings.
---

# Use Pavo

Pavo is an evidence-first approval queue for captured conversations. It wraps
Plaud CLI/MCP surfaces and local media imports so agents can preserve real
audio files, tune speaker-aware transcript evidence, scout routing
recommendations, land approved actions, and archive durable proof.

Use the Pavo Flight Path vocabulary when describing product state:

```text
Nest -> Tune -> Scout -> Land -> Home
```

- Nest: capture and preserve the source recording.
- Tune: make the record accurate and trustworthy.
- Scout: recommend routes and actions.
- Land: execute approved actions.
- Home: learn where future records belong.

## Source of Truth

Use the local Pavo CLI/package first:

```bash
pavo --help
pavo doctor
pavo config show
pavo plaud me
pavo plaud files
pavo plaud download <recording-id>
pavo audio doctor
pavo transcribe <recording-id> --context-term Plaud
```

Canonical source repo:

```text
/Users/dshanklin/repos-eidos-agi/pavo
```

Canonical product book:

```text
/Users/dshanklin/repos-eidos-agi/pavo/docs/pavo-product-book.md
```

Edited reader-facing manuscript:

```text
/Users/dshanklin/repos-eidos-agi/pavo/docs/pavo-core-manuscript.md
```

Meeting-bot complaint response design:

```text
/Users/dshanklin/repos-eidos-agi/pavo/docs/pavo-meeting-bot-complaint-response.md
```

Complaint fixture ledger:

```text
/Users/dshanklin/repos-eidos-agi/pavo/docs/pavo-complaint-fixture-ledger.md
```

Gate contracts:

```text
/Users/dshanklin/repos-eidos-agi/pavo/docs/pavo-gate-contracts.md
```

One-button UX acceptance:

```text
/Users/dshanklin/repos-eidos-agi/pavo/docs/pavo-one-button-ux-acceptance.md
```

Proof-first demo script:

```text
/Users/dshanklin/repos-eidos-agi/pavo/docs/pavo-proof-first-demo-script.md
```

Packaging and trust promises:

```text
/Users/dshanklin/repos-eidos-agi/pavo/docs/pavo-packaging-trust-promises.md
```

Anti-slop audit:

```text
/Users/dshanklin/repos-eidos-agi/pavo/docs/pavo-anti-slop-audit.md
```

Completion audit:

```text
/Users/dshanklin/repos-eidos-agi/pavo/docs/pavo-completion-audit.md
```

Use the product book for detailed Flight Path glossary/status vocabulary,
routing packet concepts, approval-state language, UI product specs, marketing
guardrails, implementation roadmap, operating doctrine, fixture ledger, and
scorecards. Use the core manuscript when the user wants the clean product
argument without the full sourcebook. Use the complaint-response design when
the work needs to answer meeting-bot category failures with concrete UX. Use
the fixture ledger and gate contracts when the work needs acceptance tests,
algorithm gates, route-packet requirements, or release criteria. Use the
one-button UX, demo, packaging, and anti-slop docs when shaping the build,
launch narrative, or buyer-facing promises. Use the completion audit when
checking whether the current product-doc goal has been satisfied.

Local non-secret config/cache root:

```text
~/Eidos/Pavo
```

## Operating Rules

- Treat original Plaud audio as the source artifact, not transcript-only data.
- Keep Plaud, Google, and OpenAI credentials in their native credential stores.
- Do not paste raw recordings, signed URLs, OAuth tokens, or voice fingerprints
  into chat, Linear, GitHub, logs, or docs.
- Keep Codex, Claude, and MCP surfaces thin; the Pavo CLI/package owns behavior.
- Prefer manifest-backed proof: command output, local file paths, hashes, and
  redacted metadata.

## Common Flows

### Check Readiness

```bash
pavo doctor
pavo audio doctor
```

### List Plaud Recordings

```bash
pavo plaud files
```

### Download Real Audio

```bash
pavo plaud download <recording-id>
```

Expected local path:

```text
~/Eidos/Pavo/cache/plaud/<recording-id>/audio.mp3
```

### Transcribe With Call-Specific Vocabulary

```bash
pavo transcribe <recording-id> --context-term Plaud --context-term Pavo
```

Expected Pavo manifest:

```text
~/Eidos/Pavo/cache/plaud/<recording-id>/pavo-transcribe-manifest.json
```

## Boundaries

Pavo may inspect local files and run local CLI commands. For external writes
such as Google Drive upload, start with dry-run or explicit user approval when
the command would create or modify remote artifacts.
