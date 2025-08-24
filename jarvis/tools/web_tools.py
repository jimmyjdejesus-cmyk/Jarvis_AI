"""
Provides web-related tools for Jarvis agents.
"""
import requests
from bs4 import BeautifulSoup

def search_web(query: str) -> str:
    """
    Performs a web search using DuckDuckGo and returns the top results.
    """
    try:
        # Using DuckDuckGo's HTML endpoint for simplicity
        res = requests.get(f"https://html.duckduckgo.com/html/?q={query}")
        res.raise_for_status()
        
        soup = BeautifulSoup(res.text, "html.parser")
        results = soup.find_all("a", class_="result__a")
        
        if not results:
            return "No search results found."
            
        output = "Web Search Results:\n"
        for i, result in enumerate(results[:5]): # Return top 5 results
            output += f"{i+1}. {result.text} - {result['href']}\n"
            
        return output
    except Exception as e:
        return f"An error occurred during web search: {str(e)}"

if __name__ == "__main__":
    search_results = search_web("LangGraph multi-agent orchestration")
    print(search_results)
