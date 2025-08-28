import os
import sys
import types
from pathlib import Path

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

root = Path(__file__).resolve().parents[1]
sys.path.append(str(root / "jarvis"))

jarvis_stub = types.ModuleType("jarvis")
ecosystem_stub = types.ModuleType("jarvis.ecosystem")
jarvis_stub.ecosystem = ecosystem_stub
ecosystem_stub.ExecutiveAgent = MagicMock()
sys.modules.setdefault("jarvis", jarvis_stub)
sys.modules.setdefault("jarvis.ecosystem", ecosystem_stub)

from jarvis_ai import cli # noqa: E402


@pytest.fixture
def mock_agent():
    mock = MagicMock()
    mock.execute_mission = AsyncMock(return_value={"result": "success"})
    return mock


def test_cli_with_objective(mock_agent):
    fake_module = types.SimpleNamespace(ExecutiveAgent=MagicMock(return_value=mock_agent))
    with patch.dict(sys.modules, {"jarvis.ecosystem": fake_module}):
        cli._run_command(
            types.SimpleNamespace(objective="test objective", code=None, context=None),
            None,
        )

    mock_agent.execute_mission.assert_called_once_with("test objective", {})

def test_cli_with_code(mock_agent, tmp_path):
    code_file = tmp_path / "code.py"
    code_file.write_text("print('hello world')")

    fake_module = types.SimpleNamespace(ExecutiveAgent=MagicMock(return_value=mock_agent))
    with patch.dict(sys.modules, {"jarvis.ecosystem": fake_module}):
        cli._run_command(
            types.SimpleNamespace(objective="test objective", code=open(code_file), context=None),
            None,
        )

    mock_agent.execute_mission.assert_called_once_with(
        "test objective", {"code": "print('hello world')"}
    )

def test_cli_with_context(mock_agent):
    fake_module = types.SimpleNamespace(ExecutiveAgent=MagicMock(return_value=mock_agent))
    with patch.dict(sys.modules, {"jarvis.ecosystem": fake_module}):
        cli._run_command(
            types.SimpleNamespace(
                objective="test objective", code=None, context="user context"
            ),
            None,
        )

    mock_agent.execute_mission.assert_called_once_with(
        "test objective", {"user_context": "user context"}
    )

def test_cli_main_with_run_command(monkeypatch, capsys):
    test_args = ["run", "test objective"]
    monkeypatch.setattr(sys, "argv", ["jarvis", *test_args])

    def mock_run_command(args, mcp_client):
        assert args.objective == "test objective"
        print("Mock run command executed")

    with patch("jarvis_ai.cli._run_command", new=mock_run_command):
        cli.main()
    
    captured = capsys.readouterr()
    assert "Mock run command executed" in captured.out