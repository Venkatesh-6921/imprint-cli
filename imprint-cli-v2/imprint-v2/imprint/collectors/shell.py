"""
Collector: Shell configuration.
Detects shell type, version, framework, theme, plugins.
"""

from __future__ import annotations

import os
import platform
import re
import subprocess
from pathlib import Path


def collect(home_dir: Path | None = None) -> dict:
    """Collect shell configuration info.

    Args:
        home_dir: User's home directory.

    Returns:
        Dict with shell type, version, framework, theme, plugins, alias/function counts.
    """
    if home_dir is None:
        home_dir = Path.home()

    shell_type = _detect_shell()
    shell_version = _get_shell_version(shell_type)

    result: dict = {
        "type": shell_type,
        "version": shell_version,
    }

    if shell_type == "zsh":
        zshrc = home_dir / ".zshrc"
        if zshrc.exists():
            content = zshrc.read_text(encoding="utf-8", errors="replace")
            result["framework"] = _detect_zsh_framework(content, home_dir)
            result["theme"] = _extract_zsh_theme(content)
            result["plugins"] = _extract_zsh_plugins(content)
            result["custom_aliases"] = _count_aliases(content)
            result["custom_functions"] = _count_functions(content)
    elif shell_type == "bash":
        bashrc = home_dir / ".bashrc"
        if bashrc.exists():
            content = bashrc.read_text(encoding="utf-8", errors="replace")
            result["custom_aliases"] = _count_aliases(content)
            result["custom_functions"] = _count_functions(content)
    elif shell_type == "powershell":
        result["custom_aliases"] = 0
        result["custom_functions"] = 0

    return result


def _detect_shell() -> str:
    """Detect the current shell type."""
    if platform.system() == "Windows":
        return "powershell"

    shell = os.environ.get("SHELL", "")
    if "zsh" in shell:
        return "zsh"
    elif "bash" in shell:
        return "bash"
    elif "fish" in shell:
        return "fish"
    return os.path.basename(shell) if shell else "unknown"


def _get_shell_version(shell_type: str) -> str | None:
    """Get shell version."""
    cmd_map = {
        "zsh": ["zsh", "--version"],
        "bash": ["bash", "--version"],
        "fish": ["fish", "--version"],
        "powershell": ["powershell", "-Command", "$PSVersionTable.PSVersion.ToString()"],
    }
    cmd = cmd_map.get(shell_type)
    if not cmd:
        return None
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True).strip()
        # Extract version number from "zsh 5.9 (x86_64-ubuntu-linux-gnu)"
        parts = output.split()
        for part in parts:
            if part[0].isdigit():
                return part
        return output.split("\n")[0]
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def _detect_zsh_framework(content: str, home_dir: Path) -> str | None:
    """Detect zsh framework (oh-my-zsh, prezto, etc.)."""
    if "oh-my-zsh" in content or (home_dir / ".oh-my-zsh").is_dir():
        return "oh-my-zsh"
    if "prezto" in content or (home_dir / ".zprezto").is_dir():
        return "prezto"
    if "zinit" in content or "zdharma" in content:
        return "zinit"
    if "antigen" in content:
        return "antigen"
    return None


def _extract_zsh_theme(content: str) -> str | None:
    """Extract ZSH_THEME from .zshrc."""
    match = re.search(r'ZSH_THEME\s*=\s*"([^"]+)"', content)
    return match.group(1) if match else None


def _extract_zsh_plugins(content: str) -> list[str]:
    """Extract plugins list from .zshrc."""
    match = re.search(r"plugins\s*=\s*\(([^)]+)\)", content)
    if match:
        plugins_str = match.group(1)
        return [p.strip() for p in plugins_str.split() if p.strip()]
    return []


def _count_aliases(content: str) -> int:
    """Count alias definitions in shell config."""
    return len(re.findall(r"^\s*alias\s+", content, re.MULTILINE))


def _count_functions(content: str) -> int:
    """Count function definitions in shell config."""
    return len(re.findall(r"^\s*(?:function\s+\w+|(\w+)\s*\(\s*\))", content, re.MULTILINE))
