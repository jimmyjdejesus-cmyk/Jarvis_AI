from __future__ import annotations

from pathlib import Path

import pytest

from jarvis.tools.fs_safety import safe_write, safe_read, PathRestrictionError


def test_safe_read_write(tmp_path: Path) -> None:
    allowlist = [str(tmp_path)]
    repo_root = tmp_path
    file = tmp_path / "file.txt"
    safe_write(file, "hello", allowlist, repo_root)
    assert safe_read(file, allowlist, repo_root) == "hello"


def test_disallowed_path(tmp_path: Path) -> None:
    allowlist: list[str] = []
    repo_root = tmp_path
    with pytest.raises(PathRestrictionError):
        safe_write(tmp_path / "file.txt", "data", allowlist, repo_root)


def test_outside_repo(tmp_path: Path) -> None:
    allowlist = [str(tmp_path.parent)]
    repo_root = tmp_path
    outside = tmp_path.parent / "file.txt"
    with pytest.raises(PathRestrictionError):
        safe_write(outside, "data", allowlist, repo_root)


def test_dry_run(tmp_path: Path) -> None:
    allowlist = [str(tmp_path)]
    repo_root = tmp_path
    path = tmp_path / "dry.txt"
    safe_write(path, "data", allowlist, repo_root, dry_run=True)
    assert not path.exists()
