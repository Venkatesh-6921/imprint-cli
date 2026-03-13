"""
Manifest — read/write environment.toml.
The centrepiece of Imprint: a human-readable description of the developer environment.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import tomli_w

from imprint.utils.platform import detect_platform


@dataclass
class Manifest:
    """Represents the full environment manifest (environment.toml)."""

    meta: dict = field(default_factory=dict)
    system: dict = field(default_factory=dict)
    dotfiles: list[str] = field(default_factory=list)
    shell: dict = field(default_factory=dict)
    vscode: dict = field(default_factory=dict)
    packages: dict = field(default_factory=dict)
    git: dict = field(default_factory=dict)
    scripts: list[str] = field(default_factory=list)
    fonts: dict = field(default_factory=dict)

    def set_meta(self, timestamp: str) -> None:
        """Populate meta section with current machine info."""
        from imprint import __version__

        info = detect_platform()
        self.meta = {
            "imprint_version": __version__,
            "snapshot_at": timestamp,
            "hostname": info.hostname,
            "os": info.os_name.lower(),
            "os_version": info.os_version,
            "username": info.username,
        }

    def to_dict(self) -> dict:
        """Convert manifest to a dict suitable for TOML serialization."""
        data: dict = {}
        if self.meta:
            data["meta"] = self.meta
        if self.system:
            data["system"] = self.system
        if self.dotfiles:
            data["dotfiles"] = {"files": self.dotfiles}
        if self.shell:
            data["shell"] = self.shell
        if self.vscode:
            # Filter out non-serializable keys
            vscode_data = {
                k: v for k, v in self.vscode.items() if k != "settings_path"
            }
            data["vscode"] = vscode_data
        if self.packages:
            data["packages"] = self.packages
        if self.git:
            data["git"] = self.git
        if self.scripts:
            data["scripts"] = {"files": self.scripts}
        if self.fonts:
            data["fonts"] = self.fonts
        return data

    def save(self, path: Path) -> None:
        """Write manifest to a TOML file."""
        data = self.to_dict()

        def _clean_dict(d: dict) -> dict:
            cleaned = {}
            for k, v in d.items():
                if v is None:
                    continue
                if isinstance(v, dict):
                    cleaned[k] = _clean_dict(v)
                elif isinstance(v, list):
                    cleaned[k] = [_clean_dict(i) if isinstance(i, dict) else i for i in v if i is not None]
                else:
                    cleaned[k] = v
            return cleaned

        data = _clean_dict(data)
        path.write_bytes(tomli_w.dumps(data).encode())

    @classmethod
    def load(cls, path: Path) -> Manifest:
        """Load manifest from a TOML file."""
        with open(path, "rb") as f:
            data = tomllib.load(f)

        manifest = cls()
        manifest.meta = data.get("meta", {})
        manifest.system = data.get("system", {})

        dotfiles_section = data.get("dotfiles", {})
        if isinstance(dotfiles_section, dict):
            manifest.dotfiles = dotfiles_section.get("files", [])
        elif isinstance(dotfiles_section, list):
            manifest.dotfiles = dotfiles_section

        manifest.shell = data.get("shell", {})
        manifest.vscode = data.get("vscode", {})
        manifest.packages = data.get("packages", {})
        manifest.git = data.get("git", {})

        scripts_section = data.get("scripts", {})
        if isinstance(scripts_section, dict):
            manifest.scripts = scripts_section.get("files", [])
        elif isinstance(scripts_section, list):
            manifest.scripts = scripts_section

        manifest.fonts = data.get("fonts", {})
        return manifest
