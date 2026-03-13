"""
Imprint CLI entry point.
All user-facing commands are defined here using Click.
"""

from __future__ import annotations

import click
from rich.console import Console

from imprint import __version__
from imprint.config import ImprintConfig

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="Imprint")
def cli() -> None:
    """
    🔏 Imprint — Stamp your developer environment on any machine.

    Commands:\n
      imp snapshot   Capture your current environment\n
      imp restore    Restore your environment on a new machine\n
      imp diff       See what has changed since your last snapshot\n
      imp update     Snapshot + push in one command\n
      imp status     Show what Imprint is tracking
    """


@cli.command()
@click.option(
    "--no-push",
    is_flag=True,
    default=False,
    help="Don't push to GitHub after snapshot",
)
@click.option(
    "--include-vscode/--no-vscode",
    default=True,
    help="Include VS Code extensions",
)
@click.option(
    "--include-packages/--no-packages",
    default=True,
    help="Include installed packages",
)
def snapshot(no_push: bool, include_vscode: bool, include_packages: bool) -> None:
    """Capture your complete developer environment."""
    config = ImprintConfig.load()

    # If pushing is enabled but no GitHub repo is configured, ask the user
    push = not no_push
    if push and not config.github_repo:
        console.print(
            "\n[bold yellow]🔗 No GitHub repository configured.[/bold yellow]"
        )
        console.print(
            "   To push snapshots to GitHub, enter your repo URL below."
        )
        console.print(
            "   [dim](Create an empty private repo on GitHub first,"
            " e.g. https://github.com/you/my-imprint-config)[/dim]"
        )
        repo_url = click.prompt(
            "\n  GitHub repo URL (leave empty to skip)",
            default="",
            show_default=False,
        )
        if repo_url.strip():
            config.github_repo = repo_url.strip()
            config.save()
            console.print(
                f"[green]✅ Saved! Future snapshots will push to:"
                f" {config.github_repo}[/green]\n"
            )
        else:
            push = False
            console.print(
                "[dim]  Skipping GitHub push. You can set it later in"
                " ~/.imprint/config.toml[/dim]\n"
            )

    from imprint.snapshot import run_snapshot

    run_snapshot(config, push=push)


@cli.command()
@click.argument("source", required=False)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Show what would be restored without doing it",
)
def restore(source: str | None, dry_run: bool) -> None:
    """
    Restore your developer environment on a new machine.

    SOURCE can be a GitHub URL (https://github.com/you/imprint-config)
    or omit it to restore from ~/.imprint/ directly.
    """
    config = ImprintConfig.load()
    if dry_run:
        console.print("[yellow]Dry run mode — no changes will be made.[/yellow]")
    from imprint.restore import run_restore

    run_restore(config, source=source)


@cli.command()
def diff() -> None:
    """Show what has changed since your last snapshot."""
    config = ImprintConfig.load()
    from imprint.diff import run_diff

    run_diff(config)


@cli.command()
def update() -> None:
    """Snapshot current state and push to GitHub."""
    config = ImprintConfig.load()
    from imprint.snapshot import run_snapshot

    run_snapshot(config, push=True)
    console.print("[green]✅ Environment updated and pushed.[/green]")


@cli.command()
def status() -> None:
    """Show what Imprint is currently tracking."""
    config = ImprintConfig.load()
    manifest_path = config.manifest_path
    if not manifest_path.exists():
        console.print("[yellow]No snapshot found. Run 'imp snapshot' first.[/yellow]")
        return

    from imprint.manifest import Manifest

    manifest = Manifest.load(manifest_path)
    console.print(f"\n[bold purple]🔏 Imprint Status[/bold purple]")
    console.print(f"   Last snapshot:   {manifest.meta.get('snapshot_at', 'unknown')}")
    console.print(f"   Machine:         {manifest.meta.get('hostname', 'unknown')}")
    console.print(
        f"   OS:              {manifest.meta.get('os', 'unknown')}"
        f" {manifest.meta.get('os_version', '')}"
    )
    console.print(f"   Python:          {manifest.system.get('python_version', 'unknown')}")
    console.print(f"   Node:            {manifest.system.get('node_version', 'N/A')}")
    console.print(f"   Dotfiles:        {len(manifest.dotfiles)} files")
    console.print(
        f"   VS Code:         {len(manifest.vscode.get('extensions', []))} extensions"
    )
    total_pkgs = sum(
        len(v.get("packages", v if isinstance(v, list) else []))
        for v in manifest.packages.values()
    )
    console.print(f"   Packages:        {total_pkgs} total")
    console.print(f"   Custom scripts:  {len(manifest.scripts)} files\n")


def main() -> None:
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
