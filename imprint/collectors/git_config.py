"""
Collector: Git configuration.
Reads user.name, user.email, core.editor, init.defaultBranch from git config.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def collect(home_dir: Path | None = None) -> dict:
    """Collect Git configuration.

    Args:
        home_dir: User's home directory (for checking .gitconfig existence).

    Returns:
        Dict with Git config values.
    """
    if home_dir is None:
        home_dir = Path.home()

    result: dict = {}

    for key in ["user.name", "user.email", "core.editor", "init.defaultBranch"]:
        value = _get_git_config(key)
        if value:
            # Convert "user.name" → "user_name"
            result_key = key.replace(".", "_")
            result[result_key] = value

    # Check for .gitignore_global
    gitignore_global = _get_git_config("core.excludesFile")
    if gitignore_global:
        result["excludes_file"] = gitignore_global

    return result


def _get_git_config(key: str) -> str | None:
    """Read a single git config value."""
    try:
        output = subprocess.check_output(
            ["git", "config", "--global", key],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        return output if output else None
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
