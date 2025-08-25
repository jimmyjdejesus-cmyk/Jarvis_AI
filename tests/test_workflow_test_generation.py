import subprocess
from pathlib import Path
import importlib.util

import asyncio

REPO_ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "integrations", REPO_ROOT / "jarvis" / "workflows" / "integrations.py"
)
integrations = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(integrations)
TestingAdapter = integrations.TestingAdapter


def test_generated_tests_run_successfully(tmp_path: Path) -> None:
    code = "def add(a, b):\n    return a + b"
    adapter = TestingAdapter()
    result = asyncio.run(adapter._generate_tests({"code": code}))
    assert result["success"]
    test_file = tmp_path / "test_generated.py"
    test_file.write_text(result["test_code"])
    completed = subprocess.run(
        ["pytest", str(test_file)], capture_output=True, text=True
    )
    assert (
        completed.returncode == 0
    ), f"Pytest failed: {completed.stdout}\n{completed.stderr}"


def test_generate_tests_invalid_code() -> None:
    adapter = TestingAdapter()
    result = asyncio.run(adapter._generate_tests({"code": "def bad(:\n pass"}))
    assert not result["success"]
    assert "Invalid Python code" in result["error"]


def test_generate_tests_missing_code() -> None:
    """Adapter should return error when code is missing."""
    adapter = TestingAdapter()
    result = asyncio.run(adapter._generate_tests({}))
    assert not result["success"]
    assert "code" in result["error"].lower()
