"""
Code Intelligence Engine Package
Provides GitHub Copilot-like functionality using local Ollama models.
"""

from .engine import CodeIntelligenceEngine, get_code_completion, record_completion_feedback

__all__ = ['CodeIntelligenceEngine', 'get_code_completion', 'record_completion_feedback']
