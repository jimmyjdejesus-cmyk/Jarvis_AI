"""
Jarvis AI - Privacy-first modular AI development assistant
"""

__version__ = "2.0.0"
__author__ = "Jimmy De Jesus"
__email__ = "jimmy@example.com"

# Re-export main components for easy access
try:
    from legacy.agent.core.core import JarvisAgent
    from legacy.agent.core.config_manager import get_config_manager, JarvisConfig
    from legacy.setup_enhanced import JarvisInstaller
except ImportError:
    # Fallback if legacy modules aren't available
    JarvisAgent = None
    get_config_manager = None
    JarvisConfig = None
    JarvisInstaller = None

__all__ = [
    "__version__",
    "__author__", 
    "__email__",
    "JarvisAgent",
    "get_config_manager",
    "JarvisConfig",
    "JarvisInstaller",
]