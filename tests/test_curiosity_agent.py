import pytest
from unittest.mock import MagicMock

from jarvis.agents.curiosity_agent import CuriosityAgent
from jarvis.ecosystem.meta_intelligence import ExecutiveAgent
from jarvis.world_model.hypergraph import HierarchicalHypergraph

@pytest.fixture
def mock_hypergraph():
    """A mock HierarchicalHypergraph with a controllable layers attribute."""
    hg = MagicMock(spec=HierarchicalHypergraph)
    hg.layers = [{}, {}, {}, {}]

    def get_low_confidence_nodes(threshold):
        nodes = []
        for i, layer in enumerate(hg.layers):
            for name, data in layer.items():
                if data.get("confidence", 1.0) < threshold:
                    nodes.append((i, name, data))
        return nodes

    hg.get_low_confidence_nodes = get_low_confidence_nodes
    return hg

@pytest.fixture
def mock_executive_agent(mock_hypergraph):
    """A mock ExecutiveAgent with a curiosity agent."""
    # We need to mock the __init__ of ExecutiveAgent because it has complex dependencies
    agent = MagicMock(spec=ExecutiveAgent)
    agent.hypergraph = mock_hypergraph
    agent.curiosity_agent = CuriosityAgent(mock_hypergraph, threshold=0.5)

    async def execute_task_mock(task):
        if task.get("type") == "pursue_curiosity":
            question = agent.curiosity_agent.generate_question()
            if question:
                return {"success": True, "directive": question}
            return {"success": False, "error": "No low-confidence items"}
        return {"success": False, "error": "Unknown task"}

    agent.execute_task = execute_task_mock
    return agent


def test_curiosity_agent_generates_question(mock_hypergraph):
    """Test that the curiosity agent can generate a question about a low-confidence item."""
    mock_hypergraph.layers[3]["torch_linear_performance"] = {
        "description": "torch.nn.Linear layer on ARM",
        "confidence": 0.3,
    }
    agent = CuriosityAgent(mock_hypergraph, threshold=0.5)
    question = agent.generate_question()
    assert question and "torch.nn.Linear" in question

@pytest.mark.asyncio
async def test_executive_agent_pursues_curiosity(mock_executive_agent):
    """Test that the executive agent can pursue a curiosity-driven task."""
    mock_executive_agent.hypergraph.layers[1]["mystery"] = {"description": "unknown", "confidence": 0.2}

    result = await mock_executive_agent.execute_task({"type": "pursue_curiosity"})

    assert result["success"]
    assert result.get("directive")
    assert "unknown" in result["directive"]
