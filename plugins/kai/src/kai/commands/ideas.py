"""kai ideas — pre-roadmap idea hopper.

Capture-without-commitment scratchpad. Distinct from:
  - kai plan (ike) — concrete tasks
  - kai vision (visionlog) — locked goals + ADRs
  - kai decide (research-md) — decision candidates with evidence

Ideas are the pre-decision holding pen: "don't forget this thought" without
committing to scope, owner, or roadmap.

Storage: one markdown file per idea under <cockpit>/ideas/, named
`<YYYY-MM-DDTHHMMSS>-<slug>.md`.

Promotion: `kai ideas promote <slug>` marks `status: promoted` and SUGGESTS
follow-up actions (create an ike task, lift to research-md candidate, etc).
Promotion does NOT auto-create downstream artifacts — that stays explicit.

NOT in v0:
  - Auto-promotion based on signal frequency. Promotion stays manual.
  - Tag taxonomy. Free-form tags only.
  - Cross-linking to ike tasks. Suggest, don't enforce.
  - Search across body content. List by metadata only.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from kai._paths import ensure_cockpit_root


app = typer.Typer(
    name="ideas",
    help="Capture and review pre-roadmap ideas. Don't forget; don't commit yet.",
    invoke_without_command=True,
    no_args_is_help=False,
    add_completion=False,
)

_console = Console()

VALID_STATUSES = ("open", "promoted", "killed")
STATUS_COLORS = {
    "open": "yellow",
    "promoted": "green",
    "killed": "dim",
}


def _ideas_dir() -> Path:
    cockpit = ensure_cockpit_root()
    d = cockpit / "ideas"
    d.mkdir(exist_ok=True)
    return d


def _slugify(text: str, max_len: int = 32) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"[\s-]+", "-", s)
    return s[:max_len].rstrip("-") or "idea"


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


def _set_frontmatter_field(text: str, field: str, value: str) -> str:
    if not text.startswith("---"):
        return text
    end = text.find("---", 3)
    if end == -1:
        return text
    fm = text[3:end]
    if re.search(rf"^{field}:", fm, re.MULTILINE):
        new_fm = re.sub(rf"^{field}:.*$", f"{field}: {value}", fm, count=1, flags=re.MULTILINE)
    else:
        new_fm = fm.rstrip() + f"\n{field}: {value}\n"
    return f"---{new_fm}---" + text[end + 3:]


def _write(title: str, body: str | None = None) -> Path:
    ideas_dir = _ideas_dir()
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y-%m-%dT%H%M%S")
    slug = _slugify(title)
    filename = f"{ts}-{slug}.md"
    path = ideas_dir / filename

    content = (
        f"---\n"
        f"status: open\n"
        f"ts: {now.isoformat(timespec='seconds')}\n"
        f"slug: {slug}\n"
        f"tags: \n"
        f"---\n\n"
        f"# {title}\n\n"
    )
    if body:
        content += f"{body}\n\n"
    content += "## Why now\n\n_(why this is on your mind right now)_\n\n## What it might enable\n\n_(what becomes possible if this works)_\n\n## What it costs\n\n_(time / scope / dependencies — be honest)_\n"

    path.write_text(content)
    return path


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        _show_help()


def _show_help() -> None:
    _console.print()
    _console.print("[bold]kai ideas[/bold] — pre-roadmap idea hopper")
    _console.print()
    _console.print("Commands:")
    _console.print('  [bold]add[/bold] "<title>"            Full idea entry with structured prompts')
    _console.print('  [bold]note[/bold] "<text>"            Lighter capture — exploration without commitment')
    _console.print("  [bold]list[/bold]                    List all ideas (newest first)")
    _console.print("  [bold]show[/bold] <slug>             Show one idea's body")
    _console.print("  [bold]promote[/bold] <slug>          Mark promoted + print follow-up suggestions")
    _console.print("  [bold]kill[/bold] <slug>             Mark killed (we considered it; no.)")
    _console.print()
    _console.print("[dim]Lineage: ideas → research-md → visionlog → ike → ship[/dim]")
    _console.print()


@app.command("add")
def cmd_add(title: str):
    """Full idea entry with structured prompts (Why now / What enables / What costs)."""
    path = _write(title)
    _console.print()
    _console.print(f"[yellow bold]idea[/yellow bold]: {title}")
    _console.print(f"[dim]→ {path.relative_to(ensure_cockpit_root().parent)}[/dim]")
    _console.print()


@app.command("note")
def cmd_note(text: str):
    """Lighter capture — exploration without commitment. No structured prompts."""
    path = _write(text, body=None)
    # Note variant: strip the structured-prompts boilerplate to keep it light
    content = path.read_text()
    light = content.split("## Why now")[0].rstrip() + "\n"
    path.write_text(light)
    _console.print()
    _console.print(f"[dim]note:[/dim] {text}")
    _console.print(f"[dim]→ {path.relative_to(ensure_cockpit_root().parent)}[/dim]")
    _console.print()


@app.command("list")
def cmd_list(
    status: str = typer.Option(None, "--status", help="Filter by status (open/promoted/killed)"),
):
    """List ideas (newest first). Filter by --status if given."""
    ideas_dir = _ideas_dir()
    entries = sorted(ideas_dir.glob("*.md"), reverse=True)
    if not entries:
        _console.print('[dim]No ideas yet. Try `kai ideas add "your idea here"`.[/dim]')
        return

    table = Table(show_header=True, header_style="bold cyan", box=None)
    table.add_column("Slug", style="bold", overflow="fold")
    table.add_column("Status")
    table.add_column("Date", style="dim")
    table.add_column("Title", overflow="fold")

    shown = 0
    for entry in entries:
        text = entry.read_text()
        fm = _parse_frontmatter(text)
        st = fm.get("status", "open")
        if status and st != status:
            continue
        color = STATUS_COLORS.get(st, "white")
        title_line = ""
        if "\n# " in text:
            title_line = text.split("\n# ", 1)[1].split("\n", 1)[0]
        table.add_row(
            fm.get("slug", entry.stem),
            f"[{color}]{st}[/{color}]",
            fm.get("ts", "?")[:10],
            title_line or entry.stem,
        )
        shown += 1

    if shown == 0:
        _console.print(f"[dim]No ideas matching status={status}.[/dim]")
        return
    _console.print(table)


@app.command("show")
def cmd_show(slug: str):
    """Show one idea's body. Pass any unique substring."""
    ideas_dir = _ideas_dir()
    matches = list(ideas_dir.glob(f"*{slug}*.md"))
    if not matches:
        _console.print(f"[red]no idea matches: {slug}[/red]")
        raise typer.Exit(1)
    if len(matches) > 1:
        _console.print("[yellow]multiple matches; showing newest[/yellow]")
    path = sorted(matches, reverse=True)[0]
    _console.print(path.read_text())


