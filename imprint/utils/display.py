"""
Rich console display helpers for Imprint.
"""

from __future__ import annotations

from rich.console import Console
from rich.table import Table
from rich.theme import Theme

# Custom theme for consistent colors
IMPRINT_THEME = Theme(
    {
        "imprint.brand": "bold purple",
        "imprint.success": "bold green",
        "imprint.warning": "bold yellow",
        "imprint.error": "bold red",
        "imprint.info": "bold blue",
        "imprint.dim": "dim",
    }
)

console = Console(theme=IMPRINT_THEME)


def print_header(text: str) -> None:
    """Print a branded header."""
    console.print(f"\n[imprint.brand]{text}[/imprint.brand]\n")


def print_success(text: str) -> None:
    console.print(f"[imprint.success]✅ {text}[/imprint.success]")


def print_warning(text: str) -> None:
    console.print(f"[imprint.warning]⚠  {text}[/imprint.warning]")


def print_error(text: str) -> None:
    console.print(f"[imprint.error]✗  {text}[/imprint.error]")


def print_info(text: str) -> None:
    console.print(f"[imprint.info]{text}[/imprint.info]")


def print_step(symbol: str, text: str, status: str = "ok") -> None:
    """Print a step result with colored symbol."""
    colour = "green" if status == "ok" else "yellow" if status == "skipped" else "red"
    sym = "✓" if status == "ok" else "⚠" if status == "skipped" else "✗"
    console.print(f"  [{colour}]{sym}[/{colour}]  {text}")


def make_summary_table(
    title: str, results: list[tuple[str, str, str]]
) -> Table:
    """Create a Rich summary table.

    Args:
        title: Table title.
        results: List of (item, status, detail) tuples.
    """
    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("Item", style="cyan")
    table.add_column("Status")
    table.add_column("Detail", style="dim")

    for item, status, detail in results:
        if status == "ok":
            table.add_row(item, "[green]✓ Restored[/green]", detail)
        elif status == "skipped":
            table.add_row(item, "[yellow]⚠ Skipped[/yellow]", detail)
        else:
            table.add_row(item, "[red]✗ Failed[/red]", detail)

    return table
