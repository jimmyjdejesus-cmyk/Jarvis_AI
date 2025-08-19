#!/usr/bin/env python3
"""
Test script for Lang family integration in Jarvis AI.

This script tests the LangChain tools, LangGraph workflow, and LangGraphUI components.
"""

import os
import sys
import json
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_langchain_tools():
    """Test LangChain tools integration."""
    print("🔧 Testing LangChain Tools...")
    
    try:
        from agent.adapters.langchain_tools import create_langchain_tools, CheckOllamaStatusTool, LANGCHAIN_AVAILABLE
        
        if not LANGCHAIN_AVAILABLE:
            print("   ⚠️ LangChain not available, testing fallback behavior")
            # Test fallback tools creation
            tools = create_langchain_tools()
            print(f"   ✅ Fallback tools list created: {len(tools)} tools")
            
            # Test Ollama status tool fallback
            ollama_tool = CheckOllamaStatusTool()
            status = ollama_tool._run()
            print(f"   🔍 Ollama status check: {status[:50]}...")
            return True
        else:
            # Create tools
            tools = create_langchain_tools()
            print(f"   ✅ Created {len(tools)} LangChain tools")
            
            # List tools
            for tool in tools:
                print(f"      - {tool.name}: {tool.description[:50]}...")
            
            # Test Ollama status tool
            ollama_tool = CheckOllamaStatusTool()
            status = ollama_tool._run()
            print(f"   🔍 Ollama status: {status}")
            
            return True
    except Exception as e:
        print(f"   ❌ LangChain tools test failed: {e}")
        return False


def test_document_loaders():
    """Test custom document loaders."""
    print("\n📚 Testing Document Loaders...")
    
    try:
        from agent.adapters.document_loaders import load_jarvis_knowledge, JarvisProjectLoader
        
        # Test project loader
        loader = JarvisProjectLoader(".", include_code=False)
        docs = loader.load()
        print(f"   ✅ Project loader found {len(docs)} documents")
        
        if docs:
            print(f"      - Example doc: {docs[0].metadata.get('type')} - {docs[0].metadata.get('filename')}")
        
        # Test knowledge loader
        knowledge_docs = load_jarvis_knowledge()
        print(f"   ✅ Knowledge loader found {len(knowledge_docs)} documents")
        
        return True
    except Exception as e:
        print(f"   ❌ Document loaders test failed: {e}")
        return False


def test_langgraph_workflow():
    """Test LangGraph workflow integration."""
    print("\n🔄 Testing LangGraph Workflow...")
    
    try:
        from agent.core.core import JarvisAgent, LANG_FAMILY_AVAILABLE
        from agent.adapters.langgraph_workflow import create_jarvis_workflow, LANGGRAPH_AVAILABLE
        import agent.tools as tools
        
        # Create a test agent
        def test_approval_callback(preview):
            print(f"   🔔 Approval request: {preview}")
            return True  # Auto-approve for testing
        
        agent = JarvisAgent(
            persona_prompt="Test agent",
            tool_registry=tools,
            approval_callback=test_approval_callback
        )
        
        if not LANGGRAPH_AVAILABLE:
            print(f"   ⚠️ LangGraph not available, testing fallback behavior")
            # Test workflow creation fallback
            workflow = create_jarvis_workflow(agent)
            print(f"   ✅ Created fallback workflow")
            
            # Test workflow execution fallback
            result = workflow.execute_workflow("test message", [])
            print(f"   ✅ Workflow executed with fallback: success={result.get('success')}")
            return True
        else:
            # Test workflow creation
            workflow = create_jarvis_workflow(agent)
            print(f"   ✅ Created workflow graph")
            
            # Test workflow execution
            result = workflow.execute_workflow("test message", [])
            print(f"   ✅ Workflow executed: success={result.get('success')}")
            
            if result.get('reflection'):
                reflection_preview = str(result['reflection'])[:100]
                print(f"   🤔 Reflection preview: {reflection_preview}...")
            
            return True
    except Exception as e:
        print(f"   ❌ LangGraph workflow test failed: {e}")
        return False


