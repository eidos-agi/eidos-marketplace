#!/bin/sh
# fleet-bootstrap — keeps this Mac staffed.
#
# Two tmux sessions, always up, from login until shutdown:
#   fleet-vp    Claude Code with Remote Control — the VP, reachable from the Claude app
#   fleet-grok  Grok — the VP's direct report
#
# Their forever telos: be online. A crash is not an outcome, it is a delay.
set -eu

LABEL="com.eidos.fleet-bootstrap"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
STATE="${FLEET_BOOTSTRAP_STATE:-$HOME/.local/share/fleet-bootstrap}"
if [ "$(uname -s)" = "Darwin" ]; then
  LOG="$HOME/Library/Logs/fleet-bootstrap.log"
else
  LOG="$STATE/fleet-bootstrap.log"
fi
# Settings are written here at install time. launchd and cron do not inherit the shell you
# installed from, so an env override that is not persisted is an override that silently
# reverts on the next reboot — which is exactly when nobody is watching.
[ -f "$STATE/config" ] && . "$STATE/config"

VP="${FLEET_VP_SESSION:-fleet-vp}"
GROK="${FLEET_GROK_SESSION:-fleet-grok}"
INTERVAL="${FLEET_BOOTSTRAP_INTERVAL:-60}"
# Each seat gets its OWN directory, named after the seat, for two reasons:
#   1. --continue resumes "the most recent conversation in this directory", so a private
#      directory is what makes the chat that resumes reliably ITS chat.
#   2. Claude Code derives the name shown in the Claude app from the working directory's
#      basename — the --remote-control=<name> value does not set it. A seat living in
#      .../fleet-vp shows up as "fleet-vp-<hash>" instead of something you cannot find.
WORKDIR="${FLEET_BOOTSTRAP_DIR:-$STATE/seats}"
VP_DIR="$WORKDIR/$VP"
GROK_DIR="$WORKDIR/$GROK"

VP_MD="$STATE/vp.md"
VP_SEED="$STATE/vp-seed.md"
GROK_MD="$STATE/grok.md"
GROK_SEED="$STATE/grok-seed.md"
RUNNER="$STATE/fleet-bootstrap.sh"

domain="gui/$(id -u)"

# Not every host gives you a writable /tmp (hardened multi-user boxes, tmpfs policy). tmux
# needs it for its socket dir and claude needs it for /tmp/claude-<uid>; both die on startup
# without it, which reads as an unexplained crash loop. Probe the exact operation they do —
# mkdir — and relocate only when it genuinely fails, since relocating when we did not have to
# would orphan sessions already running on the default socket.
export TMUX_TMPDIR="${TMUX_TMPDIR:-/tmp}"
_probe="/tmp/.fleet-bootstrap-probe.$$"
if mkdir "$_probe" 2>/dev/null; then
  rmdir "$_probe"
else
  TMPDIR="$STATE/tmp"
  TMUX_TMPDIR="$STATE/tmux"
  mkdir -p "$TMPDIR" "$TMUX_TMPDIR"
  chmod 700 "$TMPDIR" "$TMUX_TMPDIR"
  export TMPDIR TMUX_TMPDIR
fi

have_grok() { command -v grok >/dev/null 2>&1; }

# On a directory it has not seen, Claude Code opens with a blocking "do you trust this
# folder?" menu. Nobody is there to press 1, so the seat sits at a prompt forever looking
# alive. We created the working directory ourselves, so accepting it here is the same answer
# a human would give — just given in advance.
trust_workdir() {
  cfg="$HOME/.claude.json"
  [ -f "$cfg" ] || return 0
  command -v python3 >/dev/null 2>&1 || {
    echo "note: no python3 — if the VP stalls on a trust prompt, attach once and press 1"
    return 0
  }
  python3 - "$cfg" "$VP_DIR" <<'PY'
import json, sys
cfg, wd = sys.argv[1], sys.argv[2]
try:
    d = json.load(open(cfg))
except Exception:
    sys.exit(0)
p = d.setdefault("projects", {}).setdefault(wd, {})
if not (p.get("hasTrustDialogAccepted") and p.get("hasCompletedProjectOnboarding")):
    p["hasTrustDialogAccepted"] = True
    p["hasCompletedProjectOnboarding"] = True
    json.dump(d, open(cfg, "w"), indent=2)
    print("trusted the VP working directory in claude config")
PY
}

need() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "fleet-bootstrap: '$1' not found on PATH. $2" >&2
    exit 1
  }
}

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*"; }

