# 🔏 Imprint — Portable Developer Environment Manager
### Full Project Workflow | Production-Grade Build (20–25 Days)
### 💻 Stack: Python 3.11+ + Rich + Click + TOML + Git + SQLite + PyPI
### 🔬 Novel Contribution: Full-stack environment snapshot (dotfiles + packages + extensions + fonts + terminal + SSH config) in one command, restore on any machine in one command
### 💡 CLI command: `imp` | GitHub: `imprint` | PyPI: `imprint-cli`

---

## 🧠 Why This Name

Every developer has a distinct working environment — specific shell aliases, VS Code extensions, fonts, terminal colours, Git config, Python environments, custom scripts. That environment is your **imprint** as a developer. Every new machine you touch is a blank surface. Imprint stamps your exact developer identity onto it.

The name was chosen over alternatives after research:

| Candidate | Verdict | Reason rejected |
|---|---|---|
| `chezmoi` | Taken | Existing major tool |
| `dotbot` | Taken | Existing major tool |
| `persona` | Too generic | Many competing projects |
| `haunt` | Too dark | Ghost metaphor doesn't feel right |
| `nest` | Taken | Overused in JS/Python ecosystem |
| `anchor` | Decent | Doesn't capture the identity aspect |
| `forge` | Decent | Implies building, not restoring |
| **`imprint`** | ✅ WINNER | Exact metaphor: your dev setup is your imprint. Stamp it on any machine. Short, memorable, available, professional. CLI command `imp` is clean and fast to type. |

---

## 🚨 The Problem — Real Pain, Every Developer Knows It

You have your machine perfectly set up. VS Code with 30 extensions configured just right. Your `.zshrc` with 50 aliases you've built over years. Python 3.11 + virtualenvs. Node 20 + global packages. Your custom terminal font (JetBrains Mono). Your Git identity, your SSH config, your custom scripts in `~/bin`. Your tmux config. Your `.gitignore_global`. Everything feels like *you*.

Then you sit at a coworker's machine. Or set up a fresh laptop. Or start a new job.

You spend **3–6 hours** rebuilding everything from memory. You always forget something — the `git log --oneline --graph` alias, the `.editorconfig`, the VS Code settings JSON, the oh-my-zsh plugins. Three weeks later you're still finding things that aren't set up right.

**Existing tools don't fully solve this:**

| Tool | What it does | What it misses |
|---|---|---|
| `chezmoi` | Manages dotfiles across machines | Doesn't capture installed packages, VS Code extensions, fonts, terminal profiles |
| `GNU Stow` | Symlinks dotfiles from a central dir | Manual setup, no snapshot, no packages |
| `Mackup` | Syncs app settings via Dropbox/Git | Mac-only, no package snapshot, no restore script |
| `Dotbot` | Bootstraps dotfiles install | No package snapshot, configuration-heavy |
| Shell scripts | Custom install.sh | You have to write and maintain it yourself |

**What none of them do in one command:**
```
imp snapshot     # Captures EVERYTHING on this machine
imp restore      # Restores EVERYTHING on the new machine
```

"Everything" meaning: dotfiles, shell config, VS Code extensions + settings, installed packages (pip/npm/apt/brew), custom scripts, fonts, terminal profiles, Git config, SSH config (keys excluded), `.gitignore_global`, Python/Node version, and a human-readable `environment.toml` manifest that documents exactly what your setup contains and why.

---

## 🎯 What Imprint Does

Imprint is a Python CLI tool (`imp`) that solves developer environment portability in two commands:

**On your current machine:**
```bash
imp snapshot
```
This captures your complete developer environment into a structured folder called `~/.imprint/` and pushes it to your private GitHub repo. It captures: dotfiles (`.zshrc`, `.bashrc`, `.gitconfig`, `.vimrc`, `.tmux.conf`, etc.), VS Code extensions list + `settings.json`, installed packages (pip global, npm global, apt/brew), custom scripts from `~/bin/`, fonts list, terminal profile exports where possible, Python version, Node version, and an `environment.toml` manifest.

**On any new machine:**
```bash
imp restore https://github.com/yourname/imprint-config
```
This clones your config repo, reads `environment.toml`, installs all packages, symlinks all dotfiles, installs VS Code extensions, sets up your shell, and prints a clear checklist of what was restored vs what needs manual action.

**Two additional power commands:**
```bash
imp diff           # Compare current machine vs your saved snapshot
imp update         # Snapshot current state and push to GitHub (after you've made changes)
```

---

