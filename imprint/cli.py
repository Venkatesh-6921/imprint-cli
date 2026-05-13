"""
Imprint CLI v3 — 11 commands, named profiles, encryption, export, doctor.
"""

from __future__ import annotations

import click

from imprint import __version__
from imprint.config import ImprintConfig
from imprint.utils.display import (
    console,
    divider,
    print_command_header,
    print_dashboard,
    print_logo,
    print_status_bar,
    step_error,
    step_ok,
    step_warn,
)

# ── Shared options ────────────────────────────────────────

_profile_option = click.option(
    "--profile", "-p",
    default=None,
    metavar="NAME",
    help=(
        "Named profile to use "
        "(default: active profile in config.toml)."
    ),
)


# ── Root group ────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.version_option(
    version=__version__, prog_name="Imprint"
)
@_profile_option
@click.pass_context
def cli(
    ctx: click.Context, profile: str | None
) -> None:
    """Imprint — Stamp your developer environment on any machine."""
    if ctx.invoked_subcommand is None:
        config = ImprintConfig.load(profile=profile)
        print_logo()
        print_dashboard(
            version=__version__,
            profile=config.profile,
        )
        print_status_bar(
            version=__version__,
            profile=config.profile,
        )


# ── init ──────────────────────────────────────────────────

@cli.command()
def init() -> None:
    """Interactive first-run wizard — configure Imprint for this machine."""
    print_command_header(
        "imp init", "First-run setup wizard"
    )

    config = ImprintConfig.load()

    # GitHub repo
    console.print(
        "  [imp.dim]Step 1/4[/imp.dim]  GitHub repository"
    )
    console.print(
        "  [imp.dim]Create a private GitHub repo "
        "to store your config.[/imp.dim]\n"
    )
    current = config.github_repo or ""
    repo = click.prompt(
        "  GitHub repo URL",
        default=current or "",
        show_default=bool(current),
    ).strip()
    if repo:
        config.github_repo = repo

    # Auto-push preference
    console.print()
    console.print(
        "  [imp.dim]Step 2/4[/imp.dim]  Auto-push"
    )
    config.auto_push = click.confirm(
        "  Auto-push to GitHub after every snapshot?",
        default=True,
    )

    # Encryption
    console.print()
    console.print(
        "  [imp.dim]Step 3/4[/imp.dim]  Encryption"
    )
    console.print(
        "  [imp.dim]Encrypts dotfiles before pushing "
        "to GitHub.[/imp.dim]"
    )
    config.encrypt = click.confirm(
        "  Encrypt dotfiles before pushing?",
        default=False,
    )
    if config.encrypt:
        try:
            from imprint.crypto import (
                generate_key,
                save_key,
            )

            save_key(generate_key(), config.key_path)
            step_ok(
                "Encryption key generated",
                str(config.key_path),
            )
            step_warn(
                "IMPORTANT: Back up your key file "
                "— lost key = lost config."
            )
        except ImportError:
            step_warn(
                "cryptography not installed.",
                "Run:  pip install imprint-cli[crypto]",
            )
            config.encrypt = False

    # Default profile name
    console.print()
    console.print(
        "  [imp.dim]Step 4/4[/imp.dim]  Profile name"
    )
    profile_name = click.prompt(
        "  Profile name for this machine",
        default="default",
    ).strip()
    if profile_name and profile_name != "default":
        config.create_profile(profile_name)
        config.profile = profile_name

    config.save()
    console.print()
    step_ok(
        "Imprint configured!",
        f"Profile: {config.profile}"
        "  ·  ~/.imprint/config.toml",
    )
    console.print()
    console.print(
        "  [imp.dim]Next step:[/imp.dim]  "
        "[imp.cmd]imp snapshot[/imp.cmd]  "
        "[imp.dim]to capture this machine.[/imp.dim]"
    )
    console.print()


# ── snapshot ──────────────────────────────────────────────

@cli.command()
@click.option(
    "--no-push", is_flag=True, default=False,
    help="Don't push to GitHub.",
)
@click.option(
    "--no-vscode", is_flag=True, default=False,
    help="Skip VS Code extensions.",
)
@click.option(
    "--no-packages", is_flag=True, default=False,
    help="Skip package managers.",
)
@_profile_option
def snapshot(
    no_push: bool,
    no_vscode: bool,
    no_packages: bool,
    profile: str | None,
) -> None:
    """Capture your complete developer environment."""
    config = ImprintConfig.load(profile=profile)
    push = not no_push and config.auto_push

    if push and not config.github_repo:
        console.print()
        step_warn(
            "No GitHub repository configured.",
            "Run  imp init  to set one up, "
            "or use --no-push.",
        )
        console.print()
        if not click.confirm(
            "  Continue without pushing?", default=True
        ):
            return
        push = False

    from imprint.snapshot import run_snapshot

    run_snapshot(
        config,
        push=push,
        include_vscode=not no_vscode,
        include_packages=not no_packages,
    )


