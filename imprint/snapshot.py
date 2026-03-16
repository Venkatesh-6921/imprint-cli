"""
Snapshot — capture the current developer environment.
Gemini CLI-style Rich output: live progress, styled panels.
"""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

from imprint.collectors import (
    dotfiles as dotfiles_collector,
    git_config as git_collector,
    packages as packages_collector,
    scripts as scripts_collector,
    shell as shell_collector,
    system as system_collector,
    vscode as vscode_collector,
)
from imprint.config import ImprintConfig
from imprint.manifest import Manifest
from imprint.utils.display import (
    console,
    divider,
    print_command_header,
    step_ok,
    step_info,
    step_error,
)
from imprint.utils.safety import filter_safe_files


def run_snapshot(config: ImprintConfig, push: bool = True) -> Path:
    """Full snapshot of the current machine's developer environment.

    Args:
        config: Imprint configuration.
        push: Whether to push to GitHub.

    Returns:
        Path to the snapshot directory.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    snapshot_dir = config.snapshots_dir / timestamp
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    print_command_header(
        "imp snapshot",
        "Capturing your complete developer environment...",
    )

    manifest = Manifest()
    manifest.set_meta(timestamp)

    # ── Collectors ────────────────────────────────────────────────────────────
    progress = Progress(
        SpinnerColumn(spinner_name="dots", style="bright_green"),
        TextColumn("  [progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    )

    with progress:
        # 1. System info
        t = progress.add_task("[dim]Detecting system info...[/dim]", total=None)
        manifest.system = system_collector.collect()
        progress.update(t, description="[bright_green]✓[/bright_green]  System info")
        progress.stop_task(t)

        # 2. Dotfiles
        t = progress.add_task("[dim]Collecting dotfiles...[/dim]", total=None)
        found = dotfiles_collector.collect(config.home_dir)
        safe = filter_safe_files(found, config.imprintignore_path, config.home_dir)
        config.dotfiles_dir.mkdir(parents=True, exist_ok=True)
        for src in safe:
            shutil.copy2(src, config.dotfiles_dir / src.name)
        manifest.dotfiles = [f.name for f in safe]
        progress.update(t, description=f"[bright_green]✓[/bright_green]  Dotfiles  [dim]({len(safe)} files)[/dim]")
        progress.stop_task(t)

        # 3. VS Code
        t = progress.add_task("[dim]Collecting VS Code extensions...[/dim]", total=None)
        vscode_data = vscode_collector.collect()
        manifest.vscode = vscode_data
        if vscode_data.get("settings_path"):
            src_settings = Path(vscode_data["settings_path"])
            if src_settings.exists():
                shutil.copy2(src_settings, config.dotfiles_dir / "vscode_settings.json")
        n_ext = len(vscode_data.get("extensions", []))
        progress.update(t, description=f"[bright_green]✓[/bright_green]  VS Code  [dim]({n_ext} extensions)[/dim]")
        progress.stop_task(t)

        # 4. Packages
        t = progress.add_task("[dim]Collecting installed packages...[/dim]", total=None)
        packages_data = packages_collector.collect()
        manifest.packages = packages_data
        total_pkgs = sum(
            len(v.get("packages", []) if isinstance(v, dict) else [])
            for v in packages_data.values()
        )
        progress.update(t, description=f"[bright_green]✓[/bright_green]  Packages  [dim]({total_pkgs} total)[/dim]")
        progress.stop_task(t)

        # 5. Shell
        t = progress.add_task("[dim]Detecting shell config...[/dim]", total=None)
        shell_data = shell_collector.collect(config.home_dir)
        manifest.shell = shell_data
        shell_type = shell_data.get("type", "unknown")
        progress.update(t, description=f"[bright_green]✓[/bright_green]  Shell  [dim]({shell_type})[/dim]")
        progress.stop_task(t)

        # 6. Git config
        t = progress.add_task("[dim]Reading Git config...[/dim]", total=None)
        git_data = git_collector.collect(config.home_dir)
        manifest.git = git_data
        progress.update(t, description="[bright_green]✓[/bright_green]  Git config")
        progress.stop_task(t)

        # 7. Scripts
        t = progress.add_task("[dim]Collecting ~/bin scripts...[/dim]", total=None)
        bin_scripts = scripts_collector.collect(config.home_dir)
        safe_scripts = filter_safe_files(bin_scripts, config.imprintignore_path, config.home_dir)
        config.scripts_dir.mkdir(parents=True, exist_ok=True)
        for src in safe_scripts:
            shutil.copy2(src, config.scripts_dir / src.name)
        manifest.scripts = [f.name for f in safe_scripts]
        progress.update(t, description=f"[bright_green]✓[/bright_green]  Scripts  [dim]({len(safe_scripts)} files)[/dim]")
        progress.stop_task(t)

    # ── Save manifest ─────────────────────────────────────────────────────────
    manifest.save(config.manifest_path)
    shutil.copy2(config.manifest_path, snapshot_dir / "environment.toml")

    # ── Summary ───────────────────────────────────────────────────────────────
    console.print()
    divider("snapshot complete")

    from rich.table import Table
    table = Table(show_header=False, border_style="bright_black", padding=(0, 2), expand=False)
    table.add_column("", style="dim", no_wrap=True)
    table.add_column("", style="white")
    table.add_row("Dotfiles",    f"[bright_green]{len(manifest.dotfiles)}[/bright_green] files")
    table.add_row("VS Code",     f"[bright_green]{len(manifest.vscode.get('extensions', []))}[/bright_green] extensions")
    table.add_row("Packages",    f"[bright_green]{total_pkgs}[/bright_green] total")
    table.add_row("Scripts",     f"[bright_green]{len(manifest.scripts)}[/bright_green] custom scripts")
    table.add_row("Saved to",    f"[dim]{config.imprint_dir}[/dim]")
    console.print(table)

    # ── GitHub push ───────────────────────────────────────────────────────────
    if push and config.github_repo:
        console.print()
        step_info("Pushing to GitHub...", config.github_repo)
        try:
            from imprint.utils.git import push_to_github
            push_to_github(config.imprint_dir, config.github_repo)
            step_ok("Pushed!", config.github_repo)
        except Exception as e:
            step_error("Push failed", str(e))

    console.print()
    console.print(
        "  [bright_green]✓[/bright_green]  [bold]Snapshot complete![/bold]  "
        "[dim]Run[/dim]  [cyan]imp diff[/cyan]  [dim]anytime to see what changed.[/dim]"
    )
    console.print()

    return snapshot_dir