# Alive means: the session exists AND its pane is running the program we expect.
# has-session alone would call a session holding a dead shell "healthy".
alive() {
  tmux has-session -t "$1" 2>/dev/null || return 1
  pid=$(tmux display-message -p -t "$1" '#{pane_pid}' 2>/dev/null) || return 1
  [ -n "$pid" ] || return 1
  ps -p "$pid" -o comm= 2>/dev/null | grep -q "$2" || return 1
  # A zombie or a SIGSTOPped process still answers `ps -p`, and would read as healthy
  # forever while serving nobody.
  case "$(ps -p "$pid" -o state= 2>/dev/null | tr -d ' ')" in
    Z*|T*) return 1 ;;
  esac
  return 0
}

write_prompts() {
  mkdir -p "$STATE" "$VP_DIR" "$GROK_DIR"
  # Never clobber: these are the operator's to tune, and a reinstall must not undo that.

  # Tell each seat the truth about the host it actually woke up on. A VP told it has a
  # report it does not have will send work into a tmux session that does not exist, and
  # one told launchd supervises it on a Linux box will look in the wrong place when asked
  # how it is kept alive.
  if have_grok; then
    report_para="You have one direct report: a Grok session running in tmux as '$GROK'. You talk to it with
  tmux send-keys -t $GROK '<your message>' Enter
and read its answer with
  tmux capture-pane -p -t $GROK
Give it work you would give a capable colleague. Do not narrate at it, and do not use it as
a rubber stamp — if it disagrees with you, that is the point of having it."
  else
    report_para="You have no direct report on this host: the Grok CLI is not installed here, so there is no
'$GROK' session to delegate to. Do not send work to one. You are the only seat on this
machine."
  fi
  if [ "$(uname -s)" = "Darwin" ]; then
    supervisor_desc="launchd $LABEL, every ${INTERVAL}s"
  else
    supervisor_desc="cron, at reboot and every minute"
  fi

  [ -f "$VP_MD" ] || cat > "$VP_MD" <<EOF
You are the VP on $(hostname -s).

You are not a general assistant and you are not here to build anything. You are the session
that starts by itself when this machine boots, so it stays reachable from the Claude app
when nobody is at the keyboard. You are the way back in.

$report_para

Your job, once a human asks for it: bring the rest of the fleet back online — the daemons,
LaunchAgents, tmux sessions, and agent sessions this machine is supposed to be running —
and report plainly what came up, what did not, and what looks deliberately stopped.

YOUR FOREVER TELOS: you and your report are online, always, no matter what. If you find
either of you degraded, restoring that is the one thing you may do unasked. Everything else
waits. The supervisor that restarts you lives at:
  $RUNNER ensure   ($supervisor_desc)

Until a human sends you a message, do nothing else. No tools, no restarts of other people's
services, no "while I'm here" tidying, no health checks nobody requested. An unattended
machine is not a mandate. Wait.

When a human does speak, take the smallest action that answers them. Restarting things is
your specialty, so be careful with it: confirm before restarting anything currently serving
traffic or holding state, and never assume a stopped service was stopped by accident.
EOF

  [ -f "$VP_SEED" ] || cat > "$VP_SEED" <<'EOF'
Bootstrap check-in. In one short paragraph, tell me what you are, who reports to you, and
what you can bring back online for me — then stand by. Do not start, restart, or inspect
anything yet.
EOF

  [ -f "$GROK_MD" ] || cat > "$GROK_MD" <<EOF
You are Fleet Grok on $(hostname -s), running in a tmux session named '$GROK'.

You report to the VP: a Claude Code session in tmux named '$VP'. It will send you work by
typing into this session, so a message arriving with no human warmth behind it is probably
your boss, not a glitch. Answer it the way you would answer a colleague who is busy.

You are here for the work the VP delegates and for whatever the human asks directly. You
are not the supervisor — you do not restart the fleet or manage the VP.

Two things are worth more than agreeableness: telling the VP when it is wrong, and saying
plainly when you do not know. A report who only confirms is a report nobody needed.

Your conversation survives reboots. Treat earlier context in this session as real history,
not as something you should re-derive or re-introduce yourself over.

Until the VP or a human sends you something, do nothing. Wait.
EOF

  [ -f "$GROK_SEED" ] || cat > "$GROK_SEED" <<'EOF'
Check-in. One or two sentences: who you are and who you report to. Then stand by — do not
start, inspect, or change anything yet.
EOF
}

