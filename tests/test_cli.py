import os
import sys
from pathlib import Path
import types
from unittest.mock import MagicMock, patch

import pytest

root = Path(__file__).resolve().parents[1]
sys.path.append(str(root / "jarvis"))

jarvis_stub = types.ModuleType("jarvis")
ecosystem_stub = types.ModuleType("jarvis.ecosystem")
jarvis_stub.ecosystem = ecosystem_stub
ecosystem_stub.ExecutiveAgent = MagicMock()
sys.modules.setdefault("jarvis", jarvis_stub)
sys.modules.setdefault("jarvis.ecosystem", ecosystem_stub)

from jarvis_ai import cli  # noqa: E402


@pytest.fixture
def mock_meta_agent():
    """Fixture providing a stubbed ExecutiveAgent with a two-step plan."""

    mock = MagicMock()

    def plan(objective, context):
        return {
            "success": True,
            "graph": {
                "nodes": ["step1", "step2"],
                "edges": [],
            },
        }

    async def execute(objective, context):
        return {"success": True, "results": ["step1 result", "step2 result"]}

    mock.manage_directive = MagicMock(side_effect=plan)
    mock.execute_mission = MagicMock(side_effect=execute)
    return mock


def test_cli_with_objective(mock_meta_agent, capsys):
    with patch("jarvis_ai.cli.ExecutiveAgent", return_value=mock_meta_agent):
        with patch("sys.argv", ["jarvis", "test objective"]):
            result = cli.main(mcp_client=MagicMock())
            captured = capsys.readouterr()
            assert result == {
                "success": True,
                "results": ["step1 result", "step2 result"],
            }
            assert "Mission Results" in captured.out
            mock_meta_agent.execute_mission.assert_called_once()


def test_cli_with_code_and_context(mock_meta_agent, capsys):
    with patch("jarvis_ai.cli.ExecutiveAgent", return_value=mock_meta_agent):
        with open("test_code.py", "w") as f:
            f.write("print('hello')")
        with patch(
            "sys.argv",
            [
                "jarvis",
                "test objective",
                "--code",
                "test_code.py",
                "--context",
                "test context",
            ],
        ):
            cli.main(mcp_client=MagicMock())
            captured = capsys.readouterr()
            assert "Execution Graph" in captured.out
            mock_meta_agent.manage_directive.assert_called_with(
                "test objective",
                {"code": "print('hello')", "user_context": "test context"},
            )
        os.remove("test_code.py")


def test_cli_multi_step_mission(mock_meta_agent, capsys):
    with patch("jarvis_ai.cli.ExecutiveAgent", return_value=mock_meta_agent):
        with patch("sys.argv", ["jarvis", "multi step objective"]):
            cli.main(mcp_client=MagicMock())
            captured = capsys.readouterr()
            assert "step1 result" in captured.out
            assert "step2 result" in captured.out
            assert "Execution Graph" in captured.out
            assert '"step1"' in captured.out and '"step2"' in captured.out


def test_cli_plan_failure(capsys):
    """CLI prints planning errors when manage_directive fails."""

    failing_agent = MagicMock()
    failing_agent.manage_directive.side_effect = RuntimeError("plan boom")
    with patch("jarvis_ai.cli.ExecutiveAgent", return_value=failing_agent):
        with patch("sys.argv", ["jarvis", "bad objective"]):
            cli.main(mcp_client=MagicMock())
            captured = capsys.readouterr()
            assert "Mission planning failed" in captured.out


def test_cli_execution_failure(capsys):
    """CLI reports errors when execute_mission returns unsuccessfully."""

    failing_agent = MagicMock()
    failing_agent.manage_directive.return_value = {"success": True}
    failing_agent.execute_mission.return_value = {
        "success": False,
        "error": "boom",
    }
    with patch("jarvis_ai.cli.ExecutiveAgent", return_value=failing_agent):
        with patch("sys.argv", ["jarvis", "bad objective"]):
            cli.main(mcp_client=MagicMock())
            captured = capsys.readouterr()
            assert "Mission execution failed" in captured.out
