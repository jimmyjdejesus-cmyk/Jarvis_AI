from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from jarvis.tools.git_sandbox import run_git_command, sanitize_git_args
from jarvis.tools.fs_safety import PathRestrictionError


def test_git_dry_run(tmp_path: Path) -> None:
    repo_root = tmp_path
    (repo_root / '.git').mkdir()
    output = run_git_command(["status"], repo_root, dry_run=True, cwd=repo_root)
    assert output.startswith("git status")


def test_git_outside_repo(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / '.git').mkdir()
    with pytest.raises(PathRestrictionError):
        run_git_command(["status"], repo_root, dry_run=True, cwd=tmp_path)


def test_git_execute(tmp_path: Path) -> None:
    repo_root = tmp_path
    subprocess.run(["git", "init"], cwd=repo_root, check=True, stdout=subprocess.PIPE)
    out = run_git_command(["status", "--short"], repo_root, dry_run=False, cwd=repo_root)
    assert isinstance(out, str)


def test_sanitize_git_args() -> None:
    args = sanitize_git_args(["checkout", "main; rm -rf /"])
    assert args == ["checkout", "main rm -rf /"]
