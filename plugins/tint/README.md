# tint

Name and colour your terminal windows by the topic they're on. Claude Code sessions
re-label themselves as they move between projects.

**The tint is the hint. The name is the game.**

A human cannot read a colour — nobody memorises that hue 137 means `greenmark`. What a
colour does well is *peripheral*: "that window is a different thing from this one",
seen without focusing. What actually tells you *what* a window is, is its **name**. So
tint sets both, and the name is the point:

- **tmux** → renames the window (and disables `automatic-rename`, which would overwrite it)
- **bare terminal** → sets the tab title, re-asserted every turn so it wins against
  whatever else is fighting for the title bar

No daemon. No polling. No model. No network. No dependencies. It's a `case` statement
and an escape sequence, and that's the whole point.

## Install

As a Claude Code plugin (recolours Claude sessions):

```
/plugin marketplace add eidos-agi/eidos-marketplace
/plugin install tint
```

For plain shells too, add to `.zshrc`:

```zsh
source /path/to/tint/lib/shell.zsh
```

## Use

Nothing. It works out of the box — your directory layout already names your topics,
so tint reads the label you already wrote.

When it guesses wrong:

```
tint billing-migration   # pin this tree to a topic (writes ./.tint)
tint                     # what's this window's tag and colour?
tint list                # every tag and its colour
tint off                 # leave this tree alone
```

Most people never run the CLI. tint is meant to be invisible infrastructure — the
windows just start knowing what they are.

## How it works

Four ideas, none of them clever:

**Your filesystem already knows the topic.** `~/repos-greenmark/` is not ambiguous.
tint reads the tag from `.tint` → git remote org → parent directory, in that order.
No inference, because none is needed.

**OSC 11 slips under a TUI.** `printf '\033]11;#1d0909\a'` doesn't paint anything —
it redefines what "background" *means*, so the terminal repaints underneath even a
full-screen app like Claude Code. Sequences that draw pixels would fight the TUI.
This one doesn't draw.

**Hooks are the event stream.** A shell `chpwd` hook can't help: `claude` owns the
terminal for hours and never returns a prompt, so the colour would freeze at launch.
tint hooks `SessionStart`, `UserPromptSubmit`, and `PostToolUse(Edit|Write)` instead.
That last one is why it tracks cross-repo work — the window follows the *file being
edited*, not the directory you launched from.

**tmux and a bare terminal are different machines.** Inside tmux, escape sequences never
reach the emulator — `allow-passthrough` is off by default and swallows them. The usual
answer is DCS-wrapping every sequence and telling users to flip a setting. tint doesn't:
tmux already exposes both capabilities natively (`window-style bg=`, `rename-window`),
so inside tmux it just uses those. Nothing to configure.

Hook subprocesses have no controlling terminal, so outside tmux tint walks up the
process tree to find the pty. That's the only genuinely fiddly part.

## Colours

Two properties matter, and they fight:

- **Stable** — a topic's colour must never change, or your muscle memory is worthless.
- **Distinct** — two topics you see side by side must not look alike.

Maximising distance across N topics means recomputing when N grows, which moves
colours. tint resolves it by assigning greedily and *remembering*: a new topic takes
the most-distant free hue and keeps it forever. Existing topics are never recomputed.
Assignments live in `~/.config/tint/assigned.tsv` — delete a line to re-roll one.

The naive version hashed topic names into a fixed wheel. It put two of our projects on
indistinguishable blues. `test/test.zsh` asserts the minimum hue gap so that can't
come back.

**The limit, and why it's survivable:** because tint never moves an existing colour, it
can't re-space the wheel as topics accumulate — a new topic only gets the widest
*remaining* gap. Measured: 6 topics hold 45°, 20 collapse to ~12°, past what most eyes
separate. Making 20+ work would mean re-spacing on every new topic — the
colours-shuffle-overnight behaviour this design exists to prevent.

This is survivable precisely because the tint is only the hint. Past a dozen topics the
colour degrades to "these two windows are probably different", which is all a hint owes
you. The name never degrades. If colour were carrying the identity, this limit would be
fatal; because the name carries it, the limit is just a soft edge.

