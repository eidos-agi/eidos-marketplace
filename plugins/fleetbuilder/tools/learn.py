#!/usr/bin/env python3
"""fleetbuilder learn — study Daniel's Claude Code transcripts to learn how to build the
Fleet he needs, and distill it into .fleetbuilder/learnings.md.

Reads the RAW session jsonl (~/.claude/projects/<slug>/*.jsonl) for the target repo — no MCP
dependency — pulls out the human prompts (the real signal: what he asks for, corrects, keeps
wanting), and hands them to `claude -p` to distill durable lessons. Fixed-cost only: uses the
`claude` CLI, never the anthropic API (hard constraint).

Usage:
  learn.py [--repo PATH] [--sessions N] [--max-chars N]
  # defaults: repo=cwd, last 20 sessions, 60k chars of prompts

ponytail: reads the last N sessions, char-capped — not the whole history, not embeddings.
Ceiling: if the corpus outgrows one claude -p call, chunk-and-merge. Not there yet.
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys
from pathlib import Path


def project_slug(repo: Path) -> str:
    # Claude Code encodes the project dir as the abs path with / -> -
    return str(repo.resolve()).replace("/", "-")


# Prefix/substring markers of INJECTED content (slash-command expansions, skill/agent
# persona bodies, system reminders) — not things the human actually typed.
_INJECT = (
    "<command-", "<local-command", "<system-reminder", "<user-prompt-submit",
    "you are the ", "you are a ", "you are an ", "base directory for this skill",
    "# /", "caveat:", "the following", "<budget", "<persisted",
)


# Substrings that mark agent/tool NOISE captured as user turns: the fleetd auto-titler
# prompt, terminal-pane dumps, harness chatter. Not the human.
_NOISE = (
    "name what this terminal session is doing", "checking for updates",
    "new task? /clear", "cooked for", "waiting for a new instruction",
    "run /reload-plugins", "plugins updated", "tokens (b",
)


def _looks_injected(t: str) -> bool:
    low = t.lstrip().lower()
    if any(low.startswith(m) for m in _INJECT):
        return True
    if "<command-name>" in low or "tool_use_id" in low:
        return True
    if any(n in low for n in _NOISE):
        return True
    # Terminal-pane capture: ANSI escapes or a wall of box-drawing chars.
    if "\x1b[" in t or "]0;" in t:
        return True
    boxy = sum(t.count(c) for c in "│┃─━╮╯╭╰┌┐└┘·⏺✻✳✶❯")
    if boxy > 4:
        return True
    # Real directives are prose, not multi-KB blobs — long turns here are dumps/pastes.
    if len(t) > 1500:
        return True
    return False


def user_prompts(jsonl: Path) -> list[str]:
    """Human prompts only — skip tool results, attachments, system reminders, skill/command
    injections. What's left is what the human actually typed."""
    out = []
    for line in jsonl.read_text(errors="replace").splitlines():
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get("type") != "user":
            continue
        c = d.get("message", {}).get("content")
        text = None
        if isinstance(c, str):
            text = c
        elif isinstance(c, list):
            parts = [b.get("text", "") for b in c
                     if isinstance(b, dict) and b.get("type") == "text"]
            text = "\n".join(p for p in parts if p)
        if not text or not text.strip():
            continue
        if _looks_injected(text):
            continue
        out.append(text.strip())
    return out


def main() -> int:
    ap = argparse.ArgumentParser(prog="learn.py")
    ap.add_argument("--repo", default=os.getcwd())
    ap.add_argument("--sessions", type=int, default=20)
    ap.add_argument("--max-chars", type=int, default=60_000)
    ap.add_argument("--dry-run", action="store_true", help="print the corpus, skip claude -p")
    args = ap.parse_args()

    repo = Path(args.repo)
    proj = Path.home() / ".claude" / "projects" / project_slug(repo)
    if not proj.is_dir():
        print(f"fleetbuilder: no transcripts for {repo} at {proj}", file=sys.stderr)
        return 2

    files = sorted(proj.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    files = files[: args.sessions]
    if not files:
        print("fleetbuilder: no session jsonl found", file=sys.stderr)
        return 2

    prompts: list[str] = []
    for f in files:
        prompts.extend(user_prompts(f))
    corpus = "\n\n---\n\n".join(prompts)[: args.max_chars]
    print(f"fleetbuilder: {len(files)} sessions, {len(prompts)} prompts, {len(corpus)} chars",
          file=sys.stderr)

    if args.dry_run:
        print(corpus)
        return 0

    learn_dir = repo / ".fleetbuilder"
    learn_dir.mkdir(exist_ok=True)
    prior = (learn_dir / "learnings.md")
    prior_text = prior.read_text() if prior.exists() else "(none yet)"

    instruction = f"""You are the FleetBuilder Historian. Below are the human's own prompts from
his recent Claude Code sessions building Fleet. Distill DURABLE lessons for a team that builds
Fleet the way he needs — not a session summary. Output markdown with exactly these sections:

## What Fleet he needs
Concrete features/behaviors/priorities he keeps asking for or correcting. Cite the signal.

## How he builds
His disciplines and preferences (e.g. ponytail/laziest-that-works, prove-it, route git through
hancock, staircase cadence, no settings screens). What he rewards; what he rejects.

## Antibodies
Recurring frustrations or mistakes → the durable check/rule that should prevent each recurrence.

## Standing orders
Short imperative rules the build loop must obey every cycle (e.g. "don't ask, just build").

Keep it tight and specific — a teammate should act on it. Merge with, don't duplicate, the
prior learnings. Prior learnings:
---
{prior_text}
---
Recent prompts:
---
{corpus}
---"""

    try:
        r = subprocess.run(["claude", "-p", instruction], capture_output=True, text=True, timeout=180)
    except FileNotFoundError:
        print("fleetbuilder: `claude` CLI not found on PATH", file=sys.stderr)
        return 3
    if r.returncode != 0 or not r.stdout.strip():
        print(f"fleetbuilder: claude -p failed: {r.stderr[:400]}", file=sys.stderr)
        return 3

    prior.write_text(r.stdout)
    print(f"fleetbuilder: learnings updated → {prior}", file=sys.stderr)
    print(r.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
