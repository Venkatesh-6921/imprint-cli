"""Tests for safety module — .imprintignore parsing and file filtering."""

from pathlib import Path

from imprint.utils.safety import (
    filter_safe_files,
    load_ignore_patterns,
)


def test_always_exclude_ssh_keys(tmp_path: Path) -> None:
    """SSH keys should always be excluded."""
    home = tmp_path / "home"
    home.mkdir()
    ssh_dir = home / ".ssh"
    ssh_dir.mkdir()
    (ssh_dir / "id_rsa").write_text("private key")
    (ssh_dir / "id_ed25519").write_text("private key")
    (ssh_dir / "config").write_text("Host example")

    ignore_path = home / ".imprintignore"
    ignore_path.write_text("")

    files = [
        ssh_dir / "id_rsa",
        ssh_dir / "id_ed25519",
        ssh_dir / "config",
    ]
    safe = filter_safe_files(files, ignore_path, home)
    names = [f.name for f in safe]
    assert "id_rsa" not in names
    assert "id_ed25519" not in names
    assert "config" in names


def test_always_exclude_env_files(
    tmp_path: Path,
) -> None:
    """Environment files should always be excluded."""
    home = tmp_path / "home"
    home.mkdir()
    (home / ".env").write_text("SECRET=xyz")
    (home / ".env.local").write_text("DB=local")
    (home / ".zshrc").write_text("# zsh")

    ignore_path = home / ".imprintignore"
    ignore_path.write_text("")

    files = [
        home / ".env",
        home / ".env.local",
        home / ".zshrc",
    ]
    safe = filter_safe_files(files, ignore_path, home)
    names = [f.name for f in safe]
    assert ".env" not in names
    assert ".zshrc" in names


def test_custom_ignore_patterns(
    tmp_path: Path,
) -> None:
    """Custom patterns in .imprintignore should be respected."""
    home = tmp_path / "home"
    home.mkdir()
    (home / ".zshrc").write_text("# zsh")
    (home / ".gitconfig").write_text("[user]")
    (home / ".custom_tool_config").write_text("ignore me")

    ignore_path = home / ".imprintignore"
    ignore_path.write_text(".custom_tool_config\n")

    files = [
        home / ".zshrc",
        home / ".gitconfig",
        home / ".custom_tool_config",
    ]
    safe = filter_safe_files(files, ignore_path, home)
    names = [f.name for f in safe]
    assert ".zshrc" in names
    assert ".gitconfig" in names
    assert ".custom_tool_config" not in names


def test_load_patterns_includes_always_exclude() -> None:
    """load_ignore_patterns should include hardcoded patterns."""
    import tempfile

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False
    ) as f:
        f.write("# comment\ncustom_pattern\n")
        f.flush()
        patterns = load_ignore_patterns(Path(f.name))

    assert "custom_pattern" in patterns
    assert ".ssh/id_*" in patterns  # hardcoded
    assert "*secret*" in patterns   # hardcoded


def test_empty_ignore_file(tmp_path: Path) -> None:
    """Empty .imprintignore should still have hardcoded patterns."""
    ignore_path = tmp_path / ".imprintignore"
    ignore_path.write_text("")
    patterns = load_ignore_patterns(ignore_path)
    # Should have at least the hardcoded patterns
    assert len(patterns) > 0
    assert ".ssh/id_*" in patterns


def test_filter_preserves_safe_files(
    tmp_path: Path,
) -> None:
    """Regular dotfiles should pass through the filter."""
    home = tmp_path / "home"
    home.mkdir()
    safe_files = [".zshrc", ".gitconfig", ".vimrc"]
    for name in safe_files:
        (home / name).write_text("config")

    ignore_path = home / ".imprintignore"
    ignore_path.write_text("")

    files = [home / name for name in safe_files]
    result = filter_safe_files(files, ignore_path, home)
    assert len(result) == 3
