import os
import sys
import types
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

root = Path(__file__).resolve().parents[1]
sys.path.append(str(root / "jarvis"))
from jarvis_ai import cli  # noqa: E402


@pytest.fixture
def mock_agent():
    mock = MagicMock()
    mock.execute_mission = AsyncMock(return_value={"result": "success"})
    return mock


def test_cli_with_objective(mock_agent):
    fake_module = types.SimpleNamespace(ExecutiveAgent=MagicMock(return_value=mock_agent))
    with patch.dict(sys.modules, {"jarvis.ecosystem": fake_module}):
        with patch("sys.argv", ["jarvis", "run", "test objective"]):
            cli.main(mcp_client=MagicMock())
            mock_agent.execute_mission.assert_awaited_with("test objective", {})


def test_cli_with_code_and_context(mock_agent):
    fake_module = types.SimpleNamespace(ExecutiveAgent=MagicMock(return_value=mock_agent))
    with patch.dict(sys.modules, {"jarvis.ecosystem": fake_module}):
        with open("test_code.py", "w") as f:
            f.write("print('hello')")

        with patch(
            "sys.argv",
            [
                "jarvis",
                "run",
                "test objective",
                "--code",
                "test_code.py",
                "--context",
                "test context",
            ],
        ):
            cli.main(mcp_client=MagicMock())
            mock_agent.execute_mission.assert_awaited_with(
                "test objective",
                {"code": "print('hello')", "user_context": "test context"},
            )

        os.remove("test_code.py")
