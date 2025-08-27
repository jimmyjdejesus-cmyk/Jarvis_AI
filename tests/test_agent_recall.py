import sys
from pathlib import Path
import importlib.util

root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))
sys.path.append(str(root / "jarvis"))

# Load JarvisAgent from agent/core.py explicitly to avoid package collisions
core_path = root / "agent" / "core.py"
spec = importlib.util.spec_from_file_location("agent_core_file", core_path)
core_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core_module)
JarvisAgent = core_module.JarvisAgent

from memory.memory_bus import MemoryBus


def test_agent_plan_recall(tmp_path):
    bus = MemoryBus(tmp_path)
    agent = JarvisAgent(memory_bus=bus)
    response = agent.chat("hello")
    recalled = agent.plan("hello")
    assert recalled == response
    log_content = bus.read_log()
    assert "push" in log_content
    assert "recall" in log_content
