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


def test_recursive_search_and_citations_with_mocked_http() -> None:
    """Verify iterative search and citation tracking."""

    # HTML snippets for search results and page contents.  Each call to
    # ``requests.get`` will yield the next response in this list.
    search_html_1 = "<a class='result__a' href='http://a.com'>First</a>"
    read_html_1 = "<p>follow-up query</p>"
    search_html_2 = "<a class='result__a' href='http://b.com'>Second</a>"
    read_html_2 = "<p>final content</p>"

    side_effects = [
        _make_response(search_html_1),
        _make_response(read_html_1),
        _make_response(search_html_2),
        _make_response(read_html_2),
    ]

    with patch("jarvis.tools.web_tools.requests.get", side_effect=side_effects) as mock_get:
        agent = ResearchAgent()
        report = agent.research("initial query", depth=2)

    # Ensure the underlying HTTP client was invoked for each request
    assert mock_get.call_count == 4

    # The report should contain two iterations and two citations
    assert len(report["iterations"]) == 2
    assert len(report["citations"]) == 2
    assert report["citations"][0]["url"] == "http://a.com"

    # Ensure markdown/json export includes citations
    md = agent.get_report_markdown()
    js = json.loads(agent.get_report_json())
    assert "http://a.com" in md
    assert js["citations"][1]["url"] == "http://b.com"