# ── restore ───────────────────────────────────────────────

@cli.command()
@click.argument("source", required=False)
@click.option(
    "--dry-run", is_flag=True, default=False,
    help="Show what would be restored.",
)
@_profile_option
def restore(
    source: str | None,
    dry_run: bool,
    profile: str | None,
) -> None:
    """Restore your developer environment.

    SOURCE can be a GitHub URL or omit to restore from ~/.imprint/.
    """
    config = ImprintConfig.load(profile=profile)
    if dry_run:
        step_warn("Dry run — no changes will be made.")
        console.print()
    from imprint.restore import run_restore

    run_restore(
        config, source=source, dry_run=dry_run
    )


# ── diff ──────────────────────────────────────────────────

@cli.command()
@_profile_option
def diff(profile: str | None) -> None:
    """Show what has changed since your last snapshot."""
    config = ImprintConfig.load(profile=profile)
    from imprint.diff import run_diff

    run_diff(config)


# ── update ────────────────────────────────────────────────

@cli.command()
@_profile_option
def update(profile: str | None) -> None:
    """Snapshot + push to GitHub in one step."""
    config = ImprintConfig.load(profile=profile)
    from imprint.snapshot import run_snapshot

    run_snapshot(config, push=True)
    console.print()
    step_ok("Environment updated and pushed.")


# ── status ────────────────────────────────────────────────

@cli.command()
@_profile_option
def status(profile: str | None) -> None:
    """Show what Imprint is currently tracking."""
    config = ImprintConfig.load(profile=profile)
    print_command_header(
        "imp status", f"Profile: {config.profile}"
    )

    if not config.manifest_path.exists():
        step_warn(
            "No snapshot found.",
            "Run  imp snapshot  first.",
        )
        console.print()
        return

    from rich.table import Table

    from imprint.manifest import Manifest

    m = Manifest.load(config.manifest_path)
    total_pkgs = sum(
        len(
            v.get("packages", [])
            if isinstance(v, dict) else []
        )
        for v in m.packages.values()
    )

    table = Table(
        show_header=False,
        border_style="imp.border",
        padding=(0, 2),
        expand=False,
    )
    table.add_column(
        "Key", style="imp.dim", no_wrap=True
    )
    table.add_column("Value", style="#eceff4")
    table.add_row(
        "Last snapshot",
        m.meta.get("snapshot_at", "unknown"),
    )
    table.add_row(
        "Machine",
        m.meta.get("hostname", "unknown"),
    )
    table.add_row(
        "OS",
        (
            f"{m.meta.get('os', '?')} "
            f"{m.meta.get('os_version', '')}"
        ).strip(),
    )
    table.add_row(
        "Profile",
        m.meta.get("profile", "default"),
    )
    table.add_row(
        "Python",
        m.system.get("python_version", "n/a"),
    )
    table.add_row(
        "Node",
        m.system.get("node_version", "n/a"),
    )
    table.add_row(
        "Dotfiles",
        (
            f"[imp.success]{len(m.dotfiles)}"
            f"[/imp.success] files"
        ),
    )
    exts = m.vscode.get("extensions", [])
    table.add_row(
        "VS Code",
        (
            f"[imp.success]{len(exts)}"
            f"[/imp.success] extensions"
        ),
    )
    table.add_row(
        "Packages",
        (
            f"[imp.success]{total_pkgs}"
            f"[/imp.success] total"
        ),
    )
    table.add_row(
        "Scripts",
        (
            f"[imp.success]{len(m.scripts)}"
            f"[/imp.success] custom scripts"
        ),
    )
    nvim_plugins = m.neovim.get("plugins", [])
    table.add_row(
        "Neovim plugins",
        (
            f"[imp.success]{len(nvim_plugins)}"
            f"[/imp.success]"
        ),
    )
    table.add_row(
        "GitHub repo",
        (
            config.github_repo
            or "[imp.dim]not configured[/imp.dim]"
        ),
    )
    enc_status = (
        "[imp.success]yes[/imp.success]"
        if config.encrypt
        else "[imp.dim]no[/imp.dim]"
    )
    table.add_row("Encrypted", enc_status)

    console.print(table)
    console.print()
    console.print(
        "  [imp.dim]Run[/imp.dim]  "
        "[imp.cmd]imp diff[/imp.cmd]  "
        "[imp.dim]to see what changed.[/imp.dim]"
    )
    console.print()


