#!/bin/sh
# selftest — exercise the decision logic without touching a real seat.
#
# Every function here decides whether to spend quota or leave a human stranded, so each
# one leaves a runnable check behind. The rule learned the hard way: never point a proof
# at live infrastructure. An earlier ad-hoc test ran `ensure` with FLEET_GROK_SESSION=none
# and started a real Grok seat called "none" — a test that costs quota is a bad test.
#
# Run: sh scripts/selftest.sh
set -u

STATE=$(mktemp -d)
export FLEET_BOOTSTRAP_STATE="$STATE"
pass=0; fail=0

ok()   { pass=$((pass + 1)); echo "  ok   — $1"; }
bad()  { fail=$((fail + 1)); echo "  FAIL — $1"; }
is()   { [ "$2" = "$3" ] && ok "$1" || bad "$1 (got '$2', want '$3')"; }

# Library mode defines the functions and dispatches nothing. The sourced script sets
# `set -eu`, which would abort this file on the first intentionally-failing check, so
# undo it immediately after.
FLEET_BOOTSTRAP_LIB=1 . "$(dirname "$0")/fleet-bootstrap.sh" >/dev/null 2>&1 || true
set +e

echo "backoff schedule"
is "attempt 0 is immediate"   "$(backoff_for 0)" 0
is "attempt 1 is immediate"   "$(backoff_for 1)" 0
is "attempt 2 waits 2m"       "$(backoff_for 2)" 120
is "attempt 5 waits 30m"      "$(backoff_for 5)" 1800
is "beyond the table is 1h"   "$(backoff_for 99)" 3600

echo "restart budget"
rm -f "$STATE/restarts.t"
may_restart t >/dev/null 2>&1 && ok "a seat with no history may start" \
                              || bad "a seat with no history was blocked"

echo "6 $(date +%s)" > "$STATE/restarts.t"
may_restart t >/dev/null 2>&1 && bad "an exhausted budget still allowed a start" \
                              || ok "budget exhausted -> held for a human"

echo "3 $(date +%s)" > "$STATE/restarts.t"
may_restart t >/dev/null 2>&1 && bad "mid-backoff still allowed a start" \
                              || ok "mid-backoff -> held"

echo "3 $(( $(date +%s) - 600 ))" > "$STATE/restarts.t"
may_restart t >/dev/null 2>&1 && ok "backoff elapsed -> allowed again" \
                              || bad "backoff had elapsed but the start was blocked"

echo "state derivation"
P_KIND=claude; P_SESSION=false; P_PROC=""; P_PSTATE=""; P_BRIDGE=false; P_BLOCKED=""
is "no session is DEAD" "$(derive_state)" DEAD

P_SESSION=true; P_PROC=sh
is "wrong binary is DEAD" "$(derive_state)" DEAD

# TN is the real state string macOS reports for a SIGSTOPped process — verified 2026-07-25
# on an owned decoy (SN -> TN). A stopped seat answers `ps` and serves nobody.
P_PROC=claude; P_PSTATE=TN
is "stopped process is WEDGED" "$(derive_state)" WEDGED

P_PSTATE=Ss+; P_BLOCKED="not logged in"
is "blocked beats bridge" "$(derive_state)" BLOCKED_HUMAN

P_BLOCKED=""; P_BRIDGE=false
is "no bridge id is UNREGISTERED" "$(derive_state)" UNREGISTERED

P_BRIDGE=true
is "all signals good is READY" "$(derive_state)" READY

# Grok has no Remote Control, so a false bridge must not mark it UNREGISTERED.
P_KIND=grok; P_PROC=grok; P_BRIDGE=false
is "grok without a bridge is READY" "$(derive_state)" READY