def test_agent_integration():
    """Test the integrated agent with Lang family components."""
    print("\n🤖 Testing Agent Integration...")
    
    try:
        from agent.core.core import JarvisAgent, LANG_FAMILY_AVAILABLE
        import agent.tools as tools
        
        def test_approval_callback(preview):
            print(f"   🔔 Approval: {preview}")
            return True
        
        # Create agent
        agent = JarvisAgent(
            persona_prompt="Test Jarvis Agent",
            tool_registry=tools,
            approval_callback=test_approval_callback
        )
        
        print(f"   ✅ Agent created")
        print(f"   📊 Lang family available: {LANG_FAMILY_AVAILABLE}")
        
        if LANG_FAMILY_AVAILABLE:
            print(f"   📊 Lang tools available: {len(agent.langchain_tools)}")
            print(f"   📖 Knowledge docs: {len(agent.knowledge_documents)}")
            print(f"   🔄 Workflow available: {agent.langgraph_workflow is not None}")
        else:
            print(f"   ⚠️ Lang family not available, using fallback functionality")
        
        # Test workflow execution
        test_input = "check system status"
        result = agent.execute_langgraph_workflow(test_input)
        print(f"   ✅ Workflow execution: success={result.get('success')}")
        
        return True
    except Exception as e:
        print(f"   ❌ Agent integration test failed: {e}")
        return False


def test_ui_components():
    """Test UI visualization components."""
    print("\n🎨 Testing UI Components...")
    
    try:
        from agent.adapters.langgraph_ui import WorkflowVisualizer
        
        # Create visualizer
        visualizer = WorkflowVisualizer()
        print(f"   ✅ Workflow visualizer created")
        
        # Test with mock workflow result
        mock_result = {
            "plan": '{"tool": "test", "args": {}}',
            "reflection": '{"success_indicators": ["Test passed"], "concerns": [], "recommendations": ["Continue testing"]}',
            "success": True,
            "iterations": 1
        }
        
        visualizer.add_execution(mock_result)
        print(f"   ✅ Added mock execution to visualizer")
        print(f"   📊 Execution history: {len(visualizer.execution_history)} items")
        
        return True
    except Exception as e:
        print(f"   ❌ UI components test failed: {e}")
        return False


def test_config_yaml_integration():
    """Test that config.yaml remains the source of truth."""
    print("\n⚙️ Testing Config Integration...")
    
    try:
        from agent.core.config_manager import ConfigurationManager
        
        # Test config loading
        config_manager = ConfigurationManager()
        
        # Check if config path exists or use defaults
        if Path("config.yaml").exists():
            config = config_manager.load_config()
            print(f"   ✅ Config loaded from config.yaml")
            print(f"   📝 App name: {config.app_name}")
            print(f"   🔢 Version: {config.version}")
        else:
            print(f"   ⚠️ No config.yaml found, using defaults")
            print(f"   💡 Config manager created successfully")
        
        return True
    except Exception as e:
        print(f"   ❌ Config integration test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Testing Jarvis AI Lang Family Integration\n")
    
    tests = [
        test_langchain_tools,
        test_document_loaders,
        test_langgraph_workflow,
        test_agent_integration,
        test_ui_components,
        test_config_yaml_integration
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   💥 Test crashed: {e}")
            results.append(False)
    
    # Summary
    print(f"\n📋 Test Summary:")
    print(f"   ✅ Passed: {sum(results)}")
    print(f"   ❌ Failed: {len(results) - sum(results)}")
    print(f"   📊 Success rate: {sum(results)/len(results)*100:.1f}%")
    
    if all(results):
        print(f"\n🎉 All tests passed! Lang family integration is working.")
    else:
        print(f"\n⚠️ Some tests failed. Check the output above for details.")
    
    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)