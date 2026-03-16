"""
Installer: Shell setup.
Provides guidance for setting up the shell on restore.
"""

from __future__ import annotations

from rich.console import Console

console = Console()


def install(shell_data: dict) -> None:
    """Print shell setup instructions based on the manifest's shell config.

    Args:
        shell_data: Shell configuration dict from the manifest.
    """
    shell_type = shell_data.get("type", "unknown")
    framework = shell_data.get("framework")

    if shell_type == "zsh":
        if framework == "oh-my-zsh":
            console.print("  [blue]💡 oh-my-zsh detected in your snapshot.[/blue]")
            console.print("     Install: sh -c \"$(curl -fsSL "
                          "https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/"
                          "master/tools/install.sh)\"")

        plugins = shell_data.get("plugins", [])
        if plugins:
            console.print(f"  [blue]💡 Plugins to install: {', '.join(plugins)}[/blue]")

        theme = shell_data.get("theme")
        if theme:
            console.print(f"  [blue]💡 Theme: {theme}[/blue]")

    elif shell_type == "bash":
        console.print("  [blue]💡 Your .bashrc has been symlinked.[/blue]")
        console.print("     Run: source ~/.bashrc")

    elif shell_type == "powershell":
        console.print("  [blue]💡 PowerShell profile has been restored.[/blue]")
        console.print("     Restart PowerShell to apply changes.")

    console.print(
        "  [dim]Run 'source ~/.zshrc' or restart your terminal to activate.[/dim]"
    )
