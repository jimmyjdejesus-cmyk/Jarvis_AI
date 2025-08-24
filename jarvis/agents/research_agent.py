"""Research agent capable of iterative web search and summarization."""

from __future__ import annotations

import json
import logging
from typing import Callable, Dict, List

from jarvis.tools.web_tools import WebReaderTool, WebSearchTool


class ResearchAgent:
    """Agent that performs web research with citation tracking.

    The agent performs a web search, reads the resulting pages, summarises the
    content and keeps track of citations for each external source used.  It is
    intentionally lightweight and synchronous so that unit tests can patch the
    underlying HTTP requests.
    """

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
        self.citations: List[Dict[str, str]] = []
        self.last_report: Dict | None = None

    # ------------------------------------------------------------------
    def _simple_summarize(self, text: str, max_length: int = 200) -> str:
        """Very small fallback summarizer used for tests."""
        return " ".join(text.strip().split())[:max_length]

    # ------------------------------------------------------------------
    def research(self, query: str, depth: int = 1) -> Dict:
        """Run iterative search up to a specified ``depth``.

        Parameters
        ----------
        query:
            Initial search query.
        depth:
            Number of search iterations to perform.  Each iteration uses the
            previous summary as the next query.
        """

        self.session_memory = []
        self.citations = []
        self._recursive_search(query, depth)
        self.last_report = {
            "query": query,
            "iterations": self.session_memory,
            "citations": self.citations,
        }
        return self.last_report

    def _recursive_search(self, query: str, depth: int) -> None:
        if depth <= 0:
            return

        results = self.search_tool.search(query)
        processed: List[Dict[str, str]] = []
        raw_summaries: List[str] = []

        for result in results:
            url = result.get("url", "")
            try:
                content = self.reader_tool.read(url)
            except Exception:
                logging.exception("Error reading URL: %s", url)
                continue

            summary = self.summarizer(content)
            citation_id = len(self.citations) + 1
            self.citations.append(
                {"id": citation_id, "url": url, "title": result.get("title", "")}
            )

            processed.append(
                {
                    "title": result.get("title", ""),
                    "url": url,
                    "summary": f"{summary} [{citation_id}]",
                    "citation_id": citation_id,
                }
            )
            raw_summaries.append(summary)

        self.session_memory.append({"query": query, "results": processed})

        # Recurse using first raw summary as follow-up query
        if depth > 1 and raw_summaries:
            next_query = raw_summaries[0]
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

        if self.citations:
            lines.append("## References")
            for cite in self.citations:
                lines.append(f"[{cite['id']}]: {cite['title']} - {cite['url']}")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    def get_report_json(self) -> str:
        """Return the last report as JSON string."""
        if not self.last_report:
            return "{}"
        return json.dumps(self.last_report, indent=2)