# ── doctor ────────────────────────────────────────────────

@cli.command()
@_profile_option
def doctor(profile: str | None) -> None:
    """Health check — validates config, git, GitHub, and dependencies."""
    import importlib
    import shutil as sh
    import subprocess

    config = ImprintConfig.load(profile=profile)
    print_command_header(
        "imp doctor",
        "Diagnosing your Imprint setup...",
    )

    checks: list[tuple[str, bool, str]] = []

    # Config exists
    ok = config.config_path.exists()
    checks.append((
        "config.toml exists",
        ok,
        str(config.config_path),
    ))

    # Manifest exists
    ok = config.manifest_path.exists()
    checks.append((
        "Snapshot exists",
        ok,
        (
            str(config.manifest_path)
            if ok else "Run imp snapshot first"
        ),
    ))

    # Git available
    ok = bool(sh.which("git"))
    checks.append(("git binary on PATH", ok, ""))

    # GitHub repo configured
    ok = bool(config.github_repo)
    checks.append((
        "GitHub repo configured",
        ok,
        config.github_repo or "Run imp init",
    ))

    # GitHub connectivity
    if config.github_repo:
        try:
            result = subprocess.run(
                [
                    "git", "ls-remote",
                    "--exit-code", config.github_repo,
                ],
                capture_output=True,
                timeout=10,
            )
            ok = result.returncode == 0
            checks.append((
                "GitHub repo accessible",
                ok,
                config.github_repo,
            ))
        except Exception as e:
            checks.append((
                "GitHub repo accessible",
                False,
                str(e),
            ))

    # Optional deps
    for pkg, extra in [
        ("cryptography", "crypto"),
        ("watchdog", "watch"),
    ]:
        ok = importlib.util.find_spec(pkg) is not None
        detail = (
            f"pip install imprint-cli[{extra}]"
            if not ok else ""
        )
        checks.append((
            f"[{extra}] {pkg} installed",
            ok,
            detail,
        ))

    # .imprintignore exists
    ok = config.imprintignore_path.exists()
    checks.append((
        ".imprintignore in place",
        ok,
        str(config.imprintignore_path),
    ))

    # Key file (if encrypt enabled)
    if config.encrypt:
        ok = config.key_path.exists()
        checks.append((
            "Encryption key file",
            ok,
            (
                str(config.key_path)
                if ok else "Run imp encrypt --init"
            ),
        ))

    # Print
    console.print()
    for label, passed, detail in checks:
        if passed:
            step_ok(label, detail)
        else:
            step_error(label, detail)

    console.print()
    failed = sum(1 for _, p, _ in checks if not p)
    if failed == 0:
        step_ok(
            "All checks passed! Imprint is healthy."
        )
    else:
        step_warn(
            f"{failed} check(s) failed.",
            "Fix the issues above and re-run imp doctor.",
        )
    console.print()


# ── history ───────────────────────────────────────────────

@cli.command()
@click.option(
    "--limit", "-n",
    default=10,
    show_default=True,
    help="Max snapshots to show.",
)
@_profile_option
def history(limit: int, profile: str | None) -> None:
    """Browse past snapshots with a timeline view."""
    import tomllib as toml

    config = ImprintConfig.load(profile=profile)
    print_command_header(
        "imp history", f"Profile: {config.profile}"
    )

    snaps_dir = config.snapshots_dir
    if not snaps_dir.exists():
        step_warn(
            "No snapshot history.",
            "Run  imp snapshot  first.",
        )
        console.print()
        return

    entries = sorted(
        [
            d for d in snaps_dir.iterdir()
            if d.is_dir()
        ],
        key=lambda d: d.name,
        reverse=True,
    )[:limit]

    if not entries:
        step_warn("No snapshots in history directory.")
        console.print()
        return

    snapshots = []
    for entry in entries:
        toml_path = entry / "environment.toml"
        if not toml_path.exists():
            continue
        with open(toml_path, "rb") as f:
            data = toml.load(f)
        meta = data.get("meta", {})
        df_count = len(
            data.get("dotfiles", {}).get("files", [])
        )
        pkg_total = sum(
            len(
                v.get("packages", [])
                if isinstance(v, dict) else []
            )
            for v in data.get("packages", {}).values()
        )
        ext_count = len(
            data.get("vscode", {})
            .get("extensions", [])
        )
        snapshots.append({
            "timestamp": meta.get(
                "snapshot_at", entry.name
            ),
            "hostname":  meta.get("hostname", "—"),
            "dotfiles":  df_count,
            "packages":  pkg_total,
            "vscode":    ext_count,
        })

    from imprint.utils.display import (
        print_snapshot_timeline,
    )

    print_snapshot_timeline(snapshots)
    all_dirs = list(snaps_dir.iterdir())
    console.print(
        f"  [imp.dim]Showing {len(snapshots)} "
        f"of {len(all_dirs)} snapshots.[/imp.dim]"
    )
    console.print()


