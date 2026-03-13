"""
Diff — compare current machine state vs saved snapshot.
Shows added, removed, and modified items.
"""

from __future__ import annotations

from rich.console import Console

from imprint.collectors import (
    dotfiles as dotfiles_collector,
    packages as packages_collector,
    vscode as vscode_collector,
)
from imprint.config import ImprintConfig
from imprint.manifest import Manifest
from imprint.utils.safety import filter_safe_files

console = Console()


def run_diff(config: ImprintConfig) -> None:
    """Compare current machine state vs saved snapshot.

    Args:
        config: Imprint configuration.
    """
    manifest_path = config.manifest_path
    if not manifest_path.exists():
        console.print("[yellow]No snapshot found. Run 'imp snapshot' first.[/yellow]")
        return

    manifest = Manifest.load(manifest_path)
    snapshot_at = manifest.meta.get("snapshot_at", "unknown")

    console.print(
        f"\n[bold purple]🔏 Imprint Diff[/bold purple]"
        f" — Changes since last snapshot ({snapshot_at})\n"
    )
    console.print("━" * 60)

    total_changes = 0

    # ── Dotfiles ─────────────────────────────────────────────────
    console.print("\n[bold]DOTFILES[/bold]")
    current_dotfiles = dotfiles_collector.collect(config.home_dir)
    safe_current = filter_safe_files(
        current_dotfiles, config.imprintignore_path, config.home_dir
    )
    current_names = {f.name for f in safe_current}
    saved_names = set(manifest.dotfiles)

    added_dotfiles = current_names - saved_names
    removed_dotfiles = saved_names - current_names
    unchanged_dotfiles = current_names & saved_names

    for name in sorted(added_dotfiles):
        console.print(f"  [green]+[/green]  {name:<25} [green]Added[/green]")
        total_changes += 1
    for name in sorted(removed_dotfiles):
        console.print(f"  [red]-[/red]  {name:<25} [red]Removed[/red]")
        total_changes += 1
    for name in sorted(unchanged_dotfiles):
        # Check if modified by comparing file content
        saved_file = config.dotfiles_dir / name
        current_file = config.home_dir / name
        if saved_file.exists() and current_file.exists():
            try:
                if saved_file.read_bytes() != current_file.read_bytes():
                    console.print(f"  [yellow]✏[/yellow]  {name:<25} [yellow]Modified[/yellow]")
                    total_changes += 1
                else:
                    console.print(f"  [green]✔[/green]  {name:<25} Unchanged")
            except (PermissionError, OSError):
                console.print(f"  [green]✔[/green]  {name:<25} Unchanged")

    # ── VS Code Extensions ───────────────────────────────────────
    console.print("\n[bold]VS CODE EXTENSIONS[/bold]")
    current_vscode = vscode_collector.collect()
    current_exts = set(current_vscode.get("extensions", []))
    saved_exts = set(manifest.vscode.get("extensions", []))

    added_exts = current_exts - saved_exts
    removed_exts = saved_exts - current_exts

    for ext in sorted(added_exts):
        console.print(f"  [green]+[/green]  {ext:<35} [green]Added[/green]")
        total_changes += 1
    for ext in sorted(removed_exts):
        console.print(f"  [red]-[/red]  {ext:<35} [red]Removed[/red]")
        total_changes += 1
    if not added_exts and not removed_exts:
        console.print("  [green]✔[/green]  No changes")

    # ── Packages (pip) ───────────────────────────────────────────
    console.print("\n[bold]PACKAGES (pip)[/bold]")
    current_packages = packages_collector.collect()

    current_pip = set(current_packages.get("pip", {}).get("packages", []))
    saved_pip_data = manifest.packages.get("pip", {})
    saved_pip = set(saved_pip_data.get("packages", []) if isinstance(saved_pip_data, dict) else [])

    added_pip = current_pip - saved_pip
    removed_pip = saved_pip - current_pip

    for pkg in sorted(added_pip):
        console.print(f"  [green]+[/green]  {pkg:<35} [green]Added[/green]")
        total_changes += 1
    for pkg in sorted(removed_pip):
        console.print(f"  [red]-[/red]  {pkg:<35} [red]Removed[/red]")
        total_changes += 1
    if not added_pip and not removed_pip:
        console.print("  [green]✔[/green]  No changes")

    # ── Packages (npm) ───────────────────────────────────────────
    console.print("\n[bold]PACKAGES (npm)[/bold]")
    current_npm = set(current_packages.get("npm", {}).get("packages", []))
    saved_npm_data = manifest.packages.get("npm", {})
    saved_npm = set(saved_npm_data.get("packages", []) if isinstance(saved_npm_data, dict) else [])

    added_npm = current_npm - saved_npm
    removed_npm = saved_npm - current_npm

    for pkg in sorted(added_npm):
        console.print(f"  [green]+[/green]  {pkg:<35} [green]Added[/green]")
        total_changes += 1
    for pkg in sorted(removed_npm):
        console.print(f"  [red]-[/red]  {pkg:<35} [red]Removed[/red]")
        total_changes += 1
    if not added_npm and not removed_npm:
        console.print("  [green]✔[/green]  No changes")

    # ── Summary ──────────────────────────────────────────────────
    console.print(f"\n[bold]SUMMARY[/bold]")
    console.print(
        f"  {len(added_dotfiles)} dotfiles added | {len(removed_dotfiles)} removed"
        f" | {len(added_exts)} extensions added | {len(removed_exts)} removed"
        f" | {len(added_pip) + len(added_npm)} pkg changes"
    )

    if total_changes > 0:
        console.print(
            "\n  [bold]Run 'imp update' to save these changes to your snapshot.[/bold]"
        )
    else:
        console.print("\n  [green]✨ Everything is in sync![/green]")
    console.print()
