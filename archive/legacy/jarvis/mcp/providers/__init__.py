"""
Model providers for cloud-first AI routing.

Separation of Concerns:
- base.py: Abstract base classes and interfaces
- openrouter.py: OpenRouter cloud provider implementation
- ollama.py: Ollama local provider implementation
- factory.py: Provider factory for instantiation
"""

from .base import BaseModelProvider, ProviderConfig
from .openrouter import OpenRouterProvider
from .ollama import OllamaProvider
from .factory import ProviderFactory

__all__ = [
    "BaseModelProvider",
    "ProviderConfig",
    "OpenRouterProvider",
    "OllamaProvider",
    "ProviderFactory",
]
