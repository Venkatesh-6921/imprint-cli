"""Tests for collectors — mock subprocess calls."""

from pathlib import Path
from unittest.mock import patch, MagicMock

from imprint.collectors import system, dotfiles, git_config, scripts, shell


def test_system_collect_python_version() -> None:
    """System collector should always return a Python version."""
    result = system.collect()
    assert "python_version" in result
    assert result["python_version"]  # not None or empty


def test_system_collect_with_missing_tools() -> None:
    """Missing tools (node, git) should return None, not crash."""
    with patch("subprocess.check_output", side_effect=FileNotFoundError):
        result = system.collect()
    # Python version uses platform.python_version(), not subprocess
    assert result["python_version"] is not None
    assert result["node_version"] is None
    assert result["git_version"] is None


def test_dotfiles_collect(tmp_path: Path) -> None:
    """Dotfiles collector finds known dotfiles in home dir."""
    home = tmp_path / "home"
    home.mkdir()
    (home / ".zshrc").write_text("# zsh config")
    (home / ".gitconfig").write_text("[user]")
    (home / "not_a_dotfile.txt").write_text("nope")

    found = dotfiles.collect(home)
    names = [f.name for f in found]
    assert ".zshrc" in names
    assert ".gitconfig" in names
    assert "not_a_dotfile.txt" not in names


def test_dotfiles_empty_home(tmp_path: Path) -> None:
    """No dotfiles returns empty list."""
    home = tmp_path / "home"
    home.mkdir()
    assert dotfiles.collect(home) == []


def test_scripts_collect(tmp_path: Path) -> None:
    """Scripts collector finds files in ~/bin/."""
    home = tmp_path / "home"
    bin_dir = home / "bin"
    bin_dir.mkdir(parents=True)
    (bin_dir / "deploy.sh").write_text("#!/bin/bash")
    (bin_dir / "backup.sh").write_text("#!/bin/bash")

    found = scripts.collect(home)
    names = [f.name for f in found]
    assert "deploy.sh" in names
    assert "backup.sh" in names


def test_scripts_no_bin_dir(tmp_path: Path) -> None:
    """No ~/bin directory returns empty list."""
    home = tmp_path / "home"
    home.mkdir()
    assert scripts.collect(home) == []


def test_git_config_collect_mocked() -> None:
    """Git config collector reads git config values."""
    def mock_check_output(cmd, **kwargs):
        key = cmd[-1]
        values = {
            "user.name": "Test User\n",
            "user.email": "test@example.com\n",
            "core.editor": "vim\n",
            "init.defaultBranch": "main\n",
            "core.excludesFile": "~/.gitignore_global\n",
        }
        if key in values:
            return values[key]
        raise subprocess.CalledProcessError(1, cmd)

    import subprocess
    with patch("subprocess.check_output", side_effect=mock_check_output):
        result = git_config.collect()

    assert result["user_name"] == "Test User"
    assert result["user_email"] == "test@example.com"
    assert result["core_editor"] == "vim"
    assert result["init_defaultBranch"] == "main"


def test_shell_collect_zsh(tmp_path: Path) -> None:
    """Shell collector detects zsh config from .zshrc content."""
    home = tmp_path / "home"
    home.mkdir()
    zshrc_content = '''
ZSH_THEME="robbyrussell"
plugins=(git docker python)
alias ll="ls -la"
alias gs="git status"
function deploy() { echo "deploying"; }
'''
    (home / ".zshrc").write_text(zshrc_content)

    with patch("imprint.collectors.shell._detect_shell", return_value="zsh"), \
         patch("imprint.collectors.shell._get_shell_version", return_value="5.9"):
        result = shell.collect(home)

    assert result["type"] == "zsh"
    assert result["theme"] == "robbyrussell"
    assert "git" in result["plugins"]
    assert "docker" in result["plugins"]
    assert result["custom_aliases"] == 2
    assert result["custom_functions"] >= 1
