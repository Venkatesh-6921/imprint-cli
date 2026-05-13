"""
Manifest — read/write environment.toml.
v3: new collector sections, multi-format export.
"""

from __future__ import annotations

import json
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import tomli_w
import yaml

from imprint.utils.platform import detect_platform


@dataclass
class Manifest:
    meta:     dict = field(default_factory=dict)
    system:   dict = field(default_factory=dict)
    dotfiles: list[str] = field(default_factory=list)
    shell:    dict = field(default_factory=dict)
    vscode:   dict = field(default_factory=dict)
    packages: dict = field(default_factory=dict)
    git:      dict = field(default_factory=dict)
    scripts:  list[str] = field(default_factory=list)
    fonts:    dict = field(default_factory=dict)
    # v3 additions
    neovim:     dict = field(default_factory=dict)
    cursor:     dict = field(default_factory=dict)
    tmux:       dict = field(default_factory=dict)
    ssh_config: dict = field(default_factory=dict)

    def set_meta(
        self,
        timestamp: str,
        profile: str = "default",
    ) -> None:
        from imprint import __version__

        info = detect_platform()
        self.meta = {
            "imprint_version": __version__,
            "snapshot_at":     timestamp,
            "profile":         profile,
            "hostname":        info.hostname,
            "os":              info.os_name.lower(),
            "os_version":      info.os_version,
            "username":        info.username,
        }

    def to_dict(self) -> dict:
        data: dict = {}
        for key in (
            "meta", "system", "shell", "vscode",
            "packages", "git", "fonts", "neovim",
            "cursor", "tmux", "ssh_config",
        ):
            val = getattr(self, key)
            if val:
                if key == "vscode":
                    data[key] = {
                        k: v
                        for k, v in val.items()
                        if k != "settings_path"
                    }
                else:
                    data[key] = val
        if self.dotfiles:
            data["dotfiles"] = {"files": self.dotfiles}
        if self.scripts:
            data["scripts"] = {"files": self.scripts}
        return data

    def save(self, path: Path) -> None:
        data = _clean(self.to_dict())
        path.write_bytes(tomli_w.dumps(data).encode())

    @classmethod
    def load(cls, path: Path) -> Manifest:
        with open(path, "rb") as f:
            data = tomllib.load(f)
        m = cls()
        for key in (
            "meta", "system", "shell", "vscode",
            "packages", "git", "fonts", "neovim",
            "cursor", "tmux", "ssh_config",
        ):
            setattr(m, key, data.get(key, {}))

        def _list_section(key: str) -> list[str]:
            s = data.get(key, {})
            if isinstance(s, dict):
                return s.get("files", [])
            return s if isinstance(s, list) else []

        m.dotfiles = _list_section("dotfiles")
        m.scripts = _list_section("scripts")
        return m

    # ── Export ────────────────────────────────────────────

    def export_json(self, path: Path) -> None:
        path.write_text(
            json.dumps(
                self.to_dict(), indent=2, default=str
            ),
            encoding="utf-8",
        )

    def export_yaml(self, path: Path) -> None:
        path.write_text(
            yaml.dump(
                self.to_dict(),
                allow_unicode=True,
                sort_keys=False,
            ),
            encoding="utf-8",
        )

    def export_markdown(self, path: Path) -> None:
        lines: list[str] = []
        snap = self.meta.get("snapshot_at", "unknown")
        host = self.meta.get("hostname", "unknown")
        os_ = (
            f"{self.meta.get('os', '?')} "
            f"{self.meta.get('os_version', '')}"
        ).strip()
        ver = self.meta.get("imprint_version", "?")
        prof = self.meta.get("profile", "default")

        lines += [
            f"# Developer Environment — {host}",
            "",
            (
                f"> Captured by **imprint v{ver}** "
                f"on `{snap}`  ·  Profile: `{prof}`"
            ),
            "",
            "## System",
            "",
            "| Key | Value |",
            "|-----|-------|",
            f"| OS | {os_} |",
            (
                f"| Python | "
                f"{self.system.get('python_version', 'n/a')}"
                f" |"
            ),
            (
                f"| Node | "
                f"{self.system.get('node_version', 'n/a')}"
                f" |"
            ),
            (
                f"| Git | "
                f"{self.system.get('git_version', 'n/a')}"
                f" |"
            ),
            "",
        ]

        # Dotfiles
        if self.dotfiles:
            lines += ["## Dotfiles", ""]
            for f in sorted(self.dotfiles):
                lines.append(f"- `{f}`")
            lines.append("")

        # Packages
        for pm_name, pm_data in self.packages.items():
            pkgs = (
                pm_data.get("packages", [])
                if isinstance(pm_data, dict)
                else []
            )
            if pkgs:
                lines += [f"## Packages — {pm_name}", ""]
                for p in sorted(pkgs):
                    lines.append(f"- `{p}`")
                lines.append("")

        # VS Code
        exts = self.vscode.get("extensions", [])
        if exts:
            lines += ["## VS Code Extensions", ""]
            for e in sorted(exts):
                lines.append(f"- `{e}`")
            lines.append("")

        # Shell
        if self.shell:
            lines += ["## Shell", ""]
            for k, v in self.shell.items():
                lines.append(f"**{k}:** {v}")
            lines.append("")

        # Git
        if self.git:
            lines += ["## Git Config", ""]
            for k, v in self.git.items():
                lines.append(f"**{k}:** {v}")
            lines.append("")

        # Neovim
        if self.neovim:
            lines += ["## Neovim", ""]
            plugins = self.neovim.get("plugins", [])
            if plugins:
                for p in plugins:
                    lines.append(f"- `{p}`")
            lines.append("")

        path.write_text(
            "\n".join(lines), encoding="utf-8"
        )

    def export_shell_script(self, path: Path) -> None:
        """Generate a standalone install.sh."""
        snap = self.meta.get("snapshot_at", "unknown")
        lines = [
            "#!/usr/bin/env bash",
            "# Generated by imprint v3 — env restore",
            f"# Snapshot: {snap}",
            "",
            "set -euo pipefail",
            "",
        ]

        # pip
        pip_pkgs = (
            self.packages.get("pip", {})
            .get("packages", [])
        )
        if pip_pkgs:
            lines += [
                "echo '→ Installing pip packages...'",
                f"pip install {' '.join(pip_pkgs)}",
                "",
            ]

        # npm
        npm_pkgs = (
            self.packages.get("npm", {})
            .get("packages", [])
        )
        if npm_pkgs:
            lines += [
                "echo '→ Installing npm global packages...'",
                f"npm install -g {' '.join(npm_pkgs)}",
                "",
            ]

        # VS Code
        exts = self.vscode.get("extensions", [])
        if exts:
            lines += [
                "echo '→ Installing VS Code extensions...'"
            ]
            for ext in exts:
                lines.append(
                    f"code --install-extension {ext} --force"
                )
            lines.append("")

        lines += ["echo '✓ Done!'"]
        path.write_text(
            "\n".join(lines), encoding="utf-8"
        )
        path.chmod(0o755)


def _clean(d: dict) -> dict:
    cleaned = {}
    for k, v in d.items():
        if v is None:
            continue
        if isinstance(v, dict):
            cleaned[k] = _clean(v)
        elif isinstance(v, list):
            cleaned[k] = [
                _clean(i) if isinstance(i, dict) else i
                for i in v
                if i is not None
            ]
        else:
            cleaned[k] = v
    return cleaned
