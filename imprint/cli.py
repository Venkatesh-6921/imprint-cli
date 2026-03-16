"""
Imprint CLI v2 — Gemini CLI-style terminal experience.
"""

from __future__ import annotations

import click
from rich.text import Text

from imprint import __version__
from imprint.config import ImprintConfig
from imprint.utils.display import (
    console,
    print_logo,
    print_tips,
    print_status_bar,
    print_command_header,
    step_ok,
    step_warn,
    step_error,
    step_info,
    divider,
)


# ── Root group ────────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="Imprint")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """
    \b
    🔏 Imprint — Stamp your developer environment on any machine.

    \b
    Commands:
      imp snapshot   Capture your current environment
      imp restore    Restore your environment on a new machine
      imp diff       See what has changed since your last snapshot
      imp update     Snapshot + push in one command
      imp status     Show what Imprint is tracking
    """
    if ctx.invoked_subcommand is None:
        # No subcommand — show logo + tips (like `gemini` with no args)
        print_logo()
        print_tips()
        print_status_bar(version=__version__)


# ── snapshot ──────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--no-push", is_flag=True, default=False, help="Don't push to GitHub after snapshot")
@click.option("--include-vscode/--no-vscode", default=True, help="Include VS Code extensions")
@click.option("--include-packages/--no-packages", default=True, help="Include installed packages")
def snapshot(no_push: bool, include_vscode: bool, include_packages: bool) -> None:
    """Capture your complete developer environment."""
    config = ImprintConfig.load()

    push = not no_push
    if push and not config.github_repo:
        console.print()
        console.print(
            "  [yellow]>[/yellow]  [bold]No GitHub repository configured.[/bold]"
        )
        console.print(
            "      [dim]Create an empty private repo on GitHub first,[/dim]"
        )
        console.print(
            "      [dim]e.g.[/dim]  [cyan]https://github.com/you/my-imprint-config[/cyan]\n"
        )
        repo_url = click.prompt(
            "  GitHub repo URL (leave empty to skip)",
            default="",
            show_default=False,
        )
        if repo_url.strip():
            config.github_repo = repo_url.strip()
            config.save()
            step_ok("Saved!", f"Future snapshots → {config.github_repo}")
            console.print()
        else:
            push = False
            step_warn("Skipping GitHub push.", "Set it later in ~/.imprint/config.toml")
            console.print()

    from imprint.snapshot import run_snapshot
    run_snapshot(config, push=push)


# ── restore ───────────────────────────────────────────────────────────────────

@cli.command()
@click.argument("source", required=False)
@click.option("--dry-run", is_flag=True, default=False, help="Show what would be restored without doing it")
def restore(source: str | None, dry_run: bool) -> None:
    """
    Restore your developer environment on a new machine.

    SOURCE can be a GitHub URL (https://github.com/you/imprint-config)
    or omit it to restore from ~/.imprint/ directly.
    """
    config = ImprintConfig.load()
    if dry_run:
        step_warn("Dry run mode — no changes will be made.")
        console.print()
    from imprint.restore import run_restore
    run_restore(config, source=source)


# ── diff ──────────────────────────────────────────────────────────────────────

@cli.command()
def diff() -> None:
    """Show what has changed since your last snapshot."""
    config = ImprintConfig.load()
    from imprint.diff import run_diff
    run_diff(config)


# ── update ────────────────────────────────────────────────────────────────────

@cli.command()
def update() -> None:
    """Snapshot current state and push to GitHub."""
    config = ImprintConfig.load()
    from imprint.snapshot import run_snapshot
    run_snapshot(config, push=True)
    console.print()
    step_ok("Environment updated and pushed to GitHub.")


# ── status ────────────────────────────────────────────────────────────────────

@cli.command()
def status() -> None:
    """Show what Imprint is currently tracking."""
    config = ImprintConfig.load()
    manifest_path = config.manifest_path

    print_command_header("imp status", "Overview of tracked environment")

    if not manifest_path.exists():
        step_warn("No snapshot found.", "Run  imp snapshot  first.")
        console.print()
        return

    from imprint.manifest import Manifest
    m = Manifest.load(manifest_path)

    total_pkgs = sum(
        len(v.get("packages", v if isinstance(v, list) else []))
        for v in m.packages.values()
    )

    from rich.table import Table
    table = Table(show_header=False, border_style="bright_black", padding=(0, 2), expand=False)
    table.add_column("Key", style="dim", no_wrap=True)
    table.add_column("Value", style="white")

    table.add_row("Last snapshot",  m.meta.get("snapshot_at", "unknown"))
    table.add_row("Machine",        m.meta.get("hostname", "unknown"))
    table.add_row("OS",             f"{m.meta.get('os','?')} {m.meta.get('os_version','')}")
    table.add_row("Python",         m.system.get("python_version", "unknown"))
    table.add_row("Node",           m.system.get("node_version", "N/A"))
    table.add_row("Dotfiles",       f"[bright_green]{len(m.dotfiles)}[/bright_green] files")
    table.add_row("VS Code exts",   f"[bright_green]{len(m.vscode.get('extensions', []))}[/bright_green] extensions")
    table.add_row("Packages",       f"[bright_green]{total_pkgs}[/bright_green] total")
    table.add_row("Custom scripts", f"[bright_green]{len(m.scripts)}[/bright_green] files")

    console.print(table)
    console.print()
    console.print(
        "  [dim]Run[/dim]  [cyan]imp diff[/cyan]  [dim]to see what changed since this snapshot.[/dim]"
    )
    console.print()


# ── entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    cli()


if __name__ == "__main__":
    main()
