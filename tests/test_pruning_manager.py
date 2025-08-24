import pytest
from jarvis.orchestration.pruning import PruningManager


def test_guardrails_security_team(tmp_path):
    mgr = PruningManager(
        state_store={"Security": {}, "Green": {}},
        snapshots_dir=str(tmp_path)
    )
    with pytest.raises(ValueError):
        mgr.dry_run("Security", "test", "alice", context={"round": "adversarial"})


def test_guardrails_min_active(tmp_path):
    mgr = PruningManager(
        state_store={"Green": {}, "Yellow": {}},
        snapshots_dir=str(tmp_path)
    )
    with pytest.raises(ValueError):
        mgr.dry_run("Green", "test", "alice")


def test_commit_and_rollback(tmp_path):
    state = {"Green": {"x": 1}, "Yellow": {"x": 2}, "Blue": {"x": 3}}
    mgr = PruningManager(state_store=state, snapshots_dir=str(tmp_path))
    result = mgr.commit("Green", "low novelty", "bob")
    snapshot = result["snapshot"]
    assert "Green" not in mgr.active_teams
    mgr.rollback(snapshot, "Green")
    assert "Green" in mgr.active_teams
    assert mgr.state_store["Green"] == {"x": 1}
    assert mgr.audit_log()[0]["team"] == "Green"
