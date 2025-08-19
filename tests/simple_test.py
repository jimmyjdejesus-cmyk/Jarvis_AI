#!/usr/bin/env python3
"""
Simple test to debug plugin system issues.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def simple_test():
    """Simple plugin system test."""
    print("🔧 Simple Plugin Test...")
    
    try:
        # Test imports
        print("Testing imports...")
        from agent.plugin_base import BasePlugin, PluginMetadata, PluginType
        print("   ✅ plugin_base imported")
        
        from agent.plugin_registry import PluginRegistry, plugin_manager
        print("   ✅ plugin_registry imported")
        
        from agent.workflow_system import workflow_parser
        print("   ✅ workflow_system imported")
        
        from agent.plugin_adapters import GitPlugin
        print("   ✅ plugin_adapters imported")
        
        # Test plugin creation
        print("\nTesting plugin creation...")
        git_plugin = GitPlugin()
        print(f"   ✅ GitPlugin created: {git_plugin.metadata.name}")
        
        # Test plugin registration
        print("\nTesting plugin registration...")
        registry = PluginRegistry()
        success = registry.register_plugin(git_plugin)
        print(f"   ✅ Plugin registration: {success}")
        
        # Test command handling
        print("\nTesting command handling...")
        can_handle = git_plugin.can_handle("git status")
        print(f"   ✅ Can handle 'git status': {can_handle}")
        
        if can_handle:
            action = git_plugin.parse_command("git status")
            print(f"   ✅ Parsed action: {action.name if action else 'None'}")
            
            if action:
                preview = git_plugin.preview_action(action)
                print(f"   ✅ Preview: {preview}")
        
        # Test find plugins
        print("\nTesting plugin finding...")
        plugins = registry.find_plugins_for_command("git status")
        print(f"   ✅ Found {len(plugins)} plugins for 'git status'")
        
        return True
        
    except Exception as e:
        import traceback
        print(f"   ❌ Error: {e}")
        print(f"   Stack trace: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    simple_test()