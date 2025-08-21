import json
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

# Stub out the jarvis package and its subpackages to avoid heavy imports
root = Path(__file__).resolve().parents[1]
jarvis_pkg = types.ModuleType("jarvis")
jarvis_pkg.__path__ = [str(root / "jarvis")]
sys.modules.setdefault("jarvis", jarvis_pkg)

agents_pkg = types.ModuleType("jarvis.agents")
agents_pkg.__path__ = [str(root / "jarvis" / "agents")]
sys.modules.setdefault("jarvis.agents", agents_pkg)

from jarvis.agents.research_agent import ResearchAgent
from jarvis.tools import WebSearchTool, WebReaderTool


def test_recursive_search_and_citations():
    search_tool = WebSearchTool()
    reader_tool = WebReaderTool()

    search_tool.search = MagicMock(side_effect=[
        [{"title": "First", "url": "http://a.com"}],
        [{"title": "Second", "url": "http://b.com"}],
    ])
    reader_tool.read = MagicMock(side_effect=["follow-up query", "final content"])

    agent = ResearchAgent(search_tool=search_tool, reader_tool=reader_tool)
    report = agent.research("initial query", depth=2)

    assert reader_tool.read.call_count == 2
    assert search_tool.search.call_args_list[0][0][0] == "initial query"
    assert search_tool.search.call_args_list[1][0][0] == "follow-up query"
    assert len(report["iterations"]) == 2
    assert report["iterations"][0]["results"][0]["url"] == "http://a.com"

    # Ensure markdown/json export works
    md = agent.get_report_markdown()
    js = json.loads(agent.get_report_json())
    assert "http://a.com" in md
    assert js["iterations"][0]["results"][0]["url"] == "http://a.com"
