"""kai feedback — agents leave notes about kai itself.

The compound-interest substrate. Every agent using kai is a sensor for kai's
own gaps: missing subcommands, contract drift between underlying tools,
surprising behavior, wins worth keeping. A first-class capture surface so
signal doesn't escape into session logs nobody reads.

Storage: one markdown file per entry under <cockpit>/feedback/,
named `<YYYY-MM-DDTHHMMSS>-<kind>-<slug>.md`.

Lineage auto-capture (best-effort, never crashes): cwd, git repo + branch +
status, kai version, python version. Captured at write time and frozen in
the body — later git changes don't lose context.

Kinds:
  miss     — wanted kai to do X, it didn't
  drift    — runbook says X, tool contract requires Y
  surprise — undocumented or counterintuitive behavior
  win      — worked surprisingly well, keep doing it
  noise    — captured AND filtered as low-signal, used to calibrate

NOT in v0:
  - Processing pass over accumulated entries. Earn it by accumulating first.
  - Exit-code hooks (auto-capture on non-zero exit). Manual capture only.
  - Web UI. Local markdown only — same shape as ideas/, meetings/, etc.
"""
from __future__ import annotations

import platform
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from kai import __version__
from kai._paths import ensure_cockpit_root


app = typer.Typer(
    name="feedback",
    help="Capture friction + wins about kai itself. Lineage-aware.",
    invoke_without_command=True,
    no_args_is_help=False,
    add_completion=False,
)

_console = Console()

VALID_KINDS = ("miss", "drift", "surprise", "win", "noise")
KIND_COLORS = {
    "miss": "red",
    "drift": "yellow",
    "surprise": "magenta",
    "win": "green",
    "noise": "dim",
}
KIND_DESCRIPTIONS = {
    "miss": "Wanted kai to do X, it didn't",
    "drift": "Runbook says X, tool contract requires Y",
    "surprise": "Undocumented / counterintuitive behavior",
    "win": "Worked surprisingly well, keep doing it",
    "noise": "Low-signal — captured for calibration",
}


def _feedback_dir() -> Path:
    cockpit = ensure_cockpit_root()
    d = cockpit / "feedback"
    d.mkdir(exist_ok=True)
    return d


def _slugify(text: str, max_len: int = 32) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"[\s-]+", "-", s)
    return s[:max_len].rstrip("-") or "entry"


def _git_capture(cwd: Path) -> dict:
    """Best-effort git lineage. Returns {} if not a git repo or git missing."""
    try:
        def run(args: list[str]) -> str:
            return subprocess.run(
                args, capture_output=True, text=True, cwd=cwd, timeout=2
            ).stdout.strip()

        repo = run(["git", "rev-parse", "--show-toplevel"])
        if not repo:
            return {}
        return {
            "repo": repo,
            "branch": run(["git", "branch", "--show-current"]),
            "status": run(["git", "status", "--short"]),
        }
    except Exception:
        return {}


def _parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    fm: dict = {}
    for line in text[3:end].strip().split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm


def _add(kind: str, text: str) -> None:
    feedback_dir = _feedback_dir()
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y-%m-%dT%H%M%S")
    slug = _slugify(text)
    filename = f"{ts}-{kind}-{slug}.md"
    path = feedback_dir / filename

    cwd = Path.cwd()
    git = _git_capture(cwd)

    git_status_block = ""
    if git.get("status"):
        git_status_block = f"\n  ```\n{git['status']}\n  ```"

    body = (
        f"---\n"
        f"kind: {kind}\n"
        f"status: open\n"
        f"ts: {now.isoformat(timespec='seconds')}\n"
        f"slug: {slug}\n"
        f"---\n\n"
        f"# {text}\n\n"
        f"## Lineage (frozen at write)\n\n"
        f"- **cwd:** `{cwd}`\n"
        f"- **git repo:** `{git.get('repo', '—')}`\n"
        f"- **git branch:** `{git.get('branch', '—')}`\n"
        f"- **git status:**{git_status_block or ' (clean or not a git repo)'}\n"
        f"- **kai:** `{__version__}`\n"
        f"- **python:** `{platform.python_version()}`\n\n"
        f"## Notes\n\n"
        f"_(add detail here if needed)_\n"
    )
    path.write_text(body)

    color = KIND_COLORS[kind]
    _console.print()
    _console.print(f"[{color} bold]{kind}[/{color} bold]: {text}")
    cockpit_parent = ensure_cockpit_root().parent
    _console.print(f"[dim]→ {path.relative_to(cockpit_parent)}[/dim]")
    _console.print()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        _show_help()


def _show_help() -> None:
    _console.print()
    _console.print("[bold]kai feedback[/bold] — friction + wins about kai itself")
    _console.print()
    _console.print("Kinds:")
    for kind in VALID_KINDS:
        color = KIND_COLORS[kind]
        _console.print(f"  [bold {color}]{kind:<9}[/bold {color}] {KIND_DESCRIPTIONS[kind]}")
    _console.print()
    _console.print("Commands:")
    _console.print('  [bold]<kind>[/bold] "<text>"   Capture a new entry of that kind')
    _console.print("  [bold]list[/bold]            List all feedback entries")
    _console.print("  [bold]show[/bold] <slug>     Show one entry's body")
    _console.print()
    _console.print(f"[dim]Storage: {_feedback_dir()}/[/dim]")
    _console.print()


@app.command("miss")
def cmd_miss(text: str):
    """Wanted kai to do X, it didn't."""
    _add("miss", text)


@app.command("drift")
def cmd_drift(text: str):
    """Runbook says X, tool contract requires Y."""
    _add("drift", text)


@app.command("surprise")
def cmd_surprise(text: str):
    """Undocumented or counterintuitive behavior."""
    _add("surprise", text)


@app.command("win")
def cmd_win(text: str):
    """Worked surprisingly well, keep doing it."""
    _add("win", text)


@app.command("noise")
def cmd_noise(text: str):
    """Captured AND filtered as low-signal, used to calibrate."""
    _add("noise", text)


@app.command("list")
def cmd_list():
    """List all feedback entries (newest first)."""
    feedback_dir = _feedback_dir()
    entries = sorted(feedback_dir.glob("*.md"), reverse=True)
    if not entries:
        _console.print("[dim]No feedback entries yet. Try `kai feedback miss \"...\"`.[/dim]")
        return

    table = Table(show_header=True, header_style="bold cyan", box=None)
    table.add_column("Slug", style="bold", overflow="fold")
    table.add_column("Kind")
    table.add_column("Status", style="dim")
    table.add_column("Title", overflow="fold")

    for entry in entries:
        fm = _parse_frontmatter(entry.read_text())
        kind = fm.get("kind", "?")
        color = KIND_COLORS.get(kind, "white")
        title = entry.read_text().split("\n# ", 1)[-1].split("\n", 1)[0] if "\n# " in entry.read_text() else entry.stem
        table.add_row(
            entry.stem,
            f"[{color}]{kind}[/{color}]",
            fm.get("status", "?"),
            title,
        )
    _console.print(table)


@app.command("show")
def cmd_show(slug: str):
    """Show one entry's body. Pass any unique substring of the filename."""
    feedback_dir = _feedback_dir()
    matches = list(feedback_dir.glob(f"*{slug}*.md"))
    if not matches:
        _console.print(f"[red]no feedback entry matches: {slug}[/red]")
        raise typer.Exit(1)
    if len(matches) > 1:
        _console.print(f"[yellow]multiple matches; showing newest[/yellow]")
    path = sorted(matches, reverse=True)[0]
    _console.print(path.read_text())
