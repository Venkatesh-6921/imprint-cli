"""
Collector: Installed packages.
Collects pip (global), npm (global), and system packages (apt/brew/winget).
"""

from __future__ import annotations

import json
import platform
import subprocess


# pip packages that ship with Python — don't snapshot these
PIP_STDLIB = {"pip", "setuptools", "wheel", "pkg_resources", "distutils"}


def collect() -> dict:
    """Collect all installed package information.

    Returns:
        Dict with pip, npm, and system package lists.
    """
    return {
        "pip": {"packages": _get_pip_packages()},
        "npm": {"packages": _get_npm_packages()},
        "system": {
            "manager": _get_system_manager(),
            "packages": _get_system_packages(),
        },
    }


def _get_pip_packages() -> list[str]:
    """Get globally installed pip packages (non-stdlib, non-dependency)."""
    try:
        output = subprocess.check_output(
            ["pip", "list", "--format=freeze", "--not-required"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        packages = []
        for line in output.strip().split("\n"):
            if line and not any(std in line.lower() for std in PIP_STDLIB):
                packages.append(line.strip())
        return packages
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []


def _get_npm_packages() -> list[str]:
    """Get globally installed npm packages."""
    try:
        output = subprocess.check_output(
            ["npm", "list", "-g", "--depth=0", "--json"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        data = json.loads(output)
        deps = data.get("dependencies", {})
        return [f"{name}@{info.get('version', 'latest')}" for name, info in deps.items()]
    except (FileNotFoundError, subprocess.CalledProcessError, json.JSONDecodeError):
        return []


def _get_system_manager() -> str:
    """Detect the system package manager."""
    system = platform.system()
    if system == "Darwin":
        return "brew"
    elif system == "Windows":
        return "winget"
    return "apt"


def _get_system_packages() -> list[str]:
    """Get manually installed system packages."""
    manager = _get_system_manager()
    match manager:
        case "brew":
            return _get_brew_packages()
        case "winget":
            return _get_winget_packages()
        case _:
            return _get_apt_packages()


def _get_brew_packages() -> list[str]:
    """Get Homebrew formula list."""
    try:
        output = subprocess.check_output(["brew", "list", "--formula"], text=True)
        return [p.strip() for p in output.strip().split("\n") if p.strip()]
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []


def _get_apt_packages() -> list[str]:
    """Get manually installed apt packages (not auto-installed dependencies)."""
    try:
        output = subprocess.check_output(
            ["apt-mark", "showmanual"], text=True, stderr=subprocess.DEVNULL
        )
        return sorted([p.strip() for p in output.strip().split("\n") if p.strip()])
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []


def _get_winget_packages() -> list[str]:
    """Get winget installed packages (Windows) using JSON export."""
    import tempfile
    import os
    from pathlib import Path
    
    try:
        tmp_json = Path(tempfile.gettempdir()) / f"winget_export_{os.getpid()}.json"
        if tmp_json.exists():
            tmp_json.unlink()
            
        subprocess.check_call(
            ["winget", "export", "-o", str(tmp_json), "--accept-source-agreements"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        
        with open(tmp_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        packages = []
        for source in data.get("Sources", []):
            for pkg in source.get("Packages", []):
                identifier = pkg.get("PackageIdentifier")
                if identifier:
                    packages.append(identifier)
                    
        if tmp_json.exists():
            tmp_json.unlink()
            
        return packages
    except (Exception):
        return []
