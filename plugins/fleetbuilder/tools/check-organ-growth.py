#!/usr/bin/env python3
"""Does fleetbuilder's picture of its organs match what the organs can ACTUALLY do?

The skill lists emux's tools as prose — a frozen snapshot that goes stale the moment
emux grows. This reads each organ's LIVE tool surface from its source and diffs it
against .organ-tools.json (what fleetbuilder currently knows). New tools = the
organism grew; go learn their `when` and fold them into the skill.

Prints the current tools and flags anything NEW. Exit 0 always (informational);
the point is to SURFACE growth, not block. Run by the SessionStart hook so a
fleetbuild session sees the live list, not the doc."""
import json, os, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
SNAP = HERE / ".organ-tools.json"

# where each organ's live tool surface lives (source of truth), path-overridable
ORGANS = {
    "emux": os.environ.get("EMUX_SERVER",
                           str(Path.home() / "repos-eidos-agi/emux/src/emux/server.py")),
}

def live_tools(server_path: str) -> list[str] | None:
    p = Path(server_path)
    if not p.exists():
        return None
    src = p.read_text()
    # a tool is an `async def NAME` immediately after an @mcp.tool() decorator
    return sorted(set(re.findall(r"@mcp\.tool\(\)\s*\n\s*async def ([a-z_]+)", src)))

def main() -> int:
    snap = json.loads(SNAP.read_text()) if SNAP.exists() else {}
    grew = False
    for organ, path in ORGANS.items():
        known = set(snap.get(organ, []))
        current = live_tools(path)
        if current is None:
            print(f"[{organ}] live surface not found at {path} — cannot check growth")
            continue
        new = [t for t in current if t not in known]
        gone = [t for t in known if t not in current]
        if new:
            grew = True
            print(f"[{organ}] GREW — {len(new)} new tool(s) fleetbuilder does not yet know: "
                  + ", ".join(new))
            print(f"        learn their WHEN and fold them into the fleetbuild skill, then update .organ-tools.json")
        if gone:
            print(f"[{organ}] shrank — gone since snapshot: {', '.join(gone)}")
        if not new and not gone:
            print(f"[{organ}] current ({len(current)} tools) matches what fleetbuilder knows.")
    if grew:
        print("\nThe organism grew. The skill's tool list is a guide; the live tools are the truth.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
