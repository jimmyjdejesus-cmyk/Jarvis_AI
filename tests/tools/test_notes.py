from __future__ import annotations

from pathlib import Path

import pytest

from jarvis.tools.notes import add_note, list_notes


def test_add_and_list(tmp_path: Path) -> None:
    allowlist = [str(tmp_path)]
    repo_root = tmp_path
    notes_file = tmp_path / "notes.txt"
    add_note("hello", str(notes_file), allowlist, repo_root)
    assert "hello" in list_notes(str(notes_file), allowlist, repo_root)


def test_notes_permission(tmp_path: Path) -> None:
    allowlist: list[str] = []
    repo_root = tmp_path
    notes_file = tmp_path / "notes.txt"
    with pytest.raises(Exception):
        add_note("test", str(notes_file), allowlist, repo_root)


def test_notes_dry_run(tmp_path: Path) -> None:
    allowlist = [str(tmp_path)]
    repo_root = tmp_path
    notes_file = tmp_path / "notes.txt"
    add_note("hi", str(notes_file), allowlist, repo_root, dry_run=True)
    assert not notes_file.exists()
