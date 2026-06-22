"""kai — internal multitool entry point.

καί (Greek): "and" — the conjunction that joins.
解 (Japanese): "to solve, to unravel."
開 / 开: "to open, to begin."

Three surfaces:
  1. Operational subcommands — deploy / doctor (substrate)
  2. Capture surfaces — ideas / feedback (compound interest)
  3. Domain dispatchers — `kai <domain>` for grouped commands

NOT in v0:
  - Public release. Internal use only; pipx-from-clone for now.
  - Plugin system. Subcommands are static imports today.
  - Per-pilot routing. Single shared cockpit until there's a reason.
"""
from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from kai import __version__
from kai._usage import log_invocation
from kai.commands import deploy, doctor, feedback, ideas, login, ops, slack

ROOT_HELP = """\
kai is a progressive-reveal CLI. Orient before you operate.

\b
  1. SESSION CHECK → `kai doctor` (verify your tools are reachable).
  2. DEPLOY → `kai deploy <service>` (Railway via railguey).
  3. CAPTURE IDEA → `kai ideas add "<title>"` to capture without committing.
     Don't forget; don't roadmap yet. Lineage:
     ideas → research-md → visionlog → ike → ship.
  4. LEAVE FEEDBACK → `kai feedback miss "..."` for frictions about kai itself.
     Five kinds: miss / drift / surprise / win / noise.
  5. PROCESS CHECK → `kai ops guardrails` before platform provisioning.
  6. UNSURE WHAT TO RUN → bare `kai` lists all domains; `kai <domain>` drills in.

\b
Domains:
  deploy · doctor · ideas · feedback · decide · plan · vision · forge ·
  session · disk · orient · llm · mcp

καί (Greek): "and" — the conjunction that joins.
"""


app = typer.Typer(
    name="kai",
    help=ROOT_HELP,
    invoke_without_command=True,
    no_args_is_help=False,
    add_completion=False,
)

app.add_typer(deploy.app,   name="deploy",   help="Railway deploys (railguey)")
app.add_typer(doctor.app,   name="doctor",   help="Pre-flight check — tools on PATH")
app.add_typer(ideas.app,    name="ideas",    help="Pre-roadmap idea hopper")
app.add_typer(feedback.app, name="feedback", help="Friction + wins about kai itself")
app.command("login", help="Bootstrap a platform secret to Eidos Vault")(login.login_cmd)
app.add_typer(ops.app,      name="ops",      help="Founder-ops guardrails and routing")
app.add_typer(slack.app,    name="slack",    help="Operate in Slack — read, write, manage, admin")

console = Console()

DOMAINS: list[tuple[str, str, str]] = [
    ("deploy",   "Railway deploys (railguey)",                 "active"),
    ("doctor",   "Pre-flight check — tools on PATH",           "active"),
    ("ideas",    "Pre-roadmap idea hopper",                    "active"),
    ("feedback", "Capture friction about kai itself",          "active"),
    ("login",    "Acquire a platform secret to Eidos Vault",   "active"),
    ("ops",      "Founder-ops guardrails and routing",         "active"),
    ("slack",    "Operate in Slack (read/write/manage/admin)", "active"),
    ("decide",   "Decisions with evidence (research-md)",      "planned"),
    ("plan",     "Tasks and milestones (ike)",                 "planned"),
    ("vision",   "Vision, ADRs, guardrails (visionlog)",       "planned"),
    ("forge",    "Scaffolders (forge-forge family)",           "planned"),
    ("session",  "Session resume (resume-resume, claudoctor)", "planned"),
    ("disk",     "Disk + system (space-hog, apple-a-day)",     "planned"),
    ("orient",   "Memory + orient (lighthouse, hone, scribe)", "planned"),
    ("llm",      "LLM escalation (cept)",                      "planned"),
    ("mcp",      "MCP servers (cockpit-mcp, eidos-mcp)",       "planned"),
]


def _version_callback(value: bool):
    if value:
        console.print(f"kai {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False, "--version", "-v",
        callback=_version_callback, is_eager=True,
        help="Show version and exit.",
    ),
):
    """Top-level callback. Logs invocation and shows banner if no subcommand."""
    sub = ctx.invoked_subcommand
    log_invocation(f"kai {sub}" if sub else "kai")
    if sub is None:
        _show_banner()


def _show_banner() -> None:
    console.print()
    console.print("[bold]kai[/bold] — internal multitool for Daniel kai Vybhav")
    console.print("[dim]καί (Greek): \"and\" — the conjunction that joins.[/dim]")
    console.print()
    console.print("[bold]Orient before you operate.[/bold]")
    console.print()
    console.print("  [bold]1.[/bold] SESSION CHECK → [cyan]kai doctor[/cyan]")
    console.print("  [bold]2.[/bold] DEPLOY → [cyan]kai deploy <service>[/cyan]")
    console.print("  [bold]3.[/bold] CAPTURE IDEA → [cyan]kai ideas add \"<title>\"[/cyan]")
    console.print("  [bold]4.[/bold] LEAVE FEEDBACK → [cyan]kai feedback miss \"...\"[/cyan]")
    console.print("  [bold]5.[/bold] PROCESS CHECK → [cyan]kai ops guardrails[/cyan]")
    console.print("  [bold]6.[/bold] UNSURE WHAT TO RUN → bare [cyan]kai[/cyan] lists domains")
    console.print()
    console.print("  Lineage: [dim]ideas → research-md → visionlog → ike → ship[/dim]")
    console.print()

    table = Table(show_header=True, header_style="bold cyan", box=None, pad_edge=False)
    table.add_column("Domain", style="bold")
    table.add_column("Description")
    table.add_column("Status", style="dim")
    for name, desc, status in DOMAINS:
        style = "green" if status == "active" else "dim"
        table.add_row(name, desc, f"[{style}]{status}[/{style}]")
    console.print(table)
    console.print()
