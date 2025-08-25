from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

import importlib.util

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("recovery", ROOT / "jarvis/orchestration/recovery.py")
recovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recovery)  # type: ignore[attr-defined]

load_state = recovery.load_state
save_state = recovery.save_state
clear_state = recovery.clear_state

policy_spec = importlib.util.spec_from_file_location("policy", ROOT / "agent/hitl/policy.py")
policy_module = importlib.util.module_from_spec(policy_spec)
sys.modules["policy"] = policy_module
policy_spec.loader.exec_module(policy_module)  # type: ignore[attr-defined]
HITLPolicy = policy_module.HITLPolicy


def test_recovery_cycle(tmp_path, monkeypatch):
    path = tmp_path / "state.json"
    monkeypatch.setenv("JARVIS_RECOVERY_FILE", str(path))

    state = {"step": 1}
    save_state(state)
    assert load_state() == state

    clear_state()
    assert load_state() is None


def test_recovery_policy_denies(tmp_path, monkeypatch):
    path = tmp_path / "state.json"
    monkeypatch.setenv("JARVIS_RECOVERY_FILE", str(path))
    policy = HITLPolicy(config={"hitl": {"destructive_ops": ["file_write", "file_delete"]}})

    def deny(request):
        return False

    save_state({"step": 1}, policy=policy, modal=deny)
    assert not path.exists()
    # Now create file manually then attempt to clear with denial
    path.write_text("{}")
    clear_state(policy=policy, modal=deny)
    assert path.exists()
