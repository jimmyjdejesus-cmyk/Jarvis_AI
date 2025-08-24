"""Tests for JarvisAgent core parsing and execution."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from legacy.agent.core.core import JarvisAgent


@pytest.fixture
def agent():
    agent = JarvisAgent.__new__(JarvisAgent)
    agent.plugin_system_enabled = False
    agent.use_langgraph = False
    agent.langgraph_agent = None
    agent.user = "tester"
    agent.rag_endpoint = None
    agent.duckduckgo_fallback = True
    agent.llm_endpoint = None
    agent.expert_model = None
    agent.draft_model = None
    agent.tools = MagicMock()
    agent.approval_callback = MagicMock(return_value=True)
    return agent


def test_parse_natural_language_git_command(agent):
    plan = agent.parse_natural_language("git status", [])
    assert plan == [
        {
            "tool": "git_command",
            "args": {"command": "git status", "repository_path": None},
        }
    ]


def test_parse_natural_language_plugin_failure(agent):
    agent.plugin_system_enabled = True
    plan = agent.parse_natural_language("tell me something", [])
    assert plan[0]["tool"] == "llm_task"
    assert plan[0]["args"]["prompt"] == "tell me something"


def test_execute_plan_success(agent):
    step = {"tool": "git_command", "args": {"command": "git status"}}
    agent.tools.preview_tool_action.return_value = "preview"
    agent.tools.run_tool.return_value = "ok"
    results = agent.execute_plan([step])
    agent.tools.preview_tool_action.assert_called_once_with(step)
    agent.approval_callback.assert_called_once()
    agent.tools.run_tool.assert_called_once_with(
        step, expert_model=None, draft_model=None, user="tester"
    )
    assert results == [{"step": step, "result": "ok"}]


def test_execute_plan_denied(agent):
    step = {"tool": "git_command", "args": {"command": "git status"}}
    agent.tools.preview_tool_action.return_value = "preview"
    agent.approval_callback.return_value = False
    results = agent.execute_plan([step])
    agent.tools.run_tool.assert_not_called()
    assert results == [{"step": step, "result": "Denied by user"}]