# ── export ────────────────────────────────────────────────

@cli.command()
@click.option(
    "--fmt", "-f",
    type=click.Choice(
        ["json", "yaml", "md", "sh"],
        case_sensitive=False,
    ),
    default="md",
    show_default=True,
    help="Output format.",
)
@click.option(
    "--out", "-o",
    default=None,
    metavar="PATH",
    help="Output file path.",
)
@_profile_option
def export(
    fmt: str, out: str | None, profile: str | None
) -> None:
    """Export your environment manifest in multiple formats."""
    from pathlib import Path

    config = ImprintConfig.load(profile=profile)
    print_command_header(
        "imp export", f"Format: {fmt}"
    )

    if not config.manifest_path.exists():
        step_error(
            "No snapshot found.",
            "Run  imp snapshot  first.",
        )
        return

    from imprint.manifest import Manifest

    m = Manifest.load(config.manifest_path)

    ext_map = {
        "json": ".json",
        "yaml": ".yaml",
        "md": ".md",
        "sh": ".sh",
    }
    default_name = f"imprint-export{ext_map[fmt]}"
    output_path = (
        Path(out) if out
        else Path.cwd() / default_name
    )

    if fmt == "json":
        m.export_json(output_path)
    elif fmt == "yaml":
        m.export_yaml(output_path)
    elif fmt == "md":
        m.export_markdown(output_path)
    elif fmt == "sh":
        m.export_shell_script(output_path)

    step_ok(f"Exported to {output_path}")
    console.print()


# ── profile ───────────────────────────────────────────────

@cli.group()
def profile() -> None:
    """Manage named profiles (work, home, laptop, etc.)."""


@profile.command("list")
def profile_list() -> None:
    """List all profiles."""
    config = ImprintConfig.load()
    profiles = config.list_profiles()
    console.print()
    for p in profiles:
        active = (
            " [imp.accent]← active[/imp.accent]"
            if p == config.profile else ""
        )
        console.print(
            f"  [imp.cmd]{p}[/imp.cmd]{active}"
        )
    console.print()


@profile.command("create")
@click.argument("name")
def profile_create(name: str) -> None:
    """Create a new named profile."""
    config = ImprintConfig.load()
    config.create_profile(name)
    step_ok(f"Profile '{name}' created.")
    console.print()


@profile.command("use")
@click.argument("name")
def profile_use(name: str) -> None:
    """Set a profile as the active default."""
    config = ImprintConfig.load()
    if name not in config.list_profiles():
        step_error(
            f"Profile '{name}' not found.",
            "Run  imp profile create <name>  first.",
        )
        return
    config.profile = name
    config.save()
    step_ok(f"Active profile set to '{name}'.")
    console.print()


@profile.command("delete")
@click.argument("name")
@click.confirmation_option(
    prompt="Delete this profile and all its snapshots?"
)
def profile_delete(name: str) -> None:
    """Delete a named profile."""
    config = ImprintConfig.load()
    try:
        config.delete_profile(name)
        step_ok(f"Profile '{name}' deleted.")
    except ValueError as e:
        step_error(str(e))
    console.print()


# ── compare ───────────────────────────────────────────────

