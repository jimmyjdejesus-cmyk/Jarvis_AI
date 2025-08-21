from __future__ import annotations

from pathlib import Path

import pytest

from jarvis.tools import ide


def test_save_and_open(tmp_path: Path) -> None:
    allowlist = [str(tmp_path)]
    repo_root = str(tmp_path)
    file = tmp_path / "a.txt"
    ide.save_file(str(file), "data", allowlist, repo_root)
    assert ide.open_file(str(file), allowlist, repo_root) == "data"


def test_ide_disallowed(tmp_path: Path) -> None:
    allowlist: list[str] = []
    repo_root = str(tmp_path)
    file = tmp_path / "b.txt"
    with pytest.raises(Exception):
        ide.save_file(str(file), "data", allowlist, repo_root)
