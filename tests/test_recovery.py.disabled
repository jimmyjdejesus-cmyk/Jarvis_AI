from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from jarvis.orchestration.recovery import load_state, save_state, clear_state


def test_recovery_cycle(tmp_path, monkeypatch):
    path = tmp_path / "state.json"
    monkeypatch.setenv("JARVIS_RECOVERY_FILE", str(path))

    state = {"step": 1}
    save_state(state)
    assert load_state() == state

    clear_state()
    assert load_state() is None
