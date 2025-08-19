"""
Enhanced RAG (Retrieval Augmented Generation) Handler Module
Handles retrieval and augmentation of context for LLM responses with improved error handling and performance.
"""
import requests
import os
import time
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from agent.core.error_handling import robust_operation, get_logger, get_error_handler
from agent.core.config_manager import get_config


class RAGCache:
    """Simple caching system for RAG results to improve performance."""
    
    def __init__(self, max_size: int = 100, ttl_minutes: int = 30):
        self.cache = {}
        self.max_size = max_size
        self.ttl = timedelta(minutes=ttl_minutes)
        self.logger = get_logger()
    
    def _get_cache_key(self, prompt: str, files: List[str], mode: str) -> str:
        """Generate cache key for the request."""
        content = f"{prompt}:{','.join(sorted(files))}:{mode}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, prompt: str, files: List[str], mode: str) -> Optional[str]:
        """Get cached result if available and not expired."""
        key = self._get_cache_key(prompt, files, mode)
        
        if key in self.cache:
            result, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                self.logger.logger.debug(f"Cache hit for RAG query: {key[:8]}...")
                return result
            else:
                # Remove expired entry
                del self.cache[key]
        
        return None
    
    def set(self, prompt: str, files: List[str], mode: str, result: str):
        """Cache the result."""
        key = self._get_cache_key(prompt, files, mode)
        
        # Remove oldest entries if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
        self.cache[key] = (result, datetime.now())
        self.logger.logger.debug(f"Cached RAG result: {key[:8]}...")


# Global cache instance
_rag_cache = None


def get_rag_cache() -> RAGCache:
    """Get global RAG cache instance."""
    global _rag_cache
    if _rag_cache is None:
        config = get_config()
        cache_size = config.performance.cache_size_mb if hasattr(config.performance, 'cache_size_mb') else 100
        _rag_cache = RAGCache(max_size=cache_size)
    return _rag_cache


@robust_operation(operation_name="rag_answer")
def rag_answer(prompt: str, files: List[str], expert_model: str = None, 
               chat_history: List[Dict] = None, user: str = None, 
               endpoint: str = None, mode: str = "file") -> str:
    """
    Enhanced RAG function with caching, error handling, and performance monitoring.
    
    Args:
        prompt: The user's question/prompt
        files: List of file paths to use as context
        expert_model: The expert model to use
        chat_history: Previous chat history
        user: Username
        endpoint: RAG API endpoint
        mode: "file", "search", or "auto"
        
    Returns:
        Generated response with context from files
    """
    logger = get_logger()
    config = get_config()
    start_time = time.time()
    
    # Check cache first if enabled
    if config.performance.enable_caching:
        cached_result = get_rag_cache().get(prompt, files, mode)
        if cached_result:
            duration = time.time() - start_time
            logger.log_performance("rag_answer_cached", duration, {"cache_hit": True})
            return cached_result
    
    try:
        context = []
        context_header = ""
        
        if mode == "file":
            context, context_header = _process_file_context(files, config)
        elif mode == "search":
            context, context_header = _process_search_context(prompt, config)
        elif mode == "auto":
            context, context_header = _process_auto_context(prompt, files, config)
        else:
            raise ValueError(f"Unsupported RAG mode: {mode}")
        
        # Generate contextual prompt
        contextual_prompt = _build_contextual_prompt(prompt, context, context_header)
        
        # Make API call to LLM
        result = _call_llm_api(contextual_prompt, expert_model, endpoint, user, config)
        
        # Cache result if enabled
        if config.performance.enable_caching:
            get_rag_cache().set(prompt, files, mode, result)
        
        # Log performance
        duration = time.time() - start_time
        logger.log_performance("rag_answer", duration, {
            "mode": mode, 
            "files_count": len(files), 
            "context_length": len(str(context))
        })
        
        return result
        
    except Exception as e:
        error_handler = get_error_handler()
        error_info = error_handler.handle_error(e, {
            "prompt": prompt[:100],
            "mode": mode,
            "files_count": len(files),
            "user": user
        }, "rag_answer")
        
        # Return helpful error message
        return f"I apologize, but I encountered an error while processing your request: {str(e)}. Please try again or contact support if the issue persists."


def _process_file_context(files: List[str], config) -> Tuple[List[str], str]:
    """Process file-based context."""
    context = []
    if not files:
        return ["No files provided for context."], "No file context available:"
    
    for file_path in files:
        try:
            if os.path.exists(file_path):
                content = extract_file_content(file_path, config.rag.max_file_size_mb * 1024 * 1024)
                context.append(f"File: {os.path.basename(file_path)}\n{content}")
            else:
                context.append(f"File not found: {file_path}")
        except Exception as e:
            context.append(f"Error reading {file_path}: {str(e)}")
    
    return context, "Context from uploaded files:"


def _process_search_context(prompt: str, config) -> Tuple[List[str], str]:
    """Process search-based context."""
    search_results = duckduckgo_search(prompt, config.rag.max_search_results)
    return [search_results], "Context from DuckDuckGo search:"


def _process_auto_context(prompt: str, files: List[str], config) -> Tuple[List[str], str]:
    """Process automatic context selection."""
    context = []
    
    # Try file context first
    if files:
        file_context, _ = _process_file_context(files, config)
        context.extend(file_context)
        context_header = "Context from uploaded files:"
    else:
        # Try search if no files
        search_context, _ = _process_search_context(prompt, config)
        if search_context and "No results found." not in search_context[0]:
            context.extend(search_context)
            context_header = "Context from DuckDuckGo search:"
        else:
            # Fallback to browser automation if enabled
            if config.rag.enable_browser_automation:
                try:
                    from agent.browser_automation import trigger_browser_task
                    browser_result = trigger_browser_task(prompt)
                    context.append(f"Browser Automation Result: {browser_result}")
                    context_header = "Context from browser automation:"
                except ImportError:
                    context.append("Browser automation not available")
                    context_header = "Limited context available:"
            
            # Human-in-loop if enabled
            if config.rag.enable_human_in_loop:
                try:
                    from agent.human_in_loop import request_human_reasoning
                    human_reasoning = request_human_reasoning(
                        prompt,
                        reasoning_path="No relevant context found. Please provide reasoning or next steps."
                    )
                    context.append(f"Human Reasoning: {human_reasoning}")
                except ImportError:
                    pass
    
    return context, context_header


def _build_contextual_prompt(prompt: str, context: List[str], context_header: str) -> str:
    """Build the contextual prompt for the LLM."""
    return f"""
{context_header}
{chr(10).join(context)}

User Question: {prompt}

Please answer the user's question using the provided context. If the context doesn't contain relevant information, mention this in your response and provide the best answer you can based on your knowledge.
"""


def _call_llm_api(contextual_prompt: str, expert_model: str, endpoint: str, user: str, config) -> str:
    """Make API call to LLM with proper error handling."""
    try:
        from agent.tools import llm_api_call
        return llm_api_call(
            contextual_prompt, 
            expert_model or config.integrations.default_model,
            endpoint or config.integrations.ollama_endpoint,
            user
        )
    except Exception as e:
        raise Exception(f"LLM API call failed: {str(e)}")


def rag_answer_old(prompt: str, files: List[str], expert_model: str = None, 
               chat_history: List[Dict] = None, user: str = None, 
               endpoint: str = None, mode: str = "file") -> str:
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
    result = llm_api_call(contextual_prompt, expert_model, None, chat_history, user, "http://localhost:11434")
    
    # If the result is a structured CoT response, preserve it
    if isinstance(result, dict) and result.get("type") == "cot_response":
        return result
    else:
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