"""Research agent capable of iterative web search and structured reporting."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Callable, Dict, List, Any
from urllib.parse import urlparse

from jarvis.tools.web_tools import WebReaderTool, WebSearchTool
from jarvis.memory.memory_bus import MemoryBus


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
        memory_bus: MemoryBus | None = None,
    ) -> None:
        self.search_tool = search_tool or WebSearchTool()
        self.reader_tool = reader_tool or WebReaderTool()
        self.summarizer = summarizer or self._simple_summarize
        self.memory_bus = memory_bus
        self.session_memory: List[Dict[str, List[Dict[str, str]]]] = []
        self.citations: List[Dict[str, str]] = []
        # Map URLs to citation IDs for de-duplication
        self._citation_lookup: Dict[str, int] = {}
        self.last_report: Dict[str, Any] | None = None

    # ------------------------------------------------------------------
    def _simple_summarize(self, text: str, max_length: int = 200) -> str:
        """Very small fallback summarizer used for tests."""
        return " ".join(text.strip().split())[:max_length]

    # ------------------------------------------------------------------
    def _normalize_url(self, url: str) -> str:
        """Return a normalized URL for consistent citation de-duplication.

        Normalization lowercases the scheme and host and strips any trailing
        slash from the path to avoid treating cosmetic differences as distinct
        sources.
        """
        parsed = urlparse(url)
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()
        path = parsed.path.rstrip("/")
        return f"{scheme}://{netloc}{path}"

    # ------------------------------------------------------------------
    def research(self, question: str, depth: int = 1, save_dir: str | Path | None = None) -> Dict[str, Any]:
        """Run iterative search and produce a structured research report.

        Parameters
        ----------
        question:
            Initial research question.
        depth:
            Number of search iterations to perform. Each iteration uses the
            previous summary as the next query.
        save_dir:
            Optional directory where the report artifacts will be written.
        """

        self.session_memory = []
        self.citations = []
        self._citation_lookup = {}
        self._recursive_search(question, depth)

        claim_evidence = []
        for iteration in self.session_memory:
            for res in iteration["results"]:
                claim_evidence.append(
                    {
                        "claim": res["summary"].rsplit("[", 1)[0].strip(),
                        "evidence": [
                            {
                                "source_id": res["citation_id"],
                                "text": res["summary"].rsplit("[", 1)[0].strip(),
                            }
                        ],
                    }
                )

        report: Dict[str, Any] = {
            "question": question,
            "sources": self.citations,
            "claim_evidence": claim_evidence,
            "gaps": [],
        }

        # Identify quality gaps via the "blue" review and assess risk via the
        # "white" review.  Confidence is reduced if any gaps are present or
        # if a risky source is detected.
        report["gaps"] = self._blue_review(report)
        report["confidence"] = 1.0 if self._white_review(report) and not report["gaps"] else 0.5

        self.last_report = report

        if save_dir:
            self.save_report(save_dir)

        if self.memory_bus:
            self.memory_bus.log_interaction(
                agent_id="research_agent",
                team="Research",
                message=f"Completed research for question: {question}",
                data=report,
            )

        return report

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
            norm_url = self._normalize_url(url) if url else ""
            citation_id = self._citation_lookup.get(norm_url)
            if citation_id is None:
                citation_id = len(self.citations) + 1
                self._citation_lookup[norm_url] = citation_id
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
    def _blue_review(self, report: Dict[str, Any]) -> List[str]:
        """Quality review identifying missing information.

        The "blue" review focuses on the completeness of the research output
        and records any gaps that should be addressed in a future iteration.
        """

        gaps: List[str] = []
        if not report["sources"]:
            gaps.append("No sources found")
        if not report["claim_evidence"]:
            gaps.append("No claims generated")
        return gaps

    # ------------------------------------------------------------------
    def _white_review(self, report: Dict[str, Any]) -> bool:
        """Risk review verifying each source looks trustworthy.

        Currently this ensures that every source has a title and a valid
        HTTP(S) URL.  The check is intentionally conservative: if any source
        fails validation the report is marked as lower confidence.
        """

        for src in report["sources"]:
            url = src.get("url", "")
            title = src.get("title", "")
            parsed = urlparse(url)
            if not title or parsed.scheme not in ("http", "https") or not parsed.netloc:
                return False
        return True

    # ------------------------------------------------------------------
    def get_report_markdown(self) -> str:
        """Return the last report in markdown format."""
        if not self.last_report:
            return ""

        report = self.last_report
        lines = [f"# Research Report: {report['question']}", ""]
        lines.append("## Claims and Evidence")
        for ce in report["claim_evidence"]:
            lines.append(f"- **Claim:** {ce['claim']}")
            for ev in ce["evidence"]:
                lines.append(f"  - Evidence: {ev['text']} [{ev['source_id']}]")

        if report["gaps"]:
            lines.append("")
            lines.append("## Gaps")
            for gap in report["gaps"]:
                lines.append(f"- {gap}")

        if report["sources"]:
            lines.append("")
            lines.append("## Sources")
            for src in report["sources"]:
                lines.append(f"[{src['id']}]: {src['title']} - {src['url']}")

        lines.append("")
        lines.append(f"## Confidence\n{report['confidence']}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def get_report_json(self) -> str:
        """Return the last report as JSON string."""
        if not self.last_report:
            return "{}"
        return json.dumps(self.last_report, indent=2)

    # ------------------------------------------------------------------
    def save_report(self, directory: str | Path) -> None:
        """Persist the current report as JSON and Markdown files."""
        if not self.last_report:
            return

        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        slug = re.sub(r"[^a-zA-Z0-9]+", "_", self.last_report["question"].lower()).strip("_")
        json_path = directory / f"research_{slug}.json"
        md_path = directory / f"research_{slug}.md"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.last_report, f, indent=2)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(self.get_report_markdown())