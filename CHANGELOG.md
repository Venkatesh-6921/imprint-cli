# Changelog

All notable changes to **imprint-cli** are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

## [3.0.0] — 2026-05-13

### Added

- **Named Profiles**: Support for multiple named profiles (`work`, `home`, `laptop`). Switch with `imp profile use <name>`.
- **11 CLI Commands**: `init`, `snapshot`, `restore`, `diff`, `update`, `status`, `doctor`, `history`, `export`, `profile`, `compare`, `encrypt`, `watch`.
- **6 New Collectors**: Neovim (lazy.nvim/packer plugins), Cursor IDE (extensions), tmux (config/plugins), SSH config (host aliases only), Cargo (Rust crates), uv (Python tools).
- **AES-256-GCM Encryption**: Optional encryption for dotfiles before pushing to GitHub via `imp encrypt`.
- **Multi-Format Export**: Export your environment as JSON, YAML, Markdown report, or standalone shell script via `imp export --fmt <format>`.
- **Watch Mode**: Auto-snapshot on file changes with `imp watch` (requires `watchdog`).
- **Doctor Command**: Full health check — validates config, git connectivity, GitHub access, optional deps.
- **History Timeline**: Browse past snapshots in a Rich-powered timeline table.
- **Snapshot Comparison**: Diff two snapshots side-by-side with `imp compare <a> <b>`.
- **Interactive Init Wizard**: Guided first-run setup with `imp init`.
- **Nord-Inspired Theme**: Complete UI overhaul with a Nord color palette, two-panel dashboard, progress bars, and branded ASCII logo.
- **Automated PyPI Publishing**: GitHub Actions workflow using `PYPI_API_TOKEN` secret for secure publishing.
- **CI Matrix**: Test against Python 3.11, 3.12, 3.13 on Ubuntu and macOS.
- **Dependabot**: Automated dependency updates for pip and GitHub Actions.
- **Dry-Run Restore**: Preview what `imp restore` would do without making changes.
- **Branch Support**: Push snapshots to any branch (not just `main`) via config.

### Changed

- **Config System**: Migrated from flat config to profile-aware TOML with `github_branch`, `auto_push`, `encrypt`, and `theme` fields.
- **Manifest Format**: Added `neovim`, `cursor`, `tmux`, and `ssh_config` sections to `environment.toml`.
- **Display Module**: Full rewrite with Rich theme system, dashboard layout, and progress factory.
- **Git Utility**: `push_to_github()` now accepts a `branch` parameter.
- **Package Manager**: `uv` + `pyproject.toml` replaces bare `pip` + `requirements.txt`.

### Security

- **`.imprintignore` hardening**: Expanded default ignore patterns for SSH keys, API tokens, cloud credentials, shell history, and browser data.
- **SSH Config collector**: Restricted to Host aliases only — never captures keys, passwords, or IdentityFile paths.
- **Key file permissions**: Encryption keys created with `chmod 0o600`.
- **No `shell=True`**: All subprocess calls use list arguments to prevent shell injection.
- **Token-based publishing**: `PYPI_API_TOKEN` stored as GitHub repository secret, never in code.

---

## [2.0.1] — 2026-04-28

### Fixed

- Fixed import sorting issues flagged by ruff.
- Fixed unused import warnings in test files.

---

## [2.0.0] — 2026-04-15

### Added

- **Premium CLI Experience**: Branded Rich UI with progress bars and summary tables.
- **5 Commands**: `snapshot`, `restore`, `diff`, `update`, `status`.
- **7 Collectors**: System info, dotfiles, VS Code, shell, packages (pip/npm/system), git config, scripts.
- **5 Installers**: Dotfiles (symlinks), VS Code extensions, packages, scripts, shell config.
- **Safety System**: Non-bypassable `.imprintignore` with hardcoded patterns for SSH keys, tokens, and secrets.
- **GitHub Cloud Sync**: Built-in `gitpython` integration for versioned backups.
- **Cross-Platform**: Support for Linux, macOS, Windows, and WSL.
- **TOML Manifest**: Human-readable `environment.toml` for captured environment state.

---

## [1.0.0] — 2026-03-20

### Added

- Initial release.
- Basic `snapshot` and `restore` commands.
- Dotfile and VS Code extension collection.
- pip and npm package tracking.
- Git config capture.
