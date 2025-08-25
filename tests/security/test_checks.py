import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from agent.security import is_safe_path  # noqa: E402


def test_is_safe_path(tmp_path):
    base = tmp_path
    safe = tmp_path / "file.txt"
    unsafe = tmp_path / ".." / "secret.txt"
    assert is_safe_path(base, safe)
    assert not is_safe_path(base, unsafe)
