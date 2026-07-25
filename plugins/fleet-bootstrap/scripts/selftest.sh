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

echo
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
