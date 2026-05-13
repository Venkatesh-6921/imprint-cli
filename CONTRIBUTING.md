# Contributing to Imprint CLI

First off, thanks for taking the time to contribute to **Imprint**! 🎉

Imprint v3 is a massive upgrade focused on a full TUI dashboard, modular collectors/installers, and secure snapshotting. We welcome contributions of all kinds—from bug fixes and new collectors to documentation improvements.

---

## Architecture Overview

Imprint is built around a modular architecture:
- **CLI / TUI (`imprint/cli.py` & `imprint/utils/display.py`)**: The user interface. Uses `click` for CLI and `textual` for the TUI dashboard.
- **Collectors (`imprint/collectors/`)**: Extract configuration from the user's environment.
- **Installers (`imprint/installers/`)**: Apply a snapshot back to a new environment.
- **Config & Manifest (`imprint/config.py`, `imprint/manifest.py`)**: Manage profiles and structure the snapshot data.
- **Security (`imprint/crypto.py`, `imprint/utils/safety.py`)**: Ensure sensitive data is never captured in plaintext.

---

## Development Setup

We use `uv` for lightning-fast dependency management and `hatchling` as our build backend.

```bash
# 1. Clone your fork
git clone https://github.com/YOUR_USERNAME/imprint-cli.git
cd imprint-cli

# 2. Create virtual environment and install dependencies with uv
# This installs all extras (dev, crypto, watch)
uv sync --extra dev --extra full

# 3. Run the CLI in development mode
uv run imp --help

# 4. Verify formatting and tests pass
uv run ruff check .
uv run pytest tests/ -v
```

> **Note:** Do not use `pip` or generate `requirements.txt`. Always use `uv`.

---

## Git Workflow (Branch Protection)

> ⚠️ **Direct pushes to `main` are blocked.** All changes must go through a Pull Request.

1. Create a branch for your feature or fix: `git checkout -b feat/your-feature-name`
2. Commit your changes with descriptive messages: `git commit -m "feat: add support for ghostty terminal"`
3. Push to your fork: `git push origin feat/your-feature-name`
4. Open a **Pull Request** against the `main` branch of the `Venkatesh-6921/imprint-cli` repository.

### Branch Naming Conventions
- `feat/...` for new features or collectors
- `fix/...` for bug fixes
- `docs/...` for documentation updates
- `refactor/...` for structural code changes
- `test/...` for adding tests

---

## Adding a New Collector & Installer

We are always looking to support more developer tools!

### 1. The Collector
Create `imprint/collectors/your_tool.py`:
```python
from pathlib import Path

def collect(home_dir: Path) -> dict:
    """Collect tool configuration data."""
    config_path = home_dir / ".config" / "yourtool" / "config"
    if not config_path.exists():
        return {}
    
    return {"version": "1.0", "plugins": []}
```
*Remember to route all file paths through `filter_safe_files()` from `utils/safety.py` to prevent capturing secrets.*

### 2. The Installer
Create `imprint/installers/your_tool.py`:
```python
from pathlib import Path

def install(data: dict, home_dir: Path) -> None:
    """Restore tool configuration data."""
    if not data:
        return
    # write config safely
```

### 3. Wiring it up
- Add your collector to `imprint/snapshot.py` and installer to `imprint/restore.py`.
- Update the dataclass in `imprint/manifest.py`.
- Add tests in `tests/test_collectors.py` and `tests/test_restore.py`.
- Mention it in `CHANGELOG.md` under `[Unreleased]`.

---

## Code Style & Standards

- **Python 3.11+**: We rely on modern Python features (like `match/case` and modern type hinting like `list[str]`).
- **Formatting & Linting**: We use `ruff`. Line length is set to 100 characters.
- **Dependencies**: Keep them minimal. Currently relying on `click`, `rich`, `textual`, `gitpython`, `pyyaml`, and `tomli_w`.

---

## Security Guidelines

Imprint deals with user environments, which often contain highly sensitive data.
- ❌ **NEVER** capture SSH private keys, API tokens, passwords, or `.env` files.
- ❌ **NO** `shell=True` when making subprocess calls.
- ✅ **ALWAYS** use `imprint.utils.safety` functions to sanitize paths and files.

---

## Releases (Maintainers Only)

Our CI/CD pipeline automates PyPI publishing via GitHub OIDC.
When ready to release:
1. Update `__version__` in `imprint/__init__.py`.
2. Update `CHANGELOG.md` with the new version section.
3. Merge everything to `main`.
4. Tag and push:
   ```bash
   git tag v3.1.0
   git push origin main --tags
   ```

Thanks again for contributing!
