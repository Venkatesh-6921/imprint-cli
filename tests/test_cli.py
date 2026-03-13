"""Tests for the CLI entry point using Click's CliRunner."""

from click.testing import CliRunner

from imprint.cli import cli


def test_cli_help() -> None:
    """imp --help should print usage without errors."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Imprint" in result.output
    assert "snapshot" in result.output
    assert "restore" in result.output
    assert "diff" in result.output
    assert "update" in result.output
    assert "status" in result.output


def test_cli_version() -> None:
    """imp --version should print the version."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "1.0.0" in result.output


def test_snapshot_help() -> None:
    """imp snapshot --help should print snapshot options."""
    runner = CliRunner()
    result = runner.invoke(cli, ["snapshot", "--help"])
    assert result.exit_code == 0
    assert "--no-push" in result.output


def test_restore_help() -> None:
    """imp restore --help should print restore options."""
    runner = CliRunner()
    result = runner.invoke(cli, ["restore", "--help"])
    assert result.exit_code == 0
    assert "--dry-run" in result.output


def test_status_no_snapshot() -> None:
    """imp status with no snapshot should print friendly message."""
    runner = CliRunner()
    result = runner.invoke(cli, ["status"])
    # Should not crash, may say "no snapshot found"
    assert result.exit_code == 0
