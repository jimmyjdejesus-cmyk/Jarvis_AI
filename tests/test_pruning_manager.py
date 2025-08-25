import pytest

import pytest
from pathlib import Path
import sys
import importlib.util

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

# Prepare package structure for relative imports
pkg_name = "jarvis.orchestration"
pkg = importlib.util.module_from_spec(importlib.machinery.ModuleSpec(pkg_name, loader=None))
pkg.__path__ = [str(ROOT / "jarvis/orchestration")]
sys.modules[pkg_name] = pkg

spec = importlib.util.spec_from_file_location(
    f"{pkg_name}.pruning", ROOT / "jarvis/orchestration/pruning.py"
)
pruning = importlib.util.module_from_spec(spec)
sys.modules[f"{pkg_name}.pruning"] = pruning
spec.loader.exec_module(pruning)  # type: ignore[attr-defined]

PruningManager = pruning.PruningManager
policy_spec = importlib.util.spec_from_file_location("policy", ROOT / "agent/hitl/policy.py")
policy_module = importlib.util.module_from_spec(policy_spec)
sys.modules["policy"] = policy_module
policy_spec.loader.exec_module(policy_module)  # type: ignore[attr-defined]
HITLPolicy = policy_module.HITLPolicy


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


def test_commit_requires_approval(tmp_path):
    policy = HITLPolicy(config={"hitl": {"destructive_ops": ["state_prune"]}})

    def approve(request):
        return True

    mgr = PruningManager(
        state_store={"Red": {}, "Green": {}, "Yellow": {}},
        snapshots_dir=str(tmp_path),
        hitl_policy=policy,
        bq_approved=True,
    )
    mgr.commit("Red", "test", "bob", modal=approve)
    assert "Red" not in mgr.state_store

    def deny(request):
        return False

    mgr2 = PruningManager(
        state_store={"Blue": {}, "Yellow": {}, "Green": {}},
        snapshots_dir=str(tmp_path),
        hitl_policy=policy,
        bq_approved=True,
    )
    with pytest.raises(PermissionError):
        mgr2.commit("Blue", "test", "bob", modal=deny)
