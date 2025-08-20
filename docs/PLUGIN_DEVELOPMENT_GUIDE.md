# Jarvis AI Plugin Development Guide

This comprehensive guide will help you create custom plugins for the Jarvis AI extensibility framework, integrating with both the native plugin system and the Lang ecosystem (LangChain, LangGraph, LangSmith).

## Table of Contents

1. [Quick Start](#quick-start)
2. [Plugin Types](#plugin-types)
3. [SDK Reference](#sdk-reference)
4. [LangChain Integration](#langchain-integration)
5. [LangGraph Workflows](#langgraph-workflows)
6. [API Reference](#api-reference)
7. [Example Plugins](#example-plugins)
8. [Testing Plugins](#testing-plugins)
9. [Deployment](#deployment)
10. [Best Practices](#best-practices)

## Quick Start

### Installation

First, ensure you have the Jarvis AI development environment set up:

```bash
# Clone the repository
git clone https://github.com/jimmyjdejesus-cmyk/Jarvis_AI.git
cd Jarvis_AI/legacy

# Install dependencies
pip install -r requirements_enhanced.txt
```

### Creating Your First Plugin

```python
from agent.adapters.extensibility_sdk import PluginSDK, jarvis_tool
from agent.adapters.plugin_base import AutomationPlugin, PluginMetadata, PluginAction, PluginResult, PluginType

class MyFirstPlugin(AutomationPlugin):
    """A simple example plugin."""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="MyFirstPlugin",
            description="A simple plugin that greets users",
            version="1.0.0",
            author="Your Name",
            plugin_type=PluginType.AUTOMATION,
            triggers=["hello", "greet", "say hello"],
            tags=["example", "greeting"]
        )
    
    def can_handle(self, command: str, context: dict = None) -> bool:
        return "hello" in command.lower() or "greet" in command.lower()
    
    def parse_command(self, command: str, context: dict = None) -> PluginAction:
        return PluginAction(
            name="greet_user",
            description="Greet the user",
            args={"message": command, "context": context or {}}
        )
    
    def execute_action(self, action: PluginAction, context: dict = None) -> PluginResult:
        user_name = context.get("user", "there") if context else "there"
        greeting = f"Hello {user_name}! You said: {action.args.get('message', '')}"
        
        return PluginResult(
            success=True,
            output=greeting
        )

# Register the plugin
plugin_instance = MyFirstPlugin()
PluginSDK.register_plugin(plugin_instance)
```

### Using the @jarvis_tool Decorator

For simpler use cases, you can use the `@jarvis_tool` decorator:

```python
from agent.adapters.extensibility_sdk import jarvis_tool

@jarvis_tool(
    name="weather_check",
    description="Check the weather for a location",
    triggers=["weather", "forecast", "temperature"]
)
def check_weather(location: str = "current location") -> str:
    """Check weather for a given location."""
    # Your weather checking logic here
    return f"The weather in {location} is sunny and 72°F"
```

## Plugin Types

### 1. Automation Plugins

For automating development tasks like git operations, file management, etc.

```python
class GitAutomationPlugin(AutomationPlugin):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="GitAutomation",
            description="Automate git operations",
            version="1.0.0",
            author="Developer",
            plugin_type=PluginType.AUTOMATION,
            triggers=["git", "commit", "push", "pull"]
        )
```

### 2. Integration Plugins

For integrating with external services and APIs.

```python
class SlackIntegrationPlugin(IntegrationPlugin):
    def check_authentication(self) -> bool:
        # Check if Slack API token is valid
        return self.validate_slack_token()
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="SlackIntegration",
            description="Send messages to Slack channels",
            version="1.0.0",
            author="Developer",
            plugin_type=PluginType.INTEGRATION,
            triggers=["slack", "send message", "notify team"]
        )
```

### 3. Knowledge Source Plugins

For adding custom knowledge sources to the RAG system.

```python
from agent.adapters.extensibility_sdk import KnowledgeSourcePlugin

class DocumentationKnowledgeSource(KnowledgeSourcePlugin):
    def get_source_name(self) -> str:
        return "project_documentation"
    
    def can_handle_query(self, query: str, context: dict = None) -> bool:
        # Check if query is about documentation
        doc_keywords = ["docs", "documentation", "how to", "guide", "tutorial"]
        return any(keyword in query.lower() for keyword in doc_keywords)
    
    def retrieve_knowledge(self, query: str, context: dict = None, max_results: int = 10) -> list:
        # Search your documentation and return relevant results
        return [{
            "title": "Relevant Documentation",
            "content": "Documentation content here...",
            "source": self.get_source_name(),
            "relevance_score": 0.9
        }]
    
    def get_source_metadata(self) -> dict:
        return {
            "name": self.get_source_name(),
            "type": "documentation",
            "description": "Project documentation knowledge source",
            "capabilities": ["search", "retrieve"],
            "version": "1.0.0"
        }
```

### 4. Build System Plugins

For integrating with build systems and tools.

```python
from agent.adapters.extensibility_sdk import BuildSystemPlugin

class MavenBuildPlugin(BuildSystemPlugin):
    def get_build_system_name(self) -> str:
        return "maven"
    
    def detect_build_system(self, project_path: str) -> bool:
        return (Path(project_path) / "pom.xml").exists()
    
    def get_build_commands(self, project_path: str) -> list:
        return [
            {"name": "compile", "command": "mvn compile", "description": "Compile the project"},
            {"name": "test", "command": "mvn test", "description": "Run tests"},
            {"name": "package", "command": "mvn package", "description": "Package the project"}
        ]
    
    def execute_build_command(self, command: str, project_path: str, options: dict = None) -> dict:
        # Execute Maven command and return results
        pass
```

## LangChain Integration

### Using LangChain Tools

Jarvis AI plugins automatically integrate with LangChain tools:

```python
from langchain_core.tools import tool
from agent.adapters.extensibility_sdk import jarvis_tool

# Both decorators can be combined
@tool
@jarvis_tool(name="file_analyzer", description="Analyze file contents")
def analyze_file(file_path: str) -> str:
    """Analyze a file and return insights."""
    # Your analysis logic here
    return f"Analysis of {file_path}: ..."

# This creates both a LangChain tool and a Jarvis plugin
```

### Custom LangChain Tool Wrapper

```python
from langchain_core.tools import BaseTool
from agent.adapters.langchain_tools import PluginToolWrapper

class CustomLangChainTool(BaseTool):
    name = "custom_tool"
    description = "A custom LangChain tool integrated with Jarvis"
    
    def _run(self, query: str) -> str:
        # Your tool logic here
        return f"Processed: {query}"
    
    async def _arun(self, query: str) -> str:
        # Async version if needed
        return self._run(query)
```

## LangGraph Workflows

### Creating Plugin Workflows

```python
from typing import TypedDict, List
from langgraph.graph import StateGraph

class PluginWorkflowState(TypedDict):
    command: str
    context: dict
    results: List[dict]
    current_plugin: str

def create_plugin_workflow():
    """Create a LangGraph workflow for plugin execution."""
    
    def parse_command_node(state: PluginWorkflowState) -> PluginWorkflowState:
        """Parse the command and identify applicable plugins."""
        command = state["command"]
        # Find plugins that can handle this command
        from agent.adapters.plugin_registry import plugin_manager
        plugins = plugin_manager.registry.find_plugins_for_command(command, state["context"])
        
        state["results"] = [{"plugin": p.metadata.name, "can_handle": True} for p in plugins]
        return state
    
    def execute_plugin_node(state: PluginWorkflowState) -> PluginWorkflowState:
        """Execute the selected plugin."""
        if state["results"]:
            plugin_name = state["results"][0]["plugin"]
            # Execute plugin logic
            state["current_plugin"] = plugin_name
        return state
    
    # Create the workflow graph
    workflow = StateGraph(PluginWorkflowState)
    workflow.add_node("parse_command", parse_command_node)
    workflow.add_node("execute_plugin", execute_plugin_node)
    
    workflow.add_edge("parse_command", "execute_plugin")
    workflow.set_entry_point("parse_command")
    
    return workflow.compile()

# Usage
workflow = create_plugin_workflow()
result = workflow.invoke({
    "command": "git status",
    "context": {"repository_path": "/path/to/repo"},
    "results": [],
    "current_plugin": ""
})
```

### Plugin Workflow Nodes

```python
from langgraph.graph import StateGraph, add_messages

class PluginNode:
    """A LangGraph node that wraps a Jarvis plugin."""
    
    def __init__(self, plugin_name: str):
        self.plugin_name = plugin_name
    
    def __call__(self, state: dict) -> dict:
        """Execute the plugin as a graph node."""
        from agent.adapters.plugin_registry import plugin_manager
        
        plugin = plugin_manager.registry.get_plugin(self.plugin_name)
        if not plugin:
            return {"error": f"Plugin {self.plugin_name} not found"}
        
        action = plugin.parse_command(state.get("command", ""), state.get("context", {}))
        if action:
            result = plugin.execute_action(action, state.get("context", {}))
            return {
                "plugin_result": {
                    "success": result.success,
                    "output": result.output,
                    "error": result.error
                }
            }
        
        return {"error": "Could not parse command"}
```

## API Reference

### Plugin Base Classes

- **BasePlugin**: Abstract base class for all plugins
- **AutomationPlugin**: For automation tasks
- **IntegrationPlugin**: For external service integrations  
- **CommandPlugin**: For simple command-based plugins
- **WorkflowPlugin**: For complex workflow plugins

### SDK Classes

- **PluginSDK**: Main SDK for plugin development
- **KnowledgeSourcePlugin**: Base for knowledge sources
- **LanguageEnhancerPlugin**: Base for language-specific enhancements
- **BuildSystemPlugin**: Base for build system integrations
- **TestingFrameworkPlugin**: Base for testing framework integrations

### Decorators

- **@jarvis_tool**: Enhanced tool decorator for Jarvis/LangChain integration
- **@knowledge_source**: For knowledge source methods
- **@language_enhancer**: For language enhancement methods
- **@build_system**: For build system detection methods
- **@testing_framework**: For testing framework detection methods

## Example Plugins

### Docker Integration Plugin

```python
class DockerPlugin(AutomationPlugin):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="DockerIntegration",
            description="Manage Docker containers and images",
            version="1.0.0",
            author="DevOps Team",
            plugin_type=PluginType.AUTOMATION,
            triggers=["docker", "container", "image", "dockerfile"],
            tags=["docker", "containers", "devops"]
        )
    
    def can_handle(self, command: str, context: dict = None) -> bool:
        docker_keywords = ["docker", "container", "image", "dockerfile"]
        return any(keyword in command.lower() for keyword in docker_keywords)
    
    def parse_command(self, command: str, context: dict = None) -> PluginAction:
        if "build" in command.lower():
            return PluginAction(
                name="docker_build",
                description="Build Docker image",
                args={"command": command, "context": context or {}},
                requires_approval=True
            )
        elif "run" in command.lower():
            return PluginAction(
                name="docker_run",
                description="Run Docker container",
                args={"command": command, "context": context or {}},
                requires_approval=True
            )
        else:
            return PluginAction(
                name="docker_info",
                description="Get Docker information",
                args={"command": command, "context": context or {}}
            )
    
    def execute_action(self, action: PluginAction, context: dict = None) -> PluginResult:
        try:
            if action.name == "docker_build":
                result = subprocess.run(["docker", "build", "."], capture_output=True, text=True)
                return PluginResult(
                    success=result.returncode == 0,
                    output=result.stdout,
                    error=result.stderr if result.returncode != 0 else None
                )
            elif action.name == "docker_run":
                # Parse image name from command
                image_name = "myapp:latest"  # Extract from command
                result = subprocess.run(["docker", "run", image_name], capture_output=True, text=True)
                return PluginResult(
                    success=result.returncode == 0,
                    output=result.stdout,
                    error=result.stderr if result.returncode != 0 else None
                )
            elif action.name == "docker_info":
                result = subprocess.run(["docker", "info"], capture_output=True, text=True)
                return PluginResult(
                    success=result.returncode == 0,
                    output=result.stdout,
                    error=result.stderr if result.returncode != 0 else None
                )
        except Exception as e:
            return PluginResult(success=False, error=str(e))
```

### Database Query Plugin

```python
class DatabaseQueryPlugin(IntegrationPlugin):
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
    
    def check_authentication(self) -> bool:
        try:
            # Test database connection
            import sqlite3
            conn = sqlite3.connect(self.connection_string)
            conn.close()
            return True
        except:
            return False
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="DatabaseQuery",
            description="Execute database queries and analyze results",
            version="1.0.0",
            author="Data Team",
            plugin_type=PluginType.INTEGRATION,
            triggers=["query", "database", "sql", "select", "count", "analyze data"],
            tags=["database", "sql", "data", "analytics"]
        )
    
    def can_handle(self, command: str, context: dict = None) -> bool:
        sql_keywords = ["select", "count", "query", "database", "table", "sql"]
        return any(keyword in command.lower() for keyword in sql_keywords)
    
    def parse_command(self, command: str, context: dict = None) -> PluginAction:
        return PluginAction(
            name="execute_query",
            description="Execute database query",
            args={"command": command, "context": context or {}},
            requires_approval=True  # SQL queries should be approved
        )
    
    def execute_action(self, action: PluginAction, context: dict = None) -> PluginResult:
        try:
            import sqlite3
            conn = sqlite3.connect(self.connection_string)
            cursor = conn.cursor()
            
            # Extract SQL from command (simplified)
            sql_query = action.args.get("command", "")
            if "select" in sql_query.lower():
                cursor.execute(sql_query)
                results = cursor.fetchall()
                conn.close()
                
                return PluginResult(
                    success=True,
                    output=f"Query executed successfully. Returned {len(results)} rows."
                )
            else:
                conn.close()
                return PluginResult(
                    success=False,
                    error="Only SELECT queries are supported"
                )
                
        except Exception as e:
            return PluginResult(success=False, error=str(e))
```

## Testing Plugins

### Unit Testing

```python
import unittest
from agent.adapters.plugin_base import PluginAction

class TestMyPlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = MyFirstPlugin()
    
    def test_can_handle(self):
        self.assertTrue(self.plugin.can_handle("hello world"))
        self.assertFalse(self.plugin.can_handle("goodbye"))
    
    def test_parse_command(self):
        action = self.plugin.parse_command("hello there")
        self.assertIsInstance(action, PluginAction)
        self.assertEqual(action.name, "greet_user")
    
    def test_execute_action(self):
        action = PluginAction(
            name="greet_user",
            description="Test greeting",
            args={"message": "hello"}
        )
        result = self.plugin.execute_action(action, {"user": "John"})
        self.assertTrue(result.success)
        self.assertIn("Hello John", result.output)

if __name__ == "__main__":
    unittest.main()
```

### Integration Testing

```python
def test_plugin_integration():
    """Test plugin integration with the plugin manager."""
    from agent.adapters.plugin_registry import plugin_manager
    from agent.adapters.extensibility_sdk import PluginSDK
    
    # Register plugin
    plugin = MyFirstPlugin()
    success = PluginSDK.register_plugin(plugin)
    assert success, "Plugin registration failed"
    
    # Test command parsing
    action = plugin_manager.parse_command("hello world")
    assert action is not None, "Command parsing failed"
    
    # Test command execution
    result = plugin_manager.execute_action(action)
    assert result.success, f"Command execution failed: {result.error}"
```

## Deployment

### Plugin Packaging

Create a `plugin_manifest.json`:

```json
{
  "name": "MyAwesomePlugin",
  "description": "An awesome plugin for Jarvis AI",
  "version": "1.0.0",
  "author": "Your Name",
  "license": "MIT",
  "homepage": "https://github.com/you/my-awesome-plugin",
  "repository": "https://github.com/you/my-awesome-plugin.git",
  "keywords": ["jarvis", "plugin", "automation"],
  "dependencies": {
    "requests": ">=2.25.0"
  },
  "plugin_entry_point": "main",
  "supported_platforms": ["all"],
  "min_jarvis_version": "1.0.0"
}
```

### Installation Script

```python
#!/usr/bin/env python3
"""Plugin installation script."""

import json
import sys
from pathlib import Path
from agent.adapters.extensibility_sdk import PluginSDK, validate_plugin_manifest, PluginManifest

def install_plugin(plugin_path: str):
    """Install a plugin from a directory."""
    plugin_dir = Path(plugin_path)
    manifest_path = plugin_dir / "plugin_manifest.json"
    
    if not manifest_path.exists():
        print(f"Error: No plugin_manifest.json found in {plugin_path}")
        return False
    
    with open(manifest_path, 'r') as f:
        manifest_data = json.load(f)
    
    manifest = PluginManifest(**manifest_data)
    errors = validate_plugin_manifest(manifest)
    
    if errors:
        print("Plugin manifest validation errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    # Import and register the plugin
    try:
        sys.path.insert(0, str(plugin_dir))
        main_module = __import__(manifest.plugin_entry_point)
        
        if hasattr(main_module, 'register_plugin'):
            main_module.register_plugin()
            print(f"Plugin {manifest.name} installed successfully!")
            return True
        else:
            print(f"Error: Plugin entry point {manifest.plugin_entry_point} must have a register_plugin() function")
            return False
            
    except Exception as e:
        print(f"Error installing plugin: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python install_plugin.py <plugin_directory>")
        sys.exit(1)
    
    success = install_plugin(sys.argv[1])
    sys.exit(0 if success else 1)
```

## Best Practices

### 1. Plugin Design

- **Single Responsibility**: Each plugin should have a clear, single purpose
- **Descriptive Names**: Use clear, descriptive names for plugins and actions
- **Comprehensive Triggers**: Provide multiple natural language triggers
- **Error Handling**: Always handle errors gracefully and provide useful error messages

### 2. Performance

- **Lazy Loading**: Only load heavy dependencies when needed
- **Caching**: Cache results when appropriate
- **Timeouts**: Use timeouts for external API calls
- **Resource Cleanup**: Always clean up resources (files, connections, etc.)

### 3. Security

- **Input Validation**: Always validate user inputs
- **Approval for Destructive Actions**: Require approval for actions that modify system state
- **Credential Management**: Use secure credential storage
- **Sandboxing**: Consider sandboxing for untrusted code execution

### 4. Documentation

- **Clear Docstrings**: Provide comprehensive docstrings for all methods
- **Usage Examples**: Include usage examples in your documentation
- **API Documentation**: Document your plugin's API if it exposes one
- **Change Log**: Maintain a change log for your plugin versions

### 5. Testing

- **Unit Tests**: Write unit tests for all plugin functionality
- **Integration Tests**: Test integration with the Jarvis AI system
- **Mock External Dependencies**: Use mocks for external API calls in tests
- **Edge Cases**: Test edge cases and error conditions

### 6. LangChain/LangGraph Integration

- **Stateless Tools**: Keep LangChain tools stateless when possible
- **Async Support**: Implement async versions of long-running operations
- **Workflow Composition**: Design plugins to work well in LangGraph workflows
- **Monitoring**: Use LangSmith for monitoring plugin performance

## Troubleshooting

### Common Issues

1. **Plugin Not Found**: Ensure your plugin is properly registered with `PluginSDK.register_plugin()`
2. **Import Errors**: Check that all dependencies are installed and paths are correct
3. **Command Not Recognized**: Verify your trigger phrases and `can_handle()` method
4. **Execution Failures**: Check your `execute_action()` method for proper error handling

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
```

### Plugin Validation

```python
from agent.adapters.extensibility_sdk import validate_plugin_manifest

# Validate your plugin manifest
errors = validate_plugin_manifest(your_manifest)
if errors:
    print("Validation errors:", errors)
```

## Community and Support

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Contribute to documentation improvements
- **Plugin Repository**: Share your plugins with the community
- **Discord/Slack**: Join the community discussions

---

This guide provides a comprehensive foundation for developing plugins for the Jarvis AI extensibility framework. For more advanced topics and specific use cases, refer to the API documentation and example plugins in the repository.