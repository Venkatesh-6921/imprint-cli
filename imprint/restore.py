"""
Restore — restore a complete developer environment on a new machine.
Reads environment.toml, installs everything, creates symlinks.
"""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

from imprint.config import ImprintConfig
from imprint.installers import (
    dotfiles as dotfiles_installer,
    packages as packages_installer,
    scripts as scripts_installer,
    shell as shell_installer,
    vscode as vscode_installer,
)
from imprint.manifest import Manifest
from imprint.utils.display import make_summary_table

console = Console()


def run_restore(config: ImprintConfig, source: str | None = None) -> None:
    """Restore developer environment from GitHub repo or local path.

    Args:
        config: Imprint configuration.
        source: GitHub URL or local path. If None, uses ~/.imprint/.
    """
    console.print(
        "\n[bold purple]🔏 Imprint Restore[/bold purple]"
        " — Restoring your developer environment\n"
    )

    # Get the imprint config source
    imprint_dir = config.imprint_dir
    if source and source.startswith("https://github.com"):
        console.print(f"[blue]📥 Cloning config from {source}...[/blue]")
        from imprint.utils.git import clone_repo

        imprint_dir = clone_repo(source, config.imprint_dir)
    elif source:
        imprint_dir = Path(source)

    if not imprint_dir.exists():
        console.print(
            "[red]✗  No imprint config found."
            " Run 'imp snapshot' first or provide a GitHub URL.[/red]"
        )
        return

    # Load manifest
    manifest_path = imprint_dir / "environment.toml"
    if not manifest_path.exists():
        console.print(f"[red]✗  environment.toml not found in {imprint_dir}[/red]")
        return

    manifest = Manifest.load(manifest_path)
    dotfiles_dir = imprint_dir / "dotfiles"
    scripts_dir = imprint_dir / "scripts"

    results: list[tuple[str, str, str]] = []

    # ── Step 1: Dotfiles ─────────────────────────────────────────
    console.print("[bold]1/6  Symlinking dotfiles...[/bold]")
    if manifest.dotfiles:
        dotfile_results = dotfiles_installer.install(
            dotfiles_dir, config.home_dir, manifest.dotfiles
        )
        for name, status, detail in dotfile_results:
            results.append((f"dotfile: {name}", status, detail))
            symbol = "✓" if status == "ok" else "⚠" if status == "skipped" else "✗"
            colour = "green" if status == "ok" else "yellow" if status == "skipped" else "red"
            console.print(f"  [{colour}]{symbol}[/{colour}]  {name} — {detail}")
    else:
        console.print("  [yellow]⚠[/yellow]  No dotfiles in manifest")

    # ── Step 2: VS Code Extensions ───────────────────────────────
    console.print("\n[bold]2/6  Installing VS Code extensions...[/bold]")
    extensions = manifest.vscode.get("extensions", [])
    if extensions:
        vscode_results = vscode_installer.install(extensions)
        installed_count = sum(1 for _, s, _ in vscode_results if s == "ok")
        console.print(
            f"  [green]✓[/green]  {installed_count}/{len(extensions)} extensions installed"
        )
        results.append(("VS Code extensions", "ok", f"{installed_count}/{len(extensions)}"))
    else:
        console.print("  [yellow]⚠[/yellow]  No VS Code extensions in manifest")

    # ── Step 3: System packages ──────────────────────────────────
    console.print("\n[bold]3/6  Installing system packages...[/bold]")
    sys_pkg_data = manifest.packages.get("system", {})
    sys_pkgs = sys_pkg_data.get("packages", []) if isinstance(sys_pkg_data, dict) else []
    if sys_pkgs:
        manager = sys_pkg_data.get("manager", "apt") if isinstance(sys_pkg_data, dict) else "apt"
        sys_results = packages_installer.install_system(sys_pkgs, manager)
        console.print("  [green]✓[/green]  System packages install triggered")
        results.extend(sys_results)
    else:
        console.print("  [yellow]⚠[/yellow]  No system packages in manifest")

    # ── Step 4: pip packages ─────────────────────────────────────
    console.print("\n[bold]4/6  Installing pip packages...[/bold]")
    pip_data = manifest.packages.get("pip", {})
    pip_pkgs = pip_data.get("packages", []) if isinstance(pip_data, dict) else []
    if pip_pkgs:
        packages_installer.install_pip(pip_pkgs)
        console.print(f"  [green]✓[/green]  {len(pip_pkgs)} pip packages installed")
        results.append(("pip packages", "ok", f"{len(pip_pkgs)} packages"))

    # ── Step 5: npm packages ─────────────────────────────────────
    console.print("\n[bold]5/6  Installing npm packages...[/bold]")
    npm_data = manifest.packages.get("npm", {})
    npm_pkgs = npm_data.get("packages", []) if isinstance(npm_data, dict) else []
    if npm_pkgs:
        packages_installer.install_npm(npm_pkgs)
        console.print(f"  [green]✓[/green]  {len(npm_pkgs)} npm packages installed")
        results.append(("npm packages", "ok", f"{len(npm_pkgs)} packages"))

    # ── Step 6: Custom scripts + Shell ───────────────────────────
    console.print("\n[bold]6/6  Restoring ~/bin scripts & shell config...[/bold]")
    if manifest.scripts:
        scripts_installer.install(scripts_dir, config.home_dir / "bin", manifest.scripts)
        console.print(
            f"  [green]✓[/green]  {len(manifest.scripts)} scripts restored to ~/bin"
        )
        results.append(("scripts", "ok", f"{len(manifest.scripts)} scripts"))

    if manifest.shell:
        shell_installer.install(manifest.shell)

    # ── Final summary table ──────────────────────────────────────
    console.print("\n")
    table = make_summary_table("🔏 Imprint Restore Complete", results)
    console.print(table)

    ok_count = sum(1 for _, s, _ in results if s == "ok")
    console.print(f"\n[bold green]Done! {ok_count}/{len(results)} items restored.[/bold green]")
    console.print(
        "[dim]Run 'source ~/.zshrc' or restart your terminal"
        " to activate shell changes.[/dim]\n"
    )
