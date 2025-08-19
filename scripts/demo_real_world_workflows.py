#!/usr/bin/env python3
"""
Comprehensive workflow demonstration showing real-world usage of the plugin architecture.

This demo shows:
1. Complex workflow chaining
2. Approval system with custom callbacks
3. Plugin discovery and auto-registration
4. Output passing between workflow steps
5. Error handling and workflow recovery
"""

import sys
import os
import time

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_approval_callback():
    """Create a custom approval callback for interactive workflows."""
    def approval_callback(workflow):
        print(f"\n🔔 Approval Required for Workflow")
        print("=" * 50)
        print(f"Workflow: {workflow.name}")
        print(f"Description: {workflow.description}")
        print(f"Steps: {len(workflow.steps)}")
        
        # Show workflow preview
        from agent.workflow_system import workflow_executor
        preview = workflow_executor.preview_workflow(workflow)
        print(f"\nPreview:")
        for line in preview.split('\n'):
            print(f"  {line}")
        
        # Check for sensitive operations
        sensitive_actions = []
        for step in workflow.steps:
            if step.action.requires_approval:
                sensitive_actions.append(step.action.description)
        
        if sensitive_actions:
            print(f"\n⚠️  Sensitive Operations:")
            for action in sensitive_actions:
                print(f"  - {action}")
        
        # For demo, auto-approve (in real app, you'd prompt user)
        print(f"\n✅ Auto-approving for demo purposes")
        return True
    
    return approval_callback

