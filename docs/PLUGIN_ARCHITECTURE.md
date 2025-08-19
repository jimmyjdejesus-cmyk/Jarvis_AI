# Jarvis AI Plugin Architecture

The Jarvis AI plugin architecture provides an extensible framework for adding automation tools, commands, and integrations. It supports workflow chaining, approval previews, and natural language triggers.

## 🏗️ Architecture Overview

The plugin system consists of several key components:

1. **Plugin Base Classes** - Abstract interfaces for different types of plugins
2. **Plugin Registry** - Discovery and management of registered plugins
3. **Workflow System** - Chaining multiple plugin actions together
4. **Natural Language Parser** - Converting commands into plugin actions

## 🔧 Creating Plugins

### Base Plugin Interface

All plugins inherit from `BasePlugin` and must implement these methods:

```python
from agent.plugin_base import BasePlugin, PluginMetadata, PluginAction, PluginResult

class MyPlugin(BasePlugin):
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        return PluginMetadata(
            name="MyPlugin",
            description="Description of what this plugin does",
            version="1.0.0",
            author="Your Name",
            plugin_type=PluginType.AUTOMATION,
            triggers=["keyword1", "keyword2"],  # Natural language triggers
            tags=["automation", "example"]
        )
    
    def can_handle(self, command: str, context: dict = None) -> bool:
        """Check if this plugin can handle the command"""
        return "keyword" in command.lower()
    
    def parse_command(self, command: str, context: dict = None) -> PluginAction:
        """Parse command into an action"""
        return PluginAction(
            name="my_action",
            description=f"Execute: {command}",
            args={"command": command},
            requires_approval=False
        )
    
    def preview_action(self, action: PluginAction) -> str:
        """Generate preview text"""
        return f"Will execute: {action.args['command']}"
    
    def execute_action(self, action: PluginAction, context: dict = None) -> PluginResult:
        """Execute the action"""
        try:
            # Your plugin logic here
            result = do_something(action.args["command"])
            return PluginResult(success=True, output=result)
        except Exception as e:
            return PluginResult(success=False, output=None, error=str(e))
```

### Plugin Types

Choose the appropriate base class for your plugin:

- **`AutomationPlugin`** - For automation tools (git, browser, file operations)
- **`IntegrationPlugin`** - For external services (GitHub, Notion, APIs)
- **`CommandPlugin`** - For simple command-line style tools
- **`WorkflowPlugin`** - For plugins that support workflow chaining

### Example: File Operations Plugin

```python
from agent.plugin_base import AutomationPlugin, PluginMetadata, PluginType
import os

class FileOperationsPlugin(AutomationPlugin):
    def get_metadata(self):
        return PluginMetadata(
            name="FileOperationsPlugin",
            description="File and directory operations",
            version="1.0.0",
            author="Jarvis AI",
            plugin_type=PluginType.AUTOMATION,
            triggers=["create file", "delete file", "list files", "copy file"],
            tags=["files", "filesystem"]
        )
    
    def can_handle(self, command, context=None):
        file_ops = ["create", "delete", "list", "copy", "move", "file", "directory"]
        return any(op in command.lower() for op in file_ops)
    
    def parse_command(self, command, context=None):
        if "create file" in command.lower():
            # Extract filename from command
            parts = command.split("create file")
            filename = parts[1].strip() if len(parts) > 1 else "newfile.txt"
            
            return PluginAction(
                name="create_file",
                description=f"Create file: {filename}",
                args={"operation": "create", "filename": filename},
                requires_approval=False
            )
        # Add more parsing logic for other operations...
    
    def execute_action(self, action, context=None):
        operation = action.args.get("operation")
        filename = action.args.get("filename")
        
        try:
            if operation == "create":
                with open(filename, 'w') as f:
                    f.write("# Created by Jarvis AI\n")
                return PluginResult(success=True, output=f"Created file: {filename}")
            # Add more operations...
        except Exception as e:
            return PluginResult(success=False, error=str(e))
```

## 🔄 Workflow System

### Creating Workflows

Workflows chain multiple plugin actions together:

```python
from agent.workflow_system import workflow_parser

# Parse natural language into workflow
workflow = workflow_parser.parse_workflow("git status then git diff then git commit 'update'")

if workflow:
    print(f"Created workflow with {len(workflow.steps)} steps")
    for i, step in enumerate(workflow.steps, 1):
        print(f"  {i}. {step.action.description}")
```

### Workflow Patterns

The system recognizes several workflow patterns:

1. **Sequential**: `"do X then Y then Z"`
2. **Chain**: `"X, Y, Z"` (comma-separated)  
3. **Parallel**: `"do X and Y"`
4. **Conditional**: `"if X then Y"`

### Example Workflows

```python
# Sequential git workflow
"git status then git add . then git commit 'fix bug' then git push"

# Development workflow  
"pull repo, run tests, open results in pycharm"

# Code quality workflow
"review code quality and search for security issues"

# File processing workflow
"create backup file, process data, generate report"
```

### Approval System

Workflows can require approval for sensitive operations:

```python
from agent.workflow_system import workflow_executor

def approval_callback(workflow):
    """Custom approval function"""
    print(f"Workflow: {workflow.name}")
    preview = workflow_executor.preview_workflow(workflow)
    print(preview)
    
    response = input("Approve this workflow? (y/n): ")
    return response.lower() == 'y'

# Set approval callback
workflow_executor.approval_callback = approval_callback

# Execute workflow (will prompt for approval if needed)
result = workflow_executor.execute_workflow(workflow)
```

## 📋 Registration and Discovery

