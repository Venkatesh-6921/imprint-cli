"""
Collector: System information.
Detects Python, Node, Git versions and OS info.
"""

from __future__ import annotations

import platform
import subprocess


def collect() -> dict:
    """Collect system information."""
    return {
        "python_version": platform.python_version(),
        "node_version": _get_version(["node", "--version"]),
        "git_version": _get_version(["git", "--version"]),
    }


def _get_version(cmd: list[str]) -> str | None:
    """Run a command and extract the version string."""
    try:
        output = subprocess.check_output(
            cmd, stderr=subprocess.DEVNULL, text=True
        ).strip()
        # Handle "git version 2.45.1" or "v20.14.0"
        parts = output.split()
        version = parts[-1] if parts else output
        return version.lstrip("v")
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
