# LEARNINGS

Every change to getcontrol earns its place by something that went wrong. This file
records what happened, what changed, and why — so the next person (or agent) does
not re-derive it from a bug.

**The rule: no fix lands without an entry here.** A fix without its cause is a fact
nobody can re-check.

---

## 2026-07-25 — Closing beats cataloguing

**What happened.** The first working version surveyed 24 panes and offered to
adopt each one. Then we looked at idle time: 12 of the 24 were empty shells,
untouched for 7 hours, in a repo where their agent had quit hours earlier. Closing
them took one command and halved the problem. Every registry and ledger feature in
the tool, added over hours, moved the needle less.

**Changed.** Added `reap`. Idle time (`idle_h`, from the tty device mtime) became
a first-class column instead of a discarded byproduct of identity.

**Why.** The tool's headline number should be how many panes are *gone*, not how
many are catalogued. A cleanup tool whose best outcome leaves the count unchanged
has misunderstood the job.

---

## 2026-07-25 — Prevention retires more than cleanup fixes

**What happened.** All 12 husks had one cause: a shell that outlived the agent it
launched. Quit Claude, get a `zsh` prompt back, never close the window.

**Changed.** Added `start` + `shellinit`. Work is born in tmux, `exec`'d into (so
the launching shell is *replaced* and the window has nothing to fall back to), and
attach-or-create (asking twice reuses instead of multiplying).

**Why.** Three properties, three whole classes of mess gone, and none of it touches
a terminal app's API — `exec` and `tmux` are POSIX, so it behaves the same in
iTerm, Terminal, Ghostty, Warp, or over ssh. Terminal-app-specific automation
(`explode`) is the one arm that does not generalise, and it is now documented as a
last resort.

---

## 2026-07-25 — `tmux new-session -c <bad path>` does not fail

**What happened.** A pull ran against a pane whose cwd `lsof` had failed to
return. The cwd came through as `?`, which sanitized to a session named `-`, and
`tmux -c '?'` **silently used `$HOME`**. A live Claude session was killed and came
back as a fresh Claude in the home directory — the wrong conversation entirely.
Recoverable only because the transcript was still on disk.

**Changed.** `pull_blocked()` refuses before killing anything if the cwd is not a
real directory. After creation, `#{pane_current_path}` is compared to the intended
cwd. Session names strip to empty rather than becoming `-`.

**Why.** Validate every input before the first irreversible step, not after. And
never trust a shell tool's exit code as evidence of its effect — four different
silent fallbacks appeared in one day (`tmux -c`, zsh not word-splitting `$pids` so
`kill` no-ops, `login`/`zsh` ignoring SIGTERM, iTerm AppleScript timing out).

---

## 2026-07-25 — "A pane exists" is not proof a session came back

**What happened.** After the fix above, chrime resumed in the right directory —
and sat frozen on `Resume from summary / Resume full session as-is?`. Both checks
(pane exists, cwd correct) passed on a session doing nothing at all.

**Changed.** After a pull, the pane is captured and matched for confirmation
prompts; the result reports `PARKED asking a question` with the last lines of the
screen instead of claiming success.

**Why.** Verification must be behavioural, not structural. Structure says the
furniture is in the room; only reading the screen says anything is happening.
Sweeping 8 panes without this would have produced 8 frozen sessions and 8 reports
of success.

---

## 2026-07-25 — Do one before doing nine

**What happened.** Pulling a single pane exposed three separate defects (wrong
directory, bad session name, parked prompt). The plan had been to sweep nine.

**Changed.** `control --pull` stops after the first successful pull and tells you
to read the pane back. `--all` overrides.

**Why.** One-at-a-time is not caution, it is how defects get found while they are
still cheap. Nine at once would have multiplied every one of them.

---

## 2026-07-25 — `--continue` is scoped to a directory

**What happened.** Four grok panes were all sitting in `~`. `--continue` resumes
"the most recent session for the current working directory" (verified in both
`claude --help` and `grok --help`), so pulling all four would have produced four
sessions resuming **one** conversation, leaving three transcripts unreachable.

**Changed.** `pull_blocked()` counts same-harness panes sharing a cwd and refuses,
naming the choice: resume by session id, or pick one to keep and reap the rest.

**Why.** The resume contract is per-harness and per-directory, and assuming it is
per-pane silently destroys work. Half the remaining sweep was wrong for this
reason alone.

---

## 2026-07-25 — A dry run that lies is worse than none

**What happened.** The collision guard lived inside `pull()`, so
`control --pull` (dry) happily printed `would pull ttys014 …` for a pane the real
run would refuse.

**Changed.** All refusals moved to `pull_blocked()`, called by both paths.

**Why.** The dry run is the command people trust enough to run without thinking.
It has to be the most honest one in the tool, not the least.

---

## 2026-07-25 — The tool should route its own privileged actions

**What happened.** Every destructive step was hand-carried through hancock by the
agent driving the tool. That works exactly as long as the agent remembers.

**Changed.** `pull` and `reap` call `hancock check` and refuse to run unsigned.
Deliberately no `hancock add` from inside the script: the CLI tray and the MCP
tray are separate stores, so a request queued here would land where the waiting
agent cannot see it.

**Why, and the limit.** hancock exports no request id into the environment of the
commands it runs (checked). So `--signed` is a *declaration*, not proof — it
prevents an accidental self-run, not a determined one. The tray is the real
control, and pretending otherwise would be worse than saying so.

---

## 2026-07-25 — The agent is in its own survey

