# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Installation
```bash
# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Testing
```bash
# Run all tests
python -m pytest tests/ -v

# Run tests with coverage
python -m pytest tests/ --cov=imprint

# Run a specific test file
python -m pytest tests/test_cli.py -v
```

### Linting & Formatting
```bash
# Check code with ruff
ruff check .

# Fix auto-fixable issues
ruff check --fix .

# Format code (if using formatter)
# Note: Project uses ruff for linting, not formatting
```

### Building & Publishing
```bash
# Build the package
pip install build twine
python -m build

# Upload to PyPI (set TWINE_USERNAME and TWINE_PASSWORD as environment variables)
python -m twine upload dist/*
```

### CLI Usage
The main CLI entry point is `imp` (or `imprint`):
```bash
# Capture current environment
imp snapshot

# Restore from GitHub URL
imp restore https://github.com/username/repo.git

# See changes since last snapshot
imp diff

# Snapshot and push in one command
imp update

# Show current tracking status
imp status
```

## Code Architecture

### High-Level Structure
```
imprint/
├── cli.py              ← Click CLI entry point (snapshot, restore, diff, update, status)
├── config.py           ← Manages ~/.imprint/ configuration
├── manifest.py         ← environment.toml serialization/deserialization
├── snapshot.py         ← Orchestrates all data collectors
├── restore.py          ← Orchestrates all installers
├── diff.py             ← Compares current vs saved state
├── collectors/         ← Gathers system/environment data
│   ├── system.py       ← Python/Node/Git/OS versions
│   ├── dotfiles.py     ← Dotfiles discovery in $HOME
│   ├── vscode.py       ← VS Code extensions + settings.json
│   ├── shell.py        ← Shell type/framework/plugins
│   ├── packages.py     ← pip/npm/apt/brew/winget packages
│   ├── git_config.py   ← Git user configuration
│   └── scripts.py      ← ~/bin/ scripts collection
├── installers/         ← Applies collected data to new system
│   ├── dotfiles.py     ← Symlinking dotfiles
│   ├── vscode.py       ← Installing VS Code extensions
│   ├── shell.py        ← Shell setup guidance
│   ├── packages.py     ← Package installation
│   └── scripts.py      ← Restoring ~/bin/ scripts
└── utils/              ← Shared utilities
    ├── platform.py     ← OS detection (Linux/macOS/Windows/WSL)
    ├── safety.py       ← .imprintignore filtering (blocks sensitive files)
    ├── display.py      ← Rich console helpers
    └── git.py          ← GitPython wrapper
```

### Key Design Patterns
- **Modular collectors/installers**: Each data type has dedicated collector and installer modules
- **Configuration-driven**: Uses TOML for persistent configuration in ~/.imprint/
- **Safety-first**: Hard-coded .imprintignore patterns prevent capturing sensitive data
- **Cross-platform**: Abstracts OS differences through utils/platform.py
- **Orchestration**: Snapshot/restore modules coordinate the individual collectors/installers

### Data Flow
1. `imp snapshot` → snapshot.py runs all collectors → data saved to environment.toml
2. `imp restore` → restore.py runs all installers → applies data to target system
3. `imp diff` → compares current state with saved manifest
4. Configuration persisted in ~/.imprint/config.toml

### Security Features
- Automatic filtering of sensitive files via .imprintignore (SSH keys, tokens, env files, etc.)
- These patterns are hard-coded and cannot be overridden by users
- No automatic uploading without explicit GitHub repository configuration
