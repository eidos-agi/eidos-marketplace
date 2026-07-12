## Philosophy

complex-test-cases is the case authority: the thing that decides whether a green
means anything. Its one rule is that a check must have been observed RED before its
green is trusted, because a test that has never failed has never been tested. That
rule is sound, and it works — it has caught real false greens, including in the very
tools built alongside it.

But a verification tool is held to a standard nothing else is: **its own trust-
worthiness cannot itself be an unearned claim.** A test framework that is wrong is
merely buggy. A *case authority* that is wrong is a false-green factory — it stamps
"earned" on work that was not, at scale, in the one place people have stopped
checking because they trusted the stamp. So the bar for calling this tool ready is
not "it runs." It is "a stranger, verifying code neither they nor the tool helped
write, gets a green they can actually rely on."

That gap — between "the discipline is right" and "the tool can be handed to someone
who didn't build it" — is what this charter is about. The discipline earned its
place the day it refused its author's post-hoc greens. The tool has not yet earned
the right to be depended on by people who were not in the room. Prime time is the
distance between those two facts, made into a checklist that goes green the same way
every other green here does: by first being red.

## The Friction

Everything below was hit by hand, in real use, the day the tool was written — not
imagined.

Verifying code that already exists is a manual break-and-restore dance. The tool's
honest rule is that a post-hoc case cannot be red-checked, so to actually verify
existing code its author had to sabotage the code three separate times, watch each
case go red, and restore — by hand, with git. That is the correct thing to do and
nobody else will do it. The tool is honest about the problem and gives zero help
solving it, which for the most common real use — verifying code you already have —
makes it a discipline, not a product.

The record of "seen red" is an ordinary local file. `runs.jsonl` holds the
falsifiability history that every green is redeemed against, and anyone who can edit
it can fake a red that never happened. The tamper-resistance is keyed to the case's
command text, which is clever, but the record itself sits inside the producer's own
reach — the same anchoring gap that undermines any ledger nobody guards.

Author and judge are kept separate only by hope. The tool enforces "seen red"; it
does nothing to ensure the person who wrote the case is not the person who wrote the
code, nor that the case tests the thing the requirement means. A rigorously
falsifiable case pointed at the wrong property still scores green.

And the plain facts of youth: one user, no CI integration, no installable package,
and a verdict (`BROKEN`, for a command that exited 127 without running) that had to
be added mid-use because prose "cases" were silently counting as red. A tool still
discovering its own `BROKEN`-shaped holes is not a tool strangers should depend on.

## The Cost of Not

If this ships as-is and people believe its greens, the failure is uniquely bad,
because it is the failure the tool exists to prevent, committed by the tool itself.
A green from a case authority is supposed to mean "proven, by a check that could
have failed, recorded where it cannot be quietly rewritten." If any of those three
is hollow — the check was never really red, the record was edited, the case tested
the wrong thing — then the authority certifies a false green and lends it its own
credibility. People stop checking precisely because they trust the stamp; that is
the entire value, and it is also the entire blast radius. A wrong test framework
wastes an afternoon. A wrong case authority launders unearned confidence into every
project that adopts it, and the loss surfaces downstream, after the trust has
already been spent.

If it never ships at all, the cost is quieter: the discipline stays a private habit
of one author on one machine, re-implemented by hand each time, helping no one who
was not already convinced. The idea that a green must be earned is worth more than
one person's careful practice — but only if it can be handed over, and a habit that
cannot be handed over does not compound.

## Why Not The Alternatives

- **Just use pytest / a normal test framework.** — insufficient because no standard
  framework enforces red-before-green. They will happily run a test written after
  the code, pass it on the first execution, and count it as coverage — which is
  exactly the vacuous green this tool exists to refuse. pytest tells you a test
  passed; it never asks whether that test could have failed. The two tools are not
  competitors; ctc is the missing discipline layer, and adopting pytest instead is
  declining to solve the problem. (research: to be earned)

- **Use an existing mutation-testing tool for the "did it really test anything"
  part.** — insufficient as a replacement, though relevant as a component. Mutation
  testing measures whether a suite catches injected faults, which is close to the
  auto-red-check this tool needs. But it is a batch quality metric over an existing
  suite, not a per-claim admission gate tied to a requirement's meaning, and it
  says nothing about anchoring the record or separating author from judge. It is a
  part to integrate, not the whole. (research: to be earned)

