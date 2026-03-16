"""
Imprint v2 — Rich display helpers.
Gemini CLI-inspired terminal UI: ASCII logo, tips panel, styled output.
"""

from __future__ import annotations

import platform
import socket
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

# ── Theme ────────────────────────────────────────────────────────────────────

IMPRINT_THEME = Theme(
    {
        "imp.brand":   "bold bright_green",
        "imp.success": "bright_green",
        "imp.warn":    "yellow",
        "imp.error":   "bold red",
        "imp.info":    "cyan",
        "imp.dim":     "dim",
        "imp.cmd":     "bold cyan",
        "imp.add":     "bright_green",
        "imp.remove":  "red",
        "imp.modify":  "yellow",
        "imp.head":    "bold magenta",
    }
)

console = Console(theme=IMPRINT_THEME)


# ── ASCII Logo ────────────────────────────────────────────────────────────────

_LOGO_LINES = [
    "  ██╗███╗   ███╗██████╗ ██████╗ ██╗███╗   ██╗████████╗",
    "  ██║████╗ ████║██╔══██╗██╔══██╗██║████╗  ██║╚══██╔══╝",
    "  ██║██╔████╔██║██████╔╝██████╔╝██║██╔██╗ ██║   ██║   ",
    "  ██║██║╚██╔╝██║██╔═══╝ ██╔══██╗██║██║╚██╗██║   ██║   ",
    "  ██║██║ ╚═╝ ██║██║     ██║  ██║██║██║ ╚████║   ██║   ",
    "  ╚═╝╚═╝     ╚═╝╚═╝     ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝   ╚═╝   ",
]

_LOGO_COLORS = ["bright_green", "bright_green", "cyan", "cyan", "bright_green", "bright_green"]


def print_logo() -> None:
    """Print the big IMPRINT ASCII logo with gradient colors."""
    console.print()
    for line, color in zip(_LOGO_LINES, _LOGO_COLORS):
        console.print(f"[{color}]{line}[/{color}]")
    console.print()


def print_tips() -> None:
    """Print the Gemini CLI-style tips box."""
    tips = Text()
    tips.append("Tips for getting started:\n", style="bold bright_green")
    tip_items = [
        ("imp snapshot", "Capture your full environment on this machine."),
        ("imp restore <url>", "Restore everything on a new machine."),
        ("imp diff", "See what changed since your last snapshot."),
        ("imp --help", "Full list of commands and options."),
    ]
    for i, (cmd, desc) in enumerate(tip_items, 1):
        tips.append(f"  {i}. ", style="dim")
        tips.append(cmd, style="bold cyan")
        tips.append(f"  -  {desc}\n", style="dim")

    console.print(
        Panel(
            tips,
            border_style="bright_green",
            padding=(0, 2),
        )
    )


def print_status_bar(version: str = "2.0.0") -> None:
    """Print the Gemini CLI-style status bar."""
    try:
        hostname = socket.gethostname()
    except Exception:
        hostname = "localhost"
    os_name = platform.system()
    now = datetime.now().strftime("%H:%M")

    bar = Text()
    bar.append(f"  ~/.imprint", style="dim")
    bar.append("  |  ", style="bright_black")
    bar.append(f"{hostname}", style="dim")
    bar.append("  |  ", style="bright_black")
    bar.append(f"{os_name}", style="dim")
    bar.append("  |  ", style="bright_black")
    bar.append(f"imprint v{version}", style="bright_green")
    bar.append(f"  |  {now}", style="dim")

    console.print(bar)
    console.print()


# ── Section headers ───────────────────────────────────────────────────────────

def print_command_header(title: str, subtitle: str = "") -> None:
    """Print a Gemini CLI-style command header."""
    content = Text()
    content.append("  > ", style="bright_green bold")
    content.append(title, style="bold white")
    if subtitle:
        content.append(f"\n    {subtitle}", style="dim")
    console.print(Panel(content, border_style="bright_green", padding=(0, 1)))
    console.print()


# ── Step / result printers ────────────────────────────────────────────────────

def step_ok(label: str, detail: str = "") -> None:
    detail_str = f"  [dim]{detail}[/dim]" if detail else ""
    console.print(f"  [bright_green]✓[/bright_green]  {label}{detail_str}")


def step_warn(label: str, detail: str = "") -> None:
    detail_str = f"  [dim]{detail}[/dim]" if detail else ""
    console.print(f"  [yellow]⚠[/yellow]  {label}{detail_str}")


def step_error(label: str, detail: str = "") -> None:
    detail_str = f"  [dim]{detail}[/dim]" if detail else ""
    console.print(f"  [bold red]✗[/bold red]  {label}{detail_str}")


def step_info(label: str, detail: str = "") -> None:
    detail_str = f"  [dim]{detail}[/dim]" if detail else ""
    console.print(f"  [cyan]→[/cyan]  {label}{detail_str}")


def divider(label: str = "") -> None:
    if label:
        console.rule(f"[dim]{label}[/dim]", style="bright_black")
    else:
        console.rule(style="bright_black")
    console.print()


# ── Diff helpers ──────────────────────────────────────────────────────────────

def diff_add(name: str, note: str = "added") -> None:
    console.print(f"  [bright_green]+[/bright_green]  [bright_green]{name:<42}[/bright_green]  [dim]{note}[/dim]")


def diff_remove(name: str, note: str = "removed") -> None:
    console.print(f"  [red]-[/red]  [red]{name:<42}[/red]  [dim]{note}[/dim]")


def diff_modify(name: str, note: str = "modified") -> None:
    console.print(f"  [yellow]~[/yellow]  [yellow]{name:<42}[/yellow]  [dim]{note}[/dim]")


def diff_same(name: str) -> None:
    console.print(f"  [dim]=[/dim]  [dim]{name:<42}  unchanged[/dim]")


# ── Summary table ─────────────────────────────────────────────────────────────

def make_summary_table(title: str, results: list[tuple[str, str, str]]) -> Table:
    table = Table(
        title=Text(title, style="bold bright_green"),
        show_header=True,
        header_style="bold cyan",
        border_style="bright_black",
        show_lines=False,
        padding=(0, 2),
    )
    table.add_column("Item", style="white", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("Detail", style="dim")

    for item, status, detail in results:
        if status == "ok":
            table.add_row(item, "[bright_green]✓  ok[/bright_green]", detail)
        elif status == "skipped":
            table.add_row(item, "[yellow]⚠  skipped[/yellow]", detail)
        else:
            table.add_row(item, "[red]✗  failed[/red]", detail)

    return table
