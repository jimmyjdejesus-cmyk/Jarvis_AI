#!/usr/bin/env python3
"""
Jarvis AI Extensibility SDK

This module provides the SDK for third-party plugin development, enabling
easy creation of custom plugins that integrate with both the Jarvis AI
plugin system and the Lang ecosystem.
"""

from typing import Any, Dict, List, Optional, Callable, Union
import inspect
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

# Import base plugin system
from agent.adapters.plugin_base import (
    BasePlugin, PluginMetadata, PluginAction, PluginResult, PluginType,
    AutomationPlugin, IntegrationPlugin, CommandPlugin, WorkflowPlugin
)

# Import LangChain integration
try:
    from agent.adapters.langchain_tools import jarvis_tool, LANGCHAIN_AVAILABLE
except ImportError:
    LANGCHAIN_AVAILABLE = False
    
    def jarvis_tool(name: str = None, description: str = None, **kwargs):
        """Fallback decorator when LangChain is not available."""
        def decorator(func):
            return func
        return decorator


class PluginSDK:
    """Main SDK class for plugin development."""
    
    @staticmethod
    def create_automation_plugin(name: str, description: str, version: str = "1.0.0",
                                author: str = "Unknown", triggers: List[str] = None) -> type:
        """Factory method to create an automation plugin class."""
        
        class DynamicAutomationPlugin(AutomationPlugin):
            def get_metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name=name,
                    description=description,
                    version=version,
                    author=author,
                    plugin_type=PluginType.AUTOMATION,
                    triggers=triggers or []
                )
        
        DynamicAutomationPlugin.__name__ = f"{name}Plugin"
        return DynamicAutomationPlugin
    
    @staticmethod
    def create_integration_plugin(name: str, description: str, version: str = "1.0.0",
                                 author: str = "Unknown", triggers: List[str] = None) -> type:
        """Factory method to create an integration plugin class."""
        
        class DynamicIntegrationPlugin(IntegrationPlugin):
            def get_metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name=name,
                    description=description,
                    version=version,
                    author=author,
                    plugin_type=PluginType.INTEGRATION,
                    triggers=triggers or []
                )
            
            def check_authentication(self) -> bool:
                """Default implementation - override in subclass."""
                return True
        
        DynamicIntegrationPlugin.__name__ = f"{name}Plugin"
        return DynamicIntegrationPlugin
    
    @staticmethod
    def register_plugin(plugin_instance: BasePlugin) -> bool:
        """Register a plugin instance with the plugin manager."""
        try:
            from agent.adapters.plugin_registry import plugin_manager
            return plugin_manager.registry.register_plugin(plugin_instance)
        except Exception as e:
            logger.error(f"Failed to register plugin: {e}")
            return False


@dataclass
class PluginManifest:
    """Manifest for plugin packages."""
    name: str
    description: str
    version: str
    author: str
    license: str = "MIT"
    homepage: str = ""
    repository: str = ""
    keywords: List[str] = field(default_factory=list)
    dependencies: Dict[str, str] = field(default_factory=dict)
    plugin_entry_point: str = "main"
    supported_platforms: List[str] = field(default_factory=lambda: ["all"])
    min_jarvis_version: str = "1.0.0"


class KnowledgeSourcePlugin(ABC):
    """Base class for custom knowledge source plugins."""
    
    @abstractmethod
    def get_source_name(self) -> str:
        """Return the name of this knowledge source."""
        pass
    
    @abstractmethod
    def can_handle_query(self, query: str, context: Dict[str, Any] = None) -> bool:
        """Check if this knowledge source can handle the query."""
        pass
    
    @abstractmethod
    def retrieve_knowledge(self, query: str, context: Dict[str, Any] = None,
                          max_results: int = 10) -> List[Dict[str, Any]]:
        """Retrieve relevant knowledge for the query."""
        pass
    
    @abstractmethod
    def get_source_metadata(self) -> Dict[str, Any]:
        """Return metadata about this knowledge source."""
        pass