@app.command("promote")
def cmd_promote(slug: str):
    """Mark an idea promoted. Suggests follow-up actions; does NOT auto-create them."""
    path = _resolve_one(slug)
    text = path.read_text()
    new = _set_frontmatter_field(text, "status", "promoted")
    path.write_text(new)
    _console.print()
    _console.print(f"[green bold]promoted[/green bold]: {path.stem}")
    _console.print()
    _console.print("[bold]Suggested follow-ups[/bold] (run manually — promotion does not auto-create):")
    _console.print("  • [cyan]ike task create[/cyan] if it's concrete, scoped work")
    _console.print("  • [cyan]research-md candidate add[/cyan] if it needs evidence before deciding")
    _console.print("  • [cyan]visionlog goal add[/cyan] if it's a real strategic commitment")
    _console.print()


@app.command("kill")
def cmd_kill(slug: str):
    """Mark an idea killed. Keeps the file — preserves the trail of considered-and-rejected."""
    path = _resolve_one(slug)
    text = path.read_text()
    new = _set_frontmatter_field(text, "status", "killed")
    path.write_text(new)
    _console.print()
    _console.print(f"[dim]killed:[/dim] {path.stem}")
    _console.print()


def _resolve_one(slug: str) -> Path:
    ideas_dir = _ideas_dir()
    matches = list(ideas_dir.glob(f"*{slug}*.md"))
    if not matches:
        _console.print(f"[red]no idea matches: {slug}[/red]")
        raise typer.Exit(1)
    if len(matches) > 1:
        _console.print(f"[yellow]multiple matches; using newest[/yellow]")
    return sorted(matches, reverse=True)[0]