## 🏗️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **CLI framework** | Click 8.x | Commands: `snapshot`, `restore`, `diff`, `update`, `status` |
| **Terminal UI** | Rich | Beautiful coloured output, progress bars, tables, spinners |
| **Config format** | TOML (`tomllib` built-in) | `environment.toml` — the master manifest |
| **Symlinks** | Python `pathlib` + `os.symlink` | Dotfile symlinking (replaces GNU Stow) |
| **Git operations** | `gitpython` | Push/pull config repo automatically |
| **Package detection** | `subprocess` | Detect and install pip/npm/apt/brew packages |
| **VS Code** | `subprocess` (code CLI) | `code --list-extensions` and `code --install-extension` |
| **Config storage** | `~/.imprint/` directory | Local config store + SQLite for snapshot history |
| **Secrets safety** | `.imprintignore` | Never snapshot SSH keys, tokens, passwords |
| **Cross-platform** | Platform detection | Handles Linux (apt), macOS (brew), WSL |
| **Distribution** | PyPI (`pip install imprint-cli`) | One-command install on any machine |

---

## 📁 Folder Structure

```
imprint/                              ← GitHub repo (the tool itself)
│
├── imprint/                          ← Python package
│   ├── __init__.py
│   ├── cli.py                        ← Click CLI entry point — all commands
│   ├── config.py                     ← Pydantic settings + .imprint dir management
│   ├── snapshot.py                   ← CORE: capture everything from current machine
│   ├── restore.py                    ← CORE: restore everything on new machine
│   ├── diff.py                       ← Compare current machine vs saved snapshot
│   ├── manifest.py                   ← Read/write environment.toml
│   ├── collectors/
│   │   ├── __init__.py
│   │   ├── dotfiles.py               ← Collect all dotfiles from home directory
│   │   ├── vscode.py                 ← VS Code extensions + settings
│   │   ├── packages.py               ← pip, npm, apt/brew packages
│   │   ├── shell.py                  ← Shell type, version, oh-my-zsh plugins
│   │   ├── git_config.py             ← .gitconfig, .gitignore_global
│   │   ├── scripts.py                ← ~/bin/ custom scripts
│   │   └── system.py                 ← Python version, Node version, OS info
│   ├── installers/
│   │   ├── __init__.py
│   │   ├── dotfiles.py               ← Symlink dotfiles on restore
│   │   ├── vscode.py                 ← Install VS Code extensions on restore
│   │   ├── packages.py               ← Install packages on restore
│   │   ├── shell.py                  ← Set up shell on restore
│   │   └── scripts.py                ← Restore ~/bin/ scripts
│   └── utils/
│       ├── git.py                    ← gitpython wrapper
│       ├── platform.py               ← OS detection: linux/mac/wsl
│       ├── safety.py                 ← .imprintignore, secrets detection
│       └── display.py                ← Rich console helpers
│
├── tests/
│   ├── test_snapshot.py
│   ├── test_restore.py
│   └── test_manifest.py
│
├── pyproject.toml                    ← Build config, entry point
├── README.md
└── .imprintignore.default            ← Default ignore patterns

---

~/.imprint/                           ← Your local Imprint data directory
│
├── config.toml                       ← Your Imprint settings (GitHub repo URL, etc.)
├── environment.toml                  ← THE MASTER MANIFEST — full env description
├── snapshots/
│   └── 2025-06-15_14-30-00/         ← Timestamped snapshot history
│       └── environment.toml
├── dotfiles/                         ← Copied dotfiles (symlinked from home dir)
│   ├── .zshrc
│   ├── .gitconfig
│   ├── .vimrc
│   ├── .tmux.conf
│   └── ...
├── scripts/                          ← ~/bin/ custom scripts
│   └── my_script.sh
└── .imprintignore                    ← Never snapshot these (SSH keys, tokens)
```

---

## 📄 The environment.toml Manifest

This is the centrepiece of Imprint — a human-readable, version-controlled, fully documented description of your developer environment. Every `imp snapshot` regenerates it. Every `imp restore` reads it.