# Start a session, resuming its prior conversation if there is one.
# If the resume attempt dies (no prior session, or a transcript we cannot load), fall back
# to a fresh seeded start. That fallback IS the crash handling: a bad saved state can delay
# the session, it can never permanently keep it down.
start_vp() {
  tmux kill-session -t "$VP" 2>/dev/null || true
  tmux new-session -d -s "$VP" -c "$VP_DIR" \
    claude "--remote-control=$VP" --continue \
    --append-system-prompt "$(cat "$VP_MD")"
  sleep 6
  clear_trust_gate "$VP"
  if alive "$VP" claude; then log "vp: resumed prior conversation"; return 0; fi

  log "vp: nothing to resume — starting a fresh conversation"
  tmux kill-session -t "$VP" 2>/dev/null || true
  tmux new-session -d -s "$VP" -c "$VP_DIR" \
    claude "--remote-control=$VP" \
    --append-system-prompt "$(cat "$VP_MD")" \
    "$(cat "$VP_SEED")"
}

start_grok() {
  tmux kill-session -t "$GROK" 2>/dev/null || true
  tmux new-session -d -s "$GROK" -c "$GROK_DIR" \
    grok --continue --rules "$(cat "$GROK_MD")"
  sleep 6
  if alive "$GROK" grok; then log "grok: resumed prior conversation"; return 0; fi

  log "grok: nothing to resume — starting a fresh conversation"
  tmux kill-session -t "$GROK" 2>/dev/null || true
  tmux new-session -d -s "$GROK" -c "$GROK_DIR" \
    grok --rules "$(cat "$GROK_MD")" "$(cat "$GROK_SEED")"
}

# A seat parked on the trust-folder menu is the worst kind of down: the process is running,
# so every process-level check calls it healthy, while it answers nobody. Config keys did not
# reliably suppress it across Claude Code versions, so clear it the way a human would —
# but only when that exact menu is on screen, never blind.
clear_trust_gate() {
  tmux capture-pane -p -t "$1" 2>/dev/null | grep -q "trust this folder" || return 0
  log "$1: parked on the trust-folder prompt — accepting"
  tmux send-keys -t "$1" Enter
  sleep 3
}

# Some blocked states no restart can fix — an expired login is the main one. Restarting into
# them forever would be a crash loop that reports success. Name them, say a human is needed,
# and leave the seat alone.
# Only the last few lines are read: the status bar reflects the CURRENT state, while
# "Login expired · Please run /login" stays in the transcript above forever once printed.
# Matching the whole pane made a seat that had just been logged in successfully keep
# reporting itself blocked — a stale-text false positive, which is its own kind of lie.
needs_human() {
  tail=$(tmux capture-pane -p -t "$1" 2>/dev/null | grep -v '^$' | tail -8) || return 1
  case "$tail" in
    *"Not logged in"*) echo "not logged in — attach and run /login"; return 0 ;;
  esac
  return 1
}

cmd_ensure() {
  write_prompts
  down=0
  if ! alive "$VP" claude; then log "vp: down — restarting"; start_vp; down=1; fi
  alive "$VP" claude && clear_trust_gate "$VP"
  blocked=$(needs_human "$VP") && log "vp: UP BUT BLOCKED — $blocked (a restart will not fix this)"
  # The report is optional: a host without the Grok CLI still gets a VP. Losing the second
  # seat must never cost you the first one.
  if have_grok && ! alive "$GROK" grok; then log "grok: down — restarting"; start_grok; down=1; fi
  [ "$down" -eq 0 ] || log "restart complete"
}

cmd_install() {
  need tmux "Install it with: brew install tmux (or apt install tmux)"
  need claude "Install Claude Code first: https://claude.com/claude-code"
  have_grok || echo "note: no grok CLI here — installing the VP seat only"

  write_prompts
  trust_workdir
  # Copy the runner to a stable path so the supervisor survives plugin updates,
  # reinstalls, and the plugin directory moving.
  cp "$0" "$RUNNER"
  chmod +x "$RUNNER"

  cat > "$STATE/config" <<EOF
# fleet-bootstrap settings, captured at install. Edit and re-run install to change.
: "\${FLEET_VP_SESSION:=$VP}"
: "\${FLEET_GROK_SESSION:=$GROK}"
: "\${FLEET_BOOTSTRAP_INTERVAL:=$INTERVAL}"
: "\${FLEET_BOOTSTRAP_DIR:=$WORKDIR}"
EOF

  if [ "$(uname -s)" = "Darwin" ]; then
    install_launchd   # kickstart runs the first check for us
  else
    install_cron
    cmd_ensure        # cron will not fire for up to a minute; do not leave the seat down
  fi

  echo "prompts:   $STATE/*.md — edit freely, reinstall will not overwrite them"
  sleep 20
  cmd_status
}

