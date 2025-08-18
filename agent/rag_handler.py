"""
RAG (Retrieval Augmented Generation) Handler Module
Handles retrieval and augmentation of context for LLM responses.
"""
import requests
import os
from typing import List, Dict, Any


def rag_answer(prompt: str, files: List[str], expert_model: str = None, 
               chat_history: List[Dict] = None, user: str = None, 
               endpoint: str = None, mode: str = "file") -> str:
    """
    Generate an answer using RAG with provided files as context.
    
    Args:
        prompt: The user's question/prompt
        files: List of file paths to use as context
        expert_model: The expert model to use
        chat_history: Previous chat history
        user: Username
        endpoint: RAG API endpoint
        
    Returns:
        Generated response with context from files
    """
    context = []
    context_header = ""
    if mode == "file":
        if not files:
            return "No files provided for context."
        for file_path in files:
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        context.append(f"File: {os.path.basename(file_path)}\n{content[:2000]}...")
            except Exception as e:
                context.append(f"Error reading {file_path}: {str(e)}")
        context_header = "Context from uploaded files:"
    elif mode == "search":
        search_results = duckduckgo_search(prompt)
        context.append(search_results)
        context_header = "Context from DuckDuckGo search:"
    elif mode == "auto":
        # Try file context first
        if files:
            for file_path in files:
                try:
                    if os.path.exists(file_path):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            context.append(f"File: {os.path.basename(file_path)}\n{content[:2000]}...")
                except Exception as e:
                    context.append(f"Error reading {file_path}: {str(e)}")
            context_header = "Context from uploaded files:"
        else:
            # Try DuckDuckGo search
            search_results = duckduckgo_search(prompt)
            if search_results and "No results found." not in search_results:
                context.append(search_results)
                context_header = "Context from DuckDuckGo search:"
            else:
                # Trigger browser automation and human-in-loop for unsupported tasks
                from agent.browser_automation import trigger_browser_task
                from agent.human_in_loop import request_human_reasoning
                browser_result = trigger_browser_task(prompt)
                human_reasoning = request_human_reasoning(
                    prompt,
                    reasoning_path="No relevant context found in files or search. Please provide reasoning or next steps in natural language."
                )
                context.append(f"Browser Automation Result: {browser_result}")
                context.append(f"Human Reasoning: {human_reasoning}")
                context_header = "Context from browser automation and human-in-loop:"
    else:
        return "Unsupported RAG mode."

    # Combine context with prompt
    contextual_prompt = f"""
{context_header}
{chr(10).join(context)}

User Question: {prompt}

Please answer the user's question using the provided context. If the context doesn't contain relevant information, mention this in your response. If browser automation and human-in-loop were triggered, follow the reasoning path provided.
"""

    # Make API call to LLM with the contextual prompt
    from agent.tools import llm_api_call
    print(f"DEBUG RAG: Calling llm_api_call with expert_model: {expert_model}")
    result = llm_api_call(contextual_prompt, expert_model, None, chat_history, user, "http://localhost:11434")
    print(f"DEBUG RAG: Got result type: {type(result)}")
    print(f"DEBUG RAG: Result preview: {str(result)[:100]}...")
    
    # If the result is a structured CoT response, preserve it
    if isinstance(result, dict) and result.get("type") == "cot_response":
        print(f"DEBUG RAG: Preserving CoT structure")
        return result
    else:
        print(f"DEBUG RAG: Returning simple result")
        return result


def duckduckgo_search(query: str, max_results: int = 5) -> str:
    """
    Perform a DuckDuckGo search and return summarized results.
    """
    try:
        url = f"https://duckduckgo.com/html/?q={query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.ok:
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, "html.parser")
                results = []
                for a in soup.select('.result__a')[:max_results]:
                    title = a.get_text()
                    href = a.get('href')
                    results.append(f"{title}: {href}")
                return "\n".join(results) if results else "No results found."
            except ImportError:
                # BeautifulSoup not available, return simple text parsing
                return f"Search completed for '{query}' but BeautifulSoup not available for parsing. Install with: pip install beautifulsoup4"
        else:
            return f"DuckDuckGo error: {resp.status_code}"
    except Exception as e:
        return f"DuckDuckGo search failed: {e}"
    
    # Make API call to RAG endpoint
    if endpoint:
        # If endpoint is just the base URL, append /api/generate for Ollama
        if endpoint.rstrip('/') == 'http://localhost:11434':
            endpoint = 'http://localhost:11434/api/generate'
        # Always use qwen3:0.6b for Ollama
        model_name = expert_model if expert_model else "qwen3:0.6b"
        payload = {
            "model": model_name,
            "prompt": contextual_prompt,
        }
        try:
            response = requests.post(endpoint, json=payload, timeout=30)
            if response.ok:
                # Ollama returns streaming responses, but for sync API, get 'response' or 'message'
                resp_json = response.json()
                return resp_json.get("response") or resp_json.get("message") or str(resp_json)
            else:
                return f"LLM API error: {response.status_code} {response.text}"
        except Exception as e:
            return f"LLM API request failed: {e}"
    
    # Fallback to simple context-aware response
    return f"Based on the provided files, here's my understanding:\n\n{contextual_prompt}\n\n(Note: This is a fallback response. Connect to a proper RAG endpoint for enhanced responses.)"


def extract_file_content(file_path: str, max_chars: int = 5000) -> str:
    """
    Extract content from a file with size limits.
    
    Args:
        file_path: Path to the file
        max_chars: Maximum characters to extract
        
    Returns:
        File content or error message
    """
    try:
        if not os.path.exists(file_path):
            return f"File not found: {file_path}"
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(max_chars)
            if len(content) == max_chars:
                content += "... (truncated)"
            return content
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"


def prepare_context_for_rag(files: List[str]) -> Dict[str, Any]:
    """
    Prepare file context for RAG processing.
    
    Args:
        files: List of file paths
        
    Returns:
        Dictionary with processed file contexts
    """
    context = {
        "files": [],
        "total_size": 0,
        "error_files": []
    }
    
    for file_path in files:
        try:
            if os.path.exists(file_path):
                content = extract_file_content(file_path)
                context["files"].append({
                    "path": file_path,
                    "name": os.path.basename(file_path),
                    "content": content,
                    "size": len(content)
                })
                context["total_size"] += len(content)
            else:
                context["error_files"].append(f"File not found: {file_path}")
        except Exception as e:
            context["error_files"].append(f"Error processing {file_path}: {str(e)}")
    
    return context