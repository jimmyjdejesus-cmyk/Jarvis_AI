from __future__ import annotations
from __future__ import annotations

"""Git command helper with repository root enforcement and dry-run support."""

import subprocess
from pathlib import Path
from typing import Iterable, List

from .fs_safety import PathRestrictionError

UNSAFE_CHARS = {";", "&", "|", "\n"}


def sanitize_git_args(args: Iterable[str]) -> List[str]:
    """Remove potentially dangerous characters from git arguments."""
    return ["".join(c for c in a if c not in UNSAFE_CHARS) for a in args]


def run_git_command(
    args: Iterable[str],
    repo_root: str | Path,
    *,
    dry_run: bool = True,
    cwd: str | Path | None = None,
) -> str:
    """Run a git command within ``repo_root``.

    Parameters
    ----------
    args:
        Iterable of arguments excluding the ``git`` executable.
    repo_root:
        Repository root directory. All git commands must execute within this
        directory or its subdirectories.
    dry_run:
        When True, the command is not executed and the would-be command string
        is returned.
    cwd:
        Working directory to execute the command from. Defaults to the current
        working directory.
    """

    root = Path(repo_root).resolve()
    workdir = Path(cwd or Path.cwd()).resolve()
    if root not in workdir.parents and workdir != root:
        raise PathRestrictionError("git command outside repository root")

    safe_args = sanitize_git_args(list(args))
    if dry_run:
        return "git " + " ".join(safe_args)

    result = subprocess.run(
        ["git"] + safe_args, cwd=workdir, check=True, capture_output=True, text=True
    )
    return result.stdout
