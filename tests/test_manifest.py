"""Tests for the Manifest class — TOML round-trip and loading."""

import tempfile
from pathlib import Path

from imprint.manifest import Manifest


def test_manifest_round_trip(tmp_path: Path) -> None:
    """Write → read → write produces identical TOML."""
    manifest = Manifest()
    manifest.meta = {
        "imprint_version": "1.0.0",
        "snapshot_at": "2025-06-15_14-30-00",
        "hostname": "test-host",
        "os": "ubuntu",
        "os_version": "24.04",
        "username": "testuser",
    }
    manifest.system = {
        "python_version": "3.11.9",
        "node_version": "20.14.0",
        "git_version": "2.45.1",
    }
    manifest.dotfiles = [".zshrc", ".gitconfig", ".vimrc"]
    manifest.vscode = {
        "version": "1.90.0",
        "extensions": ["ms-python.python", "eamodio.gitlens"],
        "settings_included": True,
    }
    manifest.packages = {
        "pip": {"packages": ["black==24.4.2", "ruff==0.4.7"]},
        "npm": {"packages": ["typescript@5.4.5"]},
        "system": {"manager": "apt", "packages": ["git", "curl"]},
    }
    manifest.git = {"user_name": "Test User", "user_email": "test@example.com"}
    manifest.scripts = ["deploy.sh", "backup.sh"]

    # Write
    path1 = tmp_path / "env1.toml"
    manifest.save(path1)

    # Read
    loaded = Manifest.load(path1)

    # Write again
    path2 = tmp_path / "env2.toml"
    loaded.save(path2)

    # Compare
    assert path1.read_bytes() == path2.read_bytes()


def test_manifest_load_fields(tmp_path: Path) -> None:
    """Loaded manifest has all the correct field values."""
    manifest = Manifest()
    manifest.meta = {"hostname": "mypc", "snapshot_at": "2025-01-01"}
    manifest.dotfiles = [".bashrc"]
    manifest.scripts = ["go.sh"]
    manifest.vscode = {"extensions": ["ext.one"]}
    manifest.packages = {"pip": {"packages": ["requests==2.31.0"]}}

    path = tmp_path / "test.toml"
    manifest.save(path)

    loaded = Manifest.load(path)
    assert loaded.meta["hostname"] == "mypc"
    assert loaded.dotfiles == [".bashrc"]
    assert loaded.scripts == ["go.sh"]
    assert loaded.vscode["extensions"] == ["ext.one"]
    assert loaded.packages["pip"]["packages"] == ["requests==2.31.0"]


def test_manifest_empty(tmp_path: Path) -> None:
    """Empty manifest round-trips cleanly."""
    manifest = Manifest()
    path = tmp_path / "empty.toml"
    manifest.save(path)
    loaded = Manifest.load(path)
    assert loaded.dotfiles == []
    assert loaded.scripts == []
    assert loaded.meta == {}
