"""Tests for the safety module — .imprintignore filtering."""

from pathlib import Path

from imprint.utils.safety import filter_safe_files, is_safe_file, load_ignore_patterns


def test_ssh_keys_always_blocked(tmp_path: Path) -> None:
    """SSH keys must never pass the filter, even without an .imprintignore file."""
    home = tmp_path / "home"
    home.mkdir()
    ssh_dir = home / ".ssh"
    ssh_dir.mkdir()

    # Create fake SSH key files
    (ssh_dir / "id_rsa").write_text("fake key")
    (ssh_dir / "id_ed25519").write_text("fake key")
    (ssh_dir / "deploy.pem").write_text("fake cert")

    # Create a safe file
    (home / ".zshrc").write_text("# config")

    files = [
        ssh_dir / "id_rsa",
        ssh_dir / "id_ed25519",
        ssh_dir / "deploy.pem",
        home / ".zshrc",
    ]

    # No .imprintignore file — hard-coded patterns should still block
    ignore_path = tmp_path / ".imprintignore"
    safe = filter_safe_files(files, ignore_path, home)

    safe_names = [f.name for f in safe]
    assert "id_rsa" not in safe_names
    assert "id_ed25519" not in safe_names
    assert "deploy.pem" not in safe_names
    assert ".zshrc" in safe_names


def test_env_files_blocked(tmp_path: Path) -> None:
    """Environment files with secrets must be blocked."""
    home = tmp_path / "home"
    home.mkdir()
    (home / ".env").write_text("SECRET=abc")
    (home / ".env.local").write_text("SECRET=abc")
    (home / ".gitconfig").write_text("[user]")

    files = [home / ".env", home / ".env.local", home / ".gitconfig"]
    ignore_path = tmp_path / ".imprintignore"
    safe = filter_safe_files(files, ignore_path, home)

    safe_names = [f.name for f in safe]
    assert ".env" not in safe_names
    assert ".env.local" not in safe_names
    assert ".gitconfig" in safe_names


def test_custom_imprintignore(tmp_path: Path) -> None:
    """Custom .imprintignore patterns should be respected."""
    home = tmp_path / "home"
    home.mkdir()
    (home / ".zshrc").write_text("# config")
    (home / ".secret_file").write_text("secret")
    (home / ".vimrc").write_text("set number")

    # Write a custom .imprintignore
    ignore_path = tmp_path / ".imprintignore"
    ignore_path.write_text("*.secret_file\n")

    files = [home / ".zshrc", home / ".secret_file", home / ".vimrc"]
    safe = filter_safe_files(files, ignore_path, home)

    safe_names = [f.name for f in safe]
    assert ".zshrc" in safe_names
    assert ".vimrc" in safe_names
    # .secret_file matches *secret* in hardcoded patterns
    assert ".secret_file" not in safe_names


def test_history_files_blocked(tmp_path: Path) -> None:
    """Shell history files must be blocked."""
    home = tmp_path / "home"
    home.mkdir()
    (home / ".bash_history").write_text("secret commands")
    (home / ".zsh_history").write_text("secret commands")

    files = [home / ".bash_history", home / ".zsh_history"]
    ignore_path = tmp_path / ".imprintignore"
    safe = filter_safe_files(files, ignore_path, home)

    assert len(safe) == 0


def test_load_ignore_patterns_includes_hardcoded(tmp_path: Path) -> None:
    """load_ignore_patterns always includes hard-coded patterns."""
    ignore_path = tmp_path / ".imprintignore"
    patterns = load_ignore_patterns(ignore_path)
    assert ".ssh/id_*" in patterns
    assert ".bash_history" in patterns
