"""
Collector: Custom scripts.
Lists files in the user's ~/bin/ directory.
"""

from __future__ import annotations

from pathlib import Path


def collect(home_dir: Path | None = None) -> list[Path]:
    """Collect custom scripts from ~/bin/.

    Args:
        home_dir: User's home directory.

    Returns:
        List of absolute paths to script files.
    """
    if home_dir is None:
        home_dir = Path.home()

    bin_dir = home_dir / "bin"
    if not bin_dir.is_dir():
        return []

    return [f for f in bin_dir.iterdir() if f.is_file()]