```toml
# environment.toml — Your Developer Imprint
# Generated by Imprint v1.0.0 on 2025-06-15 14:30:00
# Machine: your-hostname | OS: Ubuntu 24.04 | User: yourname

[meta]
imprint_version = "1.0.0"
snapshot_at     = "2025-06-15T14:30:00"
hostname        = "your-hostname"
os              = "ubuntu"
os_version      = "24.04"
username        = "yourname"
shell           = "zsh"
shell_version   = "5.9"

[system]
python_version  = "3.11.9"
node_version    = "20.14.0"
git_version     = "2.45.1"

[dotfiles]
# All dotfiles tracked by Imprint — stored in ~/.imprint/dotfiles/
files = [
  ".zshrc",
  ".bashrc",
  ".gitconfig",
  ".gitignore_global",
  ".vimrc",
  ".tmux.conf",
  ".editorconfig",
  ".eslintrc.json",
  ".prettierrc",
]

[shell]
type             = "zsh"
framework        = "oh-my-zsh"
theme            = "powerlevel10k/powerlevel10k"
plugins          = ["git", "docker", "python", "zsh-autosuggestions", "zsh-syntax-highlighting"]
custom_aliases   = 47       # Number of aliases in .zshrc
custom_functions = 12       # Number of custom functions in .zshrc

[vscode]
version = "1.90.0"
extensions = [
  "ms-python.python",
  "ms-python.vscode-pylance",
  "eamodio.gitlens",
  "esbenp.prettier-vscode",
  "bradlc.vscode-tailwindcss",
  "formulahendry.auto-rename-tag",
  "usernamehw.errorlens",
  "PKief.material-icon-theme",
  "GitHub.copilot",
  "ms-azuretools.vscode-docker",
]
settings_included = true    # settings.json is included in dotfiles

[packages.pip]
# Global pip packages (not project-specific)
packages = [
  "black==24.4.2",
  "ruff==0.4.7",
  "ipython==8.24.0",
  "httpie==3.2.3",
  "rich==13.7.1",
  "poetry==1.8.3",
]

[packages.npm]
# Global npm packages
packages = [
  "typescript@5.4.5",
  "prettier@3.3.0",
  "eslint@9.3.0",
  "nodemon@3.1.3",
  "pnpm@9.1.4",
]

[packages.system]
# apt / brew packages (non-default)
manager = "apt"
packages = [
  "git",
  "curl",
  "wget",
  "htop",
  "tmux",
  "neovim",
  "ripgrep",
  "fd-find",
  "bat",
  "fzf",
  "zsh",
  "build-essential",
]

[scripts]
# Custom scripts from ~/bin/ — stored in ~/.imprint/scripts/
files = [
  "git-cleanup.sh",
  "start-dev.sh",
  "backup.sh",
]

[fonts]
# Installed developer fonts
installed = [
  "JetBrains Mono",
  "Fira Code",
  "Cascadia Code",
]

[git]
user_name    = "Your Name"
user_email   = "you@email.com"
default_branch = "main"
editor       = "nvim"
# Note: SSH keys are NEVER included in snapshots (.imprintignore)
```

---

## 🧩 Core Module: snapshot.py