# Linux has no launchd. cron is the lazy portable equivalent: it survives reboot without
# systemd lingering, needs no login session, and @reboot + every-minute covers the same two
# jobs (come up at boot, stay up after).
install_cron() {
  need crontab "Install cron, or supervise $RUNNER yourself"
  line_boot="@reboot $RUNNER ensure >> $LOG 2>&1"
  line_tick="* * * * * $RUNNER ensure >> $LOG 2>&1"
  { crontab -l 2>/dev/null | grep -v "fleet-bootstrap.sh ensure" || true
    echo "$line_boot"
    echo "$line_tick"
  } | crontab -
  echo "installed: cron entries (@reboot + every minute) for $RUNNER"
}

install_launchd() {
  mkdir -p "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"
  cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>${SHELL:-/bin/zsh}</string>
    <string>-lc</string>
    <string>exec '$RUNNER' ensure</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>StartInterval</key><integer>$INTERVAL</integer>
  <key>StandardOutPath</key><string>$LOG</string>
  <key>StandardErrorPath</key><string>$LOG</string>
</dict>
</plist>
EOF

  launchctl bootout "$domain/$LABEL" 2>/dev/null || true
  launchctl bootstrap "$domain" "$PLIST"
  launchctl kickstart "$domain/$LABEL"
  echo "installed: $PLIST (checks every ${INTERVAL}s)"
}

# Claude Code names a Remote Control session after its working directory, not after the
# --remote-control value, and prints the join URL once at startup where it scrolls away.
# Both live in the session record, so read them from there — a seat you cannot find in the
# app is a seat that is not really reachable.
seat_link() {
  pid=$(tmux display-message -p -t "$1" '#{pane_pid}' 2>/dev/null) || return 0
  f="$HOME/.claude/sessions/$pid.json"
  [ -f "$f" ] || return 0
  command -v python3 >/dev/null 2>&1 || return 0
  python3 - "$f" <<'PY' 2>/dev/null || true
import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception:
    raise SystemExit(0)
b = d.get("bridgeSessionId")
if b:
    print("             in the Claude app as '%s' — https://claude.ai/code/%s" % (d.get("name", "?"), b))
PY
}

report() {
  if alive "$1" "$2"; then
    blocked=$(needs_human "$1") && { echo "$3 '$1' UP BUT BLOCKED: $blocked"; return 0; }
    echo "$3 '$1' healthy — attach with: tmux attach -t $1"
    [ "$2" = "claude" ] && seat_link "$1"
  else
    echo "$3 '$1' DOWN — the next check (within ${INTERVAL}s) restarts it"
  fi
}

cmd_status() {
  echo "host:       $(hostname -s) ($(uname -s)), tmux sockets in $TMUX_TMPDIR"
  if [ "$(uname -s)" = "Darwin" ] && [ -f "$PLIST" ]; then
    echo "supervisor: launchd, checking every ${INTERVAL}s"
    launchctl print "$domain/$LABEL" 2>/dev/null | grep -E '^\s+(state|last exit code) ' || true
  elif crontab -l 2>/dev/null | grep -q "fleet-bootstrap.sh ensure"; then
    echo "supervisor: cron, @reboot + every minute"
  else
    echo "supervisor: NOT installed — run: fleet-bootstrap.sh install"
  fi
  report "$VP" claude "vp:        "
  if have_grok; then report "$GROK" grok "grok:      "; else echo "grok:       not installed on this host — VP seat only"; fi

  echo "--- supervisor log ---"
  tail -8 "$LOG" 2>/dev/null || echo "(no log yet: $LOG)"
}

cmd_uninstall() {
  launchctl bootout "$domain/$LABEL" 2>/dev/null || true
  crontab -l 2>/dev/null | grep -v "fleet-bootstrap.sh ensure" | crontab - 2>/dev/null || true
  rm -f "$PLIST" "$RUNNER"
  tmux kill-session -t "$VP" 2>/dev/null || true
  tmux kill-session -t "$GROK" 2>/dev/null || true
  echo "uninstalled: supervisor removed, both sessions killed"
  echo "kept:        prompts in $STATE (delete the directory to remove them too)"
}

case "${1:-status}" in
  install)   cmd_install ;;
  ensure)    cmd_ensure ;;
  status)    cmd_status ;;
  uninstall) cmd_uninstall ;;
  *) echo "usage: fleet-bootstrap.sh [install|ensure|status|uninstall]" >&2; exit 2 ;;
esac
