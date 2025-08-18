"""
Base classes and interfaces for the Jarvis AI plugin system.

This module defines the core interfaces that all plugins must implement,
providing a standardized way to create extensible automation tools.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum


class PluginType(Enum):
    """Types of plugins supported by the system."""
    AUTOMATION = "automation"
    INTEGRATION = "integration"
    COMMAND = "command"
    WORKFLOW = "workflow"


@dataclass
class PluginMetadata:
    """Metadata for a plugin."""
    name: str
    description: str
    version: str
    author: str
    plugin_type: PluginType
    triggers: List[str]  # Natural language triggers
    dependencies: List[str] = None
    tags: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.tags is None:
            self.tags = []


@dataclass
class PluginAction:
    """Represents a single action that a plugin can perform."""
    name: str
    description: str
    args: Dict[str, Any]
    preview: str = ""
    requires_approval: bool = False


@dataclass
class PluginResult:
    """Result of a plugin execution."""
    success: bool
    output: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BasePlugin(ABC):
    """Abstract base class for all Jarvis AI plugins."""
    
    def __init__(self):
        self._metadata = self.get_metadata()
    
    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return self._metadata
    
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Return metadata about this plugin."""
        pass
    
    @abstractmethod
    def can_handle(self, command: str, context: Dict[str, Any] = None) -> bool:
        """Check if this plugin can handle the given command."""
        pass
    
    @abstractmethod
    def parse_command(self, command: str, context: Dict[str, Any] = None) -> Optional[PluginAction]:
        """Parse a natural language command into a plugin action."""
        pass
    
    @abstractmethod
    def preview_action(self, action: PluginAction) -> str:
        """Generate a human-readable preview of what the action will do."""
        pass
    
    @abstractmethod
    def execute_action(self, action: PluginAction, context: Dict[str, Any] = None) -> PluginResult:
        """Execute the given action."""
        pass
    
    def validate_action(self, action: PluginAction) -> bool:
        """Validate that an action can be executed. Override if needed."""
        return True


class WorkflowPlugin(BasePlugin):
    """Base class for plugins that can be part of workflows."""
    
    @abstractmethod
    def get_output_schema(self) -> Dict[str, Any]:
        """Return the schema of data this plugin outputs for workflow chaining."""
        pass
    
    @abstractmethod
    def get_input_schema(self) -> Dict[str, Any]:
        """Return the schema of data this plugin expects as input."""
        pass
    
    def can_chain_with(self, other_plugin: 'WorkflowPlugin') -> bool:
        """Check if this plugin's output is compatible with another plugin's input."""
        try:
            output_schema = self.get_output_schema()
            input_schema = other_plugin.get_input_schema()
            
            # Simple compatibility check - can be enhanced
            for key, expected_type in input_schema.items():
                if key in output_schema:
                    if output_schema[key] != expected_type:
                        return False
                else:
                    # Required input not provided
                    return False
            return True
        except Exception:
            return False


class AutomationPlugin(WorkflowPlugin):
    """Base class for automation plugins (git, browser, etc.)."""
    
    def get_metadata(self) -> PluginMetadata:
        """Default metadata for automation plugins."""
        return PluginMetadata(
            name=self.__class__.__name__,
            description="Automation plugin",
            version="1.0.0",
            author="Jarvis AI",
            plugin_type=PluginType.AUTOMATION,
            triggers=[]
        )


class IntegrationPlugin(WorkflowPlugin):
    """Base class for integration plugins (GitHub, Notion, etc.)."""
    
    def get_metadata(self) -> PluginMetadata:
        """Default metadata for integration plugins."""
        return PluginMetadata(
            name=self.__class__.__name__,
            description="Integration plugin",
            version="1.0.0",
            author="Jarvis AI",
            plugin_type=PluginType.INTEGRATION,
            triggers=[]
        )
    
    @abstractmethod
    def check_authentication(self) -> bool:
        """Check if the integration is properly authenticated."""
        pass


class CommandPlugin(BasePlugin):
    """Base class for simple command plugins."""
    
    def get_metadata(self) -> PluginMetadata:
        """Default metadata for command plugins."""
        return PluginMetadata(
            name=self.__class__.__name__,
            description="Command plugin",
            version="1.0.0",
            author="Jarvis AI",
            plugin_type=PluginType.COMMAND,
            triggers=[]
        )
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Simple commands typically return string output."""
        return {"output": str}
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Simple commands typically take command string input."""
        return {"command": str}