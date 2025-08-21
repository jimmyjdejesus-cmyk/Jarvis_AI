import requests
from typing import List, Dict


class WebSearchTool:
    """Simple web search tool using DuckDuckGo API."""

    api_url = "https://api.duckduckgo.com/"

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        params = {"q": query, "format": "json", "no_redirect": 1, "no_html": 1}
        response = requests.get(self.api_url, params=params, timeout=10)
        try:
            response = requests.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            # Provide meaningful error message and context
            print(f"WebSearchTool.search: Failed to fetch results for query '{query}': {e}")
            return []
        results = []
        for topic in data.get("RelatedTopics", [])[:max_results]:
            if isinstance(topic, dict) and "FirstURL" in topic and "Text" in topic:
                results.append({"title": topic.get("Text"), "url": topic.get("FirstURL")})
        return results

    # Compatibility with Tool interface
    def execute(self, query: str, max_results: int = 5):
        return self.search(query, max_results=max_results)


class WebReaderTool:
    """Fetch raw text content from a web page."""

    def read(self, url: str) -> str:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to read URL '{url}': {e}")

    def execute(self, url: str) -> str:
        return self.read(url)
