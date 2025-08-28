import importlib
import sys
from pathlib import Path

import pytest


def get_project_memory(monkeypatch: pytest.MonkeyPatch):
    """Reload jarvis.memory with chromadb missing to use fallback."""
    monkeypatch.setitem(sys.modules, 'chromadb', None)
    sys.modules.pop('jarvis.memory.project_memory', None)
    import jarvis.memory as memory
    importlib.reload(memory)
    return memory.ProjectMemory


def test_add_and_query_round_trip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    ProjectMemory = get_project_memory(monkeypatch)
    mem = ProjectMemory(persist_directory=str(tmp_path))
    mem.add('proj', 'sess', 'hello world', {'a': 1})

    results = mem.query('proj', 'sess', 'hello')
    assert results and results[0]['text'] == 'hello world'
    assert results[0]['metadata']['a'] == 1

    mem2 = ProjectMemory(persist_directory=str(tmp_path))
    results2 = mem2.query('proj', 'sess', 'hello')
    assert results2 and results2[0]['text'] == 'hello world'


def test_query_nonexistent_returns_empty(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    ProjectMemory = get_project_memory(monkeypatch)
    mem = ProjectMemory(persist_directory=str(tmp_path))
    assert mem.query('proj', 'sess', 'nothing') == []


def test_query_corrupt_file_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    ProjectMemory = get_project_memory(monkeypatch)
    path = tmp_path / 'proj_sess.json'
    path.write_text('not json')
    mem = ProjectMemory(persist_directory=str(tmp_path))
    with pytest.raises(RuntimeError):
        mem.query('proj', 'sess', 'hello')
