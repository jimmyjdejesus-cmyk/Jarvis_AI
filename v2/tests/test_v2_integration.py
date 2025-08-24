import pathlib
import sys

import pytest

# Ensure repository root is on path when tests run from the v2 directory
sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))

from v2.agent.core.agent import JarvisAgentV2


class DummyMCPClient:
    async def generate_response(self, server: str, model: str, prompt: str) -> str:
        return "dummy specialist output"


@pytest.mark.asyncio
async def test_v2_integration():
    agent = JarvisAgentV2()

    # Patch the MCP client with a dummy to avoid network calls
    dummy = DummyMCPClient()
    agent.mcp_client = dummy
    agent.meta_core.meta_agent.mcp_client = dummy

    result = await agent.handle_request(
        "review this simple python code", code="print('hi')"
    )

    assert "code_review" in result.get("specialists_used", [])
    assert "dummy specialist output" in result["results"]["code_review"]["response"]
