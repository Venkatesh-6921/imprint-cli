"""
Imprint configuration management.
Handles the ~/.imprint/ directory, config.toml, and user settings.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import tomli_w


@dataclass
class ImprintConfig:
    """Core configuration for Imprint."""

    imprint_dir: Path = field(default_factory=lambda: Path.home() / ".imprint")
    home_dir: Path = field(default_factory=Path.home)
    github_repo: str | None = None

    @property
    def config_path(self) -> Path:
        return self.imprint_dir / "config.toml"

    @property
    def manifest_path(self) -> Path:
        return self.imprint_dir / "environment.toml"

    @property
    def dotfiles_dir(self) -> Path:
        return self.imprint_dir / "dotfiles"

    @property
    def scripts_dir(self) -> Path:
        return self.imprint_dir / "scripts"

    @property
    def snapshots_dir(self) -> Path:
        return self.imprint_dir / "snapshots"

    @property
    def imprintignore_path(self) -> Path:
        return self.imprint_dir / ".imprintignore"

    def ensure_dirs(self) -> None:
        """Create the imprint directory structure if it doesn't exist."""
        self.imprint_dir.mkdir(parents=True, exist_ok=True)
        self.dotfiles_dir.mkdir(parents=True, exist_ok=True)
        self.scripts_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

    def save(self) -> None:
        """Save current config to config.toml."""
        self.ensure_dirs()
        data: dict = {}
        if self.github_repo:
            data["github_repo"] = self.github_repo
        data["imprint_dir"] = str(self.imprint_dir)
        self.config_path.write_bytes(tomli_w.dumps(data).encode())

    @classmethod
    def load(cls) -> ImprintConfig:
        """Load config from ~/.imprint/config.toml, or create defaults."""
        config = cls()
        if config.config_path.exists():
            with open(config.config_path, "rb") as f:
                data = tomllib.load(f)
            config.github_repo = data.get("github_repo")
            if "imprint_dir" in data:
                config.imprint_dir = Path(data["imprint_dir"])
        config.ensure_dirs()
        # Copy default .imprintignore if none exists
        if not config.imprintignore_path.exists():
            default_ignore = Path(__file__).parent.parent / ".imprintignore.default"
            if default_ignore.exists():
                import shutil
                shutil.copy2(default_ignore, config.imprintignore_path)
            else:
                # Write a minimal default
                config.imprintignore_path.write_text(_DEFAULT_IMPRINTIGNORE, encoding="utf-8")
        return config


_DEFAULT_IMPRINTIGNORE = """\
# .imprintignore — Never snapshot these files
# Format: one pattern per line, same as .gitignore

# SSH keys — NEVER include
.ssh/id_*
.ssh/*.pem
.ssh/*.key

# Tokens and secrets
.env
.env.*
*.token
*secret*
*password*
*credential*
*api_key*

# GPG keys
.gnupg/

# Shell history
.bash_history
.zsh_history

# Cloud credentials
.aws/credentials
.gcloud/
.kube/

# Caches
.cache/
.npm/
node_modules/
"""
