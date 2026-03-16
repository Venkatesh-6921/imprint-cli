"""
Collector: VS Code extensions and settings.
Works on Linux, macOS, Windows, and WSL.
"""

from __future__ import annotations

import platform
import subprocess
from pathlib import Path


def collect() -> dict:
    """Collect VS Code information: version, extensions, settings path."""
    settings_path = _get_settings_path()
    return {
        "version": _get_vscode_version(),
        "extensions": _get_extensions(),
        "settings_path": str(settings_path) if settings_path else None,
        "settings_included": settings_path is not None and settings_path.exists(),
    }


def _get_extensions() -> list[str]:
    """Get list of installed VS Code extensions with versions."""
    try:
        output = subprocess.check_output(
            ["code", "--list-extensions", "--show-versions"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return [line.strip() for line in output.strip().split("\n") if line.strip()]
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []


def _get_vscode_version() -> str | None:
    """Get VS Code version."""
    try:
        output = subprocess.check_output(
            ["code", "--version"], stderr=subprocess.DEVNULL, text=True
        )
        return output.split("\n")[0].strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def _get_settings_path() -> Path | None:
    """Find the VS Code settings.json path for the current platform."""
    system = platform.system()
    home = Path.home()

    candidates: dict[str, Path] = {
        "Linux": home / ".config/Code/User/settings.json",
        "Darwin": home / "Library/Application Support/Code/User/settings.json",
        "Windows": home / "AppData/Roaming/Code/User/settings.json",
    }

    path = candidates.get(system)
    return path if path and path.exists() else None