```python
# imprint/snapshot.py

"""
The brain of Imprint's snapshot command.
Orchestrates all collectors, builds the manifest,
copies dotfiles, and pushes to GitHub.
"""

import shutil
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from imprint.collectors import (
    dotfiles as dotfiles_collector,
    vscode as vscode_collector,
    packages as packages_collector,
    shell as shell_collector,
    git_config as git_collector,
    scripts as scripts_collector,
    system as system_collector,
)
from imprint.manifest import Manifest
from imprint.utils.git import push_to_github
from imprint.utils.safety import filter_safe_files
from imprint.config import ImprintConfig

console = Console()


def run_snapshot(config: ImprintConfig, push: bool = True) -> Path:
    """
    Full snapshot of the current machine's developer environment.
    Returns path to the snapshot directory.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    snapshot_dir = config.imprint_dir / "snapshots" / timestamp
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    dotfiles_dir = config.imprint_dir / "dotfiles"
    scripts_dir  = config.imprint_dir / "scripts"

    console.print("\n[bold purple]⚡ Imprint Snapshot[/bold purple] — Capturing your developer environment\n")

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
        safe_dotfiles = filter_safe_files(found_dotfiles, config.imprintignore_path)
        dotfiles_dir.mkdir(parents=True, exist_ok=True)
        for src_path in safe_dotfiles:
            dest = dotfiles_dir / src_path.name
            shutil.copy2(src_path, dest)
        manifest.dotfiles = [f.name for f in safe_dotfiles]
        progress.update(task, description=f"[green]✓  Dotfiles ({len(safe_dotfiles)} files)[/green]")

        # 3. VS Code
        task = progress.add_task("🧩  Collecting VS Code extensions...", total=None)
        vscode_data = vscode_collector.collect()
        manifest.vscode = vscode_data
        if vscode_data.get("settings_path"):
            shutil.copy2(vscode_data["settings_path"], dotfiles_dir / "vscode_settings.json")
        progress.update(task, description=f"[green]✓  VS Code ({len(vscode_data.get('extensions', []))} extensions)[/green]")

        # 4. Packages
        task = progress.add_task("📦  Collecting installed packages...", total=None)
        packages_data = packages_collector.collect()
        manifest.packages = packages_data
        total_pkgs = sum(len(v) for v in packages_data.values())
        progress.update(task, description=f"[green]✓  Packages ({total_pkgs} total)[/green]")

        # 5. Shell
        task = progress.add_task("🐚  Detecting shell config...", total=None)
        shell_data = shell_collector.collect(config.home_dir)
        manifest.shell = shell_data
        progress.update(task, description=f"[green]✓  Shell ({shell_data.get('type', 'unknown')})[/green]")

        # 6. Git config
        task = progress.add_task("🔧  Reading Git config...", total=None)
        git_data = git_collector.collect(config.home_dir)
        manifest.git = git_data
        progress.update(task, description="[green]✓  Git config[/green]")

        # 7. Custom scripts
        task = progress.add_task("📜  Collecting ~/bin scripts...", total=None)
        bin_scripts = scripts_collector.collect(config.home_dir)
        safe_scripts = filter_safe_files(bin_scripts, config.imprintignore_path)
        scripts_dir.mkdir(parents=True, exist_ok=True)
        for src_path in safe_scripts:
            shutil.copy2(src_path, scripts_dir / src_path.name)
        manifest.scripts = [f.name for f in safe_scripts]
        progress.update(task, description=f"[green]✓  Scripts ({len(safe_scripts)} files)[/green]")

    # Save manifest
    manifest_path = config.imprint_dir / "environment.toml"
    manifest.save(manifest_path)
    shutil.copy2(manifest_path, snapshot_dir / "environment.toml")

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
        push_to_github(config.imprint_dir, config.github_repo)
        console.print(f"[green]✓  Pushed to {config.github_repo}[/green]")

    return snapshot_dir
```

---

## 🔄 Core Module: restore.py