### Manual Registration

```python
from agent.plugin_registry import plugin_manager

# Create and register plugin
my_plugin = MyPlugin()
plugin_manager.registry.register_plugin(my_plugin)
```

### Auto-Discovery

Place plugin files in these directories for automatic discovery:
- `agent/` - Built-in plugins
- `plugins/` - Custom plugins (create this directory)

### Plugin Discovery

```python
# Find plugins that can handle a command
plugins = plugin_manager.registry.find_plugins_for_command("git status")

# List all registered plugins
all_plugins = plugin_manager.registry.list_plugins()

# Get plugin info
info = plugin_manager.registry.get_plugin_info()
```

## 🗣️ Natural Language Integration

### Trigger Phrases

Register trigger phrases in your plugin metadata:

```python
def get_metadata(self):
    return PluginMetadata(
        # ...
        triggers=[
            "git status", "git commit", "git push",
            "repository status", "commit changes"
        ]
    )
```

### Command Parsing

The system tries multiple approaches to parse commands:

1. **Trigger matching** - Check registered trigger phrases
2. **Plugin can_handle()** - Call each plugin's can_handle method
3. **Workflow patterns** - Look for workflow keywords (then, and, etc.)
4. **Legacy fallback** - Use existing command parsing

### Context

Commands can include context information:

```python
context = {
    "files": ["app.py", "test.py"],
    "repository_path": "/path/to/repo",
    "user": "developer",
    "chat_history": [...]
}

action = plugin.parse_command("review these files", context)
```

## 🔌 Integration Examples

### Integrating with Existing Jarvis AI

The plugin system integrates seamlessly with the existing codebase:

```python
from agent.core import JarvisAgent

# Create agent with plugin support
agent = JarvisAgent(
    persona_prompt="AI Assistant", 
    tool_registry={},
    approval_callback=my_approval_function
)

# Parse commands (now supports workflows)
plan = agent.parse_natural_language("git status then review code", files=[])

# Execute plan
for step in plan:
    result = run_tool(step)
    print(result)
```

### Streamlit UI Integration

```python
import streamlit as st
from agent.workflow_system import workflow_parser, workflow_executor

# In your Streamlit app
user_command = st.text_input("Enter command or workflow:")

if user_command:
    # Try parsing as workflow
    workflow = workflow_parser.parse_workflow(user_command)
    
    if workflow:
        # Show preview
        preview = workflow_executor.preview_workflow(workflow)
        st.text_area("Workflow Preview:", value=preview, height=200)
        
        if st.button("Execute Workflow"):
            result = workflow_executor.execute_workflow(workflow)
            if result.success:
                st.success("Workflow completed successfully!")
                for i, step_result in enumerate(result.step_results, 1):
                    st.write(f"Step {i}: {step_result.output}")
            else:
                st.error(f"Workflow failed: {result.error}")
```

## 📚 Advanced Features

### Workflow Dependencies

Steps can depend on outputs from previous steps:

```python
from agent.workflow_system import WorkflowStep

step2 = WorkflowStep(
    action=my_action,
    plugin_name="MyPlugin",
    depends_on=[0],  # Depends on step 1
    output_mapping={"file_path": "input_file"}  # Map outputs to inputs
)
```

### Custom Workflow Patterns

Extend the workflow parser with custom patterns:

```python
from agent.workflow_system import WorkflowParser

class CustomWorkflowParser(WorkflowParser):
    def __init__(self):
        super().__init__()
        # Add custom patterns
        self.workflow_patterns.append({
            'pattern': r'repeat (.+?) (\d+) times',
            'type': 'repeat'
        })
    
    def _parse_repeat_workflow(self, command, context=None):
        # Custom parsing logic
        pass
```

### Plugin Validation

Add validation to your plugins:

```python
def validate_action(self, action):
    """Validate action before execution"""
    if action.name == "delete_file":
        filename = action.args.get("filename")
        if not filename or filename in ["/", "system32"]:
            return False
    return True
```

## 🧪 Testing Plugins

### Unit Testing

```python
import unittest
from agent.plugin_base import PluginAction

class TestMyPlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = MyPlugin()
    
    def test_can_handle(self):
        self.assertTrue(self.plugin.can_handle("my command"))
        self.assertFalse(self.plugin.can_handle("other command"))
    
    def test_parse_command(self):
        action = self.plugin.parse_command("my command")
        self.assertIsNotNone(action)
        self.assertEqual(action.name, "my_action")
    
    def test_execute_action(self):
        action = PluginAction(name="my_action", args={"test": True})
        result = self.plugin.execute_action(action)
        self.assertTrue(result.success)
```

### Integration Testing

```python
from agent.plugin_registry import PluginRegistry

def test_plugin_integration():
    registry = PluginRegistry()
    plugin = MyPlugin()
    
    # Test registration
    assert registry.register_plugin(plugin)
    
    # Test discovery
    plugins = registry.find_plugins_for_command("my command")
    assert len(plugins) == 1
    assert plugins[0] == plugin
```

## 📖 Examples

See the included example files:
- `demo_core_features.py` - Core plugin system demonstration
- `demo_plugin_architecture.py` - Complete workflow examples
- `test_plugin_system.py` - Comprehensive test suite

## 🚀 Getting Started

1. **Create your plugin** by inheriting from an appropriate base class
2. **Implement required methods** (can_handle, parse_command, execute_action)
3. **Register your plugin** with the plugin manager
4. **Test with natural language commands**
5. **Create workflows** by chaining multiple actions

The plugin architecture is designed to be simple to use while providing powerful extensibility for complex automation workflows.