echo "event records survive hostile values"
# Regression: a process name with a quote produced invalid JSON and would have silently
# corrupted the research corpus. Found 2026-07-25, 20 minutes after the corpus shipped.
EVENTS="$STATE/events.jsonl"; : > "$EVENTS"
P_SEAT='seat'; P_KIND=claude; P_SESSION=true; P_PSTATE='Ss+'; P_BRIDGE=true; P_STATUS=idle
P_PROC='cla"ude\x'; P_BLOCKED='he said "no" \ then left'
emit_event READY none
if command -v python3 >/dev/null 2>&1; then
  python3 -c "import json,sys; [json.loads(l) for l in open('$EVENTS')]" 2>/dev/null \
    && ok "quotes and backslashes still yield valid JSON" \
    || bad "hostile field values produced invalid JSON"
else
  echo "  skip — no python3 to validate JSON"
fi

echo "config is parsed, not executed"
# The config used to be sourced. Anything able to write that predictable path got code
# execution as this user every 60s, at login, forever. These prove it is now inert data.
CFG="$STATE/cfgtest"; mkdir -p "$CFG"
cat > "$CFG/config" <<'EOF'
FLEET_VP_SESSION=legit-seat
EVIL=$(touch /tmp/fb-pwned-marker)
FLEET_BOOTSTRAP_INTERVAL=90
`touch /tmp/fb-pwned-marker2`
FLEET_GROK_SESSION=has spaces and ; semicolons
EOF
rm -f /tmp/fb-pwned-marker /tmp/fb-pwned-marker2
( unset FLEET_VP_SESSION FLEET_BOOTSTRAP_INTERVAL FLEET_GROK_SESSION
  FLEET_BOOTSTRAP_STATE="$CFG" FLEET_BOOTSTRAP_LIB=1 \
    . "$(dirname "$0")/fleet-bootstrap.sh" >/dev/null 2>&1
  printf '%s|%s|%s\n' "$VP" "$INTERVAL" "$GROK" > "$CFG/out" ) 2>/dev/null || true
read_out=$(cat "$CFG/out" 2>/dev/null || echo "|||")

[ -e /tmp/fb-pwned-marker ] || [ -e /tmp/fb-pwned-marker2 ] \
  && bad "config execution: a command in the config file RAN" \
  || ok "config execution: no command in the config file ran"

is "good key is honoured"        "$(echo "$read_out" | cut -d'|' -f1)" legit-seat
is "numeric key is honoured"     "$(echo "$read_out" | cut -d'|' -f2)" 90
is "unsafe value is ignored"     "$(echo "$read_out" | cut -d'|' -f3)" fleet-grok
rm -f /tmp/fb-pwned-marker /tmp/fb-pwned-marker2

echo "legacy config format still parses"
# Regression: switching the config to KEY=VALUE without a migration path broke a live host
# on deploy. Legacy lines were rejected as unsafe, the seat name fell back to its default,
# and the supervisor stopped recognising the seat it was already running — one cron tick
# away from starting a duplicate. Old installs must keep working.
LEG="$STATE/legacy"; mkdir -p "$LEG"
cat > "$LEG/config" <<'EOF'
# fleet-bootstrap settings, captured at install.
: "${FLEET_VP_SESSION:=hostkey-vp}"
: "${FLEET_BOOTSTRAP_INTERVAL:=60}"
EOF
( unset FLEET_VP_SESSION FLEET_BOOTSTRAP_INTERVAL
  FLEET_BOOTSTRAP_STATE="$LEG" FLEET_BOOTSTRAP_LIB=1 \
    . "$(dirname "$0")/fleet-bootstrap.sh" >/dev/null 2>&1
  printf '%s|%s\n' "$VP" "$INTERVAL" > "$LEG/out" ) 2>/dev/null || true
leg_out=$(cat "$LEG/out" 2>/dev/null || echo "||")
is "legacy seat name survives"  "$(echo "$leg_out" | cut -d'|' -f1)" hostkey-vp
is "legacy interval survives"   "$(echo "$leg_out" | cut -d'|' -f2)" 60

echo
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
