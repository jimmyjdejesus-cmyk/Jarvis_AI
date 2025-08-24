from pathlib import Path
import importlib.util
import sys

# Ensure repository root on path for absolute imports
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

# Load modules directly from file paths to avoid package initialization side-effects
spec_agents = importlib.util.spec_from_file_location(
    "jarvis.orchestration.agents", ROOT / "jarvis" / "orchestration" / "agents.py"
)
agents = importlib.util.module_from_spec(spec_agents)
sys.modules["jarvis.orchestration.agents"] = agents
spec_agents.loader.exec_module(agents)
MetaAgent = agents.MetaAgent

spec_super = importlib.util.spec_from_file_location(
    "jarvis.ecosystem.superintelligence", ROOT / "jarvis" / "ecosystem" / "superintelligence.py"
)
superintelligence = importlib.util.module_from_spec(spec_super)
sys.modules["jarvis.ecosystem.superintelligence"] = superintelligence
spec_super.loader.exec_module(superintelligence)


def test_meta_agent_planning_and_metrics(tmp_path):
    meta = MetaAgent(directory=tmp_path)
    proj_dir = tmp_path / "proj"
    orchestrator = meta.spawn_orchestrator("simple objective for testing", directory=str(proj_dir))
    result = {"outcome": "ok"}
    feedback = meta.register_result(orchestrator, result)

    metrics = meta.get_metrics()
    assert metrics["plans"][0]["objective"] == "simple objective for testing"
    assert metrics["critic_feedback"][0]["success"] is True
    assert feedback["success"] is True

    agg = superintelligence.get_emergent_metrics()
    assert agg["total_runs"] == 1
    assert agg["success_rate"] == 1.0
