#!/usr/bin/env python3
"""
Comprehensive demo of the Jarvis AI plugin architecture.

This script demonstrates:
1. Plugin registration and discovery
2. Workflow chaining
3. Approval previews  
4. Natural language triggers
5. Backward compatibility
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo_plugin_system():
    """Demonstrate the plugin system."""
    print("🚀 Jarvis AI Plugin Architecture Demo")
    print("=" * 50)
    
    # Initialize the plugin system
    print("\n1. 🔧 Initializing Plugin System...")
    try:
        from agent.tools import initialize_plugin_system
        success = initialize_plugin_system()
        print(f"   Plugin system initialized: {'✅ Success' if success else '❌ Failed'}")
    except Exception as e:
        print(f"   ❌ Initialization failed: {e}")
        return
    
    # Show registered plugins
    print("\n2. 📋 Registered Plugins:")
    try:
        from agent.plugin_registry import plugin_manager
        plugins = plugin_manager.registry.list_plugins()
        for plugin in plugins:
            print(f"   - {plugin.metadata.name}: {plugin.metadata.description}")
            print(f"     Triggers: {', '.join(plugin.metadata.triggers[:3])}...")
    except Exception as e:
        print(f"   ❌ Error listing plugins: {e}")
        return
    
    # Demonstrate workflow parsing
    print("\n3. 🔄 Workflow Parsing Demo:")
    workflow_commands = [
        "git status then git diff",
        "review code then search for bugs", 
        "git commit 'fix issue' then git push",
        "open in pycharm main.py"
    ]
    
    try:
        from agent.workflow_system import workflow_parser, workflow_executor
        
        for command in workflow_commands:
            print(f"\n   Command: '{command}'")
            workflow = workflow_parser.parse_workflow(command)
            
            if workflow:
                print(f"   ✅ Parsed into workflow with {len(workflow.steps)} steps:")
                for i, step in enumerate(workflow.steps, 1):
                    print(f"      {i}. {step.action.name}: {step.action.description}")
                
                # Show preview
                print(f"   📋 Preview:")
                preview = workflow_executor.preview_workflow(workflow)
                for line in preview.split('\n'):
                    print(f"      {line}")
            else:
                print(f"   ⚠️  Not parsed as workflow, trying individual command...")
                # Try as individual command
                action = plugin_manager.parse_command(command)
                if action:
                    print(f"   ✅ Parsed as single action: {action.name}")
                else:
                    print(f"   ❌ Could not parse command")
    except Exception as e:
        print(f"   ❌ Workflow demo error: {e}")
    
    # Demonstrate natural language triggers
    print("\n4. 🗣️ Natural Language Trigger Demo:")
    test_commands = [
        "git status",
        "git commit 'test message'",
        "open in pycharm src/main.py:42",
        "review code quality in app.py",
        "search for authentication function",
        "go to google.com and search for python"
    ]
    
    try:
        for command in test_commands:
            plugins = plugin_manager.registry.find_plugins_for_command(command)
            print(f"   '{command}'")
            print(f"      → {len(plugins)} matching plugin{'s' if len(plugins) != 1 else ''}")
            for plugin in plugins:
                action = plugin.parse_command(command)
                if action:
                    requires_approval = " [NEEDS APPROVAL]" if action.requires_approval else ""
                    print(f"         • {plugin.metadata.name}: {action.description}{requires_approval}")
    except Exception as e:
        print(f"   ❌ Natural language demo error: {e}")
    
    # Demonstrate backward compatibility
    print("\n5. ⬅️ Backward Compatibility Demo:")
    try:
        from agent.core import JarvisAgent
        
        agent = JarvisAgent(
            persona_prompt="Demo agent",
            tool_registry={},
            approval_callback=None
        )
        
        legacy_commands = ["git status", "open in pycharm main.py"]
        
        for command in legacy_commands:
            print(f"   Testing legacy parsing: '{command}'")
            plan = agent.parse_natural_language(command, [])
            if plan:
                print(f"      ✅ Parsed into {len(plan)} step{'s' if len(plan) != 1 else ''}")
                for step in plan:
                    print(f"         - {step['tool']}: {step.get('description', 'No description')}")
            else:
                print(f"      ❌ No plan generated")
    except Exception as e:
        print(f"   ❌ Backward compatibility demo error: {e}")
    
    # Summary
    print("\n6. 📊 Plugin Architecture Features:")
    print("   ✅ Plugin Discovery and Registration")
    print("   ✅ Natural Language Command Parsing")
    print("   ✅ Workflow Chaining Support")
    print("   ✅ Approval Preview System")
    print("   ✅ Backward Compatibility") 
    print("   ✅ Extensible Plugin Framework")
    
    print("\n🎉 Plugin Architecture Demo Complete!")
    print("\nTo add new plugins:")
    print("1. Inherit from BasePlugin, AutomationPlugin, or IntegrationPlugin")
    print("2. Implement required methods (can_handle, parse_command, execute_action)")
    print("3. Register with plugin_manager.registry.register_plugin()")
    print("4. Or place in agent/ or plugins/ directory for auto-discovery")

if __name__ == "__main__":
    demo_plugin_system()