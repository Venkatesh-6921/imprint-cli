"""
Imprint v3 — Rich display helpers.
Upgraded theme: Nord-inspired palette, richer components, live progress.
"""

from __future__ import annotations

import platform
import socket
from datetime import datetime

from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

# ── Theme ─────────────────────────────────────────────────────────────────────

IMPRINT_THEME = Theme(
    {
        # Brand
        "imp.brand":    "bold #88c0d0",       # Nord frost blue
        "imp.accent":   "bold #a3be8c",        # Nord green
        "imp.logo1":    "#88c0d0",
        "imp.logo2":    "#81a1c1",
        # State
        "imp.success":  "#a3be8c",
        "imp.warn":     "#ebcb8b",
        "imp.error":    "bold #bf616a",
        "imp.info":     "#88c0d0",
        # Diff
        "imp.add":      "#a3be8c",
        "imp.remove":   "#bf616a",
        "imp.modify":   "#ebcb8b",
        "imp.same":     "dim",
        # Misc
        "imp.dim":      "dim",
        "imp.cmd":      "bold #88c0d0",
        "imp.head":     "bold #b48ead",
        "imp.border":   "#4c566a",
        "imp.hl":       "#eceff4",
    }
)

console = Console(theme=IMPRINT_THEME)


# ── ASCII Logo ─────────────────────────────────────────────────────────────────

_LOGO_LINES = [
    "  ██╗███╗   ███╗██████╗ ██████╗ ██╗███╗   ██╗████████╗",
    "  ██║████╗ ████║██╔══██╗██╔══██╗██║████╗  ██║╚══██╔══╝",
    "  ██║██╔████╔██║██████╔╝██████╔╝██║██╔██╗ ██║   ██║   ",
    "  ██║██║╚██╔╝██║██╔═══╝ ██╔══██╗██║██║╚██╗██║   ██║   ",
    "  ██║██║ ╚═╝ ██║██║     ██║  ██║██║██║ ╚████║   ██║   ",
    "  ╚═╝╚═╝     ╚═╝╚═╝     ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝   ╚═╝  ",
]

_LOGO_ALTS = [
    "imp.logo1", "imp.logo1", "imp.logo2",
    "imp.logo2", "imp.logo1", "imp.logo1",
]


def print_logo() -> None:
    console.print()
    for line, style in zip(_LOGO_LINES, _LOGO_ALTS):
        console.print(f"[{style}]{line}[/{style}]")
    console.print(
        "  [imp.dim]v3.0.0  ·  Stamp your dev environment"
        " on any machine[/imp.dim]"
    )
    console.print()


# ── Dashboard (replaces old print_tips) ──────────────────────────────────────

def print_dashboard(
    version: str, profile: str = "default"
) -> None:
    """Full `imp` no-args dashboard — two-panel layout."""
    try:
        hostname = socket.gethostname()
    except Exception:
        hostname = "localhost"
    os_name = platform.system()
    now = datetime.now().strftime("%Y-%m-%d  %H:%M")

    # Left panel — commands
    cmd_text = Text()
    cmd_text.append("Quick commands\n\n", style="bold #eceff4")
    cmds = [
        ("imp snapshot",         "Capture full environment"),
        ("imp restore <url>",    "Restore on a new machine"),
        ("imp diff",             "What changed since snapshot"),
        ("imp update",           "Snapshot + push in one step"),
        ("imp init",             "First-run interactive wizard"),
        ("imp doctor",           "Health check & diagnostics"),
        ("imp history",          "Browse past snapshots"),
        ("imp export --fmt md",  "Export env as Markdown report"),
        ("imp profile use work", "Switch to named profile"),
        ("imp compare s1 s2",    "Diff two snapshots"),
    ]
    for cmd, desc in cmds:
        cmd_text.append(f"  {cmd:<28}", style="imp.cmd")
        cmd_text.append(f"{desc}\n", style="imp.dim")

    left = Panel(
        cmd_text,
        border_style="imp.border",
        padding=(0, 1),
        title="[imp.brand]commands[/imp.brand]",
    )

    # Right panel — machine info
    info_table = Table(
        show_header=False, box=None, padding=(0, 1)
    )
    info_table.add_column("k", style="imp.dim", no_wrap=True)
    info_table.add_column("v", style="#eceff4")
    info_table.add_row("machine",  hostname)
    info_table.add_row("os",       os_name)
    info_table.add_row("version",  f"imprint v{version}")
    info_table.add_row(
        "profile",
        f"[imp.accent]{profile}[/imp.accent]",
    )
    info_table.add_row("time",     now)

    right = Panel(
        info_table,
        border_style="imp.border",
        padding=(0, 1),
        title="[imp.brand]machine[/imp.brand]",
    )

    console.print(
        Columns([left, right], equal=True, expand=True)
    )
    console.print()


def print_status_bar(
    version: str = "3.0.0", profile: str = "default"
) -> None:
    try:
        hostname = socket.gethostname()
    except Exception:
        hostname = "localhost"
    now = datetime.now().strftime("%H:%M")
    bar = Text()
    bar.append("  ~/.imprint", style="imp.dim")
    bar.append("  ·  ", style="imp.border")
    bar.append(hostname, style="imp.dim")
    bar.append("  ·  ", style="imp.border")
    bar.append(f"profile:{profile}", style="imp.accent")
    bar.append("  ·  ", style="imp.border")
    bar.append(f"imprint v{version}", style="imp.brand")
    bar.append(f"  ·  {now}", style="imp.dim")
    console.print(bar)
    console.print()