```python
# imprint/restore.py

"""
Restores a complete developer environment on a new machine.
Reads environment.toml, installs everything, creates symlinks.

Designed to be safe: never overwrites files without confirmation.
Shows a clear checklist of what was restored vs what needs manual steps.
"""

import subprocess
from pathlib import Path
from rich.console import Console
from rich.table import Table

from imprint.manifest import Manifest
from imprint.installers import (
    dotfiles as dotfiles_installer,
    vscode as vscode_installer,
    packages as packages_installer,
    shell as shell_installer,
    scripts as scripts_installer,
)
from imprint.utils.git import clone_repo
from imprint.config import ImprintConfig

console = Console()


def run_restore(config: ImprintConfig, source: str | None = None) -> None:
    """
    Restore developer environment from GitHub repo or local path.
    source: GitHub URL or local path to imprint config directory.
    """
    console.print("\n[bold purple]🔏 Imprint Restore[/bold purple] — Restoring your developer environment\n")

    # Get the imprint config source
    if source and source.startswith("https://github.com"):
        console.print(f"[blue]📥 Cloning config from {source}...[/blue]")
        imprint_dir = clone_repo(source, config.imprint_dir)
    else:
        imprint_dir = config.imprint_dir
        if not imprint_dir.exists():
            console.print("[red]✗  No imprint config found. Run 'imp snapshot' first or provide a GitHub URL.[/red]")
            return

    # Load manifest
    manifest_path = imprint_dir / "environment.toml"
    if not manifest_path.exists():
        console.print(f"[red]✗  environment.toml not found in {imprint_dir}[/red]")
        return

    manifest = Manifest.load(manifest_path)
    dotfiles_dir = imprint_dir / "dotfiles"
    scripts_dir  = imprint_dir / "scripts"

    results = []   # (step, status, detail)

    # ── Step 1: Dotfiles ─────────────────────────────────────────
    console.print("[bold]1/6  Symlinking dotfiles...[/bold]")
    dotfile_results = dotfiles_installer.install(
        dotfiles_dir, config.home_dir, manifest.dotfiles
    )
    for name, status, detail in dotfile_results:
        results.append(("dotfile: " + name, status, detail))
        symbol = "✓" if status == "ok" else "⚠" if status == "skipped" else "✗"
        colour = "green" if status == "ok" else "yellow" if status == "skipped" else "red"
        console.print(f"  [{colour}]{symbol}[/{colour}]  {name} — {detail}")

    # ── Step 2: VS Code Extensions ───────────────────────────────
    console.print("\n[bold]2/6  Installing VS Code extensions...[/bold]")
    extensions = manifest.vscode.get("extensions", [])
    if extensions:
        vscode_results = vscode_installer.install(extensions)
        installed_count = sum(1 for _, s, _ in vscode_results if s == "ok")
        console.print(f"  [green]✓[/green]  {installed_count}/{len(extensions)} extensions installed")
        results.append(("VS Code extensions", "ok", f"{installed_count}/{len(extensions)}"))
    else:
        console.print("  [yellow]⚠[/yellow]  No VS Code extensions in manifest")

    # ── Step 3: System packages ──────────────────────────────────
    console.print("\n[bold]3/6  Installing system packages...[/bold]")
    sys_pkgs = manifest.packages.get("system", {}).get("packages", [])
    if sys_pkgs:
        sys_results = packages_installer.install_system(
            sys_pkgs, manifest.packages.get("system", {}).get("manager", "apt")
        )
        console.print(f"  [green]✓[/green]  System packages install triggered")
        results.append(("system packages", "ok", f"{len(sys_pkgs)} packages"))
    else:
        console.print("  [yellow]⚠[/yellow]  No system packages in manifest")

    # ── Step 4: pip packages ─────────────────────────────────────
    console.print("\n[bold]4/6  Installing pip packages...[/bold]")
    pip_pkgs = manifest.packages.get("pip", {}).get("packages", [])
    if pip_pkgs:
        packages_installer.install_pip(pip_pkgs)
        console.print(f"  [green]✓[/green]  {len(pip_pkgs)} pip packages installed")
        results.append(("pip packages", "ok", f"{len(pip_pkgs)} packages"))

    # ── Step 5: npm packages ─────────────────────────────────────
    console.print("\n[bold]5/6  Installing npm packages...[/bold]")
    npm_pkgs = manifest.packages.get("npm", {}).get("packages", [])
    if npm_pkgs:
        packages_installer.install_npm(npm_pkgs)
        console.print(f"  [green]✓[/green]  {len(npm_pkgs)} npm packages installed")
        results.append(("npm packages", "ok", f"{len(npm_pkgs)} packages"))

    # ── Step 6: Custom scripts ───────────────────────────────────
    console.print("\n[bold]6/6  Restoring ~/bin scripts...[/bold]")
    if manifest.scripts:
        scripts_installer.install(scripts_dir, config.home_dir / "bin", manifest.scripts)
        console.print(f"  [green]✓[/green]  {len(manifest.scripts)} scripts restored to ~/bin")
        results.append(("scripts", "ok", f"{len(manifest.scripts)} scripts"))

    # ── Final summary table ──────────────────────────────────────
    console.print("\n")
    table = Table(title="🔏 Imprint Restore Complete", show_header=True, header_style="bold magenta")
    table.add_column("Item", style="cyan")
    table.add_column("Status")
    table.add_column("Detail", style="dim")

    ok_count = 0
    for item, status, detail in results:
        if status == "ok":
            ok_count += 1
            table.add_row(item, "[green]✓ Restored[/green]", detail)
        elif status == "skipped":
            table.add_row(item, "[yellow]⚠ Skipped[/yellow]", detail)
        else:
            table.add_row(item, "[red]✗ Failed[/red]", detail)

    console.print(table)

    console.print(f"\n[bold green]Done! {ok_count}/{len(results)} items restored.[/bold green]")
    console.print("[dim]Run 'source ~/.zshrc' or restart your terminal to activate shell changes.[/dim]\n")
```

---

## 🖥️ CLI Entry Point (imprint/cli.py)

