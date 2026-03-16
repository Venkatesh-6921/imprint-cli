"""
Platform detection utilities.
Identifies OS type: Linux, macOS, Windows, or WSL.
"""

from __future__ import annotations

import platform
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class OSType(Enum):
    LINUX = "linux"
    MACOS = "macos"
    WINDOWS = "windows"
    WSL = "wsl"


@dataclass
class PlatformInfo:
    """Detected platform information."""

    os_type: OSType
    os_name: str  # e.g. "Ubuntu", "macOS", "Windows"
    os_version: str  # e.g. "24.04", "14.5", "11"
    hostname: str
    username: str

    @property
    def package_manager(self) -> str:
        """Return the system package manager for this platform."""
        match self.os_type:
            case OSType.MACOS:
                return "brew"
            case OSType.WINDOWS:
                return "winget"
            case OSType.WSL | OSType.LINUX:
                return "apt"


def detect_platform() -> PlatformInfo:
    """Detect the current platform."""
    import getpass
    import socket

    system = platform.system()
    hostname = socket.gethostname()
    username = getpass.getuser()

    if system == "Linux":
        # Check for WSL
        if _is_wsl():
            os_type = OSType.WSL
        else:
            os_type = OSType.LINUX
        os_name, os_version = _get_linux_info()
    elif system == "Darwin":
        os_type = OSType.MACOS
        os_name = "macOS"
        os_version = platform.mac_ver()[0] or "unknown"
    elif system == "Windows":
        os_type = OSType.WINDOWS
        os_name = "Windows"
        os_version = platform.version()
    else:
        os_type = OSType.LINUX
        os_name = system
        os_version = platform.release()

    return PlatformInfo(
        os_type=os_type,
        os_name=os_name,
        os_version=os_version,
        hostname=hostname,
        username=username,
    )


def _is_wsl() -> bool:
    """Check if running inside Windows Subsystem for Linux."""
    try:
        with open("/proc/version", encoding="utf-8") as f:
            return "microsoft" in f.read().lower()
    except (FileNotFoundError, PermissionError):
        return False


def _get_linux_info() -> tuple[str, str]:
    """Get Linux distribution name and version."""
    try:
        with open("/etc/os-release", encoding="utf-8") as f:
            lines = f.readlines()
        info: dict[str, str] = {}
        for line in lines:
            if "=" in line:
                key, _, value = line.strip().partition("=")
                info[key] = value.strip('"')
        return info.get("NAME", "Linux"), info.get("VERSION_ID", "unknown")
    except FileNotFoundError:
        return "Linux", platform.release()
