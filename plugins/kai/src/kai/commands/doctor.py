"""kai doctor — pre-flight check.

Verifies each underlying tool kai dispatches to is on PATH and callable.
Returns non-zero exit if any required tool is missing.

Storage: none — read-only inspection.

NOT in v0:
  - Network checks (e.g. railguey can reach Railway). That's `kai pipeline`'s
    job — a multi-stage flow check, not just presence.
  - Auto-fix. Prints what's missing; user installs.
  - Tool version compatibility. Just presence today.
  - $PATH diagnostics. If `which` says it's there, we trust it.
"""
from __future__ import annotations

import shutil
from dataclasses import dataclass

import typer
from rich.console import Console
from rich.table import Table


app = typer.Typer(
    name="doctor",
    help="Pre-flight check — verify your tools are reachable.",
    invoke_without_command=True,
    no_args_is_help=False,
    add_completion=False,
)

_console = Console()


@dataclass
class Tool:
    name: str
    description: str
    required: bool


TOOLS: list[Tool] = [
    Tool("git",           "git CLI — needed for lineage capture",                  True),
    Tool("railguey",      "Railway deploys (kai deploy)",                          False),
    Tool("ike",           "Tasks + milestones (kai plan)",                         False),
    Tool("cept",          "LLM escalation (kai llm)",                              False),
    Tool("visionlog",     "Vision + ADRs (kai vision)",                            False),
    Tool("research-md",   "Decisions with evidence (kai decide)",                  False),
    Tool("forge-forge",   "Scaffolders (kai forge)",                               False),
    Tool("resume-resume", "Session resume (kai session)",                          False),
    Tool("claudoctor",    "Claude Code health (kai session)",                      False),
    Tool("lighthouse",    "Memory + orient (kai orient)",                          False),
    Tool("hone",          "Memory polish (kai orient)",                            False),
    Tool("scribe",        "Devlog (kai orient)",                                   False),
    Tool("space-hog",     "Disk audit (kai disk)",                                 False),
    Tool("apple-a-day",   "macOS health (kai disk)",                               False),
]


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        run_check()


@app.command("check")
def cmd_check():
    """Run the pre-flight check (default action when you run `kai doctor`)."""
    run_check()


def run_check() -> None:
    table = Table(
        title="kai doctor — pre-flight",
        show_header=True,
        header_style="bold cyan",
        title_style="bold",
    )
    table.add_column("Tool", style="bold")
    table.add_column("Status")
    table.add_column("Path", style="dim", overflow="fold")
    table.add_column("Note", style="dim", overflow="fold")

    missing_required = 0
    missing_optional = 0
    present = 0

    for tool in TOOLS:
        path = shutil.which(tool.name)
        if path:
            status = "[green]✓ present[/green]"
            present += 1
        elif tool.required:
            status = "[red]✗ MISSING (required)[/red]"
            missing_required += 1
        else:
            status = "[yellow]○ not installed[/yellow]"
            missing_optional += 1
        table.add_row(tool.name, status, path or "—", tool.description)

    _console.print()
    _console.print(table)
    _console.print()
    _console.print(
        f"[green]{present} present[/green] · "
        f"[yellow]{missing_optional} optional missing[/yellow] · "
        f"[red]{missing_required} required missing[/red]"
    )
    _console.print()

    if missing_required:
        _console.print("[red bold]Required tools missing. Install before kai will be useful.[/red bold]")
        raise typer.Exit(1)
