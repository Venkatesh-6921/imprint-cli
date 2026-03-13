"""
Collector: Dotfiles.
Scans the home directory for known developer dotfiles.
"""

from __future__ import annotations

from pathlib import Path

# Known dotfiles to look for in the home directory
KNOWN_DOTFILES = [
    ".zshrc",
    ".bashrc",
    ".bash_profile",
    ".profile",
    ".gitconfig",
    ".gitignore_global",
    ".vimrc",
    ".tmux.conf",
    ".editorconfig",
    ".eslintrc.json",
    ".eslintrc.js",
    ".prettierrc",
    ".prettierrc.json",
    ".npmrc",
    ".yarnrc",
    ".wgetrc",
    ".curlrc",
    ".inputrc",
    ".screenrc",
    ".nanorc",
    ".pylintrc",
    ".flake8",
    ".pydistutils.cfg",
    # PowerShell profile (Windows support)
    "Documents/PowerShell/Microsoft.PowerShell_profile.ps1",
    "Documents/WindowsPowerShell/Microsoft.PowerShell_profile.ps1",
]


def collect(home_dir: Path | None = None) -> list[Path]:
    """Find all dotfiles present in the home directory.

    Args:
        home_dir: User's home directory. Defaults to Path.home().

    Returns:
        List of absolute paths to found dotfiles.
    """
    if home_dir is None:
        home_dir = Path.home()

    found: list[Path] = []

    for name in KNOWN_DOTFILES:
        path = home_dir / name
        if path.is_file():
            found.append(path)

    return found
