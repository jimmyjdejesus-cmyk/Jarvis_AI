#!/usr/bin/env python3
"""
Focused demo of the core plugin architecture features.

This demo shows the plugin system without external dependencies.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_sample_plugin():
    """Create a sample plugin for demo purposes."""
    from agent.plugin_base import AutomationPlugin, PluginMetadata, PluginAction, PluginResult, PluginType
    
    class SamplePlugin(AutomationPlugin):
        def get_metadata(self):
            return PluginMetadata(
                name="SamplePlugin",
                description="A sample plugin for demo purposes",
                version="1.0.0",
                author="Jarvis AI",
                plugin_type=PluginType.AUTOMATION,
                triggers=["sample", "test", "demo"],
                tags=["demo", "example"]
            )
        
        def can_handle(self, command, context=None):
            return any(trigger in command.lower() for trigger in ["sample", "test", "demo"])
        
        def parse_command(self, command, context=None):
            if not self.can_handle(command, context):
                return None
            
            return PluginAction(
                name="sample_action",
                description=f"Sample action for: {command}",
                args={"command": command},
                preview=f"Will execute sample action: {command}",
                requires_approval=False
            )
        
        def preview_action(self, action):
            command = action.args.get("command", "unknown")
            return f"Sample plugin will process: {command}"
        
        def execute_action(self, action, context=None):
            command = action.args.get("command", "")
            return PluginResult(
                success=True,
                output=f"Sample plugin executed: {command}",
                metadata={"action": "sample", "input": command}
            )
        
        def get_output_schema(self):
            return {"output": str, "success": bool}
        
        def get_input_schema(self):
            return {"command": str}
    
    return SamplePlugin()

def demo_core_features():
    """Demo the core plugin architecture features."""
    print("🚀 Jarvis AI Plugin Architecture - Core Features Demo")
    print("=" * 60)
    
    try:
        # Import core components
        from agent.plugin_base import BasePlugin, PluginMetadata, PluginType
        from agent.plugin_registry import PluginRegistry, plugin_manager
        from agent.workflow_system import workflow_parser, workflow_executor
        
        print("✅ Core imports successful")
        
        # 1. Plugin Registration Demo
        print("\n1. 🔧 Plugin Registration Demo:")
        
        # Create and register sample plugin
        sample_plugin = create_sample_plugin()
        registry = PluginRegistry()
        success = registry.register_plugin(sample_plugin)
        
        print(f"   Sample plugin registered: {'✅ Success' if success else '❌ Failed'}")
        print(f"   Plugin name: {sample_plugin.metadata.name}")
        print(f"   Plugin triggers: {sample_plugin.metadata.triggers}")
        
        # 2. Command Parsing Demo
        print("\n2. 🗣️ Command Parsing Demo:")
        
        test_commands = [
            "run sample test",
            "execute demo command",
            "test the plugin system"
        ]
        
        for command in test_commands:
            print(f"\n   Command: '{command}'")
            
            # Test if plugin can handle
            can_handle = sample_plugin.can_handle(command)
            print(f"   Can handle: {can_handle}")
            
            if can_handle:
                # Parse command
                action = sample_plugin.parse_command(command)
                if action:
                    print(f"   Parsed action: {action.name}")
                    print(f"   Description: {action.description}")
                    
                    # Show preview
                    preview = sample_plugin.preview_action(action)
                    print(f"   Preview: {preview}")
                    
                    # Execute action
                    result = sample_plugin.execute_action(action)
                    print(f"   Execution: {'✅ Success' if result.success else '❌ Failed'}")
                    print(f"   Output: {result.output}")
        
        # 3. Plugin Discovery Demo
        print("\n3. 🔍 Plugin Discovery Demo:")
        
        # Register plugin with the main manager
        plugin_manager.registry.register_plugin(sample_plugin)
        
        plugins = plugin_manager.registry.find_plugins_for_command("run sample test")
        print(f"   Found {len(plugins)} plugins for 'run sample test'")
        
        for plugin in plugins:
            print(f"   - {plugin.metadata.name}: {plugin.metadata.description}")
        
        # 4. Workflow Creation Demo
        print("\n4. 🔄 Workflow Creation Demo:")
        
        # Create a simple workflow
        from agent.plugin_base import PluginAction
        from agent.workflow_system import WorkflowStep, Workflow, WorkflowStatus
        
        # Create workflow steps
        step1 = WorkflowStep(
            action=PluginAction(
                name="sample_action",
                description="First step",
                args={"command": "initialize demo"}
            ),
            plugin_name="SamplePlugin"
        )
        
        step2 = WorkflowStep(
            action=PluginAction(
                name="sample_action", 
                description="Second step",
                args={"command": "process data"}
            ),
            plugin_name="SamplePlugin",
            depends_on=[0]  # Depends on step 1
        )
        
        # Create workflow
        workflow = Workflow(
            name="Demo Workflow",
            description="A sample workflow for demonstration",
            steps=[step1, step2]
        )
        
        print(f"   Created workflow: {workflow.name}")
        print(f"   Steps: {len(workflow.steps)}")
        
        # Generate preview
        preview = workflow_executor.preview_workflow(workflow)
        print(f"   Preview:")
        for line in preview.split('\n'):
            print(f"      {line}")
        
        # 5. Extension Demo
        print("\n5. 🧩 Extension Demo:")
        
        class CustomPlugin(sample_plugin.__class__):
            def get_metadata(self):
                metadata = super().get_metadata()
                metadata.name = "CustomPlugin"
                metadata.description = "Extended plugin with custom behavior"
                metadata.triggers = ["custom", "extended"]
                return metadata
            
            def can_handle(self, command, context=None):
                return "custom" in command.lower() or super().can_handle(command, context)
        
        custom_plugin = CustomPlugin()
        registry.register_plugin(custom_plugin)
        
        print(f"   Created custom plugin: {custom_plugin.metadata.name}")
        print(f"   Custom triggers: {custom_plugin.metadata.triggers}")
        
        # 6. Architecture Summary
        print("\n6. 📊 Architecture Summary:")
        print("   ✅ Plugin Base Classes (BasePlugin, AutomationPlugin, etc.)")
        print("   ✅ Plugin Registry (discovery, registration, lookup)")
        print("   ✅ Workflow System (chaining, dependencies, previews)")
        print("   ✅ Natural Language Parsing")
        print("   ✅ Action Preview and Approval")
        print("   ✅ Extensible Plugin Framework")
        
        print("\n🎉 Core Features Demo Complete!")
        
        print("\n📖 Usage Guide:")
        print("   1. Create plugin by inheriting from BasePlugin")
        print("   2. Implement required methods: can_handle, parse_command, execute_action")
        print("   3. Register with plugin_manager.registry.register_plugin()")
        print("   4. Plugin automatically available for natural language commands")
        print("   5. Workflows can chain multiple plugin actions")
        print("   6. Approval system handles sensitive operations")
        
        return True
        
    except Exception as e:
        import traceback
        print(f"❌ Demo failed: {e}")
        print(f"Stack trace: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    demo_core_features()