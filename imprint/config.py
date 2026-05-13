"""
Imprint configuration management.
v3: Named profiles, per-profile imprint dirs, theme setting.
"""

from __future__ import annotations

import shutil
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import tomli_w

_DEFAULT_PROFILE = "default"


@dataclass
class ImprintConfig:
    """Core configuration for Imprint. Supports named profiles."""

    base_dir: Path = field(
        default_factory=lambda: Path.home() / ".imprint"
    )
    home_dir: Path = field(default_factory=Path.home)
    profile: str = _DEFAULT_PROFILE
    github_repo: str | None = None
    github_branch: str = "main"
    encrypt: bool = False        # encrypt dotfiles before push
    auto_push: bool = True       # push on snapshot by default
    theme: str = "nord"          # future: allow alternate themes

    # ── Derived paths ─────────────────────────────────────

    @property
    def imprint_dir(self) -> Path:
        if self.profile == _DEFAULT_PROFILE:
            return self.base_dir
        return self.base_dir / "profiles" / self.profile

    @property
    def config_path(self) -> Path:
        return self.base_dir / "config.toml"

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

    @property
    def key_path(self) -> Path:
        """Path to the per-profile AES key file (never committed)."""
        return self.imprint_dir / ".imprint.key"

    # ── Directory management ──────────────────────────────

    def ensure_dirs(self) -> None:
        for d in (
            self.imprint_dir,
            self.dotfiles_dir,
            self.scripts_dir,
            self.snapshots_dir,
        ):
            d.mkdir(parents=True, exist_ok=True)

    # ── Persistence ───────────────────────────────────────

    def save(self) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)
        data: dict = {
            "profile":       self.profile,
            "github_branch": self.github_branch,
            "auto_push":     self.auto_push,
            "encrypt":       self.encrypt,
            "theme":         self.theme,
        }
        if self.github_repo:
            data["github_repo"] = self.github_repo
        self.config_path.write_bytes(
            tomli_w.dumps(data).encode()
        )

    @classmethod
    def load(
        cls, profile: str | None = None
    ) -> ImprintConfig:
        config = cls()
        if config.config_path.exists():
            with open(config.config_path, "rb") as f:
                data = tomllib.load(f)
            config.github_repo = data.get("github_repo")
            config.github_branch = data.get(
                "github_branch", "main"
            )
            config.auto_push = data.get("auto_push", True)
            config.encrypt = data.get("encrypt", False)
            config.theme = data.get("theme", "nord")
            config.profile = data.get(
                "profile", _DEFAULT_PROFILE
            )

        # CLI --profile flag overrides saved profile
        if profile:
            config.profile = profile

        config.ensure_dirs()
        _bootstrap_imprintignore(config)
        return config

    # ── Profile helpers ───────────────────────────────────

    def list_profiles(self) -> list[str]:
        profiles = [_DEFAULT_PROFILE]
        profiles_dir = self.base_dir / "profiles"
        if profiles_dir.exists():
            profiles += [
                d.name
                for d in profiles_dir.iterdir()
                if d.is_dir()
            ]
        return profiles

    def create_profile(self, name: str) -> None:
        profile_dir = self.base_dir / "profiles" / name
        profile_dir.mkdir(parents=True, exist_ok=True)

    def delete_profile(self, name: str) -> None:
        if name == _DEFAULT_PROFILE:
            raise ValueError(
                "Cannot delete the default profile."
            )
        profile_dir = self.base_dir / "profiles" / name
        if profile_dir.exists():
            shutil.rmtree(profile_dir)


def _bootstrap_imprintignore(
    config: ImprintConfig,
) -> None:
    """Copy default .imprintignore into the profile dir if missing."""
    if not config.imprintignore_path.exists():
        default = (
            Path(__file__).parent.parent
            / ".imprintignore.default"
        )
        if default.exists():
            shutil.copy2(default, config.imprintignore_path)
        else:
            config.imprintignore_path.write_text(
                _DEFAULT_IGNORE, encoding="utf-8"
            )


_DEFAULT_IGNORE = """\
# .imprintignore — Never snapshot these files
.ssh/id_*
.ssh/*.pem
.ssh/*.key
.env
.env.*
*.token
*secret*
*password*
*credential*
*api_key*
.gnupg/
.bash_history
.zsh_history
.aws/credentials
.gcloud/
.kube/
.cache/
.npm/
node_modules/
"""
