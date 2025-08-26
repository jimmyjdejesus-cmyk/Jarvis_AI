"""Web utilities used by research-oriented agents.

The module intentionally keeps dependencies light so it can be imported in
test environments.  All network access is performed through ``requests`` and
can therefore be easily mocked during unit tests.
"""

from __future__ import annotations

from typing import Dict, List

import requests
from bs4 import BeautifulSoup


class WebSearchTool:
    """Simple DuckDuckGo web search helper.

    The tool scrapes DuckDuckGo's HTML results page and returns a list of
    dictionaries containing the result title and URL.  It purposefully keeps
    the implementation minimal and synchronous so that tests can patch
    ``requests.get`` to provide deterministic behaviour.
    """

    def search(self, query: str, limit: int = 5) -> List[Dict[str, str]]:
        """Search DuckDuckGo for ``query``.

        Parameters
        ----------
        query:
            Search terms.
        limit:
            Maximum number of results to return.

        Returns
        -------
        List[Dict[str, str]]
            A list of dictionaries with ``title`` and ``url`` keys.
        """

        res = requests.get("https://duckduckgo.com/html/", params={"q": query}, timeout=10)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, "html.parser")
        results: List[Dict[str, str]] = []
        for link in soup.select("a.result__a")[:limit]:
            results.append({"title": link.get_text(), "url": link.get("href", "")})
        return results


class WebReaderTool:
    """Fetch a web page and return plain text content."""

    def read(self, url: str) -> str:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        return soup.get_text(separator=" ", strip=True)


def search_web(query: str) -> str:
    """Legacy helper returning a formatted string of search results."""
    try:  # pragma: no cover - simple wrapper kept for backwards compatibility
        tool = WebSearchTool()
        results = tool.search(query)
        if not results:
            return "No search results found."
        output = "Web Search Results:\n"
        for i, result in enumerate(results[:5]):  # Return top 5 results
            output += f"{i+1}. {result['title']} - {result['url']}\n"
        return output
    except Exception as e:  # pragma: no cover - network errors mocked in tests
        return f"An error occurred during web search: {str(e)}"


if __name__ == "__main__":  # pragma: no cover - manual smoke test
    search_results = search_web("LangGraph multi-agent orchestration")
    print(search_results)
