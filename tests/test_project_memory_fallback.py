import importlib
import multiprocessing
import sys
import threading
from pathlib import Path

import pytest


def get_project_memory(monkeypatch: pytest.MonkeyPatch):
    """Reload jarvis.memory with chromadb missing to use fallback."""
    monkeypatch.setitem(sys.modules, 'chromadb', None)
    sys.modules.pop('jarvis.memory.project_memory', None)
    import jarvis.memory as memory
    importlib.reload(memory)
    return memory.ProjectMemory


def _mp_worker(persist_dir: str, idx: int) -> None:
    sys.modules['chromadb'] = None
    sys.modules.pop('jarvis.memory.project_memory', None)
    import jarvis.memory as memory
    importlib.reload(memory)
    mem = memory.ProjectMemory(persist_directory=persist_dir)
    mem.add('proj', 'sess', f'text-{idx}')


def test_add_and_query_round_trip(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ProjectMemory = get_project_memory(monkeypatch)
    mem = ProjectMemory(persist_directory=str(tmp_path))
    mem.add('proj', 'sess', 'hello world', {'a': 1})

    results = mem.query('proj', 'sess', 'hello')
    assert results and results[0]['text'] == 'hello world'
    assert results[0]['metadata']['a'] == 1

    mem2 = ProjectMemory(persist_directory=str(tmp_path))
    results2 = mem2.query('proj', 'sess', 'hello')
    assert results2 and results2[0]['text'] == 'hello world'


def test_query_nonexistent_returns_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ProjectMemory = get_project_memory(monkeypatch)
    mem = ProjectMemory(persist_directory=str(tmp_path))
    assert mem.query('proj', 'sess', 'nothing') == []


def test_query_corrupt_file_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ProjectMemory = get_project_memory(monkeypatch)
    path = tmp_path / 'proj_sess.json'
    path.write_text('not json')
    mem = ProjectMemory(persist_directory=str(tmp_path))
    with pytest.raises(RuntimeError):
        mem.query('proj', 'sess', 'hello')


def test_update_and_delete(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ProjectMemory = get_project_memory(monkeypatch)
    mem = ProjectMemory(persist_directory=str(tmp_path))
    record_id = mem.add('proj', 'sess', 'hello', {'a': 1})

    mem.update(
        'proj', 'sess', record_id, text='hi', metadata={'a': 2}
    )
    results = mem.query('proj', 'sess', 'hi')
    assert results and results[0]['metadata']['a'] == 2

    mem.delete('proj', 'sess', record_id)
    assert mem.query('proj', 'sess') == []
    with pytest.raises(KeyError):
        mem.delete('proj', 'sess', record_id)


def test_concurrent_add(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ProjectMemory = get_project_memory(monkeypatch)
    mem = ProjectMemory(persist_directory=str(tmp_path))

    def worker(idx: int) -> None:
        mem.add('proj', 'sess', f'text-{idx}')

    threads = [
        threading.Thread(target=worker, args=(i,)) for i in range(5)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(mem.query('proj', 'sess')) == 5


def test_concurrent_instances(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Separate instances writing to the same directory should not clobber."""

    ProjectMemory = get_project_memory(monkeypatch)

    def worker(idx: int) -> None:
        mem = ProjectMemory(persist_directory=str(tmp_path))
        mem.add('proj', 'sess', f'text-{idx}')

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    mem = ProjectMemory(persist_directory=str(tmp_path))
    assert len(mem.query('proj', 'sess')) == 5


def test_multiprocess_add(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    get_project_memory(monkeypatch)  # ensure fallback is loaded in parent
    processes = [
        multiprocessing.Process(target=_mp_worker, args=(str(tmp_path), i))
        for i in range(5)
    ]
    for p in processes:
        p.start()
    for p in processes:
        p.join()

    ProjectMemory = get_project_memory(monkeypatch)
    mem = ProjectMemory(persist_directory=str(tmp_path))
    assert len(mem.query('proj', 'sess')) == 5


def test_update_missing_file_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    ProjectMemory = get_project_memory(monkeypatch)
    mem = ProjectMemory(persist_directory=str(tmp_path))
    with pytest.raises(KeyError):
        mem.update('proj', 'sess', 'bad-id', text='hi')


def test_update_corrupt_file_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    ProjectMemory = get_project_memory(monkeypatch)
    path = tmp_path / 'proj_sess.json'
    path.write_text('not json')
    mem = ProjectMemory(persist_directory=str(tmp_path))
    with pytest.raises(RuntimeError):
        mem.update('proj', 'sess', 'bad-id', text='hi')


def test_delete_missing_file_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    ProjectMemory = get_project_memory(monkeypatch)
    mem = ProjectMemory(persist_directory=str(tmp_path))
    with pytest.raises(KeyError):
        mem.delete('proj', 'sess', 'bad-id')


def test_delete_corrupt_file_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    ProjectMemory = get_project_memory(monkeypatch)
    path = tmp_path / 'proj_sess.json'
    path.write_text('not json')
    mem = ProjectMemory(persist_directory=str(tmp_path))
    with pytest.raises(RuntimeError):
        mem.delete('proj', 'sess', 'bad-id')