---
name: russianpencil
description: Reach for this at the "whoa, wtf, this must be complicated" moment — any time a task, system, plan, or codebase in front of you looks intimidatingly complex and you want to know whether it actually is. Turns that reaction into a number: strips the requirement to its verb, prices the obvious path, enumerates the solution CLASSES, and returns one of three honest verdicts — PENCIL, NO PENCIL, or PENCIL-DON'T-SWITCH. Triggers on "russianpencil", "russianpencil it", "pencil this", "find the pencil", "whoa this looks complicated", "this must be complicated", "this feels way too hard", "is there a cheaper way", "this got out of hand", "am I overbuilding this", "did we need all this". NOT a coding-style mode — it decides WHAT should exist, not how tersely to write it.
---

# RussianPencil

NASA needed to write in zero gravity. The story goes that they spent millions on a
pressurized pen while the Soviets brought a pencil.

**The story is mostly false, and that is the point of this skill.** NASA did use pencils,
then stopped: graphite tips snap, and conductive dust drifting through electronics in a
pure-oxygen cabin is a fire you cannot walk away from. The Fisher Space Pen was built on
private money, not NASA's. NASA bought them for about $2.40 each. **So did the Soviets.**
Everyone ended up with the pen.

The joke survives because a satisfying simplification feels true. This skill exists to find
cheap answers **and to refuse the ones that are merely satisfying**. If it starts finding a
pencil every time, it has stopped working and become a mood.

## When to reach for it

**Whoa. Wtf. This must be complicated.**

That's the trigger. You've come up against something — a task, a system, a plan, a codebase,
a vendor's integration guide — and it looks intimidating. Big. Like it's going to cost you a
week. Something in you flinches.

RussianPencil it.

**That flinch is a good trigger and a worthless verdict.** It tells you to look. It does not
tell you anything is wrong. Apparent complexity and real complexity are different quantities,
and the flinch cannot tell them apart — it fires on both. Plenty of things look complicated
because they *are*, and the honest end of this skill is often "yeah, it's hard, it's hard for a
reason, go do the work." The flinch is where the descent starts, never where it lands.

Run it on things with a real bill attached. A twenty-minute reframe to save ten minutes is the
space pen, and you built it.

## What this is not

Not a terseness mode — ponytail and its family own that, and own it well: reflexive, per-diff,
*"stop at the first rung that holds."* That is laziness of **effort**, and it is right almost
always.

But a reflex cannot see across a system. Every over-built thing was assembled from
individually-lazy decisions, each locally the shortest option available. **Short diffs do not
add up to a small system.** And lines are the wrong unit anyway — nobody was ever bankrupted by
lines. Services, subscriptions, dependencies, migrations, and 3am pages are what actually cost.

RussianPencil is the opposite trade: **spend real thought, once, to buy an order-of-magnitude
cheaper outcome.** Laziness of **result**. The two compose and must not be merged — RussianPencil
picks the pencil, ponytail keeps the pencil short.

## The descent

In order. The value is in 1 and 3; skipping to 5 produces confident garbage.

**0. Name what feels heavy.** One sentence, plain. This is the only step where the feeling gets
a vote.

**1. Strip the requirement to its verb.** One sentence, no solution nouns. *"Write in zero
gravity"* — not *"build a pressurized pen."* If you cannot state it without naming the thing
that already exists, you do not have a requirement, you have an attachment. Everything gets
scored against this sentence, so write it down first.

**2. Price the obvious path.** Whatever you'd do if you never ran this skill. A number, not a
vibe — guess if you must, because a guess can be argued with and a feeling cannot.

- *A task that looks hard:* the cost of doing it the obvious hard way. Hours, mostly.
- *A plan not built yet:* build cost + carry cost.
- *A thing already built:* **carry cost** — what it costs per year merely to keep existing:
  maintenance, attention, breakage, and the tax it levies on every future change that has to
  route around it. Plus **migration cost** if you replace it.
- **Sunk cost is gone. Do not price it.** What you already spent is neither a reason to keep
  nor a reason to leave. It is the single most common way this descent gets rigged.

If the number comes back small, stop — you flinched at something cheap. A thing that looks
ugly but costs nothing is not your problem. Go do something that matters.

**3. Enumerate solution CLASSES. Minimum three.** A class is a *mechanism*, not a product.
"Postgres" and "MySQL" are one class. The classes for writing in zero-G: pressurize the ink /
use a medium that needs no ink / don't write, record instead. Most searches die here — three
flavors of one class, priced, and a round of self-congratulation. Force the third class to be
uncomfortable.

**Always include the null class, argued seriously:**
- For a hard-looking task → *"just do it the obvious way."* It's hard, it's hard for a reason,
  grind it out.
- For a plan → *"don't solve it."*
- For a built thing → *"keep it."* Replacing something that works costs migration and buys risk.

The null class wins more often than anyone is comfortable with. That's not a flaw in the skill.

**4. Price each class to one order of magnitude.** $1 / $10 / $100 / $1k. An hour / a day / a
week / a quarter. Precision is waste — the exponent is the entire signal. A replacement must
beat **carry + migration**, not just carry.

**5. Apply the 10x rule, and let it fail.** If the cheapest viable class is not ~10x cheaper,
**there is no pencil here.** One line, keep what stands. Most things have no pencil. A pass that
always finds one is lying to be liked.

**6. Name the ceiling you just bought.** Every pencil sheds graphite. Say what breaks and at what
scale: *"fine to 10k rows, falls over past that, upgrade path is X."* A cheap answer with an
unnamed ceiling is a deferred outage wearing a win's clothes.

**7. Verify the cheap class against a primary source.** Satisfying and true feel identical from
the inside. Read the docs, run the command, query the ledger — confirm the class actually does
the thing before recommending it. This step is where the pencil-in-space story dies, and where
most of this skill's wrong answers will die too.

## Output

A table, then one verdict. Nothing else.

| Class | Mechanism | Cost | Meets stripped req? | Ceiling |
|---|---|---|---|---|
| (what stands) | … | carry $$/yr | yes | … |
| … | … | $ + $mig | yes | breaks at … |
| null | keep it / don't solve it | $0 | … | — |

Then exactly one of:

- **`PENCIL: <class>.`** ~<N>x cheaper than carry + migration. Ceiling: <what breaks, when>. Verified by: <source>.
- **`NO PENCIL.`** Cheapest viable class is <class> at <N>x. Not enough. Keep what stands.
- **`PENCIL, DON'T SWITCH.`** <class> is <N>x cheaper, but migration costs <M> and doesn't pay back before <horizon>. Keep what stands — **and build the next one this way.**

All three are successes. `NO PENCIL` means the thing survived an honest attack, which is worth
more than a pencil you walk back in a month. `PENCIL, DON'T SWITCH` is how you stop repeating a
mistake without paying to undo it.

## Refusals

- The feeling is a trigger, never evidence. Never let "this feels complicated" reach the verdict.
- Never grade a class on how good the story is. *"We replaced the whole service with a cron job"*
  is a great story and is sometimes an outage.
- Sunk cost is not a class and not an argument. Neither is "we already know this stack."
- Never price a class you have not confirmed exists. A hallucinated cheap class is the most
  expensive thing this skill can produce.
- Never soften a verdict to be agreeable. The user asked because they wanted the number.
