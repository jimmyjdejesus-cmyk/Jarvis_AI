import pytest
from unittest.mock import AsyncMock, MagicMock

from jarvis.mcp.model_router import ModelRouter

# --- Mock Fixtures ---

@pytest.fixture
def mock_mcp_client():
    """Creates a mock MCPClient for testing the router."""
    client = MagicMock()
    client.check_server_health = AsyncMock(return_value=True)
    client.generate_response = AsyncMock(side_effect=lambda server, model, prompt: f"Response from {server}/{model}")
    return client

@pytest.fixture
def router(mock_mcp_client):
    """Creates a ModelRouter instance with the mock client."""
    return ModelRouter(mock_mcp_client)

# --- Tests ---

@pytest.mark.asyncio
async def test_route_by_task_type(router, mock_mcp_client):
    """Should select a model with the 'coding' strength for a coding task."""
    prompt = "Write a python function to calculate fibonacci."
    # With a high quality bias, it should pick the higher quality coding model
    await router.route_request(prompt, task_type="coding", quality_vs_cost=0.8)

    # gpt-4 and claude-3.5-sonnet are both good at coding, gpt-4 has higher quality score
    mock_mcp_client.generate_response.assert_called_with("openai", "gpt-4", prompt)
    assert "gpt-4" in router.last_justification

@pytest.mark.asyncio
async def test_route_by_context_window(router, mock_mcp_client):
    """Should select a model that can handle a large prompt."""
    # Create a prompt larger than gpt-4's context window but smaller than claude's
    prompt = "a" * 10000
    await router.route_request(prompt)

    # claude-3.5-sonnet is the only model with a large enough context window
    mock_mcp_client.generate_response.assert_called_with("anthropic", "claude-3.5-sonnet", prompt)
    assert "claude-3.5-sonnet" in router.last_justification

@pytest.mark.asyncio
async def test_route_by_cheapest(router, mock_mcp_client):
    """Should select the cheapest model when quality_vs_cost is 0."""
    prompt = "A simple question."
    await router.route_request(prompt, quality_vs_cost=0.0)

    # llama3.2 is the cheapest model
    mock_mcp_client.generate_response.assert_called_with("ollama", "llama3.2", prompt)
    assert "llama3.2" in router.last_justification

@pytest.mark.asyncio
async def test_route_by_highest_quality(router, mock_mcp_client):
    """Should select the highest quality model when quality_vs_cost is 1."""
    prompt = "A complex philosophical question."
    await router.route_request(prompt, quality_vs_cost=1.0)

    # gpt-4 has the highest quality score
    mock_mcp_client.generate_response.assert_called_with("openai", "gpt-4", prompt)
    assert "gpt-4" in router.last_justification

@pytest.mark.asyncio
async def test_fallback_on_unhealthy_server(router, mock_mcp_client):
    """Should fall back to the next best model if the preferred one is on an unhealthy server."""
    # Make the 'openai' server (for gpt-4) appear unhealthy
    mock_mcp_client.check_server_health.side_effect = lambda server: server != "openai"

    prompt = "A complex philosophical question."
    await router.route_request(prompt, quality_vs_cost=1.0)

    # It should skip gpt-4 and fall back to the next highest quality, claude-3.5-sonnet
    mock_mcp_client.generate_response.assert_called_with("anthropic", "claude-3.5-sonnet", prompt)
    assert "claude-3.5-sonnet" in router.last_justification

@pytest.mark.asyncio
async def test_force_local_execution(router, mock_mcp_client):
    """Should use the local model when force_local is True."""
    prompt = "This must run locally."
    await router.route_request(prompt, force_local=True)

    mock_mcp_client.generate_response.assert_called_with("ollama", "llama3.2", prompt)
    assert "Forced local" in router.last_justification
