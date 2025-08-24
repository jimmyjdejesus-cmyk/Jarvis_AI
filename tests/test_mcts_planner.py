import asyncio
import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

sys.path.append(str(ROOT))

from benchmarks import BenchmarkScenario, BenchmarkRunner, benchmark_table


# Load MissionPlanner and MCTSPlanner without importing heavy jarvis package
mission_spec = importlib.util.spec_from_file_location(
    "jarvis.agents.mission_planner", ROOT / "jarvis" / "agents" / "mission_planner.py"
)
mission_module = importlib.util.module_from_spec(mission_spec)
sys.modules["jarvis.agents.mission_planner"] = mission_module
mission_spec.loader.exec_module(mission_module)
MissionPlanner = mission_module.MissionPlanner

mcts_spec = importlib.util.spec_from_file_location(
    "jarvis.planning.mcts_planner", ROOT / "jarvis" / "planning" / "mcts_planner.py"
)
mcts_module = importlib.util.module_from_spec(mcts_spec)
sys.modules["jarvis.planning.mcts_planner"] = mcts_module
mcts_spec.loader.exec_module(mcts_module)
MCTSPlanner = mcts_module.MCTSPlanner


class DummyClient:
    """Deterministic client returning stepwise expansions."""

    def generate_response(self, model: str, prompt: str) -> str:  # noqa: D401
        if "completed tasks:" not in prompt:
            return "1. Gather requirements\n2. Design architecture\n3. Implement features"
        if "completed tasks: []" in prompt:
            return "1. Gather requirements\n2. Design architecture\n3. Implement features"
        if "'Gather requirements'" in prompt and "'Design architecture'" not in prompt:
            return "1. Design architecture\n2. Implement features"
        if "'Design architecture'" in prompt and "'Implement features'" not in prompt:
            return "1. Implement features"
        return ""


def test_mcts_planner_generates_plan():
    planner = MCTSPlanner(client=DummyClient(), iterations=10)
    plan = planner.plan("Build an app")
    assert plan == [
        "Gather requirements",
        "Design architecture",
        "Implement features",
    ]


def _scenario_factory(planner):
    async def _run(_ctx):
        tasks = planner.plan("Build an app")
        return " ".join(tasks)

    return BenchmarkScenario("plan", _run)


def test_benchmark_compare_planners():
    mission_runner = BenchmarkRunner([_scenario_factory(MissionPlanner(DummyClient()))])
    mcts_runner = BenchmarkRunner([_scenario_factory(MCTSPlanner(DummyClient(), iterations=10))])
    mission_metrics = asyncio.run(mission_runner.run("baseline"))
    mcts_metrics = asyncio.run(mcts_runner.run("mcts"))
    table = benchmark_table(mcts_metrics, mission_metrics)
    assert table[0]["success_balanced"] == 1.0
    assert table[0]["success_no_prune"] == 1.0
