"""
Restore — restore a complete developer environment on a new machine.
Gemini CLI-style UI: numbered steps, clean progress, summary table.
"""

from __future__ import annotations

from pathlib import Path

from imprint.config import ImprintConfig
from imprint.installers import (
    dotfiles as dotfiles_installer,
    packages as packages_installer,
    scripts as scripts_installer,
    shell as shell_installer,
    vscode as vscode_installer,
)
from imprint.manifest import Manifest
from imprint.utils.display import (
    console,
    divider,
    make_summary_table,
    print_command_header,
    step_error,
    step_info,
    step_ok,
    step_warn,
)


def _section(n: int, total: int, label: str) -> None:
    console.print(f"\n  [dim]{n}/{total}[/dim]  [bold]{label}[/bold]")


def run_restore(config: ImprintConfig, source: str | None = None) -> None:
    """Restore developer environment from GitHub repo or local path."""

    print_command_header(
        "imp restore",
        "Restoring your complete developer environment...",
    )

    # ── Resolve source ────────────────────────────────────────────────────────
    imprint_dir = config.imprint_dir

    if source and source.startswith("https://github.com"):
        step_info("Cloning config repo...", source)
        try:
            from imprint.utils.git import clone_repo
            imprint_dir = clone_repo(source, config.imprint_dir)
            step_ok("Cloned!", str(imprint_dir))
        except Exception as e:
            step_error("Clone failed", str(e))
            return
    elif source:
        imprint_dir = Path(source)

    if not imprint_dir.exists():
        step_error(
            "No imprint config found.",
            "Run  imp snapshot  first or provide a GitHub URL.",
        )
        console.print()
        return

    manifest_path = imprint_dir / "environment.toml"
    if not manifest_path.exists():
        step_error("environment.toml not found", str(imprint_dir))
        return

    manifest = Manifest.load(manifest_path)
    dotfiles_dir = imprint_dir / "dotfiles"
    scripts_dir  = imprint_dir / "scripts"

    results: list[tuple[str, str, str]] = []
    TOTAL = 6

    # ── 1: Dotfiles ───────────────────────────────────────────────────────────
    _section(1, TOTAL, "Symlinking dotfiles")
    if manifest.dotfiles:
        dotfile_results = dotfiles_installer.install(
            dotfiles_dir, config.home_dir, manifest.dotfiles
        )
        for name, status, detail in dotfile_results:
            results.append((f"dotfile: {name}", status, detail))
            if status == "ok":
                step_ok(name, detail)
            elif status == "skipped":
                step_warn(name, detail)
            else:
                step_error(name, detail)
    else:
        step_warn("No dotfiles in manifest")

    # ── 2: VS Code ────────────────────────────────────────────────────────────
    _section(2, TOTAL, "Installing VS Code extensions")
    extensions = manifest.vscode.get("extensions", [])
    if extensions:
        vscode_results = vscode_installer.install(extensions)
        installed_count = sum(1 for _, s, _ in vscode_results if s == "ok")
        step_ok(
            f"{installed_count}/{len(extensions)} extensions installed",
        )
        results.append(("VS Code extensions", "ok", f"{installed_count}/{len(extensions)}"))
    else:
        step_warn("No VS Code extensions in manifest")

    # ── 3: System packages ────────────────────────────────────────────────────
    _section(3, TOTAL, "Installing system packages")
    sys_pkg_data = manifest.packages.get("system", {})
    sys_pkgs = sys_pkg_data.get("packages", []) if isinstance(sys_pkg_data, dict) else []
    if sys_pkgs:
        manager = sys_pkg_data.get("manager", "apt") if isinstance(sys_pkg_data, dict) else "apt"
        sys_results = packages_installer.install_system(sys_pkgs, manager)
        step_ok("System packages install triggered", f"{len(sys_pkgs)} packages via {manager}")
        results.extend(sys_results)
    else:
        step_warn("No system packages in manifest")

    # ── 4: pip ────────────────────────────────────────────────────────────────
    _section(4, TOTAL, "Installing pip packages")
    pip_data = manifest.packages.get("pip", {})
    pip_pkgs = pip_data.get("packages", []) if isinstance(pip_data, dict) else []
    if pip_pkgs:
        packages_installer.install_pip(pip_pkgs)
        step_ok(f"{len(pip_pkgs)} pip packages installed")
        results.append(("pip packages", "ok", f"{len(pip_pkgs)} packages"))
    else:
        step_warn("No pip packages in manifest")

    # ── 5: npm ────────────────────────────────────────────────────────────────
    _section(5, TOTAL, "Installing npm packages")
    npm_data = manifest.packages.get("npm", {})
    npm_pkgs = npm_data.get("packages", []) if isinstance(npm_data, dict) else []
    if npm_pkgs:
        packages_installer.install_npm(npm_pkgs)
        step_ok(f"{len(npm_pkgs)} npm packages installed")
        results.append(("npm packages", "ok", f"{len(npm_pkgs)} packages"))
    else:
        step_warn("No npm packages in manifest")

    # ── 6: Scripts + Shell ────────────────────────────────────────────────────
    _section(6, TOTAL, "Restoring ~/bin scripts & shell config")
    if manifest.scripts:
        scripts_installer.install(scripts_dir, config.home_dir / "bin", manifest.scripts)
        step_ok(f"{len(manifest.scripts)} scripts restored to ~/bin")
        results.append(("scripts", "ok", f"{len(manifest.scripts)} scripts"))
    if manifest.shell:
        shell_installer.install(manifest.shell)
        step_ok("Shell config applied")

    # ── Summary ───────────────────────────────────────────────────────────────
    console.print()
    divider()
    table = make_summary_table("Restore Summary", results)
    console.print(table)

    ok_count = sum(1 for _, s, _ in results if s == "ok")
    console.print()
    console.print(
        f"  [bright_green]✓[/bright_green]  [bold]Done![/bold]  "
        f"[dim]{ok_count}/{len(results)} items restored.[/dim]"
    )
    console.print(
        "  [dim]Run[/dim]  [cyan]source ~/.zshrc[/cyan]  "
        "[dim]or restart your terminal to activate shell changes.[/dim]"
    )
    console.print()
