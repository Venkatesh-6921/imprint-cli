"""
Installer: Dotfiles.
Symlinks dotfiles from ~/.imprint/dotfiles/ to the home directory.
"""

from __future__ import annotations

import os
import platform
from pathlib import Path


def install(
    dotfiles_dir: Path, home_dir: Path, dotfile_names: list[str]
) -> list[tuple[str, str, str]]:
    """Symlink dotfiles to the home directory.

    Args:
        dotfiles_dir: Path to ~/.imprint/dotfiles/.
        home_dir: User's home directory.
        dotfile_names: List of dotfile filenames to install.

    Returns:
        List of (name, status, detail) tuples.
    """
    results: list[tuple[str, str, str]] = []

    for name in dotfile_names:
        src = dotfiles_dir / name
        dest = home_dir / name

        if not src.exists():
            results.append((name, "failed", f"Source not found: {src}"))
            continue

        # Handle nested paths (e.g., Documents/PowerShell/profile.ps1)
        dest.parent.mkdir(parents=True, exist_ok=True)

        if dest.exists() or dest.is_symlink():
            if dest.is_symlink():
                # Already a symlink — update it
                dest.unlink()
                _create_symlink(src, dest)
                results.append((name, "ok", "Updated symlink"))
            else:
                # Existing file — skip to avoid data loss
                results.append(
                    (name, "skipped", f"File already exists at {dest} — not overwriting")
                )
        else:
            _create_symlink(src, dest)
            results.append((name, "ok", f"Symlinked → {dest}"))

    return results


def _create_symlink(src: Path, dest: Path) -> None:
    """Create a symbolic link, handling Windows compatibility."""
    if platform.system() == "Windows":
        # On Windows, symlinks may require admin privileges
        # Fall back to copy if symlink fails
        try:
            os.symlink(src, dest)
        except OSError:
            import shutil
            shutil.copy2(src, dest)
    else:
        os.symlink(src, dest)
