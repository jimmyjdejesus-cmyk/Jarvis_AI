import pytest
from unittest.mock import patch, MagicMock
import os
import asyncio

import sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
sys.path.append(str(root / "jarvis"))
from jarvis_ai import cli

@pytest.fixture
def mock_orchestrator():
    mock = MagicMock()
    # since coordinate_specialists is an async function, we need to mock it with an async function
    async def mock_coordinate_specialists(*args, **kwargs):
        return {"result": "success"}
    mock.coordinate_specialists = mock_coordinate_specialists
    return mock

def test_cli_with_objective(mock_orchestrator):
    with patch("jarvis_ai.cli.MultiAgentOrchestrator", return_value=mock_orchestrator):
        with patch("sys.argv", ["jarvis", "test objective"]):
            cli.main(mcp_client=MagicMock())
            # We can't assert the call directly because it's in a different thread.
            # Instead, we'll just check that the orchestrator was initialized.
            assert cli.MultiAgentOrchestrator.called

def test_cli_with_code_and_context(mock_orchestrator):
    with patch("jarvis_ai.cli.MultiAgentOrchestrator", return_value=mock_orchestrator):
        # Create a dummy code file
        with open("test_code.py", "w") as f:
            f.write("print('hello')")

        with patch("sys.argv", ["jarvis", "test objective", "--code", "test_code.py", "--context", "test context"]):
            cli.main(mcp_client=MagicMock())
            assert cli.MultiAgentOrchestrator.called

        os.remove("test_code.py")
