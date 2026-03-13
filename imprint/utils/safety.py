"""
Safety module — .imprintignore parsing and file filtering.
Ensures sensitive files (SSH keys, tokens, credentials) are NEVER included.
"""

from __future__ import annotations

import fnmatch
from pathlib import Path


# Hard-coded patterns that are ALWAYS excluded, regardless of .imprintignore
_ALWAYS_EXCLUDE = [
    ".ssh/id_*",
    ".ssh/*.pem",
    ".ssh/*.key",
    "*.env",
    ".env.*",
    "*secret*",
    "*password*",
    "*credential*",
    "*api_key*",
    "*_token",
    "*.token",
    ".gnupg/*",
    ".bash_history",
    ".zsh_history",
]


def load_ignore_patterns(imprintignore_path: Path) -> list[str]:
    """Load patterns from .imprintignore file.

    Merges file patterns with the hard-coded always-exclude list.
    Returns list of glob patterns.
    """
    patterns = list(_ALWAYS_EXCLUDE)

    if imprintignore_path.exists():
        for line in imprintignore_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                patterns.append(line)

    return patterns


def is_safe_file(file_path: Path, home_dir: Path, patterns: list[str]) -> bool:
    """Check if a file is safe to include in a snapshot.

    Args:
        file_path: Absolute path to the file.
        home_dir: User's home directory for computing relative paths.
        patterns: List of glob patterns to exclude.

    Returns:
        True if the file is safe, False if it matches an exclude pattern.
    """
    try:
        rel_path = file_path.relative_to(home_dir)
    except ValueError:
        rel_path = file_path

    rel_str = str(rel_path).replace("\\", "/")
    name = file_path.name

    for pattern in patterns:
        # Match against relative path
        if fnmatch.fnmatch(rel_str, pattern):
            return False
        # Match against just the filename
        if fnmatch.fnmatch(name, pattern):
            return False
        # Match against path components
        if "/" in pattern and fnmatch.fnmatch(rel_str, f"*/{pattern}"):
            return False

    return True


def filter_safe_files(
    files: list[Path], imprintignore_path: Path, home_dir: Path | None = None
) -> list[Path]:
    """Filter a list of file paths, removing any that match ignore patterns.

    Args:
        files: List of absolute file paths.
        imprintignore_path: Path to .imprintignore file.
        home_dir: User's home directory (defaults to Path.home()).

    Returns:
        List of safe file paths.
    """
    if home_dir is None:
        home_dir = Path.home()

    patterns = load_ignore_patterns(imprintignore_path)
    return [f for f in files if is_safe_file(f, home_dir, patterns)]
