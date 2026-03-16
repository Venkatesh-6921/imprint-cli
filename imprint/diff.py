"""
Diff — compare current machine state vs saved snapshot.
Gemini CLI-style: git-diff inspired output with +/-/~ markers.
"""

from __future__ import annotations

from imprint.collectors import (
    dotfiles as dotfiles_collector,
    packages as packages_collector,
    vscode as vscode_collector,
)
from imprint.config import ImprintConfig
from imprint.manifest import Manifest
from imprint.utils.display import (
    console,
    diff_add,
    diff_modify,
    diff_remove,
    diff_same,
    divider,
    print_command_header,
    step_ok,
    step_warn,
)
from imprint.utils.safety import filter_safe_files


def _section_header(label: str) -> None:
    console.print(f"\n  [bold cyan]{label}[/bold cyan]")
    console.print(f"  [bright_black]{'─' * 50}[/bright_black]")


def run_diff(config: ImprintConfig) -> None:
    """Compare current machine state vs saved snapshot.

    Args:
        config: Imprint configuration.
    """
    if not config.manifest_path.exists():
        step_warn("No snapshot found.", "Run  imp snapshot  first.")
        console.print()
        return

    manifest = Manifest.load(config.manifest_path)
    snapshot_at = manifest.meta.get("snapshot_at", "unknown")

    print_command_header(
        "imp diff",
        f"Changes since last snapshot  ({snapshot_at})",
    )

    total_changes = 0

    # ── Dotfiles ──────────────────────────────────────────────────────────────
    _section_header("DOTFILES")
    current_dotfiles = dotfiles_collector.collect(config.home_dir)
    safe_current = filter_safe_files(current_dotfiles, config.imprintignore_path, config.home_dir)
    current_names = {f.name for f in safe_current}
    saved_names   = set(manifest.dotfiles)

    added_df   = current_names - saved_names
    removed_df = saved_names   - current_names
    common_df  = current_names & saved_names

    for name in sorted(added_df):
        diff_add(name)
        total_changes += 1
    for name in sorted(removed_df):
        diff_remove(name)
        total_changes += 1

    for name in sorted(common_df):
        saved_file   = config.dotfiles_dir / name
        current_file = config.home_dir / name
        if saved_file.exists() and current_file.exists():
            try:
                if saved_file.read_bytes() != current_file.read_bytes():
                    diff_modify(name)
                    total_changes += 1
                else:
                    diff_same(name)
            except (PermissionError, OSError):
                diff_same(name)

    if not added_df and not removed_df and not any(
        (config.dotfiles_dir / n).exists() and (config.home_dir / n).exists() and
        (config.dotfiles_dir / n).read_bytes() != (config.home_dir / n).read_bytes()
        for n in common_df
    ):
        console.print("  [dim]  no changes[/dim]")

    # ── VS Code ───────────────────────────────────────────────────────────────
    _section_header("VS CODE EXTENSIONS")
    current_vscode = vscode_collector.collect()
    current_exts   = set(current_vscode.get("extensions", []))
    saved_exts     = set(manifest.vscode.get("extensions", []))

    added_ext   = current_exts - saved_exts
    removed_ext = saved_exts   - current_exts

    for ext in sorted(added_ext):
        diff_add(ext)
        total_changes += 1
    for ext in sorted(removed_ext):
        diff_remove(ext)
        total_changes += 1
    if not added_ext and not removed_ext:
        console.print("  [dim]  no changes[/dim]")

    # ── pip ───────────────────────────────────────────────────────────────────
    _section_header("PACKAGES  (pip)")
    current_packages = packages_collector.collect()

    current_pip  = set(current_packages.get("pip", {}).get("packages", []))
    saved_pip_d  = manifest.packages.get("pip", {})
    saved_pip    = set(saved_pip_d.get("packages", []) if isinstance(saved_pip_d, dict) else [])

    added_pip   = current_pip - saved_pip
    removed_pip = saved_pip   - current_pip

    for pkg in sorted(added_pip):
        diff_add(pkg)
        total_changes += 1
    for pkg in sorted(removed_pip):
        diff_remove(pkg)
        total_changes += 1
    if not added_pip and not removed_pip:
        console.print("  [dim]  no changes[/dim]")

    # ── npm ───────────────────────────────────────────────────────────────────
    _section_header("PACKAGES  (npm)")
    current_npm  = set(current_packages.get("npm", {}).get("packages", []))
    saved_npm_d  = manifest.packages.get("npm", {})
    saved_npm    = set(saved_npm_d.get("packages", []) if isinstance(saved_npm_d, dict) else [])

    added_npm   = current_npm - saved_npm
    removed_npm = saved_npm   - current_npm

    for pkg in sorted(added_npm):
        diff_add(pkg)
        total_changes += 1
    for pkg in sorted(removed_npm):
        diff_remove(pkg)
        total_changes += 1
    if not added_npm and not removed_npm:
        console.print("  [dim]  no changes[/dim]")

    # ── Summary ───────────────────────────────────────────────────────────────
    console.print()
    divider("summary")

    add_count = len(added_df) + len(added_ext) + len(added_pip) + len(added_npm)
    rem_count = len(removed_df) + len(removed_ext) + len(removed_pip) + len(removed_npm)

    if total_changes > 0:
        parts = []
        if add_count:   parts.append(f"[bright_green]+{add_count} added[/bright_green]")
        if rem_count:   parts.append(f"[red]-{rem_count} removed[/red]")
        mod_count = total_changes - add_count - rem_count
        if mod_count:   parts.append(f"[yellow]~{mod_count} modified[/yellow]")

        console.print("  " + "  ·  ".join(parts))
        console.print()
        console.print(
            "  [dim]Run[/dim]  [cyan]imp update[/cyan]  "
            "[dim]to save these changes to your snapshot.[/dim]"
        )
    else:
        console.print("  [bright_green]✓[/bright_green]  Everything is in sync!")
        console.print(
            "  [dim]No changes since snapshot at[/dim]  [cyan]" + snapshot_at + "[/cyan]"
        )

    console.print()