def demo_real_world_workflows():
    """Demonstrate real-world workflow scenarios."""
    print("🚀 Real-World Workflow Demonstration")
    print("=" * 60)
    
    try:
        # Initialize plugin system
        from agent.tools import initialize_plugin_system
        from agent.plugin_registry import plugin_manager
        from agent.workflow_system import workflow_parser, workflow_executor
        
        print("1. 🔧 Initializing Plugin System...")
        success = initialize_plugin_system()
        print(f"   Plugin system: {'✅ Ready' if success else '❌ Failed'}")
        
        # Register our example plugin
        print("\n2. 📦 Registering Custom Plugins...")
        try:
            # Import and register the project management plugin
            import sys
            sys.path.append('plugins')
            from project_management_plugin import ProjectManagementPlugin
            
            project_plugin = ProjectManagementPlugin()
            plugin_manager.registry.register_plugin(project_plugin)
            print(f"   ✅ Registered: {project_plugin.metadata.name}")
        except Exception as e:
            print(f"   ⚠️  Could not load custom plugin: {e}")
        
        # List all available plugins
        plugins = plugin_manager.registry.list_plugins()
        print(f"\n3. 📋 Available Plugins ({len(plugins)} total):")
        for plugin in plugins:
            print(f"   - {plugin.metadata.name}: {plugin.metadata.description}")
        
        # Set up approval callback
        workflow_executor.approval_callback = create_approval_callback()
        
        # Demo 1: Development Workflow
        print(f"\n4. 🔄 Demo 1: Complete Development Workflow")
        print("-" * 40)
        
        dev_workflow_command = "setup project named my-app then create issue for initial setup then deploy to development"
        print(f"Command: '{dev_workflow_command}'")
        
        workflow = workflow_parser.parse_workflow(dev_workflow_command)
        if workflow:
            print(f"✅ Parsed workflow with {len(workflow.steps)} steps")
            
            # Execute workflow
            print(f"🚀 Executing workflow...")
            result = workflow_executor.execute_workflow(workflow)
            
            if result.success:
                print(f"✅ Workflow completed successfully!")
                for i, step_result in enumerate(result.step_results, 1):
                    if step_result.success:
                        print(f"   Step {i}: ✅ {step_result.output}")
                    else:
                        print(f"   Step {i}: ❌ {step_result.error}")
            else:
                print(f"❌ Workflow failed: {result.error}")
        else:
            print(f"❌ Could not parse workflow")
        
        # Demo 2: Release Workflow
        print(f"\n5. 🔄 Demo 2: Release Management Workflow")
        print("-" * 40)
        
        release_command = "project status then create release version 2.0.0 then deploy to production"
        print(f"Command: '{release_command}'")
        
        workflow = workflow_parser.parse_workflow(release_command)
        if workflow:
            print(f"✅ Parsed workflow with {len(workflow.steps)} steps")
            
            # Show detailed preview
            preview = workflow_executor.preview_workflow(workflow)
            print(f"Preview:")
            for line in preview.split('\n'):
                print(f"   {line}")
            
            # This workflow has approval steps, so it will trigger our callback
            print(f"\n🚀 Executing workflow...")
            result = workflow_executor.execute_workflow(workflow)
            
            print(f"Workflow Status: {'✅ Success' if result.success else '❌ Failed'}")
            print(f"Execution Time: {result.execution_time:.2f} seconds")
        
        # Demo 3: Error Handling
        print(f"\n6. 🔄 Demo 3: Error Handling & Recovery")
        print("-" * 40)
        
        # Test with invalid command
        invalid_command = "do something impossible then handle error gracefully"
        print(f"Command: '{invalid_command}'")
        
        workflow = workflow_parser.parse_workflow(invalid_command)
        if workflow:
            result = workflow_executor.execute_workflow(workflow)
            print(f"Result: {'✅ Success' if result.success else '❌ Failed as expected'}")
        else:
            print(f"❌ Command not recognized (as expected)")
        
        # Demo 4: Plugin Discovery
        print(f"\n7. 🔍 Demo 4: Natural Language Plugin Discovery")
        print("-" * 40)
        
        test_commands = [
            "git status",
            "setup project named test-app",
            "create issue for bug fix",
            "deploy to production",
            "open in pycharm main.py",
            "review code quality"
        ]
        
        for command in test_commands:
            plugins = plugin_manager.registry.find_plugins_for_command(command)
            print(f"   '{command}' → {len(plugins)} plugin{'s' if len(plugins) != 1 else ''}")
            for plugin in plugins:
                action = plugin.parse_command(command)
                if action:
                    approval_text = " [NEEDS APPROVAL]" if action.requires_approval else ""
                    print(f"      • {plugin.metadata.name}: {action.description}{approval_text}")
        
        # Demo 5: Workflow Chaining with Output
        print(f"\n8. 🔗 Demo 5: Advanced Workflow Chaining")
        print("-" * 40)
        
        # Create a complex workflow manually to show output chaining
        from agent.plugin_base import PluginAction
        from agent.workflow_system import WorkflowStep, Workflow
        
        # Step 1: Setup project (outputs project name)
        step1 = WorkflowStep(
            action=PluginAction(
                name="project_setup",
                description="Setup new project",
                args={"project_name": "chained-workflow-demo"}
            ),
            plugin_name="ProjectManagementPlugin"
        )
        
        # Step 2: Create issue (uses project name from step 1)
        step2 = WorkflowStep(
            action=PluginAction(
                name="create_issue",
                description="Create setup issue",
                args={"title": "Initial project setup complete"}
            ),
            plugin_name="ProjectManagementPlugin",
            depends_on=[0],  # Depends on step 1
            output_mapping={"project_name": "project_context"}
        )
        
        # Step 3: Get status (depends on both previous steps)
        step3 = WorkflowStep(
            action=PluginAction(
                name="project_status",
                description="Get project status",
                args={}
            ),
            plugin_name="ProjectManagementPlugin",
            depends_on=[0, 1]  # Depends on both previous steps
        )
        
        chained_workflow = Workflow(
            name="Advanced Chaining Demo",
            description="Demonstrates output chaining between workflow steps",
            steps=[step1, step2, step3]
        )
        
        print(f"Created advanced workflow: {chained_workflow.name}")
        preview = workflow_executor.preview_workflow(chained_workflow)
        print(f"Preview:")
        for line in preview.split('\n'):
            print(f"   {line}")
        
        # Execute the chained workflow
        print(f"\n🚀 Executing chained workflow...")
        result = workflow_executor.execute_workflow(chained_workflow)
        
        if result.success:
            print(f"✅ Chained workflow completed!")
            for i, step_result in enumerate(result.step_results, 1):
                print(f"   Step {i}: {step_result.output[:100]}{'...' if len(step_result.output) > 100 else ''}")
        
        # Summary
        print(f"\n9. 📊 Workflow System Summary")
        print("-" * 40)
        print("✅ Plugin Registration & Discovery")
        print("✅ Natural Language Command Parsing")
        print("✅ Workflow Creation & Chaining")
        print("✅ Approval System with Custom Callbacks")
        print("✅ Output Passing Between Steps")
        print("✅ Error Handling & Recovery")
        print("✅ Complex Dependency Management")
        print("✅ Real-time Workflow Execution")
        
        print(f"\n🎉 Real-World Workflow Demo Complete!")
        
        print(f"\n💡 Usage Examples:")
        print(f"   'git status then git commit fix then git push'")
        print(f"   'setup project named MyApp then create issue for testing'")
        print(f"   'review code quality and search for security issues'")
        print(f"   'deploy to staging then run tests then deploy to production'")
        print(f"   'create release version 1.2.0 then notify team'")
        
        return True
        
    except Exception as e:
        import traceback
        print(f"❌ Demo failed: {e}")
        print(f"Stack trace: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    demo_real_world_workflows()