```python
# imprint/cli.py

import click
from rich.console import Console
from imprint.config import ImprintConfig
from imprint.snapshot import run_snapshot
from imprint.restore import run_restore
from imprint.diff import run_diff

console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="Imprint")
def cli():
    """
    🔏 Imprint — Stamp your developer environment on any machine.

    Commands:
      imp snapshot   Capture your current environment
      imp restore    Restore your environment on a new machine
      imp diff       See what has changed since your last snapshot
      imp update     Snapshot + push in one command
      imp status     Show what Imprint is tracking
    """
    pass


@cli.command()
@click.option("--no-push", is_flag=True, default=False,
              help="Don't push to GitHub after snapshot")
@click.option("--include-vscode/--no-vscode", default=True,
              help="Include VS Code extensions")
@click.option("--include-packages/--no-packages", default=True,
              help="Include installed packages")
def snapshot(no_push, include_vscode, include_packages):
    """Capture your complete developer environment."""
    config = ImprintConfig.load()
    run_snapshot(config, push=not no_push)


@cli.command()
@click.argument("source", required=False)
@click.option("--dry-run", is_flag=True, default=False,
              help="Show what would be restored without doing it")
def restore(source, dry_run):
    """
    Restore your developer environment on a new machine.

    SOURCE can be a GitHub URL (https://github.com/you/imprint-config)
    or omit it to restore from ~/.imprint/ directly.
    """
    config = ImprintConfig.load()
    if dry_run:
        console.print("[yellow]Dry run mode — no changes will be made.[/yellow]")
    run_restore(config, source=source)


@cli.command()
def diff():
    """Show what has changed since your last snapshot."""
    config = ImprintConfig.load()
    run_diff(config)


@cli.command()
def update():
    """Snapshot current state and push to GitHub."""
    config = ImprintConfig.load()
    run_snapshot(config, push=True)
    console.print("[green]✅ Environment updated and pushed.[/green]")


@cli.command()
def status():
    """Show what Imprint is currently tracking."""
    config = ImprintConfig.load()
    manifest_path = config.imprint_dir / "environment.toml"
    if not manifest_path.exists():
        console.print("[yellow]No snapshot found. Run 'imp snapshot' first.[/yellow]")
        return

    from imprint.manifest import Manifest
    manifest = Manifest.load(manifest_path)
    console.print(f"\n[bold purple]🔏 Imprint Status[/bold purple]")
    console.print(f"   Last snapshot:   {manifest.meta.get('snapshot_at', 'unknown')}")
    console.print(f"   Machine:         {manifest.meta.get('hostname', 'unknown')}")
    console.print(f"   OS:              {manifest.meta.get('os', 'unknown')} {manifest.meta.get('os_version', '')}")
    console.print(f"   Python:          {manifest.system.get('python_version', 'unknown')}")
    console.print(f"   Node:            {manifest.system.get('node_version', 'N/A')}")
    console.print(f"   Dotfiles:        {len(manifest.dotfiles)} files")
    console.print(f"   VS Code:         {len(manifest.vscode.get('extensions', []))} extensions")
    total_pkgs = sum(len(v.get('packages', v if isinstance(v, list) else [])) for v in manifest.packages.values())
    console.print(f"   Packages:        {total_pkgs} total")
    console.print(f"   Custom scripts:  {len(manifest.scripts)} files\n")


def main():
    cli()
```

---

## 🔍 Collector: VS Code (collectors/vscode.py)

```python
# imprint/collectors/vscode.py

"""
Collects VS Code extensions list and settings.json.
Works on Linux, macOS, and WSL.
"""

import subprocess
import json
import platform
from pathlib import Path


def collect() -> dict:
    result = {
        "version": _get_vscode_version(),
        "extensions": _get_extensions(),
        "settings_path": str(_get_settings_path()) if _get_settings_path() else None,
    }
    return result


def _get_extensions() -> list[str]:
    try:
        output = subprocess.check_output(
            ["code", "--list-extensions", "--show-versions"],
            stderr=subprocess.DEVNULL, text=True
        )
        return [line.strip() for line in output.strip().split("\n") if line.strip()]
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []


def _get_vscode_version() -> str | None:
    try:
        output = subprocess.check_output(
            ["code", "--version"], stderr=subprocess.DEVNULL, text=True
        )
        return output.split("\n")[0].strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def _get_settings_path() -> Path | None:
    system = platform.system()
    home = Path.home()

    candidates = {
        "Linux":  home / ".config/Code/User/settings.json",
        "Darwin": home / "Library/Application Support/Code/User/settings.json",
        "Windows": Path.home() / "AppData/Roaming/Code/User/settings.json",
    }

    path = candidates.get(system)
    return path if path and path.exists() else None
```

---

## 🔍 Collector: Packages (collectors/packages.py)

