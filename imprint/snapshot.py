"""
Snapshot — capture the current developer environment.
Orchestrates all collectors, builds manifest, copies files, pushes to GitHub.
"""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

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
from imprint.utils.safety import filter_safe_files

console = Console()


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

    console.print(
        "\n[bold purple]⚡ Imprint Snapshot[/bold purple]"
        " — Capturing your developer environment\n"
    )

    manifest = Manifest()
    manifest.set_meta(timestamp)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:

        # 1. System info
        task = progress.add_task("📋  Detecting system info...", total=None)
        manifest.system = system_collector.collect()
        progress.update(task, description="[green]✓  System info[/green]")

        # 2. Dotfiles
        task = progress.add_task("📁  Collecting dotfiles...", total=None)
        found_dotfiles = dotfiles_collector.collect(config.home_dir)
        safe_dotfiles = filter_safe_files(
            found_dotfiles, config.imprintignore_path, config.home_dir
        )
        config.dotfiles_dir.mkdir(parents=True, exist_ok=True)
        for src_path in safe_dotfiles:
            dest = config.dotfiles_dir / src_path.name
            shutil.copy2(src_path, dest)
        manifest.dotfiles = [f.name for f in safe_dotfiles]
        progress.update(
            task,
            description=f"[green]✓  Dotfiles ({len(safe_dotfiles)} files)[/green]",
        )

        # 3. VS Code
        task = progress.add_task("🧩  Collecting VS Code extensions...", total=None)
        vscode_data = vscode_collector.collect()
        manifest.vscode = vscode_data
        if vscode_data.get("settings_path"):
            settings_src = Path(vscode_data["settings_path"])
            if settings_src.exists():
                shutil.copy2(settings_src, config.dotfiles_dir / "vscode_settings.json")
        progress.update(
            task,
            description=(
                f"[green]✓  VS Code"
                f" ({len(vscode_data.get('extensions', []))} extensions)[/green]"
            ),
        )

        # 4. Packages
        task = progress.add_task("📦  Collecting installed packages...", total=None)
        packages_data = packages_collector.collect()
        manifest.packages = packages_data
        total_pkgs = sum(
            len(v.get("packages", []) if isinstance(v, dict) else [])
            for v in packages_data.values()
        )
        progress.update(
            task,
            description=f"[green]✓  Packages ({total_pkgs} total)[/green]",
        )

        # 5. Shell
        task = progress.add_task("🐚  Detecting shell config...", total=None)
        shell_data = shell_collector.collect(config.home_dir)
        manifest.shell = shell_data
        progress.update(
            task,
            description=f"[green]✓  Shell ({shell_data.get('type', 'unknown')})[/green]",
        )

        # 6. Git config
        task = progress.add_task("🔧  Reading Git config...", total=None)
        git_data = git_collector.collect(config.home_dir)
        manifest.git = git_data
        progress.update(task, description="[green]✓  Git config[/green]")

        # 7. Custom scripts
        task = progress.add_task("📜  Collecting ~/bin scripts...", total=None)
        bin_scripts = scripts_collector.collect(config.home_dir)
        safe_scripts = filter_safe_files(
            bin_scripts, config.imprintignore_path, config.home_dir
        )
        config.scripts_dir.mkdir(parents=True, exist_ok=True)
        for src_path in safe_scripts:
            shutil.copy2(src_path, config.scripts_dir / src_path.name)
        manifest.scripts = [f.name for f in safe_scripts]
        progress.update(
            task,
            description=f"[green]✓  Scripts ({len(safe_scripts)} files)[/green]",
        )

    # Save manifest
    manifest.save(config.manifest_path)
    shutil.copy2(config.manifest_path, snapshot_dir / "environment.toml")

    # Summary
    console.print()
    console.print("[bold green]✅ Snapshot complete![/bold green]")
    console.print(f"   Dotfiles:    {len(manifest.dotfiles)} files")
    console.print(f"   VS Code:     {len(manifest.vscode.get('extensions', []))} extensions")
    console.print(f"   Packages:    {total_pkgs} packages")
    console.print(f"   Scripts:     {len(manifest.scripts)} custom scripts")
    console.print(f"   Saved to:    {config.imprint_dir}")

    if push and config.github_repo:
        console.print("\n[bold blue]📤 Pushing to GitHub...[/bold blue]")
        from imprint.utils.git import push_to_github

        push_to_github(config.imprint_dir, config.github_repo)
        console.print(f"[green]✓  Pushed to {config.github_repo}[/green]")

    return snapshot_dir
