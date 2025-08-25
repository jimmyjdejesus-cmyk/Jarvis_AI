"""Tests for the :mod:`jarvis.agents.research_agent` module.

The tests mock out network access by patching ``requests.get`` so that the
agent's web scraping utilities can be exercised without performing real HTTP
requests.
"""

from __future__ import annotations

import json
import sys
import types
from pathlib import Path
from unittest.mock import Mock, patch

# Stub out the jarvis package to avoid importing heavy optional dependencies
root = Path(__file__).resolve().parents[1]
jarvis_pkg = types.ModuleType("jarvis")
jarvis_pkg.__path__ = [str(root / "jarvis")]
sys.modules.setdefault("jarvis", jarvis_pkg)

agents_pkg = types.ModuleType("jarvis.agents")
agents_pkg.__path__ = [str(root / "jarvis" / "agents")]
sys.modules.setdefault("jarvis.agents", agents_pkg)

tools_pkg = types.ModuleType("jarvis.tools")
tools_pkg.__path__ = [str(root / "jarvis" / "tools")]
sys.modules.setdefault("jarvis.tools", tools_pkg)

from jarvis.agents.research_agent import ResearchAgent


def _make_response(text: str) -> Mock:
    resp = Mock()
    resp.status_code = 200
    resp.text = text
    resp.raise_for_status = Mock()
    return resp


def test_structured_report_and_artifact_saving(tmp_path: Path) -> None:
    """Verify structured report generation and artifact persistence."""

    search_html = "<a class='result__a' href='http://example.com'>France</a>"
    read_html = "<p>The capital of France is Paris.</p>"

    side_effects = [
        _make_response(search_html),
        _make_response(read_html),
    ]

    with patch("jarvis.tools.web_tools.requests.get", side_effect=side_effects) as mock_get:
        agent = ResearchAgent()
        report = agent.research("What is the capital of France?", save_dir=tmp_path)

    assert mock_get.call_count == 2
    assert report["question"] == "What is the capital of France?"
    assert report["sources"][0]["url"] == "http://example.com"
    assert report["claim_evidence"][0]["claim"] == "The capital of France is Paris."
    assert report["gaps"] == []
    assert report["confidence"] == 1.0

    md_path = tmp_path / "research_what_is_the_capital_of_france.md"
    json_path = tmp_path / "research_what_is_the_capital_of_france.json"
    assert md_path.exists() and json_path.exists()

    # Ensure markdown/json export includes citation
    md_text = md_path.read_text()
    js = json.loads(json_path.read_text())
    assert "http://example.com" in md_text
    assert js["sources"][0]["url"] == "http://example.com"