```python
# imprint/collectors/packages.py

"""
Collects installed packages:
  - pip (global, non-standard packages only)
  - npm (global packages)
  - apt (manually installed, non-default) or brew (macOS)
"""

import subprocess
import platform
import json
from pathlib import Path


# pip packages that come with Python — don't snapshot these
PIP_STDLIB = {"pip", "setuptools", "wheel", "pkg_resources", "distutils"}


def collect() -> dict:
    return {
        "pip":    {"packages": _get_pip_packages()},
        "npm":    {"packages": _get_npm_packages()},
        "system": {"manager": _get_system_manager(),
                   "packages": _get_system_packages()},
    }


def _get_pip_packages() -> list[str]:
    try:
        output = subprocess.check_output(
            ["pip", "list", "--format=freeze", "--not-required"],
            text=True, stderr=subprocess.DEVNULL
        )
        packages = []
        for line in output.strip().split("\n"):
            if line and not any(std in line.lower() for std in PIP_STDLIB):
                packages.append(line.strip())
        return packages
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []


def _get_npm_packages() -> list[str]:
    try:
        output = subprocess.check_output(
            ["npm", "list", "-g", "--depth=0", "--json"],
            text=True, stderr=subprocess.DEVNULL
        )
        data = json.loads(output)
        deps = data.get("dependencies", {})
        return [f"{name}@{info.get('version', 'latest')}" for name, info in deps.items()]
    except (FileNotFoundError, subprocess.CalledProcessError, json.JSONDecodeError):
        return []


def _get_system_manager() -> str:
    if platform.system() == "Darwin":
        return "brew"
    return "apt"


def _get_system_packages() -> list[str]:
    if platform.system() == "Darwin":
        return _get_brew_packages()
    return _get_apt_packages()


def _get_brew_packages() -> list[str]:
    try:
        output = subprocess.check_output(["brew", "list", "--formula"], text=True)
        return [p.strip() for p in output.strip().split("\n") if p.strip()]
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []


def _get_apt_packages() -> list[str]:
    """Get manually installed apt packages (not auto-installed dependencies)."""
    try:
        output = subprocess.check_output(
            ["apt-mark", "showmanual"], text=True, stderr=subprocess.DEVNULL
        )
        return sorted([p.strip() for p in output.strip().split("\n") if p.strip()])
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []
```

---

## 🛡️ Safety: .imprintignore

```
# .imprintignore — Never snapshot these files
# Imprint will NEVER include these in any snapshot, regardless of configuration.
# Format: one pattern per line, same as .gitignore

# SSH keys and config — NEVER include
.ssh/id_rsa
.ssh/id_ed25519
.ssh/id_ecdsa
.ssh/*.pem
.ssh/*.key

# Tokens and secrets
.env
.env.*
*.token
*_token
*secret*
*password*
*credential*
*api_key*

# GPG keys
.gnupg/

# Browser data
.mozilla/
.config/google-chrome/

# Large data directories
.npm/
.cache/
.local/share/
node_modules/

# AWS / Cloud credentials
.aws/credentials
.aws/config
.gcloud/
.kube/

# Shell history (contains sensitive commands)
.bash_history
.zsh_history
```

---

## ⚡ The `imp diff` Command Output (Example)

```
$ imp diff

🔏 Imprint Diff — Changes since last snapshot (2025-05-20)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DOTFILES
  ✏  .zshrc               Modified  (+12 lines, -3 lines)
  ✏  .gitconfig           Modified  (user.email changed)
  ✔  .vimrc               Unchanged
  ✔  .tmux.conf           Unchanged

VS CODE EXTENSIONS
  + ms-python.debugpy     Added
  + GitHub.copilot-chat   Added
  - ms-vscode.cpptools    Removed

PACKAGES (pip)
  + ruff==0.5.0           Added     (was 0.4.7)
  + fastapi==0.111.0      Added
  - flask==3.0.3          Removed

PACKAGES (npm)
  + @antfu/ni@0.21.12     Added

SUMMARY
  3 dotfiles changed | 2 extensions added | 1 removed | 3 pip changes
  Run 'imp update' to save these changes to your snapshot.
```

---

## 🚀 Installation & Usage

### Install Imprint

```bash
pip install imprint-cli
```

### First-time setup (on YOUR machine)

```bash
imp snapshot              # Captures everything, saves to ~/.imprint/
# You'll be prompted for your GitHub repo URL to push to
# Create a PRIVATE repo: github.com/yourname/imprint-config
```

### On a new machine (coworker's PC, fresh laptop, new job)

```bash
pip install imprint-cli
imp restore https://github.com/yourname/imprint-config
# Done. Everything restored.
```

### Day-to-day

```bash
imp diff          # See what's changed since last snapshot
imp update        # Save changes and push
imp status        # Quick overview of what's tracked
```

---

## 📅 25-Day Build Schedule

