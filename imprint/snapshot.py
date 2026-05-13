"""
Snapshot v3 — adds neovim, cursor, tmux, ssh_config collectors.
Progress bar with percentages.
"""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from imprint.collectors import (
    cursor as cursor_collector,
)
from imprint.collectors import (
    dotfiles as dotfiles_collector,
)
from imprint.collectors import (
    git_config as git_collector,
)
from imprint.collectors import (
    neovim as neovim_collector,
)
from imprint.collectors import (
    packages as packages_collector,
)
from imprint.collectors import (
    scripts as scripts_collector,
)
from imprint.collectors import (
    shell as shell_collector,
)
from imprint.collectors import (
    ssh_config as ssh_config_collector,
)
from imprint.collectors import (
    system as system_collector,
)
from imprint.collectors import (
    tmux as tmux_collector,
)
from imprint.collectors import (
    vscode as vscode_collector,
)
from imprint.config import ImprintConfig
from imprint.manifest import Manifest
from imprint.utils.display import (
    console,
    divider,
    make_snapshot_progress,
    print_command_header,
    step_error,
    step_info,
    step_ok,
)
from imprint.utils.safety import filter_safe_files

_COLLECTORS = [
    "System info",
    "Dotfiles",
    "VS Code",
    "Packages",
    "Shell config",
    "Git config",
    "Scripts",
    "Neovim",
    "Cursor IDE",
    "Tmux",
    "SSH config",
]


def run_snapshot(
    config: ImprintConfig,
    push: bool = True,
    include_vscode: bool = True,
    include_packages: bool = True,
) -> Path:
    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )
    snapshot_dir = config.snapshots_dir / timestamp
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    print_command_header(
        "imp snapshot",
        f"Profile: {config.profile}"
        "  ·  Capturing environment...",
    )

    manifest = Manifest()
    manifest.set_meta(
        timestamp, profile=config.profile
    )

    progress = make_snapshot_progress()
    total = len(_COLLECTORS)
    main_task = progress.add_task(
        "[imp.dim]Collecting...[/imp.dim]",
        total=total,
    )

    def _tick(label: str) -> None:
        progress.update(
            main_task,
            description=f"[imp.dim]{label}[/imp.dim]",
            advance=1,
        )

    with progress:
        # 1. System
        _tick("Detecting system info...")
        manifest.system = system_collector.collect()

        # 2. Dotfiles
        _tick("Collecting dotfiles...")
        found = dotfiles_collector.collect(
            config.home_dir
        )
        safe = filter_safe_files(
            found,
            config.imprintignore_path,
            config.home_dir,
        )
        config.dotfiles_dir.mkdir(
            parents=True, exist_ok=True
        )
        for src in safe:
            shutil.copy2(
                src, config.dotfiles_dir / src.name
            )
        manifest.dotfiles = [f.name for f in safe]

        # 3. VS Code
        _tick("VS Code extensions...")
        if include_vscode:
            vscode_data = vscode_collector.collect()
            manifest.vscode = vscode_data
            settings_path = vscode_data.get(
                "settings_path"
            )
            if settings_path:
                src = Path(settings_path)
                if src.exists():
                    shutil.copy2(
                        src,
                        config.dotfiles_dir
                        / "vscode_settings.json",
                    )

        # 4. Packages
        _tick("Installed packages...")
        if include_packages:
            manifest.packages = (
                packages_collector.collect()
            )

        # 5. Shell
        _tick("Shell config...")
        manifest.shell = shell_collector.collect(
            config.home_dir
        )

        # 6. Git
        _tick("Git config...")
        manifest.git = git_collector.collect(
            config.home_dir
        )

        # 7. Scripts
        _tick("~/bin scripts...")
        bin_scripts = scripts_collector.collect(
            config.home_dir
        )
        safe_scripts = filter_safe_files(
            bin_scripts,
            config.imprintignore_path,
            config.home_dir,
        )
        config.scripts_dir.mkdir(
            parents=True, exist_ok=True
        )
        for src in safe_scripts:
            shutil.copy2(
                src, config.scripts_dir / src.name
            )
        manifest.scripts = [
            f.name for f in safe_scripts
        ]

        # 8. Neovim
        _tick("Neovim config...")
        manifest.neovim = neovim_collector.collect(
            config.home_dir
        )

        # 9. Cursor IDE
        _tick("Cursor IDE...")
        manifest.cursor = cursor_collector.collect()

        # 10. Tmux
        _tick("Tmux config...")
        manifest.tmux = tmux_collector.collect(
            config.home_dir
        )

        # 11. SSH config (safe — no keys)
        _tick("SSH config (safe)...")
        manifest.ssh_config = (
            ssh_config_collector.collect(
                config.home_dir
            )
        )

    # Save manifest
    manifest.save(config.manifest_path)
    shutil.copy2(
        config.manifest_path,
        snapshot_dir / "environment.toml",
    )

    # Summary
    console.print()
    divider("snapshot complete")
    from rich.table import Table

    table = Table(
        show_header=False,
        border_style="imp.border",
        padding=(0, 2),
        expand=False,
    )
    table.add_column("", style="imp.dim", no_wrap=True)
    table.add_column("", style="#eceff4")

    total_pkgs = sum(
        len(
            v.get("packages", [])
            if isinstance(v, dict) else []
        )
        for v in manifest.packages.values()
    )
    table.add_row(
        "Dotfiles",
        (
            f"[imp.success]"
            f"{len(manifest.dotfiles)}"
            f"[/imp.success]"
        ),
    )
    exts = manifest.vscode.get("extensions", [])
    table.add_row(
        "VS Code",
        (
            f"[imp.success]{len(exts)}"
            f"[/imp.success] extensions"
        ),
    )
    table.add_row(
        "Packages",
        (
            f"[imp.success]{total_pkgs}"
            f"[/imp.success] total"
        ),
    )
    table.add_row(
        "Scripts",
        (
            f"[imp.success]"
            f"{len(manifest.scripts)}"
            f"[/imp.success]"
        ),
    )
    nvim_plugins = manifest.neovim.get("plugins", [])
    table.add_row(
        "Neovim",
        (
            f"[imp.success]{len(nvim_plugins)}"
            f"[/imp.success] plugins"
        ),
    )
    table.add_row(
        "Profile",
        manifest.meta.get("profile", "default"),
    )
    table.add_row(
        "Saved to",
        f"[imp.dim]{config.imprint_dir}[/imp.dim]",
    )
    console.print(table)

    # Encrypt if configured
    if config.encrypt and config.key_path.exists():
        console.print()
        step_info(
            "Encrypting dotfiles before push..."
        )
        try:
            from imprint.crypto import encrypt_dir

            count = encrypt_dir(
                config.dotfiles_dir, config.key_path
            )
            step_ok(f"Encrypted {count} files.")
        except Exception as e:
            step_error("Encryption failed", str(e))

    # Push
    if push and config.github_repo:
        console.print()
        step_info(
            "Pushing to GitHub...",
            config.github_repo,
        )
        try:
            from imprint.utils.git import (
                push_to_github,
            )

            push_to_github(
                config.imprint_dir,
                config.github_repo,
                branch=config.github_branch,
            )
            step_ok("Pushed!", config.github_repo)
        except Exception as e:
            step_error("Push failed", str(e))

    console.print()
    step_ok(
        "Snapshot complete!",
        "Run  imp diff  anytime to see what changed.",
    )
    console.print()

    return snapshot_dir
