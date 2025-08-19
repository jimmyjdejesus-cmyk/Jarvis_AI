"""
Enhanced RAG Handler - Consolidated version for local Ollama integration
Uses local context processing with fallback to browser automation only for unsupported tasks.
"""

from agent.features.rag_handler import rag_answer as enhanced_rag_answer

def rag_answer(prompt, files, model_name, chat_history, user, endpoint):
    """
    Enhanced RAG function using local context with automatic mode selection.
    Prioritizes local file context, falls back to search, then browser automation.
    """
    return enhanced_rag_answer(
        prompt=prompt,
        files=files,
        expert_model=model_name,
        chat_history=chat_history,
        user=user,
        endpoint=endpoint,
        mode="auto"  # Use auto mode for intelligent context selection
    )