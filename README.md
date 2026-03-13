# 🔏 Imprint

**Stamp your developer environment on any machine.**

One command to snapshot everything — dotfiles, VS Code extensions, packages, shell config, custom scripts.  
One command to restore on any new machine.

```bash
# Install directly from PyPI (Recommended)
pip install imprint-cli

# OR install latest directly from GitHub
pip install git+https://github.com/Venkatesh-6921/imprint-cli.git
```

## The Problem

You have your machine perfectly set up. VS Code with 30 extensions. Your `.zshrc` with 50 aliases. Python, Node, custom scripts, fonts. Then you sit at a new machine and spend **3–6 hours** rebuilding everything from memory.

**Imprint fixes this in two commands:**

```bash
imp snapshot    # Captures EVERYTHING on this machine
imp restore     # Restores EVERYTHING on the new machine
```

## Quick Start

### 1. On Your Current Machine

```bash
pip install imprint-cli
imp snapshot
```

This captures your complete environment into `~/.imprint/`. On the first run, it will automatically prompt you for an empty GitHub repository URL so that it can securely back up your configuration to the cloud!

### 2. On a New Machine

```bash
pip install imprint-cli
imp restore https://github.com/your-username/my-imprint-config.git
```

Done. Everything restored.

### Day-to-Day

```bash
imp diff      # See what's changed since last snapshot
imp update    # Save changes and push
imp status    # Quick overview of what's tracked
```

## What Gets Captured

| Category | Details |
|---|---|
| **Dotfiles** | `.zshrc`, `.bashrc`, `.gitconfig`, `.vimrc`, `.tmux.conf`, `.editorconfig`, PowerShell profiles |
| **VS Code** | All extensions list + `settings.json` |
| **Packages** | pip (global), npm (global), apt / brew / winget |
| **Shell** | Type, version, framework (oh-my-zsh), theme, plugins, alias count |
| **Git** | `user.name`, `user.email`, editor, default branch |
| **Scripts** | Everything in `~/bin/` |
| **System** | Python version, Node version, Git version, OS info |

## Tech Stack

| Layer | Technology |
|---|---|
| CLI | Click 8.x |
| Terminal UI | Rich (spinners, tables, colors) |
| Config | TOML (tomllib + tomli_w) |
| Git | GitPython |
| Platform | Linux, macOS, Windows, WSL |

## Architecture

```
imprint/
├── cli.py              ← Click CLI — snapshot, restore, diff, update, status
├── config.py           ← ImprintConfig — manages ~/.imprint/
├── manifest.py         ← environment.toml read/write
├── snapshot.py         ← Orchestrates all collectors
├── restore.py          ← Orchestrates all installers
├── diff.py             ← Compare current vs saved
├── collectors/
│   ├── system.py       ← Python/Node/Git versions
│   ├── dotfiles.py     ← Find dotfiles in $HOME
│   ├── vscode.py       ← Extensions + settings.json
│   ├── shell.py        ← Shell type, framework, plugins
│   ├── packages.py     ← pip/npm/apt/brew/winget
│   ├── git_config.py   ← Git config values
│   └── scripts.py      ← ~/bin/ scripts
├── installers/
│   ├── dotfiles.py     ← Symlink dotfiles
│   ├── vscode.py       ← Install extensions
│   ├── packages.py     ← Install packages
│   ├── shell.py        ← Shell setup guidance
│   └── scripts.py      ← Restore ~/bin/
└── utils/
    ├── platform.py     ← OS detection (Linux/macOS/Windows/WSL)
    ├── safety.py       ← .imprintignore filtering
    ├── display.py      ← Rich console helpers
    └── git.py          ← GitPython wrapper
```

## Security

Imprint **never** captures sensitive files. The `.imprintignore` system blocks:

- SSH keys (`.ssh/id_*`, `*.pem`, `*.key`)
- Tokens and secrets (`*.token`, `*secret*`, `*api_key*`)
- Environment files (`.env`, `.env.*`)
- Cloud credentials (`.aws/credentials`, `.gcloud/`, `.kube/`)
- Shell history (`.bash_history`, `.zsh_history`)
- GPG keys (`.gnupg/`)

These patterns are **hard-coded** and cannot be overridden.

## Testing

```bash
pip install -e ".[dev]"
python -m pytest tests/ -v
```

## For Developers: Publishing to PyPI

If you fork or clone this repository and want to publish your own version to PyPI:

1. Create an account on [PyPI](https://pypi.org/) and generate an API token (`__token__`).
2. Build the project:
   ```bash
   pip install build twine
   python -m build
   ```
3. Upload to PyPI securely (Recommended to set token as an environment variable to prevent terminal parsing errors):
   ```powershell
   # Windows PowerShell
   $env:TWINE_USERNAME="__token__"
   $env:TWINE_PASSWORD="pypi-your-token-here"
   python -m twine upload dist/*
   ```
   ```bash
   # Linux/macOS
   export TWINE_USERNAME="__token__"
   export TWINE_PASSWORD="pypi-your-token-here"
   python -m twine upload dist/*
   ```

## License

MIT
