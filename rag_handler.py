# rag_handler.py
from duckduckgo_search import DDGS
# Import our new non-streaming function
from ollama_client import generate_non_streamed_response


def extract_relevant_snippets(sources, query, model):
    """
    NEW: Uses an LLM to extract only the most relevant sentences from search results.
    """
    print("--- RAG: Starting snippet extraction ---")
    relevant_snippets = []
    for source in sources:
        extraction_prompt = (
            f"Please extract and return ONLY the sentences from the following text that are MOST RELEVANT "
            f"to the user's question: '{query}'\n\n"
            f"If no part of the text is relevant, return an empty string.\n\n"
            f"--- TEXT TO ANALYZE ---\n"
            f"{source['body']}"
        )
        # Use our new non-streaming function for this internal task
        extracted_text = generate_non_streamed_response(model, extraction_prompt)

        if extracted_text and extracted_text.strip():
            relevant_snippets.append(extracted_text.strip())
            print(f"--- RAG: Found relevant snippet from {source['title']} ---")

    return "\n\n".join(relevant_snippets)


def get_augmented_prompt(query: str, model: str) -> tuple[str, list]:
    """
    Performs a web search, extracts relevant snippets, and returns an
    augmented prompt and a list of sources.
    """
    print("--- RAG: Starting web search ---")
    try:
        sources = []
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=5)]
            for r in results:
                sources.append({'title': r['title'], 'url': r['href'], 'body': r['body']})

        if not sources:
            return query, []

        # This is the new "Smart" step
        refined_context = extract_relevant_snippets(sources, query, model)

        if not refined_context:
            print("--- RAG: No relevant snippets found after extraction. Using original prompt. ---")
            return query, sources  # Return original query but still show sources

        print("--- RAG: Building final prompt with refined context ---")
        augmented_prompt = (
            f"Based on the following highly relevant, extracted information from a web search, "
            f"please provide a comprehensive answer to the user's question.\n\n"
            f"--- REFINED WEB CONTEXT ---\n"
            f"{refined_context}\n"
            f"--- END OF CONTEXT ---\n\n"
            f"User Question: {query}"
        )
        # We return the original sources, even though we only used snippets
        return augmented_prompt, [{'title': s['title'], 'url': s['url']} for s in sources]

    except Exception as e:
        print(f"RAG search failed: {e}")
        return query, []