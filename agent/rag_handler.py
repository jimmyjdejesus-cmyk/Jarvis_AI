"""
RAG (Retrieval Augmented Generation) Handler Module
Handles retrieval and augmentation of context for LLM responses.
"""
import requests
import os
from typing import List, Dict, Any


def rag_answer(prompt: str, files: List[str], expert_model: str = None, 
               chat_history: List[Dict] = None, user: str = None, 
               endpoint: str = None) -> str:
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
    if not files:
        return "No files provided for context."
    
    # Read and prepare context from files
    context = []
    for file_path in files:
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    context.append(f"File: {os.path.basename(file_path)}\n{content[:2000]}...")  # Limit content size
        except Exception as e:
            context.append(f"Error reading {file_path}: {str(e)}")
    
    # Combine context with prompt
    contextual_prompt = f"""
Context from uploaded files:
{chr(10).join(context)}

User Question: {prompt}

Please answer the user's question using the provided context. If the context doesn't contain relevant information, mention this in your response.
"""
    
    # Make API call to RAG endpoint
    if endpoint:
        payload = {
            "prompt": contextual_prompt,
            "expert_model": expert_model,
            "chat_history": chat_history or [],
            "user": user,
            "files": files
        }
        try:
            response = requests.post(endpoint, json=payload, timeout=30)
            if response.ok:
                return response.json().get("response", "No response from RAG endpoint.")
            else:
                return f"RAG API error: {response.status_code} {response.text}"
        except Exception as e:
            return f"RAG API request failed: {e}"
    
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