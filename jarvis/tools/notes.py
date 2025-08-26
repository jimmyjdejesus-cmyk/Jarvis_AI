from __future__ import annotations

"""Simple note taking utilities."""

from typing import Iterable, List

from .fs_safety import safe_read, safe_write
from .registry import registry


def add_note(
    note: str,
    notes_file: str,
    allowlist: Iterable[str],
    repo_root: str,
    *,
    dry_run: bool = False,
) -> None:
    """Append a note to the specified file."""
    try:
        existing = safe_read(notes_file, allowlist, repo_root)
    except FileNotFoundError:
        existing = ""
    new_content = (existing + "\n" if existing else "") + note
    safe_write(notes_file, new_content + "\n", allowlist, repo_root, dry_run=dry_run)


def list_notes(notes_file: str, allowlist: Iterable[str], repo_root: str) -> List[str]:
    """Return list of notes from file."""
    try:
        content = safe_read(notes_file, allowlist, repo_root)
    except FileNotFoundError:
        return []
    return [line for line in content.splitlines() if line]


registry.register(
    name="add_note",
    func=add_note,
    description="Append a note to a file with safety checks",
    capabilities=["notes"],
)
registry.register(
    name="list_notes",
    func=list_notes,
    description="List notes from a file with safety checks",
    capabilities=["notes"],
)
