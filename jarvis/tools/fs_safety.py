from __future__ import annotations

"""File system safety helpers with allowlist enforcement and dry-run support."""

from pathlib import Path
from typing import Iterable


class PathRestrictionError(PermissionError):
    """Raised when a path violates safety restrictions."""


def _resolve(path: str | Path) -> Path:
    """Resolve a path to an absolute canonical form."""
    return Path(path).expanduser().resolve()


def ensure_path_is_allowed(
    path: str | Path,
    allowlist: Iterable[str] | None,
    repo_root: str | Path,
) -> Path:
    """Validate a path against an allowlist and repository root.

    Parameters
    ----------
    path: str | Path
        Target file system path.
    allowlist: Iterable[str] | None
        Iterable of allowed directory prefixes. If empty or ``None`` no paths
        are allowed.
    repo_root: str | Path
        Root directory of the git repository. All paths must reside within
        this directory.

    Returns
    -------
    Path
        The resolved path if allowed.

    Raises
    ------
    PathRestrictionError
        If the path is outside the repository root or not in the allowlist.
    """

    resolved = _resolve(path)
    root = _resolve(repo_root)

    # Ensure path is within repository root
    if root not in resolved.parents and resolved != root:
        raise PathRestrictionError("path outside repository root")

    # Enforce allowlist if provided
    if allowlist:
        allowed = [_resolve(Path(root) / a) if not a.startswith("/") else _resolve(a) for a in allowlist]
        if not any(resolved == a or a in resolved.parents for a in allowed):
            raise PathRestrictionError("path not in allowlist")
    else:
        raise PathRestrictionError("path not in allowlist")

    return resolved


def safe_read(
    path: str | Path,
    allowlist: Iterable[str] | None,
    repo_root: str | Path,
) -> str:
    """Read file content after safety checks."""
    resolved = ensure_path_is_allowed(path, allowlist, repo_root)
    return resolved.read_text()


def safe_write(
    path: str | Path,
    content: str,
    allowlist: Iterable[str] | None,
    repo_root: str | Path,
    *,
    dry_run: bool = False,
) -> None:
    """Write content to a file if permitted. No-op when ``dry_run`` is True."""
    resolved = ensure_path_is_allowed(path, allowlist, repo_root)
    if dry_run:
        return
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(content)