Prune `assigned.tsv` or pin what you care about in `overrides.tsv`.

Force a specific colour in `~/.config/tint/overrides.tsv`:

```
eidos-agi	138 79 255
scratch	none
```

## Not doing

**Clustering topics out of session history.** Tempting, and wrong for this: clustering
is hostile to stability (refit → cluster ids shuffle → your colours rewrite themselves
overnight), it needs a `k` chosen up front, and it hands you "cluster 3" rather than a
name — so it doesn't remove a model, it adds a pipeline in front of one.

`lib/tag.zsh` is the seam. Override `tint_tag_for()` and nothing downstream changes.
If path-tags ever prove insufficient, a smarter tagger drops in there. So far they
haven't.

## Requires

zsh. Nothing else.

**In tmux** tint uses tmux's own commands, so nothing else is needed — notably NOT
`allow-passthrough`, which is off by default and would otherwise swallow every escape
sequence. Verified against a live tmux 3.6a session in `test/integration.zsh`.

**Outside tmux** you need a terminal that honours OSC 11 (iTerm2, Kitty, WezTerm,
Alacritty, xterm). Tab *colouring* (OSC 6) is iTerm2-only and is ignored elsewhere; the
window background and the title work everywhere.

**Light themes:** the default dims the tint toward black. On a light theme that makes
dark text unreadable, so set `TINT_MODE=light` to wash toward white instead. `TINT_DIM`
(default 13) controls the strength either way.

## Test

```
zsh test/test.zsh         # the two properties that ARE the product: stable + distinct
zsh test/stress.zsh       # adversarial: try to break the library
zsh test/integration.zsh  # the hook and the CLI -- what users actually touch
```

Set `TINT_TTY=/some/file` to point a hook at a file instead of your terminal — that's
how the integration suite asserts the emitted bytes, and it's the easiest way to debug.

## Stress-tested

`zsh test/stress.zsh` is an adversarial suite — it exists because every bug below was
one I'd have argued was impossible:

- **`typeset -F` without `-g`** — sourcing `color.zsh` from inside a function made the
  colour constants local, so they vanished and every window silently went **black**.
- **`local path=` in zsh** — `path` is tied to `$PATH`. Naming a local variable `path`
  clobbers command lookup for the rest of the function.
- **`echo "-"`** — zsh eats a lone `-` as an end-of-options marker and prints nothing,
  so the "deliberately uncoloured" sentinel silently read as "no override set".
- **`$((#c[i]))`** — zsh char-code arithmetic evaluates to 0, so every topic hashed to
  the same colour.
- **Concurrent sessions** — 12 sessions starting at once all read an empty state file
  and picked the same hue. Now serialised with an atomic `mkdir` lock.
- **Greedy `${p##*//*/}`** — ate through to the last slash, turning an https remote into
  the tag `repo.git`.

Tabs/newlines in topic names, glob metacharacters (`*`, `[x]`, `a?b`), quotes, leading
dashes, corrupt state rows, unwritable state dirs, and paths with spaces are all
covered. Every one of these failed *silently* before it was tested for — which is the
whole argument for the suite.

A second round, once the hook and CLI were tested rather than just the library:

- **`cat` on a terminal** — the hook read stdin unconditionally, so running it by hand
  hung forever. Now guarded with `[[ -t 0 ]]`.
- **CRLF state file** — a row synced from another machine left `90\r`, and the trailing
  `^M` crashed the hue maths with `bad math expression`.
- **Stale lock** — a holder that crashed left the lockdir behind, costing every future
  call the full 1s timeout, forever. Now reaped after 10s.
- **tty walk started at `$PPID`** — skipping the process's own terminal. Starts at `$$`.
- **python3** — dropped. The payload parse is a zsh regex now, which removes tint's only
  runtime dependency and a fork on every turn.

Three of the "failures" in that round were bugs in the *tests*, worth recording because
they'd fool anyone: `script(1)` on macOS captures zero bytes (even for a raw `printf`),
so it cannot test escape output at all; `zsh -c "cmd"` exec-optimises, which silently
reparents the hook and made the tty walk find the wrong terminal; and a fixture in a
temp dir isn't taggable, so it tested nothing while appearing to pass.

MIT.
