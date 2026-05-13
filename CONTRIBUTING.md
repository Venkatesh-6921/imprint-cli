# Contributing to imprint-cli

Thanks for helping make imprint-cli better! Here's everything you need.

---

## Ways to contribute

- **Add a new collector** — support a tool we don't capture yet (e.g., Docker, Zellij, Starship)
- **Improve an existing collector** — better parsing, more data, edge case handling
- **Fix a bug** — something doesn't snapshot or restore correctly
- **Add an installer** — restore support for a new collector
- **Improve the UI** — better Rich output, new themes, dashboard enhancements
- **Write tests** — increase coverage for collectors, config, and CLI
- **Documentation** — fix typos, improve README, add examples

---

## Development setup

```bash
# Clone and set up
git clone https://github.com/Venkatesh-6921/imprint-cli
cd imprint-cli

# Create virtual environment with uv
uv sync --extra dev

# Verify everything works
uv run ruff check .
uv run pytest tests/ -v
```

> **Note:** We use `uv` for package management. Do NOT use bare `pip` or `requirements.txt`.

---

## Git workflow

> **⚠️ Direct pushes to `main` are not allowed.** All changes go through pull requests.

### For every change — no matter how small:

```bash
# 1. Create a branch from latest main
git checkout main && git pull
git checkout -b fix/short-description     # or feat/, docs/, refactor/

# 2. Make your changes, then validate
uv run ruff check .
uv run pytest tests/ -v

# 3. Commit
git add -A
git commit -m "fix: what you changed and why"

# 4. Push your branch (never main)
git push origin fix/short-description

# 5. Open a Pull Request on GitHub
```

### Branch naming

| Prefix | Use for |
|---|---|
| `fix/` | Bug fixes |
| `feat/` | New features or collectors |
| `docs/` | Documentation only |
| `refactor/` | Code restructuring (no behavior change) |
| `test/` | Adding or improving tests |

### Releases (maintainers only)

Version bumps and PyPI releases happen via tags on `main`:

```bash
# After merging PRs, on main:
git tag v3.x.x
git push origin main --tags    # triggers OIDC PyPI publish via CI
```

---

## Adding a new collector

1. Create `imprint/collectors/your_tool.py`:

```python
"""Collect YourTool configuration."""

from __future__ import annotations

from pathlib import Path


def collect(home_dir: Path) -> dict:
    """Collect YourTool config data.

    Args:
        home_dir: User home directory.

    Returns:
        Dict with tool configuration data.
    """
    config_path = home_dir / ".config" / "yourtool" / "config"
    if not config_path.exists():
        return {}

    # Parse and return relevant data
    return {
        "version": "...",
        "plugins": [...],
    }
```

2. Add it to `imprint/snapshot.py` collector imports and collection logic.
3. Add the section to `imprint/manifest.py` dataclass fields.
4. Write tests in `tests/test_collectors.py`.
5. Update `CHANGELOG.md` under `[Unreleased]`.

---

## Code style

- **Python 3.11+** — use modern syntax (match/case, `X | Y` unions, etc.)
- **Linter:** `ruff` with rules `E, F, I, N, W, UP` — line length 100
- **Dependencies:** `click`, `rich`, `textual`, `gitpython`, `pyyaml`, `tomli_w` — keep it minimal
- **Separation:** Collectors read data, installers apply data, CLI orchestrates
- **Security:** NEVER capture secrets, keys, or passwords. Always route through `safety.py`

---

## Security guidelines

When adding a new collector, ensure:

- ❌ No SSH private keys, API tokens, or passwords are ever captured
- ❌ No `shell=True` in subprocess calls
- ❌ No `eval()` or `exec()` on user data
- ✅ All file paths go through `filter_safe_files()` from `utils/safety.py`
- ✅ Sensitive data patterns are in `.imprintignore.default`

---

## Reporting a bug

Open an issue with:
- Your OS and Python version
- The command you ran and the full error traceback
- Output of `imp doctor` if possible

---

## License

By contributing, you agree your changes are licensed under MIT.
