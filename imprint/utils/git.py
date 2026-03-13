"""
Git utilities for Imprint.
Handles pushing config to GitHub and cloning repos.
"""

from __future__ import annotations

from pathlib import Path

import git as gitpython


def push_to_github(imprint_dir: Path, repo_url: str) -> None:
    """Push the imprint config directory to a GitHub repo.

    If the directory isn't a git repo yet, initializes one.
    Commits all changes and pushes to origin/main.

    Args:
        imprint_dir: Path to ~/.imprint/.
        repo_url: GitHub repo URL.
    """
    try:
        repo = gitpython.Repo(imprint_dir)
    except gitpython.InvalidGitRepositoryError:
        repo = gitpython.Repo.init(imprint_dir)

    # Ensure remote is set
    if "origin" not in [r.name for r in repo.remotes]:
        repo.create_remote("origin", repo_url)
    else:
        origin = repo.remotes.origin
        if origin.url != repo_url:
            origin.set_url(repo_url)

    # Add all files and commit
    repo.git.add(A=True)

    if repo.is_dirty(untracked_files=True) or repo.untracked_files:
        repo.index.commit("Imprint snapshot update")

    # Push to main
    origin = repo.remotes.origin
    try:
        origin.push(refspec="HEAD:main")
    except gitpython.GitCommandError:
        # If main doesn't exist remotely, try pushing with --set-upstream
        origin.push(refspec="HEAD:main", set_upstream=True)


def clone_repo(url: str, dest: Path) -> Path:
    """Clone a GitHub repo to the destination directory.

    If the destination already exists, pulls latest changes instead.

    Args:
        url: GitHub repo URL.
        dest: Destination directory.

    Returns:
        Path to the cloned/updated directory.
    """
    if dest.exists() and (dest / ".git").is_dir():
        repo = gitpython.Repo(dest)
        origin = repo.remotes.origin
        origin.pull()
    else:
        dest.mkdir(parents=True, exist_ok=True)
        gitpython.Repo.clone_from(url, dest)

    return dest
