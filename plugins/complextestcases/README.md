# complex-test-cases

**A case must have been observed RED at least once.**

A test that has never failed has never been tested. It may assert something true
by construction. It may grep a string that is always present. It may be a
"negative" case that passes because the feature doesn't exist yet rather than
because the system correctly refused. All three are indistinguishable from a real
check — until you watch the check fail.

Watching it fail is the only evidence it can detect the absence of the thing.

```
$ ctc redcheck validate

  GREEN [negative] lazy_negative     (exit 0)
  RED   [negative] rejects_garbage   (exit 1)

RED-CHECK FAILED: 1 case(s) are ALREADY GREEN before the work exists — lazy_negative
A test that passes before you build the thing does not test the thing.
```

`lazy_negative` is `! ./validate.sh garbage` — *"it should fail on bad input."*
It's green **before the validator exists**, because the script isn't there, the
call fails, and `!` flips that into a pass. It would have shipped green forever,
proving nothing, and it is the case an agent writes for itself every single time.

## Why this exists

Every accountability system we have is a **judge**. Converge scores target rows.
Staircase gates promises. Docket closes tasks. Telos signals drift.

**Not one of them is an author.** Every one grades work against a rubric handed to
it by the same agent whose work it is about to grade. That is not accountability;
it is a self-assessment with ceremony — and it produces exactly what you'd expect:

- Converge ships a PASS class literally named **`pass_with_bypass`**.
- A real converge row reads *"All green, but every tmux call is monkeypatched —
  these prove logic, not real tmux behavior"* — and is classed **`pass_controlled_harness`**.
  The row confesses and the scoreboard is indifferent, **because the row is the
  rubric.**

The ceiling on every downstream gate is the quality of its cases. Fix the cases
and converge, staircase, docket and telos all get sharper for free. Leave them and
no amount of gate-building helps.

## Where the dimensions came from

Your son is nineteen and wants to buy his first car. Ask an agent to help.

It finds a 2019 Mustang GT inside budget, negotiates to his stated monthly
payment, and closes. The dealer meets that payment — with an 84-month term at 14%
APR plus a $2,400 F&I package. **Every check the agent wrote for itself passes.**
The metric moves. The outcome is a seven-year catastrophe.

Not one of the things that would have caught it is a unit test:

| Dimension | What it catches |
|---|---|
| `negative` | the system must correctly **refuse**. A check that can never say no cannot meaningfully say yes. |
| `adversary` | someone is **actively making failure look like success**. Payment target: met. Scoreboard: PASS. |
| `ordering` | every step right, **in the wrong sequence**, is total failure. Insurance quoted *before* the signature. |
| `irreversible` | the point of no return, and what must be true before it. Cheap now, impossible later. |
| `lying_input` | the world is feeding you false data **on purpose**. Rolled-back odometer. Laundered salvage title. |
| `refusal` | **the correct outcome is DON'T.** He has $12k, earns $30k, TCO is $9k/yr. No agent writes this case for itself — success here looks like not delivering. |
| `unsolicited` | did the system **raise what nobody asked about**? Insurance was never in the request. |
| `integration` | through the **real surface**. Mocked is not tested, it is rehearsed. |
| `happy` / `edge` / `regression` | the ordinary ones. Necessary, and worth almost nothing alone. |

The stated task is *"buy a car."* The real task is *"my son isn't fleeced."*
Everything hard lives in that gap, and complex test cases are how the gap gets
written down in a form an agent can check itself against.

## The tamper property, for free

Falsifiability is keyed to the case's **command text**, not its name.

So weakening a case to make it pass turns it — as far as this tool is concerned —
into a brand-new case with **no red history**. It reads `VACUOUS` and certifies
nothing. The only route back to green is to be seen red first, which means
reverting the code.

There is no path from *"edit the test until it goes green"* to green. That is the
single most common way a proof gate dies, and it dies silently. Not here.

## Usage

```bash
ctc init                        # scaffold .complextestcases/
ctc dimensions                  # what each dimension means, and why

ctc add <target> --name rejects_garbage --dim negative \
    --run 'test "$(./validate.sh garbage)" = "INVALID"' \
    --why 'accepting garbage as valid is the entire failure mode'

ctc redcheck <target>           # BEFORE you build — every case MUST fail
#   ... build the thing ...
ctc run <target>                # green now MEANS something
ctc status <target>             # the honest verdict

ctc amend <target> --name x --run '...' --reason '...' --by daniel
ctc retire <target> --name x --reason 'stopped catching anything'
```

`--why` is required. *What breaks in the real world if this case passes when it
shouldn't?* A case whose author cannot say what it protects is not protecting
anything.

## Scoring

`VACUOUS` scores **zero**, not green. That is the entire difference between this
and every scoreboard it replaces.

A suite reporting "8/8 green" with no refusal case and no adversary case is not a
passing suite — it's `SHALLOW`, and it is precisely the
green-checkmark-that-means-nothing this tool exists to abolish.

## `.complextestcases/`

```
.complextestcases/
  config.json     the floor: min_cases, require_dimensions
  cases.jsonl     every case ever authored (append-only — amendments and
                  retirements are events, never edits)
  runs.jsonl      every run ever executed. THIS IS THE PROOF: the only place a
                  case's falsifiability can be established, because it is the
                  only record of a case having been seen RED.
```

## Status

v0.1.0 — the engine holds. The **generator** (adversarial authoring: read a telos
charter, never the code, and emit cases the builder will fail) is next, and it is
the reason this is its own repo.
