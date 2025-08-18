"""
Plugin registry and discovery system for Jarvis AI.

This module manages plugin discovery, registration, and provides
an interface for finding and executing plugins based on natural language commands.
"""

import os
import importlib
import importlib.util
from typing import Dict, List, Optional, Type, Any
import logging
from pathlib import Path

from agent.plugin_base import BasePlugin, PluginMetadata, PluginAction, PluginResult, PluginType


logger = logging.getLogger(__name__)


class PluginRegistry:
    """Central registry for managing plugins."""
    
    def __init__(self):
        self._plugins: Dict[str, BasePlugin] = {}
        self._plugin_paths: List[str] = []
        self._trigger_map: Dict[str, List[str]] = {}  # trigger phrase -> plugin names
    
    def register_plugin(self, plugin: BasePlugin) -> bool:
        """Register a plugin instance."""
        try:
            plugin_name = plugin.metadata.name
            if plugin_name in self._plugins:
                logger.warning(f"Plugin {plugin_name} already registered, overwriting")
            
            self._plugins[plugin_name] = plugin
            
            # Register triggers
            for trigger in plugin.metadata.triggers:
                trigger_lower = trigger.lower()
                if trigger_lower not in self._trigger_map:
                    self._trigger_map[trigger_lower] = []
                if plugin_name not in self._trigger_map[trigger_lower]:
                    self._trigger_map[trigger_lower].append(plugin_name)
            
            logger.info(f"Registered plugin: {plugin_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to register plugin: {e}")
            return False
    
    def unregister_plugin(self, plugin_name: str) -> bool:
        """Unregister a plugin."""
        if plugin_name not in self._plugins:
            return False
        
        plugin = self._plugins[plugin_name]
        
        # Remove from trigger map
        for trigger in plugin.metadata.triggers:
            trigger_lower = trigger.lower()
            if trigger_lower in self._trigger_map:
                if plugin_name in self._trigger_map[trigger_lower]:
                    self._trigger_map[trigger_lower].remove(plugin_name)
                if not self._trigger_map[trigger_lower]:
                    del self._trigger_map[trigger_lower]
        
        del self._plugins[plugin_name]
        logger.info(f"Unregistered plugin: {plugin_name}")
        return True
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get a registered plugin by name."""
        return self._plugins.get(plugin_name)
    
    def list_plugins(self, plugin_type: Optional[PluginType] = None) -> List[BasePlugin]:
        """List all registered plugins, optionally filtered by type."""
        plugins = list(self._plugins.values())
        if plugin_type:
            plugins = [p for p in plugins if p.metadata.plugin_type == plugin_type]
        return plugins
    
    def find_plugins_for_command(self, command: str, context: Dict[str, Any] = None) -> List[BasePlugin]:
        """Find plugins that can handle the given command."""
        matching_plugins = []
        command_lower = command.lower()
        
        # First, check trigger-based matching
        for trigger, plugin_names in self._trigger_map.items():
            if trigger in command_lower:
                for plugin_name in plugin_names:
                    plugin = self._plugins.get(plugin_name)
                    if plugin and plugin not in matching_plugins:
                        matching_plugins.append(plugin)
        
        # Then, check each plugin's can_handle method
        for plugin in self._plugins.values():
            if plugin not in matching_plugins:
                try:
                    if plugin.can_handle(command, context):
                        matching_plugins.append(plugin)
                except Exception as e:
                    logger.warning(f"Plugin {plugin.metadata.name} failed can_handle check: {e}")
        
        return matching_plugins
    
    def add_plugin_path(self, path: str):
        """Add a directory to search for plugins."""
        if path not in self._plugin_paths:
            self._plugin_paths.append(path)
    
    def discover_plugins(self) -> int:
        """Discover and load plugins from registered paths."""
        discovered = 0
        
        for plugin_path in self._plugin_paths:
            discovered += self._discover_plugins_in_path(plugin_path)
        
        return discovered
    
    def _discover_plugins_in_path(self, path: str) -> int:
        """Discover plugins in a specific path."""
        discovered = 0
        path_obj = Path(path)
        
        if not path_obj.exists():
            logger.warning(f"Plugin path does not exist: {path}")
            return 0
        
        # Look for Python files that might contain plugins
        for py_file in path_obj.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            
            try:
                module_name = py_file.stem
                spec = importlib.util.spec_from_file_location(module_name, py_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Look for plugin classes in the module
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            issubclass(attr, BasePlugin) and 
                            attr != BasePlugin and
                            not attr.__name__.startswith('_')):
                            
                            try:
                                plugin_instance = attr()
                                if self.register_plugin(plugin_instance):
                                    discovered += 1
                            except Exception as e:
                                logger.error(f"Failed to instantiate plugin {attr_name}: {e}")
            
            except Exception as e:
                logger.error(f"Failed to load plugin file {py_file}: {e}")
        
        return discovered
    
    def get_plugin_info(self) -> Dict[str, Dict]:
        """Get information about all registered plugins."""
        info = {}
        for name, plugin in self._plugins.items():
            metadata = plugin.metadata
            info[name] = {
                "name": metadata.name,
                "description": metadata.description,
                "version": metadata.version,
                "author": metadata.author,
                "type": metadata.plugin_type.value,
                "triggers": metadata.triggers,
                "tags": metadata.tags,
                "dependencies": metadata.dependencies
            }
        return info


class PluginManager:
    """High-level manager for plugin operations."""
    
    def __init__(self):
        self.registry = PluginRegistry()
        self._setup_default_plugin_paths()
    
    def _setup_default_plugin_paths(self):
        """Setup default paths to search for plugins."""
        # Add the agent directory (where existing tools are)
        agent_dir = os.path.join(os.path.dirname(__file__))
        self.registry.add_plugin_path(agent_dir)
        
        # Add a plugins directory if it exists
        plugins_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "plugins")
        if os.path.exists(plugins_dir):
            self.registry.add_plugin_path(plugins_dir)
    
    def initialize(self) -> int:
        """Initialize the plugin system by discovering and loading plugins."""
        return self.registry.discover_plugins()
    
    def parse_command(self, command: str, context: Dict[str, Any] = None) -> Optional[PluginAction]:
        """Parse a command and return the first matching plugin action."""
        plugins = self.registry.find_plugins_for_command(command, context)
        
        for plugin in plugins:
            try:
                action = plugin.parse_command(command, context)
                if action:
                    return action
            except Exception as e:
                logger.warning(f"Plugin {plugin.metadata.name} failed to parse command: {e}")
        
        return None
    
    def execute_action(self, action: PluginAction, context: Dict[str, Any] = None) -> PluginResult:
        """Execute a plugin action."""
        # Find the plugin that can handle this action
        for plugin in self.registry.list_plugins():
            try:
                # Check if this plugin created the action (simple check by name matching)
                if action.name.startswith(plugin.metadata.name.lower()):
                    if plugin.validate_action(action):
                        return plugin.execute_action(action, context)
            except Exception as e:
                logger.warning(f"Plugin {plugin.metadata.name} failed to execute action: {e}")
        
        return PluginResult(success=False, output=None, error="No plugin found to execute action")
    
    def preview_action(self, action: PluginAction) -> str:
        """Get a preview of what an action will do."""
        for plugin in self.registry.list_plugins():
            try:
                if action.name.startswith(plugin.metadata.name.lower()):
                    return plugin.preview_action(action)
            except Exception as e:
                logger.warning(f"Plugin {plugin.metadata.name} failed to preview action: {e}")
        
        return f"Action: {action.name} with args: {action.args}"


# Global plugin manager instance
plugin_manager = PluginManager()