from agent.core import JarvisAgent
from jarvis.memory.memory_bus import MemoryBus


def test_agent_plan_recall(tmp_path):
    bus = MemoryBus(tmp_path)
    agent = JarvisAgent(memory_bus=bus)
    response = agent.chat("hello")
    recalled = agent.plan("hello")
    assert recalled == response
    log_content = bus.read_log()
    assert "push" in log_content
    assert "recall" in log_content