class LanguageEnhancerPlugin(ABC):
    """Base class for language-specific enhancer plugins."""
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Return list of supported programming languages."""
        pass
    
    @abstractmethod
    def enhance_code_analysis(self, code: str, language: str, 
                            context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enhance code analysis for the specific language."""
        pass
    
    @abstractmethod
    def get_language_specific_tools(self, language: str) -> List[str]:
        """Return language-specific tools and commands."""
        pass


class BuildSystemPlugin(ABC):
    """Base class for build system integration plugins."""
    
    @abstractmethod
    def get_build_system_name(self) -> str:
        """Return the name of the build system."""
        pass
    
    @abstractmethod
    def detect_build_system(self, project_path: str) -> bool:
        """Detect if this build system is used in the project."""
        pass
    
    @abstractmethod
    def get_build_commands(self, project_path: str) -> List[Dict[str, Any]]:
        """Get available build commands for the project."""
        pass
    
    @abstractmethod
    def execute_build_command(self, command: str, project_path: str,
                            options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a build command."""
        pass


class TestingFrameworkPlugin(ABC):
    """Base class for testing framework integration plugins."""
    
    @abstractmethod
    def get_framework_name(self) -> str:
        """Return the name of the testing framework."""
        pass
    
    @abstractmethod
    def detect_framework(self, project_path: str) -> bool:
        """Detect if this testing framework is used in the project."""
        pass
    
    @abstractmethod
    def get_test_commands(self, project_path: str) -> List[Dict[str, Any]]:
        """Get available test commands for the project."""
        pass
    
    @abstractmethod
    def run_tests(self, test_path: str = None, project_path: str = None,
                 options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run tests and return results."""
        pass


# Convenience decorators for plugin development
def knowledge_source(name: str, description: str = "", priority: int = 0):
    """Decorator for knowledge source methods."""
    def decorator(func):
        func._knowledge_source_name = name
        func._knowledge_source_description = description
        func._knowledge_source_priority = priority
        return func
    return decorator


def language_enhancer(languages: List[str], priority: int = 0):
    """Decorator for language enhancer methods."""
    def decorator(func):
        func._supported_languages = languages
        func._enhancer_priority = priority
        return func
    return decorator


def build_system(name: str, file_patterns: List[str] = None):
    """Decorator for build system detection methods."""
    def decorator(func):
        func._build_system_name = name
        func._build_system_patterns = file_patterns or []
        return func
    return decorator


def testing_framework(name: str, file_patterns: List[str] = None):
    """Decorator for testing framework detection methods."""
    def decorator(func):
        func._testing_framework_name = name
        func._testing_framework_patterns = file_patterns or []
        return func
    return decorator


# Example plugin templates
class ExampleKnowledgeSourcePlugin(KnowledgeSourcePlugin):
    """Example implementation of a knowledge source plugin."""
    
    def __init__(self, source_name: str = "example_source"):
        self.source_name = source_name
    
    def get_source_name(self) -> str:
        return self.source_name
    
    def can_handle_query(self, query: str, context: Dict[str, Any] = None) -> bool:
        # Example: handle queries containing specific keywords
        keywords = ["example", "sample", "demo"]
        return any(keyword in query.lower() for keyword in keywords)
    
    def retrieve_knowledge(self, query: str, context: Dict[str, Any] = None,
                          max_results: int = 10) -> List[Dict[str, Any]]:
        # Example implementation
        return [{
            "title": "Example Knowledge",
            "content": f"Example knowledge for query: {query}",
            "source": self.source_name,
            "relevance_score": 0.8
        }]
    
    def get_source_metadata(self) -> Dict[str, Any]:
        return {
            "name": self.source_name,
            "type": "example",
            "description": "Example knowledge source for demonstration",
            "capabilities": ["query", "retrieve"],
            "version": "1.0.0"
        }


class ExampleLanguageEnhancerPlugin(LanguageEnhancerPlugin):
    """Example implementation of a language enhancer plugin."""
    
    def get_supported_languages(self) -> List[str]:
        return ["python", "javascript", "typescript"]
    
    def enhance_code_analysis(self, code: str, language: str,
                            context: Dict[str, Any] = None) -> Dict[str, Any]:
        # Example enhancement - add language-specific insights
        enhancements = {
            "language": language,
            "suggestions": [
                f"Consider using {language}-specific best practices",
                f"Optimize for {language} performance characteristics"
            ],
            "patterns_detected": [],
            "complexity_score": len(code.split('\n')) / 10
        }
        
        if language == "python":
            enhancements["suggestions"].append("Consider using type hints")
            enhancements["patterns_detected"].append("python_specific_patterns")
        
        return enhancements
    
    def get_language_specific_tools(self, language: str) -> List[str]:
        tools_map = {
            "python": ["pylint", "black", "mypy", "pytest"],
            "javascript": ["eslint", "prettier", "jest"],
            "typescript": ["tslint", "prettier", "jest", "tsc"]
        }
        return tools_map.get(language, [])


# Utility functions for plugin development
def validate_plugin_manifest(manifest: PluginManifest) -> List[str]:
    """Validate a plugin manifest and return any errors."""
    errors = []
    
    if not manifest.name:
        errors.append("Plugin name is required")
    
    if not manifest.description:
        errors.append("Plugin description is required")
    
    if not manifest.version:
        errors.append("Plugin version is required")
    
    if not manifest.author:
        errors.append("Plugin author is required")
    
    return errors


def create_plugin_from_functions(name: str, functions: List[Callable],
                                description: str = "", triggers: List[str] = None) -> BasePlugin:
    """Create a plugin from a list of functions."""
    
    class FunctionBasedPlugin(AutomationPlugin):
        def __init__(self):
            self.functions = {func.__name__: func for func in functions}
        
        def get_metadata(self) -> PluginMetadata:
            return PluginMetadata(
                name=name,
                description=description or f"Plugin created from {len(functions)} functions",
                version="1.0.0",
                author="Dynamic",
                plugin_type=PluginType.AUTOMATION,
                triggers=triggers or []
            )
        
        def can_handle(self, command: str, context: Dict[str, Any] = None) -> bool:
            # Check if command mentions any of our function names
            command_lower = command.lower()
            return any(func_name.lower() in command_lower for func_name in self.functions.keys())
        
        def parse_command(self, command: str, context: Dict[str, Any] = None) -> Optional[PluginAction]:
            # Simple parsing - look for function names in command
            for func_name, func in self.functions.items():
                if func_name.lower() in command.lower():
                    return PluginAction(
                        name=func_name,
                        description=f"Execute {func_name}",
                        args={"command": command, "context": context or {}}
                    )
            return None
        
        def execute_action(self, action: PluginAction, context: Dict[str, Any] = None) -> PluginResult:
            try:
                func = self.functions.get(action.name)
                if not func:
                    return PluginResult(success=False, error=f"Function {action.name} not found")
                
                # Execute the function
                result = func(**action.args)
                return PluginResult(success=True, output=result)
                
            except Exception as e:
                return PluginResult(success=False, error=str(e))
    
    return FunctionBasedPlugin()


# Export main SDK components
__all__ = [
    'PluginSDK',
    'PluginManifest', 
    'KnowledgeSourcePlugin',
    'LanguageEnhancerPlugin',
    'BuildSystemPlugin',
    'TestingFrameworkPlugin',
    'ExampleKnowledgeSourcePlugin',
    'ExampleLanguageEnhancerPlugin',
    'jarvis_tool',
    'knowledge_source',
    'language_enhancer', 
    'build_system',
    'testing_framework',
    'validate_plugin_manifest',
    'create_plugin_from_functions'
]