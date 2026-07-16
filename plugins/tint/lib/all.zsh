# tint all -- retrofit every window that already exists.
#
# Why this exists: hooks and .zshrc only affect what you open NEXT. On install,
# every window you already have stays untinted, which is exactly the moment the
# tool has to prove itself. Nothing here needs the shell's cooperation:
#   tmux  knows every pane's cwd  (pane_current_path)
#   a tty tells us its foreground process, and lsof tells us that process's cwd
#
# ponytail: no daemon watching windows. This is a one-shot sweep you run once at
# install; the hooks keep things current after that.

_tint_apply_tmux_pane() {  # pane_id window_id path
  local pid=$1 wid=$2 p=$3 n g bg
  n=$(tint_tag_for "$p") || return 1
  g=$(tint_group_for "$p") || g=$n
  bg=$(tint_bgtint_for_tag "$g") || return 1
  tmux set -p -t "$pid" window-style "bg=$bg" 2>/dev/null
  tmux set -w -t "$wid" automatic-rename off 2>/dev/null
  tmux rename-window -t "$wid" "$n" 2>/dev/null
  print -r -- "  tmux $wid  $n ($g)"
}

_tint_tty_cwd() {  # /dev/ttysNNN -> cwd of its foreground process
  local t=${1#/dev/} pid
  pid=$(ps -t "$t" -o pid=,stat= 2>/dev/null | awk '$2 ~ /\+/ {print $1}' | tail -1)
  [[ -z "$pid" ]] && pid=$(ps -t "$t" -o pid= 2>/dev/null | tail -1)
  [[ -z "$pid" ]] && return 1
  lsof -a -d cwd -p "$pid" -Fn 2>/dev/null | grep '^n' | head -1 | cut -c2-
}

_tint_tty_is_tmux() {  # skip the terminal hosting a tmux client; its panes are
  local t=${1#/dev/}    # styled individually and we'd fight ourselves
  ps -t "$t" -o comm= 2>/dev/null | grep -q '^tmux' && return 0
  return 1
}

tint_all() {
  local did=0
  if command -v tmux >/dev/null 2>&1 && tmux list-panes -a >/dev/null 2>&1; then
    local pid wid p
    while read -r pid wid p; do
      [[ -z "$p" ]] && continue
      _tint_apply_tmux_pane "$pid" "$wid" "$p" && (( did++ ))
    done < <(tmux list-panes -a -F '#{pane_id} #{window_id} #{pane_current_path}' 2>/dev/null)
  fi

  local t cwd n g
  for t in $(ps -e -o tty= 2>/dev/null | sort -u | grep '^ttys'); do
    t=/dev/$t
    [[ -c "$t" && -w "$t" ]] || continue
    _tint_tty_is_tmux "$t" && continue
    ( exec 3>"$t" ) 2>/dev/null || continue
    cwd=$(_tint_tty_cwd "$t") || continue
    [[ -n "$cwd" ]] || continue
    n=$(tint_tag_for "$cwd") || continue
    g=$(tint_group_for "$cwd") || g=$n
    tint_emit "$n" "$g" > "$t" 2>/dev/null && { print -r -- "  tty  $t  $n ($g)"; (( did++ )) }
  done
  print -r -- "tinted $did existing window(s)"
}
