"""
Installer: System, pip, and npm packages.
Handles apt, brew, winget, pip, and npm installations.
"""

from __future__ import annotations

import subprocess

from rich.console import Console

console = Console()


def install_system(packages: list[str], manager: str) -> list[tuple[str, str, str]]:
    """Install system packages using the detected package manager.

    Args:
        packages: List of package names.
        manager: Package manager name (apt, brew, winget).

    Returns:
        List of (package, status, detail) tuples.
    """
    results: list[tuple[str, str, str]] = []

    match manager:
        case "apt":
            try:
                subprocess.check_call(
                    ["sudo", "apt-get", "install", "-y"] + packages,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                results.append(("system packages", "ok", f"{len(packages)} via apt"))
            except (FileNotFoundError, subprocess.CalledProcessError) as e:
                results.append(("system packages", "failed", str(e)))
        case "brew":
            try:
                subprocess.check_call(
                    ["brew", "install"] + packages,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                results.append(("system packages", "ok", f"{len(packages)} via brew"))
            except (FileNotFoundError, subprocess.CalledProcessError) as e:
                results.append(("system packages", "failed", str(e)))
        case "winget":
            installed = 0
            for i, pkg in enumerate(packages, 1):
                try:
                    console.print(f"  [dim]({i}/{len(packages)}) winget install {pkg}...[/dim]", end="\r")
                    subprocess.check_call(
                        ["winget", "install", "--id", pkg, "-e", "--silent",
                         "--accept-source-agreements", "--accept-package-agreements"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    installed += 1
                except (FileNotFoundError, subprocess.CalledProcessError):
                    pass
            # Clear line
            console.print(" " * 60, end="\r")
            results.append(("system packages", "ok", f"{installed}/{len(packages)} via winget"))
        case _:
            results.append(("system packages", "skipped", f"Unknown manager: {manager}"))

    return results


def install_pip(packages: list[str]) -> None:
    """Install pip packages globally."""
    if not packages:
        return
    for i, pkg in enumerate(packages, 1):
        try:
            console.print(f"  [dim]({i}/{len(packages)}) pip install {pkg}...[/dim]", end="\r")
            subprocess.check_call(
                ["pip", "install", pkg],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
    console.print(" " * 60, end="\r")


def install_npm(packages: list[str]) -> None:
    """Install npm packages globally."""
    if not packages:
        return
    for i, pkg in enumerate(packages, 1):
        try:
            console.print(f"  [dim]({i}/{len(packages)}) npm install {pkg}...[/dim]", end="\r")
            subprocess.check_call(
                ["npm", "install", "-g", pkg],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
    console.print(" " * 60, end="\r")
