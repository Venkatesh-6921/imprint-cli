"""
Installer: VS Code extensions.
Installs extensions using the `code` CLI.
"""

from __future__ import annotations

import subprocess


def install(extensions: list[str]) -> list[tuple[str, str, str]]:
    """Install VS Code extensions.

    Args:
        extensions: List of extension IDs (e.g., "ms-python.python").

    Returns:
        List of (extension_id, status, detail) tuples.
    """
    results: list[tuple[str, str, str]] = []

    for ext in extensions:
        # Strip version if present (e.g., "ms-python.python@2024.1.1" → "ms-python.python")
        ext_id = ext.split("@")[0] if "@" in ext else ext
        try:
            subprocess.check_output(
                ["code", "--install-extension", ext_id, "--force"],
                stderr=subprocess.DEVNULL,
                text=True,
            )
            results.append((ext_id, "ok", "Installed"))
        except FileNotFoundError:
            results.append((ext_id, "failed", "VS Code CLI not found"))
            break  # No point trying more if code CLI isn't available
        except subprocess.CalledProcessError as e:
            results.append((ext_id, "failed", f"Install failed: {e}"))

    return results
