import subprocess
import sys
import types
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _patch_required_modules() -> None:
    """Insert dummy modules so legacy tools can import."""
    sys.modules["agent.features"] = types.ModuleType("agent.features")
    sys.modules["tools"] = types.ModuleType("tools")
    dummy_modules = {
        "agent.features.file_ingest": types.SimpleNamespace(ingest_file=lambda f: f),
        "agent.features.browser_automation": types.SimpleNamespace(automate_browser=lambda a: a),
        "agent.features.image_generation": types.SimpleNamespace(generate_image=lambda p: p),
        "agent.features.rag_handler": types.SimpleNamespace(rag_answer=lambda *a, **k: ""),
        "agent.features.code_review": types.SimpleNamespace(review_file=lambda *a, **k: ""),
        "agent.features.code_search": types.SimpleNamespace(search_code=lambda *a, **k: []),
        "agent.features.repo_context": types.SimpleNamespace(get_repository_context=lambda *a, **k: {}),
        "tools.code_intelligence": types.SimpleNamespace(
            engine=types.SimpleNamespace(
                get_code_completion=lambda *a, **k: [],
                record_completion_feedback=lambda *a, **k: True,
            )
        ),
    }
    sys.modules.update(dummy_modules)


_patch_required_modules()

from legacy.agent.tools import run_tool


def _init_repo(path):
    """Create a git repository with a single commit for testing."""
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=path, check=True)
    (path / "README.md").write_text("hello")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=path, check=True, capture_output=True)


def test_git_status(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)

    step = {
        "tool": "git_command",
        "args": {"command": "status", "repository_path": str(repo)},
    }
    output = run_tool(step)
    assert "On branch" in output


def test_git_command_not_allowed(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)

    step = {
        "tool": "git_command",
        "args": {
            "command": "clone https://example.com/foo.git",
            "repository_path": str(repo),
        },
    }
    with pytest.raises(ValueError):
        run_tool(step)


def test_git_command_missing_repo():
    step = {
        "tool": "git_command",
        "args": {"command": "status", "repository_path": "/nonexistent"},
    }
    with pytest.raises(FileNotFoundError):
        run_tool(step)


def test_git_command_failure(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)

    step = {
        "tool": "git_command",
        "args": {"command": "log --badflag", "repository_path": str(repo)},
    }
    with pytest.raises(RuntimeError):
        run_tool(step)

