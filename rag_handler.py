from duckduckgo_search import DDGS

def get_augmented_prompt(user_prompt, max_results=3):
    """
    Performs a DuckDuckGo web search and returns an augmented prompt with context and citations.
    Args:
        user_prompt (str): The user's original prompt.
        max_results (int): Number of web results to include.
    Returns:
        tuple: (augmented_prompt: str, sources: list of dict(title, url))
    """
    sources = []
    context = ""
    try:
        with DDGS() as ddgs:
            results = ddgs.text(user_prompt, max_results=max_results)
            for res in results:
                title = res.get("title", "")
                body = res.get("body", "")
                url = res.get("href", "")
                context += f"Source: {title}\nURL: {url}\nSummary: {body}\n\n"
                sources.append({"title": title, "url": url})

        augmented_prompt = (
            f"You are a helpful AI assistant. Use the following real-time web search context to answer the user's question.\n\n"
            f"{context}\n"
            f"User question: {user_prompt}\n"
            f"If you use any information from the sources above, cite them."
        )
        return augmented_prompt, sources
    except Exception as e:
        # Fallback: Just return original prompt
        return user_prompt, []