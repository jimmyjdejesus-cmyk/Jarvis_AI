"""Tests for jarvis_sdk agent and tool registration APIs."""

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from jarvis_sdk import (
    agent_registry,
    jarvis_agent,
    jarvis_tool,
    registry,
    tool_registry,
)


@jarvis_tool(description="Echo input")
def echo(text: str) -> str:
    return text


@jarvis_agent(description="Dummy agent")
class DummyAgent:
    def run(self) -> str:
        return "ok"


def test_tool_registered() -> None:
    assert "echo" in tool_registry.all()
    assert tool_registry.all()["echo"].plugin is echo
    # Global registry should also contain the tool
    assert "echo" in registry.all()


def test_agent_registered() -> None:
    assert "DummyAgent" in agent_registry.all()
    assert agent_registry.all()["DummyAgent"].plugin is DummyAgent
    # Global registry should also contain the agent
    assert "DummyAgent" in registry.all()