# ── Section headers ──────────────────────────────────────────────────────────

def print_command_header(
    title: str, subtitle: str = ""
) -> None:
    content = Text()
    content.append("  ❯ ", style="imp.accent bold")
    content.append(title, style="bold #eceff4")
    if subtitle:
        content.append(f"\n    {subtitle}", style="imp.dim")
    console.print(
        Panel(content, border_style="imp.accent", padding=(0, 1))
    )
    console.print()


# ── Step printers ─────────────────────────────────────────────────────────────

def step_ok(label: str, detail: str = "") -> None:
    d = f"  [imp.dim]{detail}[/imp.dim]" if detail else ""
    console.print(
        f"  [imp.success]✓[/imp.success]  {label}{d}"
    )


def step_warn(label: str, detail: str = "") -> None:
    d = f"  [imp.dim]{detail}[/imp.dim]" if detail else ""
    console.print(
        f"  [imp.warn]⚠[/imp.warn]  {label}{d}"
    )


def step_error(label: str, detail: str = "") -> None:
    d = f"  [imp.dim]{detail}[/imp.dim]" if detail else ""
    console.print(
        f"  [imp.error]✗[/imp.error]  {label}{d}"
    )


def step_info(label: str, detail: str = "") -> None:
    d = f"  [imp.dim]{detail}[/imp.dim]" if detail else ""
    console.print(
        f"  [imp.info]→[/imp.info]  {label}{d}"
    )


# ── Divider ───────────────────────────────────────────────────────────────────

def divider(label: str = "") -> None:
    if label:
        console.rule(
            f"[imp.dim]{label}[/imp.dim]",
            style="imp.border",
        )
    else:
        console.rule(style="imp.border")
    console.print()


# ── Diff helpers ──────────────────────────────────────────────────────────────

def diff_add(name: str, note: str = "added") -> None:
    console.print(
        f"  [imp.add]+[/imp.add]  "
        f"[imp.add]{name:<46}[/imp.add]  "
        f"[imp.dim]{note}[/imp.dim]"
    )


def diff_remove(name: str, note: str = "removed") -> None:
    console.print(
        f"  [imp.remove]-[/imp.remove]  "
        f"[imp.remove]{name:<46}[/imp.remove]  "
        f"[imp.dim]{note}[/imp.dim]"
    )


def diff_modify(name: str, note: str = "modified") -> None:
    console.print(
        f"  [imp.modify]~[/imp.modify]  "
        f"[imp.modify]{name:<46}[/imp.modify]  "
        f"[imp.dim]{note}[/imp.dim]"
    )


def diff_same(name: str) -> None:
    console.print(
        f"  [imp.same]=[/imp.same]  "
        f"[imp.same]{name:<46}  unchanged[/imp.same]"
    )


# ── Summary table ─────────────────────────────────────────────────────────────

def make_summary_table(
    title: str, results: list[tuple[str, str, str]]
) -> Table:
    table = Table(
        title=Text(title, style="bold #eceff4"),
        show_header=True,
        header_style="imp.brand",
        border_style="imp.border",
        show_lines=False,
        padding=(0, 2),
    )
    table.add_column("Item", style="#eceff4", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("Detail", style="imp.dim")

    for item, status, detail in results:
        if status == "ok":
            table.add_row(
                item,
                "[imp.success]✓  ok[/imp.success]",
                detail,
            )
        elif status == "skipped":
            table.add_row(
                item,
                "[imp.warn]⚠  skipped[/imp.warn]",
                detail,
            )
        else:
            table.add_row(
                item,
                "[imp.error]✗  failed[/imp.error]",
                detail,
            )
    return table


# ── Snapshot progress factory ─────────────────────────────────────────────────

def make_snapshot_progress() -> Progress:
    return Progress(
        SpinnerColumn(
            spinner_name="dots2", style="imp.accent"
        ),
        TextColumn(
            "  [progress.description]{task.description}"
        ),
        BarColumn(
            bar_width=22,
            style="imp.border",
            complete_style="imp.accent",
        ),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    )


# ── History timeline ──────────────────────────────────────────────────────────

def print_snapshot_timeline(
    snapshots: list[dict],
) -> None:
    """Print a timeline table of past snapshots.

    Args:
        snapshots: list of dicts with keys: timestamp,
            hostname, dotfiles, packages, vscode.
    """
    if not snapshots:
        step_warn(
            "No snapshots found.",
            "Run  imp snapshot  first.",
        )
        return

    table = Table(
        title=Text("Snapshot History", style="bold #eceff4"),
        show_header=True,
        header_style="imp.brand",
        border_style="imp.border",
        padding=(0, 2),
    )
    table.add_column(
        "#", justify="right", style="imp.dim", width=4
    )
    table.add_column(
        "Timestamp", style="#eceff4", no_wrap=True
    )
    table.add_column("Machine", style="imp.dim")
    table.add_column(
        "Dotfiles", justify="right", style="imp.info"
    )
    table.add_column(
        "Packages", justify="right", style="imp.info"
    )
    table.add_column(
        "VSCode", justify="right", style="imp.info"
    )

    for i, s in enumerate(reversed(snapshots), 1):
        table.add_row(
            str(i),
            s.get("timestamp", "—"),
            s.get("hostname", "—"),
            str(s.get("dotfiles", "—")),
            str(s.get("packages", "—")),
            str(s.get("vscode", "—")),
        )
    console.print(table)
    console.print()
