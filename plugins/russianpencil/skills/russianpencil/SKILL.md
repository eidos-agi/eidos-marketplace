---
name: russianpencil
description: A keyword meaning "there's got to be an easier way — go back to first principles and stop worrying about the very specific task in front of us." Say it when a task, plan, system, or integration looks intimidating and you suspect the difficulty is coming from the framing rather than the problem. Drops the current task, restates the actual goal with no solution nouns in it, enumerates the mechanisms that could reach that goal, and either finds the stupidly-easier one or says plainly that there isn't one. Triggers on "russianpencil", "russianpencil it", "pencil this", "there's got to be an easier way", "whoa this must be complicated", "why is this so hard", "am I overbuilding this", "step back and think about this from first principles". NOT a coding-style mode — it changes altitude, not verbosity.
---

# RussianPencil

NASA needed to write in zero gravity. The story goes that they spent millions on a
pressurized pen while the Soviets brought a pencil.

**The story is false, and that is load-bearing here.** NASA used pencils and stopped —
graphite snaps, and conductive dust in a pure-oxygen cabin is a fire you cannot walk away
from. Fisher built the pen on private money, not NASA's. NASA bought them at about $2.40
each. **So did the Soviets.** Everyone ended up with the pen.

The joke survives because a satisfying simplification *feels* true. So this skill has two
jobs, and the second one is the hard one: find the easier way, **and refuse the easier way
that is merely satisfying.**

## What the keyword means

> *There's got to be an easier way — if we go back to first principles and stop worrying
> about the very specific task in front of us.*

That's it. Someone says **russianpencil** and you change altitude.

The trap it breaks: **the specific task in front of you is a cage, and you cannot see the
cage because you are busy being excellent inside it.** NASA's engineers were not stupid.
They were *good* at "make ink flow without gravity" — competent, rigorous, and solving the
wrong sentence. Nobody catches that by trying harder at the task. The task is what's
blinding you.

So the flinch — *whoa, this must be complicated* — is a good trigger and a worthless
verdict. It fires identically on things that are hard and things that are merely framed
badly. Telling those apart is the entire job.

## The move

**1. Put the task down.** Say out loud what we were grinding on, and set it aside. You
cannot do the next step while still holding it.

**2. Go up one level. What are we actually trying to achieve?** One sentence. **No solution
nouns.** *"Make marks on a surface"* — not *"make ink flow in zero-G."* If you cannot say it
without naming the thing we were already building, you are still in the cage. Go up again.
This step is the skill. Everything else is bookkeeping.

**3. From up there, cold: what are the ways to get that?** Mechanisms, not products —
"Postgres" and "MySQL" are one way, not two. At least three. **One of them must be "don't"**
— don't do it, don't build it, don't solve it — argued seriously, because it wins more often
than is comfortable.

**4. Is one of them stupidly, obviously easier?** Not 20% easier — that's noise, and chasing
it is its own space pen. Easier like graphite is easier than a pressurized ink cartridge.
That's the pencil. Take it.

**5. If none is, say so.** *"No pencil — it's hard because it's hard."* This is a real answer
and a common one. Some things are complicated because the problem is complicated, and the
honest end of this skill is often "yeah, go grind it out." A pass that finds a pencil every
time is not a pass, it's a mood.

**6. Before you recommend the easy one, check that it's real.** Satisfying and true feel
identical from the inside. Read the doc, run the command, check the ledger. This is the step
that kills the pencil-in-space story, and it will kill most of this skill's wrong answers.

**7. Name what it costs you.** Every pencil sheds graphite. Say what breaks and roughly
when: *"fine until 10k rows, then it isn't."* An easy answer with an unnamed ceiling is a
deferred outage wearing a win's clothes.

## Output

Short. The reframed goal, the ways you saw, the verdict.

- **`PENCIL: <the easier way>.`** Because the real goal was <stripped sentence>, not <the task
  we were stuck in>. Breaks when: <ceiling>. Checked: <how you know it's real>.
- **`NO PENCIL.`** The goal really is <stripped sentence>, and <task> is close to the honest
  way to get it. It's hard because it's hard.

Both are successes. `NO PENCIL` means the framing survived an honest attack — worth more than
a pencil you walk back next week.

## Refusals

- The flinch is a trigger, never evidence. It never reaches the verdict.
- Never grade an idea on how good the story is. *"We deleted the whole service and used a cron
  job"* is a great story and is sometimes an outage.
- Never skip step 2 to get to step 4 faster. A cheap answer to the unreframed task is just the
  old cage, painted.
- Never recommend a way you have not confirmed exists. A hallucinated easy path is the most
  expensive thing this skill can produce.
- Sunk cost is not an argument. Neither is "we already know this stack."
- Never manufacture a pencil to be agreeable. They asked because they wanted the truth, and
  "it's genuinely hard" is one of the two right answers.
