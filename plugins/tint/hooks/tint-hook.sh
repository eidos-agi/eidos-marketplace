#!/bin/zsh
# Recolor the terminal window to match the topic this Claude Code session is on.
#
# Wired to three events, most-recent-evidence-wins:
#   SessionStart / UserPromptSubmit -> session cwd  (where you are)
#   PostToolUse Edit|Write          -> edited file  (what you're actually touching)
# The second is why it tracks cross-repo work: the window follows the file, not
# the directory you happened to launch from.
#
# Why not a shell chpwd hook: `claude` owns the terminal for hours and never
# gives the shell a prompt back, so the color would freeze at launch.
# ponytail: no daemon, no polling, no model. The hooks ARE the event stream.

root=${0:A:h:h}
source $root/lib/color.zsh 2>/dev/null || exit 0
source $root/lib/tag.zsh   2>/dev/null || exit 0

# Tool subprocesses have no controlling terminal (/dev/tty is "device not
# configured"), so walk up the process tree until we hit the pty the terminal owns.
_tint_find_tty() {
  local p=$$ t                        # start at self: it may own a tty already
  while [[ -n "$p" && "$p" -gt 1 ]]; do
    t=$(ps -o tty= -p "$p" 2>/dev/null | tr -d ' ')
    [[ -n "$t" && "$t" != "??" ]] && { echo "/dev/$t"; return 0 }
    p=$(ps -o ppid= -p "$p" 2>/dev/null | tr -d ' ')
  done
  return 1
}

# ponytail: only read stdin if it isn't a terminal. `cat` on a tty blocks
# forever, so running this hook by hand would hang the shell.
payload=""
[[ -t 0 ]] || payload=$(cat 2>/dev/null)

# PostToolUse carries the edited path in tool_input.file_path; other events don't.
# ponytail: zsh regex, not python3 -- drops the only runtime dependency and a
# ~30ms fork on every turn. Paths with JSON escapes are not worth a parser.
target=""
[[ "$payload" =~ '"file_path"[[:space:]]*:[[:space:]]*"([^"]*)"' ]] && target=$match[1]
[[ -z "$target" ]] && target="${CLAUDE_PROJECT_DIR:-$PWD}"

# TINT_TTY overrides discovery: lets tests assert the emitted bytes without a
# pty, and lets you debug by pointing a hook at a file.
tag=$(tint_tag_for "$target") || exit 0
grp=$(tint_group_for "$target") || grp=$tag

# Inside tmux the escapes never reach the emulator, but tmux does the same job
# natively -- tint_apply picks the right machine. A tty is only needed outside it.
tty=${TINT_TTY:-$(_tint_find_tty)}
[[ -n "$tty" || -n "$TMUX" ]] || exit 0   # headless (cloud/CI) -> no-op
tint_apply "$tag" "$grp" "$tty"
exit 0
