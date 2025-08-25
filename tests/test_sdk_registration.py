"""Tests for jarvis_sdk registration decorators."""

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from jarvis_sdk import (
    agent_registry,
    critic_registry,
    crew_registry,
    jarvis_agent,
    jarvis_critic,
    jarvis_crew,
    jarvis_tool,
    registry,
    tool_registry,
)


@jarvis_tool(description="Echo input", permissions=["net"])
def echo(text: str) -> str:
    return text


@jarvis_agent(description="Dummy agent")
class DummyAgent:
    def run(self) -> str:
        return "ok"


@jarvis_crew(description="Crew that echoes")
class EchoCrew:
    def run(self, text: str) -> str:
        return text


@jarvis_critic(description="Check length", permissions=["audit"])
def length_check(text: str, max_length: int = 5) -> str:
    return "ok" if len(text) <= max_length else "too long"


def test_tool_registered() -> None:
    assert "echo" in tool_registry.all()
    assert tool_registry.all()["echo"].plugin is echo
    assert tool_registry.all()["echo"].permissions == ["net"]
    # Global registry should also contain the tool
    assert "echo" in registry.all()


def test_agent_registered() -> None:
    assert "DummyAgent" in agent_registry.all()
    assert agent_registry.all()["DummyAgent"].plugin is DummyAgent
    # Global registry should also contain the agent
    assert "DummyAgent" in registry.all()


def test_crew_registered() -> None:
    assert "EchoCrew" in crew_registry.all()
    assert crew_registry.all()["EchoCrew"].plugin is EchoCrew
    assert "EchoCrew" in registry.all()


def test_critic_registered() -> None:
    assert "length_check" in critic_registry.all()
    assert critic_registry.all()["length_check"].permissions == ["audit"]
    assert "length_check" in registry.all()

