from __future__ import annotations

"""Basic IDE-style file manipulation tools."""

from typing import Iterable

from .fs_safety import safe_read, safe_write
from .registry import registry


def open_file(path: str, allowlist: Iterable[str], repo_root: str) -> str:
    """Return file contents if permitted."""
    return safe_read(path, allowlist, repo_root)


def save_file(
    path: str,
    content: str,
    allowlist: Iterable[str],
    repo_root: str,
    *,
    dry_run: bool = False,
) -> None:
    """Write content to a file using safety checks."""
    safe_write(path, content, allowlist, repo_root, dry_run=dry_run)


registry.register(
    name="open_file",
    func=open_file,
    description="Read a file from the repository with safety checks",
    capabilities=["file-system"],
)
registry.register(
    name="save_file",
    func=save_file,
    description="Write a file within the repository respecting safety checks",
    capabilities=["file-system"],
)
