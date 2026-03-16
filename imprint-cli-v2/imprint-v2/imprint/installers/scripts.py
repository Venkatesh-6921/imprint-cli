"""
Installer: Custom scripts.
Copies scripts to ~/bin/ and makes them executable.
"""

from __future__ import annotations

import os
import platform
import shutil
import stat
from pathlib import Path


def install(scripts_dir: Path, bin_dir: Path, script_names: list[str]) -> None:
    """Restore custom scripts to ~/bin/.

    Args:
        scripts_dir: Path to ~/.imprint/scripts/.
        bin_dir: Destination directory (~/bin/).
        script_names: List of script filenames to restore.
    """
    bin_dir.mkdir(parents=True, exist_ok=True)

    for name in script_names:
        src = scripts_dir / name
        dest = bin_dir / name

        if not src.exists():
            continue

        shutil.copy2(src, dest)

        # Make executable on Unix-like systems
        if platform.system() != "Windows":
            current_mode = dest.stat().st_mode
            dest.chmod(current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
