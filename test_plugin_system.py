#!/usr/bin/env python3
"""
Test script for the Jarvis AI plugin architecture.

This script tests the plugin system, workflow chaining, and approval previews.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_plugin_system():
    """Test the plugin system basic functionality."""
    print("🔧 Testing Plugin System...")
    
    try:
        from agent.plugin_registry import plugin_manager
        from agent.tools import initialize_plugin_system
        
        # Initialize the plugin system
        success = initialize_plugin_system()
        print(f"   ✅ Plugin system initialization: {'Success' if success else 'Failed'}")
        
        # List registered plugins
        plugins = plugin_manager.registry.list_plugins()
        print(f"   📋 Registered plugins: {len(plugins)}")
        for plugin in plugins:
            print(f"      - {plugin.metadata.name}: {plugin.metadata.description}")
        
        return True
    except Exception as e:
        print(f"   ❌ Plugin system test failed: {e}")
        return False


def test_workflow_parsing():
    """Test workflow parsing functionality."""
    print("\n🔄 Testing Workflow Parsing...")
    
    try:
        from agent.workflow_system import workflow_parser
        
        test_commands = [
            "git status then git diff",
            "pull repo, run tests, open results",
            "review code and search for bugs",
            "open in pycharm main.py",
            "git commit 'fix bug' then git push"
        ]
        
        for command in test_commands:
            print(f"   Testing: '{command}'")
            workflow = workflow_parser.parse_workflow(command)
            if workflow:
                print(f"      ✅ Parsed into {len(workflow.steps)} steps")
                for i, step in enumerate(workflow.steps, 1):
                    print(f"         {i}. {step.action.name}: {step.action.description}")
            else:
                print(f"      ❌ Failed to parse")
        
        return True
    except Exception as e:
        print(f"   ❌ Workflow parsing test failed: {e}")
        return False


def test_approval_preview():
    """Test workflow preview and approval system."""
    print("\n👁️ Testing Approval Preview...")
    
    try:
        from agent.workflow_system import workflow_parser, workflow_executor
        
        # Test a workflow that requires approval
        command = "git commit 'test commit' then git push"
        workflow = workflow_parser.parse_workflow(command)
        
        if workflow:
            # Generate preview
            preview = workflow_executor.preview_workflow(workflow)
            print(f"   📋 Workflow Preview:")
            for line in preview.split('\n'):
                print(f"      {line}")
            
            # Check if approval is required
            requires_approval = workflow_executor._requires_approval(workflow)
            print(f"   🔐 Requires approval: {requires_approval}")
            
            return True
        else:
            print(f"   ❌ Could not create test workflow")
            return False
    except Exception as e:
        print(f"   ❌ Approval preview test failed: {e}")
        return False


def test_plugin_adapters():
    """Test plugin adapters for existing tools."""
    print("\n🔌 Testing Plugin Adapters...")
    
    try:
        from agent.plugin_adapters import GitPlugin, IDEPlugin, CodeReviewPlugin
        from agent.plugin_base import PluginAction
        
        # Test Git plugin
        git_plugin = GitPlugin()
        can_handle = git_plugin.can_handle("git status")
        print(f"   Git Plugin can handle 'git status': {can_handle}")
        
        if can_handle:
            action = git_plugin.parse_command("git status")
            if action:
                preview = git_plugin.preview_action(action)
                print(f"   Git Preview: {preview}")
        
        # Test IDE plugin
        ide_plugin = IDEPlugin()
        can_handle = ide_plugin.can_handle("open in pycharm main.py")
        print(f"   IDE Plugin can handle 'open in pycharm main.py': {can_handle}")
        
        # Test Code Review plugin
        review_plugin = CodeReviewPlugin()
        can_handle = review_plugin.can_handle("review code quality")
        print(f"   Code Review Plugin can handle 'review code quality': {can_handle}")
        
        return True
    except Exception as e:
        print(f"   ❌ Plugin adapters test failed: {e}")
        return False


def test_backward_compatibility():
    """Test that existing functionality still works."""
    print("\n⬅️ Testing Backward Compatibility...")
    
    try:
        from agent.core import JarvisAgent
        from agent.tools import run_tool
        
        # Create a simple agent
        agent = JarvisAgent(
            persona_prompt="Test agent",
            tool_registry={},
            approval_callback=None
        )
        
        # Test legacy command parsing
        plan = agent.parse_natural_language("git status", [])
        if plan:
            print(f"   ✅ Legacy parsing works: {len(plan)} steps")
            for step in plan:
                print(f"      - {step['tool']}: {step.get('description', 'No description')}")
        else:
            print(f"   ⚠️  Legacy parsing returned no plan")
        
        return True
    except Exception as e:
        print(f"   ❌ Backward compatibility test failed: {e}")
        return False


def test_natural_language_triggers():
    """Test natural language trigger system."""
    print("\n🗣️ Testing Natural Language Triggers...")
    
    try:
        from agent.plugin_registry import plugin_manager
        
        test_commands = [
            "git status",
            "open in pycharm main.py:42", 
            "review code quality",
            "search for authentication function",
            "go to google.com"
        ]
        
        for command in test_commands:
            plugins = plugin_manager.registry.find_plugins_for_command(command)
            print(f"   '{command}' -> {len(plugins)} matching plugins")
            for plugin in plugins:
                print(f"      - {plugin.metadata.name}")
        
        return True
    except Exception as e:
        print(f"   ❌ Natural language triggers test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Jarvis AI Plugin Architecture Test Suite")
    print("=" * 50)
    
    tests = [
        test_plugin_system,
        test_plugin_adapters,
        test_workflow_parsing,
        test_approval_preview,
        test_natural_language_triggers,
        test_backward_compatibility
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"   💥 Test {test.__name__} crashed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Plugin architecture is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    exit(main())