@cli.command()
@click.argument("snapshot_a")
@click.argument("snapshot_b")
@_profile_option
def compare(
    snapshot_a: str,
    snapshot_b: str,
    profile: str | None,
) -> None:
    """Compare two snapshots side by side.

    SNAPSHOT_A and SNAPSHOT_B are timestamp directory names
    (e.g. 2025-01-15_10-00-00) or 'latest' / 'previous'.
    """

    config = ImprintConfig.load(profile=profile)
    print_command_header(
        "imp compare",
        f"{snapshot_a} vs {snapshot_b}",
    )

    def resolve_snap(name: str):
        snaps = sorted(
            [
                d for d in config.snapshots_dir.iterdir()
                if d.is_dir()
            ],
            key=lambda d: d.name,
        )
        if name == "latest":
            return snaps[-1] if snaps else None
        if name == "previous":
            return snaps[-2] if len(snaps) >= 2 else None
        return config.snapshots_dir / name

    dir_a = resolve_snap(snapshot_a)
    dir_b = resolve_snap(snapshot_b)

    for label, d in [("A", dir_a), ("B", dir_b)]:
        if not d or not (d / "environment.toml").exists():
            step_error(
                f"Snapshot {label} not found: {d}"
            )
            return

    from imprint.manifest import Manifest
    from imprint.utils.display import (
        diff_add,
        diff_remove,
    )

    m_a = Manifest.load(dir_a / "environment.toml")
    m_b = Manifest.load(dir_b / "environment.toml")

    def _compare_lists(
        label: str, a: list, b: list
    ) -> None:
        added = set(b) - set(a)
        removed = set(a) - set(b)
        console.print(
            f"\n  [imp.brand]{label}[/imp.brand]"
        )
        console.print(
            f"  [imp.border]{'─' * 50}[/imp.border]"
        )
        for item in sorted(added):
            diff_add(item, f"in {snapshot_b}")
        for item in sorted(removed):
            diff_remove(
                item, f"removed in {snapshot_b}"
            )
        if not added and not removed:
            console.print(
                "  [imp.dim]  no changes[/imp.dim]"
            )

    _compare_lists(
        "DOTFILES", m_a.dotfiles, m_b.dotfiles
    )
    _compare_lists(
        "VS CODE",
        m_a.vscode.get("extensions", []),
        m_b.vscode.get("extensions", []),
    )

    for pm in ("pip", "npm", "cargo"):
        a_pkgs = (
            m_a.packages.get(pm, {})
            .get("packages", [])
        )
        b_pkgs = (
            m_b.packages.get(pm, {})
            .get("packages", [])
        )
        _compare_lists(
            f"PACKAGES ({pm})", a_pkgs, b_pkgs
        )

    console.print()
    divider()
    step_ok(f"Compared {snapshot_a} vs {snapshot_b}")
    console.print()


# ── encrypt ───────────────────────────────────────────────

@cli.command()
@click.option(
    "--init", "do_init",
    is_flag=True, default=False,
    help="Generate a new encryption key.",
)
@click.option(
    "--decrypt", "do_decrypt",
    is_flag=True, default=False,
    help="Decrypt dotfiles.",
)
@_profile_option
def encrypt(
    do_init: bool,
    do_decrypt: bool,
    profile: str | None,
) -> None:
    """Encrypt (or decrypt) dotfiles in your imprint directory."""
    try:
        from imprint.crypto import (
            decrypt_dir,
            encrypt_dir,
            generate_key,
            save_key,
        )
    except ImportError:
        step_error(
            "cryptography package not installed.",
            "Run:  pip install imprint-cli[crypto]",
        )
        return

    config = ImprintConfig.load(profile=profile)
    print_command_header(
        "imp encrypt",
        "AES-256-GCM encryption for dotfiles",
    )

    if do_init:
        key = generate_key()
        save_key(key, config.key_path)
        step_ok(
            "New key generated.",
            str(config.key_path),
        )
        step_warn(
            "Back up this key file "
            "— it cannot be recovered."
        )
        config.encrypt = True
        config.save()
        console.print()
        return

    if not config.key_path.exists():
        step_error(
            "No key file found.",
            "Run  imp encrypt --init  to generate one.",
        )
        return

    if do_decrypt:
        count = decrypt_dir(
            config.dotfiles_dir, config.key_path
        )
        step_ok(f"Decrypted {count} files.")
    else:
        count = encrypt_dir(
            config.dotfiles_dir, config.key_path
        )
        step_ok(f"Encrypted {count} files.")

    console.print()


# ── watch ─────────────────────────────────────────────────

@cli.command()
@click.option(
    "--interval",
    default=300,
    show_default=True,
    help="Check interval in seconds.",
)
@_profile_option
def watch(interval: int, profile: str | None) -> None:
    """Watch for environment changes and auto-snapshot."""
    try:
        from imprint.watch import run_watch
    except ImportError:
        step_error(
            "watchdog not installed.",
            "Run:  pip install imprint-cli[watch]",
        )
        return

    config = ImprintConfig.load(profile=profile)
    print_command_header(
        "imp watch",
        f"Watching for changes every {interval}s"
        "  (Ctrl+C to stop)",
    )
    run_watch(config, interval=interval)


# ── Entry point ───────────────────────────────────────────

def main() -> None:
    cli()


if __name__ == "__main__":
    main()