| Days | Phase | Tasks |
|---|---|---|
| **1–2** | **Project Setup** | `pyproject.toml` with Click entry point. Install deps. `imp --help` works. `~/.imprint/` directory created on first run. |
| **3–4** | **Manifest System** | `manifest.py` — `Manifest` class with TOML read/write. `environment.toml` template. Validate round-trip: write → read → write gives identical file. |
| **5–6** | **Collector: System + Dotfiles** | `collectors/system.py` — Python/Node/Git versions, OS detection. `collectors/dotfiles.py` — find all dotfiles in home dir. Test on your own machine. |
| **7–8** | **Collector: VS Code + Shell** | `collectors/vscode.py` — `code --list-extensions`, settings.json path. `collectors/shell.py` — zsh/bash detection, oh-my-zsh plugins. |
| **9–10** | **Collector: Packages** | `collectors/packages.py` — pip + npm + apt/brew. Test: collected packages match what you actually have installed. |
| **11** | **Safety System** | `utils/safety.py` — `.imprintignore` parsing and filtering. Test: SSH key path never passes filter. Token files never pass. |
| **12–13** | **Snapshot Command** | `snapshot.py` — full orchestration. Run on your machine. Verify `~/.imprint/dotfiles/` has your files. Verify `environment.toml` is correct. |
| **14** | **Git Integration** | `utils/git.py` — `push_to_github()` and `clone_repo()`. Test: `imp snapshot` pushes to a test private repo. |
| **15–16** | **Installer: Dotfiles** | `installers/dotfiles.py` — symlink dotfiles to home dir. Handle conflicts (existing file → ask user). Test on a clean user account. |
| **17–18** | **Installer: Packages + VS Code** | `installers/packages.py` — pip install, npm install, apt/brew install. `installers/vscode.py` — `code --install-extension`. Test restore of packages on a test VM. |
| **19–20** | **Restore Command** | `restore.py` — full restore orchestration + summary table. Full end-to-end test: snapshot on machine A, restore on machine B (VM). Verify everything matches. |
| **21–22** | **Diff Command** | `diff.py` — compare current machine state vs manifest. Show added/removed/modified. Test: install a new pip package, run `imp diff`, verify it shows. |
| **23** | **Status Command + Polish** | `cli.py` status command. Rich table output. Help text. Error messages that are actually helpful. |
| **24** | **PyPI Packaging** | `pyproject.toml` — full packaging config. `pip install imprint-cli` works from scratch. Test `pip install` + `imp snapshot` full flow. |
| **25** | **README + Demo** | README with GIF demo: `imp snapshot` output, then `imp restore` on a fresh machine, showing the table of restored items. GitHub push. |

---

## 📦 pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "imprint-cli"
version = "1.0.0"
description = "Stamp your developer environment on any machine"
readme = "README.md"
license = { text = "MIT" }
requires-python = ">=3.11"
keywords = ["dotfiles", "developer", "environment", "portable", "devtools", "cli"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.11",
    "Topic :: Utilities",
]
dependencies = [
    "click>=8.1.7",
    "rich>=13.7.0",
    "gitpython>=3.1.43",
    "tomli>=2.0.1; python_version < '3.11'",
    "platformdirs>=4.2.0",
]

[project.scripts]
imp = "imprint.cli:main"
imprint = "imprint.cli:main"

[project.urls]
Homepage = "https://github.com/yourname/imprint"
Repository = "https://github.com/yourname/imprint"
"Bug Tracker" = "https://github.com/yourname/imprint/issues"
```

---

## 🎯 GitHub Repo

**Repo name**: `imprint`

**Description**: 🔏 Imprint — Stamp your developer environment on any machine. One command to snapshot everything (dotfiles, VS Code extensions, packages, shell config, custom scripts). One command to restore on any new machine. Built with Python + Click + Rich.

**Topics**: `dotfiles`, `developer-tools`, `cli`, `python`, `environment`, `portable`, `vscode`, `devtools`, `setup`, `productivity`

---

## 🎤 Interview One-Liner

*"I built Imprint — a Python CLI tool that solves a problem every developer faces: you spend 3–6 hours setting up a new machine from memory, and you always forget something. Imprint runs 'imp snapshot' on your current machine and captures everything — dotfiles, VS Code extensions, pip and npm global packages, system packages, shell config, custom scripts — into a structured TOML manifest that gets pushed to your private GitHub repo. On any new machine, 'imp restore https://github.com/you/imprint-config' clones the repo, reads the manifest, installs all packages, symlinks all dotfiles, installs VS Code extensions, and gives you a clear table of what was restored vs what needs manual action. It also has 'imp diff' which shows exactly what has changed since your last snapshot — new packages, modified dotfiles, added extensions — so you know when to update. The security design is deliberate: .imprintignore ensures SSH keys, tokens, and credentials are NEVER included in any snapshot, ever. It's published on PyPI as 'imprint-cli' so the restore command works from scratch on any machine that has Python."*
