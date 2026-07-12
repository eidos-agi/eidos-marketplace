#!/bin/sh
# FleetBuilder "keep it moving" hook — fires on Stop. ADVISORY only: it surfaces the cadence
# state and the next unblocked task so the loop doesn't drift to a caretaker stop. It does NOT
# block (no forced continuation) — a Stop hook that always blocks traps the user.
#
# ponytail: advisory nudge, exit 0. Ceiling — if you want true self-driving continuation,
# emit a `{"decision":"block","reason":...}` JSON here, but only behind an explicit opt-in env
# flag so a session can always end. Not enabled by default on purpose.

# Staircase cadence: below-buffer means production should outpace release → keep building.
if command -v staircase >/dev/null 2>&1 && [ -d .staircase ]; then
  staircase status 2>/dev/null | grep -iE "ALARM|Buffer:" | sed 's/^/  fleetbuilder: /'
fi

# Next unblocked task, if a docket is present.
if [ -f .docket/docket.json ]; then
  pid=$(sed -n 's/.*"id"[^"]*"\([^"]*\)".*/\1/p' .docket/docket.json | head -1)
  if command -v docket-md >/dev/null 2>&1 && [ -n "$pid" ]; then
    next=$(docket-md task-list --project-id "$pid" 2>/dev/null | grep -E "^○" | head -1)
    [ -n "$next" ] && echo "  fleetbuilder: next unblocked → ${next#○ }"
  fi
fi
exit 0