**What happened.** Checking which tty this process runs on returned `ttys017` — a
Claude pane sitting in the survey alongside the others, indistinguishable from a
pull target. `control --pull --all` would have killed the agent performing the
sweep, mid-sweep, leaving the work half-done and nobody alive to report it.

**Changed.** `self_tty()` walks the parent chain (tool subprocesses are detached,
so `getppid()` is not enough — the controlling terminal is several ancestors up).
`pull_blocked()` and `reapable()` both refuse it; `survey` marks it.

**Why.** A tool that acts on processes is itself a process. Nothing in the design
had accounted for the operator being inside the population it operates on.

---

## 2026-07-25 — PATH is not the same everywhere the tool runs

**What happened.** The same pull that worked by hand failed under hancock, twice,
with `cwd unknown ('?')`. Direct probe: `lsof_rc=127`. hancock runs with a minimal
PATH that excludes `/usr/sbin`, so `lsof` did not exist, `sh()` caught the
exception and returned `""`, and every pane's cwd became unknown. **This — not a
race, not a timeout — is what resumed a live Claude session in the wrong
directory.**

**Changed.** Binaries resolve through `shutil.which` with absolute fallbacks
(`/usr/sbin/lsof`, `/bin/ps`, `/opt/homebrew/bin/tmux`, …). A missing tool is
recorded in `MISSING` and `pull_blocked()` refuses outright: *"cannot see the
machine properly — refusing to act blind."* Also: a stale pid no longer poisons the
batched `lsof` (per-pid retry), proven by a unit check with a bogus pid.

**Why, and why it matters beyond the pull.** The same failure silently breaks
`reap`, `status`, and any launchd or cron run — every one of them reading empty
data and acting on it. A tool that destroys things must treat "I cannot see" as a
hard stop, never as "nothing there". This is the third silent-fallback bug in one
day; the pattern, not the instance, is the lesson.

---

## 2026-07-26 — Five of six defects were one defect: matching shape instead of meaning

**What happened.** Six real defects surfaced over two days. Written into a table
for EID-1049, five of them collapsed into a single class:

| what was asserted | what was actually true |
|---|---|
| a pane exists → the session came back | it resumed in the wrong directory |
| the cwd is right → the session is working | it was frozen on a resume menu |
| exit code 0 → the command did its job | `lsof` was missing from PATH, output empty |
| a leading glyph → the agent is busy | `✻ Churned for 43s` is past tense; it had finished |
| a registry row → a live worker | 63 of 81 rows named the dead |

Every one asserts on **structure** and infers **behaviour**. The structure was
present and the behaviour was absent, and the two are indistinguishable from
outside unless you look at content.

**Changed.** `getcontrol classify` — one classifier for what a pane is actually
doing (`busy · asking · staged · idle · dead`), with the real captures as
regression fixtures in `selfcheck`, including the past-tense case that fooled two
earlier detectors. `fleet-perpetual` calls it rather than grepping for itself:
two copies of a subtle rule is one copy too many.

**Why, and the rule it produces.** Verification must read *content*, not shape.
Before asserting a state, name the observation that would be different if the
assertion were false — and go make that observation. "A process exists" is never
evidence that work is happening.

**What it found immediately.** Ninety seconds after existing, it found six of
eighteen sessions holding unsent instructions from the operator — a third of the
fleet idle while the human believed it had been asked (EID-1048). None of the
supervision built that night had noticed; the tree's catch rate at that point was
0 of 6 (EID-1049).

---

## 2026-07-26 — The antibody caught the disease

**What happened.** `classify` was written to stop asserting on shape instead of
meaning — the class of defect behind five earlier bugs. Within minutes it
reported that **6 of 18 sessions were holding unsent instructions from the
operator**, "a third of the fleet never heard the human". An Urgent issue was
filed and the operator was told.

It was false. Every instruction had been delivered.

Claude Code renders the previous message as a **dim placeholder** in an empty
composer. `capture-pane -p` strips escapes, making the placeholder byte-identical
to real staged input:

```
before:            ❯ continue with EID-1019
after typing ZZ:   ❯ ZZ                      <- the composer was EMPTY
after backspace:   ❯ continue with EID-1019  <- placeholder returned
```

With escapes intact they are trivially distinct — the placeholder is wrapped in
`ESC[2m`, real input is not.

**Changed.** `classify` reads `capture-pane -pe` and treats a dim composer as
idle. Both cases are fixtures in `selfcheck` with the real captured bytes.

**Why this one matters most.** The tool built to prevent shape-over-meaning
committed shape-over-meaning, one level down: it read *text after a prompt* as
evidence of intent, when the evidence that answers the question is the styling.
Stripping escapes did not lose formatting — it destroyed the only available
signal.

And the process failure underneath: `busy` and `idle` were tested against known
answers. `staged` was not. **The untested state is the one that lied.** One
keystroke would have falsified it, before the issue was filed and before the
operator was told. Before believing a new check, feed it a case whose answer you
already know — and the check you skip testing is the check that will be wrong.

---

## Still open

- **Identity is the hard part of any registry.** ttys recycle, pids recycle,
  session names get reused. Half the bugs traced back to "what is this thing,
  durably?" Keys are `tmux:<session>@<created>` / `proc:<pid>@<lstart>` — decided
  early enough to be cheap, which is the only reason they were.
- **The unit of work is the task, not the pane.** Governance is still enforced per
  pane, which is why linking feels like paperwork. Grouping by repo/work would
  collapse many decisions into few.
- **The emux registry is never validated.** Entries are written and trusted; no
  check that the session still answers. The same false comfort this tool was built
  to remove.
- **`--linear-issue` is never validated.** A typo registers exactly like a real
  issue, so the governance gate currently enforces that you typed *something*.
