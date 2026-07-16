#!/usr/bin/env python3
"""Antibody for the miner's signal/noise filter. `python3 tools/learn_test.py`.
The filter is the money logic: if it lets skill injections / terminal dumps through, the
distilled learnings turn to garbage. Each case below is a real pattern seen in transcripts."""
from learn import _looks_injected

# (text, should_be_filtered)
CASES = [
    ("More", False),                                                    # real short directive
    ("Check EID for fleet", False),                                     # real directive
    ("fix it since the other agent is missing things", False),          # real prose
    ("<command-message>ship</command-message>", True),                  # slash-command expansion
    ("You are the SKEPTIC — a separate, adversarial mind", True),       # agent persona injection
    ("Base directory for this skill: /Users/x/.claude/skills/ship", True),  # skill body
    ("In 2 to 4 words, name what this terminal session is doing.", True),   # fleetd titler prompt
    ("Checking for updates\nChecking for updates", True),               # harness chatter
    ("\x1b[32mgreen\x1b[0m ❯ ✻ Cooked for 4m", True),                   # terminal-pane dump
    ("x" * 1600, True),                                                 # oversized blob (paste/dump)
]

fails = 0
for text, want in CASES:
    got = _looks_injected(text)
    tag = "ok" if got == want else "FAIL"
    if got != want:
        fails += 1
        print(f"{tag}: want filtered={want} got={got} :: {text[:50]!r}")
print(f"--- {len(CASES)-fails}/{len(CASES)} passed ---")
raise SystemExit(1 if fails else 0)
