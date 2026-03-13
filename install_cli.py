"""
Install script — copies imp.bat to a directory on the system PATH
so that `imp snapshot`, `imp diff`, etc. work directly in terminal.
"""

import shutil
import sys
import sysconfig
from pathlib import Path


def install_wrapper():
    """Copy imp.bat to the Python Scripts directory (which is usually in PATH)."""
    scripts_dir = Path(sysconfig.get_path("scripts"))
    source_dir = Path(__file__).parent / "scripts"

    bat_src = source_dir / "imp.bat"
    bat_dest = scripts_dir / "imp.bat"

    print(f"Installing imp.bat to: {bat_dest}")
    shutil.copy2(bat_src, bat_dest)
    print("✅ Done! You can now run 'imp snapshot', 'imp diff', etc. directly.")

    # Also check if Scripts dir is in PATH
    path_dirs = [p.lower() for p in (sys.prefix + "\\Scripts").split(";")]
    scripts_lower = str(scripts_dir).lower()
    path_env = [p.lower().strip() for p in (
        __import__("os").environ.get("PATH", "").split(";")
    )]

    if scripts_lower not in path_env:
        print(f"\n⚠ WARNING: {scripts_dir} is NOT in your PATH.")
        print("  Add it to your PATH by running this in PowerShell (Admin):")
        print(f'  [Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";{scripts_dir}", "User")')
        print("  Then restart your terminal.")


if __name__ == "__main__":
    install_wrapper()