- **Ship it now; the discipline works, the rest is polish.** — insufficient because
  the "polish" is the trust. A case authority whose record can be edited and whose
  post-hoc greens can't be red-checked without a manual dance is not a rough edge on
  a working product; it is a working idea without a trustworthy product around it.
  Shipping it as-is is how the tool becomes the false-green factory its own charter
  warns about. (research: to be earned)

- **Keep it as a private script; it only needs to serve this ecosystem.** —
  insufficient because the whole thesis is that earned greens compound only when
  they travel. An unshippable discipline is a habit, and a habit dies with its
  author's attention. (research: to be earned)

## The Unique Offer

A green a stranger can trust. Not "the tests passed" — that you can get anywhere —
but "this check was proven capable of failing, against this exact code, and the
proof is recorded where the person who wrote the code cannot have quietly forged
it." That is a claim no ordinary test framework makes, and none can make it without
the three things this charter's requirements build: the red-before-green rule, the
anchored record, and the separation of author from judge. Remove any one and the
green decays back into "it passed on my machine."

The product, then, is not "tests." It is *transferable, un-forgeable earned-ness* —
verification you can hand to someone who did not write the code and did not build
the tool, and have it still mean something in their hands. Every other testing
tool answers "did this run without failing?" This one answers a harder and more
valuable question: "was this success discriminated from failure by a check that
could have caught it, and can I prove that to a skeptic who trusts neither of us?"
When the answer is yes and the proof travels, a green stops being a claim and
becomes evidence — and evidence is the only thing worth building a case authority
to produce.

## How It Grows

The tool verifies itself, first. ctc keeps its own `.complextestcases/` suite, and
every one of its own guarantees is an earned green — red-checked against a broken
ctc, then green against the real one. A case authority that cannot pass its own
discipline has no standing to enforce it on anyone else, so self-verification is not
vanity; it is the precondition for the first external user.

Every false green that escapes becomes a new case, seen red, so the specific way the
tool was fooled once cannot pass twice — the same rule it enforces on others,
enforced on itself. The `BROKEN` verdict was born this way, from a prose case that
exited 127 and counted as red; the next hole will be closed the same way. And the
requirement floors move only with evidence: a gate that turns out to reject good
suites is loosened, on purpose, and recorded — because the floors are hypotheses,
not scripture.

## Metric

name: pct_prime_time_requirements_earned
kind: percent
target: 100

## Serves

parent: root
how: complex-test-cases is the case-authority organ of the Eidos conscience — the
  thing that makes an earned green mean something everywhere else. It serves the
  Eidos root by being the trustworthy floor every other green stands on.

## Invariants

### a_green_always_requires_a_seen_red
must: No case is ever credited as passing unless it was observed RED at least once against the exact command it carries; a check that never failed certifies nothing.
case: cd "$(git rev-parse --show-toplevel)" && python3 -m pytest tests/test_ctc.py -q -k "vacuous or red_history or seen_red"
irreversible: false

### broken_is_never_counted_as_red
must: A command that could not execute (exit 126/127) is BROKEN, never RED — a typo can never certify a claim as falsifiable.
case: cd "$(git rev-parse --show-toplevel)" && python3 -m pytest tests/test_ctc.py -q -k "broken"
irreversible: false

## Requirements

### self_verified
must: ctc keeps its own complex-test-cases suite and every claim is earned green — the tool passes its own discipline.
case: test -f .complextestcases/cases.jsonl && python3 tools/ctc.py status ctc

### auto_redcheck_existing_code
must: A mode red-checks post-hoc cases WITHOUT a manual break-and-restore — it mutates the guarded code (or diffs a ref) and confirms each case actually catches the break.
case: test -x tools/ctc_autoredcheck && tools/ctc_autoredcheck --self-test

### run_record_anchored
must: The falsifiability record (runs.jsonl) is anchored outside the producer's silent reach — committed/append-verified — so a red history cannot be forged by editing a local file.
case: test -f tools/ctc_anchor.py && python3 tools/ctc_anchor.py --verify

### author_and_judge_separation
must: The tool records who authored each case vs. who produced the code under test, and flags a case whose author is also its code's producer.
case: test -f .complextestcases/authorship.jsonl && python3 tools/ctc.py authorship --check

### installable_and_versioned
must: The tool is installable by a stranger in one command (uvx/pip), versioned, published.
case: uvx complex-test-cases --version

### ci_gate
must: ctc runs in CI and fails the build on any RED, VACUOUS, or BROKEN case in a required suite.
case: test -f .github/workflows/ctc.yml && grep -q "ctc" .github/workflows/ctc.yml

## Preferences

- zero runtime dependencies, stdlib only
- the CLI reads like the discipline, not like a framework
- boring, precise, and honest over clever
