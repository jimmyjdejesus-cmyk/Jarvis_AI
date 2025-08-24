"""Research agent capable of iterative web search and summarization."""

from __future__ import annotations

import json
from typing import Callable, Dict, List

from jarvis.tools import WebSearchTool, WebReaderTool


class ResearchAgent:
    """Agent that performs web research with citation tracking."""

    def __init__(
        self,
        search_tool: WebSearchTool | None = None,
        reader_tool: WebReaderTool | None = None,
        summarizer: Callable[[str], str] | None = None,
    ) -> None:
        self.search_tool = search_tool or WebSearchTool()
        self.reader_tool = reader_tool or WebReaderTool()
        self.summarizer = summarizer or self._simple_summarize
        self.session_memory: List[Dict[str, List[Dict[str, str]]]] = []
        self.last_report: Dict | None = None

    def _simple_summarize(self, text: str, max_length: int = 200) -> str:
        """Very small fallback summarizer used for tests."""
        return text.strip().replace("\n", " ")[:max_length]

    # ------------------------------------------------------------------
    def research(self, query: str, depth: int = 1) -> Dict:
        """Run iterative search up to a specified depth."""
        self.session_memory = []
        self._recursive_search(query, depth)
        self.last_report = {"query": query, "iterations": self.session_memory}
        return self.last_report

    def _recursive_search(self, query: str, depth: int) -> None:
        if depth <= 0:
            return

        results = self.search_tool.search(query)
        summaries = []
        for result in results:
            try:
                content = self.reader_tool.read(result["url"])
            except Exception:
                logging.exception(f"Error reading URL: {result.get('url', '')}")
                continue
            summary = self.summarizer(content)
            summaries.append(
                {"title": result.get("title", ""), "url": result["url"], "summary": summary}
            )

        self.session_memory.append({"query": query, "results": summaries})

        # Recurse using first summary as follow-up query
        if depth > 1 and summaries:
            next_query = summaries[0]["summary"]
            self._recursive_search(next_query, depth - 1)

    # ------------------------------------------------------------------
    def get_report_markdown(self) -> str:
        """Return the last report in markdown format."""
        if not self.last_report:
            return ""
        lines = [f"# Research Report: {self.last_report['query']}", ""]
        for idx, iteration in enumerate(self.last_report["iterations"], 1):
            lines.append(f"## Iteration {idx}: {iteration['query']}")
            for res in iteration["results"]:
                lines.append(f"- [{res['title']}]({res['url']}): {res['summary']}")
            lines.append("")
        return "\n".join(lines)

    def get_report_json(self) -> str:
        """Return the last report as JSON string."""
        if not self.last_report:
            return "{}"
        return json.dumps(self.last_report, indent=2)
