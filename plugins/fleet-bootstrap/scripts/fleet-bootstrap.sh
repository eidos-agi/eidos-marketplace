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
# Settings are written at install time. launchd and cron do not inherit the shell you
# installed from, so an env override that is not persisted silently reverts on the next
# reboot — exactly when nobody is watching.
#
# PARSED, never sourced. Sourcing a file at a predictable path would hand anything able to
# write it arbitrary code execution as this user, every 60s, at login, forever — a better
# persistence primitive than most malware builds, installed by the one component designed
# to survive everything. Only known keys are accepted, and only conservative values; an
# unrecognised line is ignored, never executed.
#
# Reads BOTH the current KEY=VALUE form and the legacy `: "${KEY:=VALUE}"` shell form that
# earlier installs wrote. Not politeness — omitting it broke a live host on deploy: the
# legacy lines were rejected as unsafe, the seat name fell back to its default, and the
# supervisor stopped recognising the seat it was already running. A format change without
# a migration path is a regression shipped to every host that upgrades.
if [ -f "$STATE/config" ]; then
  while IFS='=' read -r _k _v || [ -n "$_k" ]; do
    _k=$(printf '%s' "$_k" | tr -cd 'A-Za-z0-9_')   # legacy: strips `: "${` and the `:`
    _v=${_v%\}\"}                                    # legacy: strips the trailing `}"`
    case "$_v" in ''|*[!A-Za-z0-9_./-]*) continue ;; esac
    case "$_k" in
      FLEET_VP_SESSION)          FLEET_VP_SESSION="${FLEET_VP_SESSION:-$_v}" ;;
      FLEET_GROK_SESSION)        FLEET_GROK_SESSION="${FLEET_GROK_SESSION:-$_v}" ;;
      FLEET_BOOTSTRAP_INTERVAL)  FLEET_BOOTSTRAP_INTERVAL="${FLEET_BOOTSTRAP_INTERVAL:-$_v}" ;;
      FLEET_BOOTSTRAP_DIR)       FLEET_BOOTSTRAP_DIR="${FLEET_BOOTSTRAP_DIR:-$_v}" ;;
      FLEET_BACKOFF_MAX)         FLEET_BACKOFF_MAX="${FLEET_BACKOFF_MAX:-$_v}" ;;
    esac
  done < "$STATE/config"
fi

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
EVENTS="$STATE/events.jsonl"

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

# ---- single-runner lock ------------------------------------------------------------
# cron starts a second ensure if the first one hangs (launchd will not). Two concurrent
# runs can both decide a seat is down and both start it. mkdir is atomic on POSIX, so it
# is the lock primitive that needs no flock dependency.
LOCK="$STATE/.ensure.lock"
take_lock() {
  if mkdir "$LOCK" 2>/dev/null; then
    trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT INT TERM
    return 0
  fi
  # A crashed run would otherwise hold the lock forever, which would silently disable
  # the supervisor — a worse failure than the overlap it prevents. Break it if it is
  # older than 10 minutes; a healthy ensure takes ~15s at worst.
  if [ -n "$(find "$LOCK" -maxdepth 0 -mmin +10 2>/dev/null)" ]; then
    log "lock: stale (>10m) — breaking it"
    rmdir "$LOCK" 2>/dev/null || true
    mkdir "$LOCK" 2>/dev/null || return 1
    trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT INT TERM
    return 0
  fi
  return 1
}

# ---- restart budget ----------------------------------------------------------------
# Without this, a start that can never succeed (a CLI flag that changed under us, a
# corrupt state dir) retries 1,440x/day, each attempt submitting a seeded prompt against
# real quota, silently. Backoff turns a permanent failure into a bounded cost and a loud
# one. Restarting is the supervisor's only power; a budget is what keeps it honest.
BACKOFF_MAX="${FLEET_BACKOFF_MAX:-6}"

# Seconds to wait before attempt N: immediate, 2m, 5m, 15m, 30m, then hourly.
backoff_for() {
  case "$1" in
    0|1) echo 0 ;; 2) echo 120 ;; 3) echo 300 ;;
    4) echo 900 ;; 5) echo 1800 ;; *) echo 3600 ;;
  esac
}

restart_count() { [ -f "$STATE/restarts.$1" ] && cut -d' ' -f1 "$STATE/restarts.$1" || echo 0; }
restart_last()  { [ -f "$STATE/restarts.$1" ] && cut -d' ' -f2 "$STATE/restarts.$1" || echo 0; }
record_restart() { echo "$2 $(date +%s)" > "$STATE/restarts.$1"; }
clear_restarts() { rm -f "$STATE/restarts.$1"; }

# ---- state streaks -----------------------------------------------------------------
# Some states are only worth acting on once they PERSIST. A seat that has just started is
# briefly UNREGISTERED while Remote Control registers; restarting on the first sighting
# would kill healthy seats mid-handshake and could loop forever. Count consecutive
# observations instead, and act only when the state has proven itself.
streak_bump() {
  _f="$STATE/streak.$1"
  if [ "$(cut -d' ' -f1 "$_f" 2>/dev/null)" = "$2" ]; then
    _n=$(( $(cut -d' ' -f2 "$_f" 2>/dev/null || echo 0) + 1 ))
  else
    _n=1
  fi
  echo "$2 $_n" > "$_f"
  echo "$_n"
}
streak_clear() { rm -f "$STATE/streak.$1"; }

# may_restart — is starting this seat allowed right now? Echoes the reason when not.
may_restart() {
  n=$(restart_count "$1"); last=$(restart_last "$1")
  [ -n "$n" ] || n=0; [ -n "$last" ] || last=0
  if [ "$n" -ge "$BACKOFF_MAX" ]; then
    echo "held after $n consecutive failed starts — a human has to look"
    return 1
  fi
  wait=$(backoff_for "$n"); now=$(date +%s)
  if [ $((now - last)) -lt "$wait" ]; then
    echo "backoff, $((wait - now + last))s left after $n failed starts"
    return 1
  fi
  return 0
}

# Both logs grow forever otherwise. Rotate at ~1MB, keep one generation.
rotate() {
  [ -f "$1" ] || return 0
  sz=$(wc -c < "$1" 2>/dev/null | tr -d ' ') || return 0
  [ -n "$sz" ] || return 0
  [ "$sz" -gt "${2:-1048576}" ] || return 0
  mv "$1" "$1.1" 2>/dev/null || return 0
  : > "$1"
}

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
  # PROVEN 2026-07-25 on an owned decoy: state went SN -> TN under SIGSTOP and this case
  # matched, so alive() returned 1. The branch logic is exercised; the full path through
  # a launchd-spawned seat is not (those processes are outside an agent's signal reach).
  case "$(ps -p "$pid" -o state= 2>/dev/null | tr -d ' ')" in
    Z*|T*) return 1 ;;
  esac
  return 0
}

# probe_seat — gather every FREE signal about a seat into P_* globals, so the same
# evidence feeds both the decision and the record. Sets no policy; just observes.
#
# Deliberately records DERIVED booleans from the pane, never its text: the pane holds
# real conversations, and a supervisor log is the wrong place for them.
probe_seat() {
  P_SEAT="$1"; P_KIND="$2"
  P_SESSION=false; P_PROC=""; P_PSTATE=""; P_BRIDGE=false; P_STATUS=""; P_BLOCKED=""

  tmux has-session -t "$P_SEAT" 2>/dev/null || return 0
  P_SESSION=true
  pid=$(tmux display-message -p -t "$P_SEAT" '#{pane_pid}' 2>/dev/null) || return 0
  [ -n "$pid" ] || return 0
  P_PROC=$(ps -p "$pid" -o comm= 2>/dev/null | sed 's|.*/||' | tr -d ' ')
  P_PSTATE=$(ps -p "$pid" -o state= 2>/dev/null | tr -d ' ')

  # The session record is written by the seat itself. bridgeSessionId is the ONLY
  # authoritative proof that Remote Control actually registered — a seat can run for
  # hours, healthy by every process check, and be invisible to the app without it.
  # NOTE: updatedAt in that same file is NOT a heartbeat. Measured 2168s stale on a
  # healthy idle seat; it tracks state transitions, not time. Never gate liveness on it.
  # Read two plain lines rather than eval-ing generated shell. The generator is ours and
  # the values are constrained, but eval-of-generated-code is the same hazard shape as
  # sourcing the config, and a plain read costs nothing.
  if [ "$P_KIND" = claude ] && [ -f "$HOME/.claude/sessions/$pid.json" ] && command -v python3 >/dev/null 2>&1; then
    out=$(python3 - "$HOME/.claude/sessions/$pid.json" <<'PY' 2>/dev/null || true
import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception:
    print("false"); print(""); raise SystemExit(0)
print("true" if d.get("bridgeSessionId") else "false")
print(str(d.get("status", ""))[:16])
PY
)
    P_BRIDGE=$(printf '%s' "$out" | sed -n 1p)
    P_STATUS=$(printf '%s' "$out" | sed -n 2p)
    [ "$P_BRIDGE" = true ] || P_BRIDGE=false
  fi

  blocked=$(needs_human "$P_SEAT") && P_BLOCKED="$blocked"
  return 0
}

# emit_event — one JSONL record per seat per check, evidence and all.
#
# This is the v1 deliverable. v1 cannot honestly answer "can this seat respond?" without
# spending the shared quota whose exhaustion is itself a failure mode — so instead it
# records what every cheap signal returned, and lets v2 be designed from which ones
# actually predicted muteness. Conclusions go in the human log; evidence goes here.

# j — make a value safe to sit inside a JSON string.
#
# Every field here is a short identifier (a process name, a state token, a reason), never
# free prose, so stripping the characters that would need escaping is honest and cheap.
# It is not cosmetic: a process name containing a quote produced a syntactically invalid
# record, which would have silently corrupted the corpus this whole phase exists to build.
# A malformed line in an append-only research log is worse than a missing one — it breaks
# every reader that comes after it.
j() { printf '%s' "$1" | tr -d '"\\' | tr -c -d '[:print:]' | cut -c1-"${2:-60}"; }

emit_event() {
  state="$1"; action="$2"
  printf '{"ts":"%s","host":"%s","seat":"%s","kind":"%s","state":"%s","session":%s,"proc":"%s","pstate":"%s","bridge":%s,"status":"%s","blocked":"%s","action":"%s","v":1}\n' \
    "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$(j "$(hostname -s)")" "$(j "$P_SEAT" 40)" "$(j "$P_KIND" 16)" \
    "$(j "$state" 20)" "$P_SESSION" "$(j "$P_PROC" 32)" "$(j "$P_PSTATE" 8)" "$P_BRIDGE" "$(j "$P_STATUS" 16)" \
    "$(j "$P_BLOCKED")" "$(j "$action" 16)" >> "$EVENTS"
}

# ---- generated-state versioning ----------------------------------------------------
# Identity prompts are never clobbered, which is right: operator edits are sacred. But the
# same rule lets every host accumulate instructions that were true at install time and then
# silently rot. HOSTKEY's VP spent hours believing it ran on a Mac, under launchd, with a
# Grok report that did not exist — it would have sent work to a session that was never
# there. Stale instructions do not crash; they make a seat confidently wrong, which is
# worse than down and invisible to every health check.
#
# The whole trick is telling "the operator edited this" apart from "we generated this and
# it is now stale". A hash of what we last generated answers exactly that.
hash_stdin() {
  if command -v shasum >/dev/null 2>&1; then shasum -a 256 | cut -d' ' -f1
  elif command -v sha256sum >/dev/null 2>&1; then sha256sum | cut -d' ' -f1
  else cksum | cut -d' ' -f1   # weak, but a changed file still changes it
  fi
}

# install_prompt <path> <file-holding-freshly-generated-content>
#   absent             -> write it, record the hash
#   matches our stamp  -> untouched by the operator, so refresh freely
#   differs            -> operator edited it, or it predates versioning: LEAVE IT, say so
#
# Takes a FILE rather than a string on purpose: the generated prompts contain parentheses,
# and `var=$(cat <<EOF ... )` mis-parses on them. A temp file sidesteps every quoting and
# substitution hazard at the cost of one write.
install_prompt() {
  _path="$1"; _src="$2"; _stamp="$STATE/.$(basename "$_path").gen"
  _new=$(hash_stdin < "$_src")

  if [ ! -f "$_path" ]; then
    cp "$_src" "$_path"
    printf '%s\n' "$_new" > "$_stamp"
    return 0
  fi

  _cur=$(hash_stdin < "$_path")
  [ "$_cur" = "$_new" ] && return 0            # already current; say nothing

  if [ -f "$_stamp" ] && [ "$_cur" = "$(cat "$_stamp" 2>/dev/null)" ]; then
    cp "$_src" "$_path"
    printf '%s\n' "$_new" > "$_stamp"
    log "$(basename "$_path"): refreshed — generated, unmodified, and the host facts changed"
    return 0
  fi

  # No stamp means the file predates versioning and its provenance is unknown. Treating
  # unknown as "operator edited" is the conservative direction: the cost is a stale prompt
  # that gets REPORTED, versus silently overwriting something a human wrote.
  # Say it once per distinct situation, not once per tick. ensure runs every 60s, so an
  # unconditional warning here would write 1,440 identical lines a day and bury the events
  # that matter — a supervisor that cries wolf on schedule is one nobody reads.
  _warn="$STATE/.$(basename "$_path").warned"
  _key="$_cur:$_new"
  [ "$(cat "$_warn" 2>/dev/null)" = "$_key" ] && return 0
  printf '%s\n' "$_key" > "$_warn"

  if [ -f "$_stamp" ]; then
    log "$(basename "$_path"): stale vs the current template but edited — left alone. To adopt: rm '$_path'"
  else
    log "$(basename "$_path"): stale vs the current template, provenance unknown (predates versioning) — left alone. To adopt: rm '$_path'"
  fi
  return 0
}

write_prompts() {
  mkdir -p "$STATE" "$VP_DIR" "$GROK_DIR"
  _gen="$STATE/.generated.tmp"
  # Generated content is refreshed only while it stays byte-identical to what we last
  # generated; the moment the operator touches it, it is theirs (GUARD-004).

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

  cat > "$_gen" <<EOF
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
  install_prompt "$VP_MD" "$_gen"

  cat > "$_gen" <<'EOF'
Bootstrap check-in. In one short paragraph, tell me what you are, who reports to you, and
what you can bring back online for me — then stand by. Do not start, restart, or inspect
anything yet.
EOF
  install_prompt "$VP_SEED" "$_gen"

  cat > "$_gen" <<EOF
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
  install_prompt "$GROK_MD" "$_gen"

  cat > "$_gen" <<'EOF'
Check-in. One or two sentences: who you are and who you report to. Then stand by — do not
start, inspect, or change anything yet.
EOF
  install_prompt "$GROK_SEED" "$_gen"
}

# Start a session, resuming its prior conversation if there is one.
# If the resume attempt dies (no prior session, or a transcript we cannot load), fall back
# to a fresh seeded start. That fallback IS the crash handling: a bad saved state can delay
# the session, it can never permanently keep it down.
# wait_ready — poll until the seat is up, or the ceiling is reached.
#
# Replaces a fixed `sleep 6`. Every observed successful resume took 6-7 seconds against
# that 6-second timeout, so success turned on sub-second jitter — and losing did not
# retry, it killed the resumed session and started fresh, destroying the conversation
# --continue exists to protect. Slow must not be fatal.
wait_ready() {
  waited=0
  while [ "$waited" -lt "${3:-30}" ]; do
    alive "$1" "$2" && return 0
    sleep 2
    waited=$((waited + 2))
  done
  return 1
}

start_vp() {
  tmux kill-session -t "$VP" 2>/dev/null || true
  tmux new-session -d -s "$VP" -c "$VP_DIR" \
    claude "--remote-control=$VP" --continue \
    --append-system-prompt "$(cat "$VP_MD")"
  clear_trust_gate "$VP"
  if wait_ready "$VP" claude; then log "vp: resumed prior conversation"; return 0; fi

  # Say what was observed, not what is assumed. The old message claimed "nothing to
  # resume" when all that was ever measured was "not up in time" — asserting a cause the
  # code never saw. A fresh start here may well be discarding a real conversation.
  log "vp: --continue did not come up within 30s — falling back to a fresh conversation"
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
  if wait_ready "$GROK" grok; then log "grok: resumed prior conversation"; return 0; fi

  log "grok: --continue did not come up within 30s — falling back to a fresh conversation"
  tmux kill-session -t "$GROK" 2>/dev/null || true
  tmux new-session -d -s "$GROK" -c "$GROK_DIR" \
    grok --rules "$(cat "$GROK_MD")" "$(cat "$GROK_SEED")"
}

# A seat parked on the trust-folder menu is the worst kind of down: the process is running,
# so every process-level check calls it healthy, while it answers nobody. Config keys did not
# reliably suppress it across Claude Code versions, so clear it the way a human would —
# but only when that exact menu is on screen, never blind.
clear_trust_gate() {
  pane=$(tmux capture-pane -p -t "$1" 2>/dev/null) || return 0
  case "$pane" in *"trust this folder"*) ;; *) return 0 ;; esac

  # Confirm the highlighted option is the one we mean to accept before pressing anything.
  # A blind Enter presses whatever is selected: the menu is "1. Yes, I trust" / "2. No,
  # exit", so if a future version lands with a different default, a blind Enter would make
  # the supervisor close its own seat — on every tick, forever. Match the marker, or leave
  # it for a human. Answer prompts you can see; never type blind.
  if printf '%s' "$pane" | grep -q '❯.*1\..*rust'; then
    log "$1: trust prompt with option 1 selected — confirming"
    tmux send-keys -t "$1" Enter
    sleep 3
  else
    log "$1: trust prompt visible but option 1 is NOT selected — leaving it for a human"
  fi
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

# derive_state — name what the evidence in P_* actually says.
#
# Not yet the full classifier (EID-1017): MUTE needs the account-health signal that does
# not exist yet, and UNREGISTERED is observed here but not yet acted on. Naming the states
# now means the event stream starts collecting them immediately, so when the classifier
# lands it can be tuned against real history instead of guesses.
derive_state() {
  [ "$P_SESSION" = true ] || { echo DEAD; return; }
  [ -n "$P_PROC" ] && echo "$P_PROC" | grep -q "$P_KIND" || { echo DEAD; return; }
  case "$P_PSTATE" in Z*|T*) echo WEDGED; return ;; esac
  [ -n "$P_BLOCKED" ] && { echo BLOCKED_HUMAN; return; }
  # A claude seat with no bridge id is running and invisible to the app. Observed for
  # hours on HOSTKEY: healthy by every process check, unreachable by the human.
  [ "$P_KIND" = claude ] && [ "$P_BRIDGE" = false ] && { echo UNREGISTERED; return; }
  echo READY
}

# tend_seat — probe, classify, and respond according to what the state actually is.
#
# The response is NOT uniform, which is the point. Restarting is right for DEAD and
# WEDGED, useless for BLOCKED_HUMAN (an expired login survives any restart), and will be
# actively harmful for MUTE once that state exists — a restart submits a seeded prompt
# against a quota that is already gone, deepening the outage while reporting a fix.
tend_seat() {
  seat="$1"; kind="$2"
  probe_seat "$seat" "$kind"
  state=$(derive_state)

  case "$state" in
    DEAD|WEDGED)
      if ! reason=$(may_restart "$seat"); then
        log "$seat: $state but $reason"
        emit_event "$state" held
        return 0
      fi
      n=$(restart_count "$seat")
      log "$seat: $state — restarting (attempt $((n + 1)))"
      emit_event "$state" restart
      case "$kind" in claude) start_vp ;; grok) start_grok ;; esac
      if alive "$seat" "$kind"; then
        clear_restarts "$seat"
      else
        record_restart "$seat" "$((n + 1))"
        log "$seat: start did not come up healthy — attempt $((n + 1)) recorded"
      fi
      return 1
      ;;
    UNREGISTERED)
      # Running, healthy by every process check, and invisible to the Claude app because
      # Remote Control never registered. Observed for hours on HOSTKEY after a seat started
      # while logged out. A restart is the only fix — but registration takes a moment, so
      # act only once the state has persisted, or a fresh seat gets killed mid-handshake.
      n=$(streak_bump "$seat" UNREGISTERED)
      if [ "$n" -lt 3 ]; then
        emit_event "$state" waiting
        return 0
      fi
      if ! reason=$(may_restart "$seat"); then
        log "$seat: UNREGISTERED for ${n} checks but $reason"
        emit_event "$state" held
        return 0
      fi
      k=$(restart_count "$seat")
      log "$seat: UNREGISTERED for ${n} checks — no Remote Control; restarting (attempt $((k + 1)))"
      emit_event "$state" restart
      case "$kind" in claude) start_vp ;; grok) start_grok ;; esac
      if alive "$seat" "$kind"; then clear_restarts "$seat"; else record_restart "$seat" "$((k + 1))"; fi
      streak_clear "$seat"
      return 1
      ;;
    BLOCKED_HUMAN)
      log "$seat: UP BUT BLOCKED — $P_BLOCKED (a restart will not fix this)"
      emit_event "$state" none
      streak_clear "$seat"
      ;;
    *)
      emit_event "$state" none
      clear_restarts "$seat"
      streak_clear "$seat"
      ;;
  esac
  return 0
}

cmd_ensure() {
  # Never let two runs fight over the same seats.
  take_lock || { log "ensure: another run holds the lock — skipping this tick"; return 0; }
  rotate "$LOG"; rotate "$EVENTS"
  write_prompts
  down=0

  tend_seat "$VP" claude || down=1
  alive "$VP" claude && clear_trust_gate "$VP"

  # The report is optional: a host without the Grok CLI still gets a VP. Losing the second
  # seat must never cost you the first one.
  if have_grok; then tend_seat "$GROK" grok || down=1; fi

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
  #
  # Write-then-rename, because `cp` is NOT atomic and the supervisor fires every 60s: a
  # tick that lands mid-copy executes a half-written script. That is not hypothetical —
  # `line 372: MANAGER: unbound variable` appears once in the Mac's log, naming a variable
  # that exists in no version of this file. rename(2) is atomic on the same filesystem, so
  # a tick sees either the old runner or the new one, never a torn one.
  cp "$0" "$RUNNER.new"
  chmod +x "$RUNNER.new"
  mv -f "$RUNNER.new" "$RUNNER"

  # Plain KEY=VALUE, because this file is parsed and must never be shell.
  cat > "$STATE/config" <<EOF
# fleet-bootstrap settings, captured at install. Edit and re-run install to change.
# Parsed, not sourced: only these keys are read, and only plain values.
FLEET_VP_SESSION=$VP
FLEET_GROK_SESSION=$GROK
FLEET_BOOTSTRAP_INTERVAL=$INTERVAL
FLEET_BOOTSTRAP_DIR=$WORKDIR
EOF
  chmod 600 "$STATE/config"

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

# Library mode: when sourced by selftest, define everything and dispatch nothing. Without
# this the only way to exercise a decision function is to run the real supervisor against
# real seats, which is how an earlier test started a live Grok session by accident.
if [ "${FLEET_BOOTSTRAP_LIB:-}" = 1 ]; then
  return 0 2>/dev/null || exit 0
fi

case "${1:-status}" in
  install)   cmd_install ;;
  ensure)    cmd_ensure ;;
  status)    cmd_status ;;
  uninstall) cmd_uninstall ;;
  *) echo "usage: fleet-bootstrap.sh [install|ensure|status|uninstall]" >&2; exit 2 ;;
esac
