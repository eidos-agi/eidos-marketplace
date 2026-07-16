---
name: complextestcases
version: 0.1.0
description: "Author complex test cases BEFORE building — cases that can actually catch something. Use when about to build a non-trivial feature, when writing acceptance criteria, converge target rows, staircase promises, or telos charter claims, or whenever you're about to write a test for code you already wrote. Triggers on 'complex test cases', 'ctc', 'acceptance criteria', 'what should this be tested against', 'redcheck', 'is this test any good'."
---

# complextestcases

**A case must have been observed RED at least once.**

## The one rule

A test that has never failed has never been tested. If you write a test *after*
the code and it passes on its first run, you have learned nothing: it may assert
something true by construction, it may grep a string that's always present, it may
be a "negative" case that passes because the feature is missing rather than
because the system refused.

So: **author cases before the work, and `ctc redcheck` them.** Every case must be
RED before you build. Then, and only then, does green mean something.

## When you are about to write a test for code that already exists

Stop. That test cannot be red-checked, so it will read `VACUOUS` and score **zero**.
That is correct and you should not work around it. Either:

- revert/stash the code, author the case, watch it go red, then restore; or
- accept that this case certifies nothing and say so out loud.

Do **not** author a case you have never seen fail and then report the suite as green.
That is the failure this whole tool exists to abolish.

## The dimensions, and the one you will skip

Run `ctc dimensions` for the full list. The floor is `negative`, `adversary`,
`refusal` — and **`refusal` is the one you will skip**, every time, because it is
the case whose correct outcome is *don't do the thing you were asked to do*. Every
incentive inside a task points away from writing it. That is exactly why it must
be written from outside the task.

| Dimension | The question it asks |
|---|---|
| `negative` | can the system correctly say NO? |
| `adversary` | is someone actively making failure look like success? |
| `ordering` | do the steps have to happen in a sequence, with no undo? |
| `irreversible` | what is cheap now and impossible later? |
| `lying_input` | what if the world is feeding false data on purpose? |
| `refusal` | **is there a world-state where the right answer is DON'T?** |
| `unsolicited` | what should the system raise that nobody asked about? |
| `integration` | does it work through the REAL surface, unmocked? |

## Workflow

```bash
ctc init
ctc add <target> --name <case> --dim <dim> --run '<cmd, exit 0 iff satisfied>' \
    --why '<what breaks in the real world if this wrongly passes>'
ctc redcheck <target>     # ALL RED, or the cases are wrong. Fix them now — it's free.
#   ... build ...
ctc run <target>          # now green means something
ctc status <target>
```

## Anti-patterns

- **Do not** report `VACUOUS` as green. It scores zero. That is the point.
- **Do not** amend a case to make it pass. The amendment erases its red history
  (falsifiability is keyed to the command text), so it goes VACUOUS and certifies
  nothing. There is no path from "edit the test until it's green" to green.
- **Do not** write only `happy` cases and call the suite passing. That is `SHALLOW`.
- **Do not** mock the surface under test and call it `integration`. Mocked is not
  tested, it is rehearsed.
