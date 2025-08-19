#!/usr/bin/env python3
"""
Test script to verify Lang family integration works in the Streamlit app.
"""

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_streamlit_imports():
    """Test that all imports work in the Streamlit context."""
    print("🧪 Testing Streamlit Integration...")
    
    try:
        # Test core agent import
        from agent.core.core import JarvisAgent
        print("   ✅ JarvisAgent imported")
        
        # Test Lang adapters
        from agent.adapters.langchain_tools import create_langchain_tools
        from agent.adapters.langgraph_workflow import create_jarvis_workflow  
        from agent.adapters.langgraph_ui import render_langgraph_ui
        from agent.adapters.document_loaders import load_jarvis_knowledge
        print("   ✅ Lang adapters imported")
        
        # Test tools
        import agent.tools as tools
        print("   ✅ Agent tools imported")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_creation():
    """Test creating an agent with Lang family support."""
    print("\n🤖 Testing Agent Creation...")
    
    try:
        from agent.core.core import JarvisAgent
        import agent.tools as tools
        
        def approval_callback(preview):
            return True
        
        agent = JarvisAgent(
            persona_prompt="Test agent",
            tool_registry=tools,
            approval_callback=approval_callback
        )
        
        print(f"   ✅ Agent created successfully")
        print(f"   📊 LangChain tools: {len(agent.langchain_tools)}")
        print(f"   📖 Knowledge docs: {len(agent.knowledge_documents)}")
        print(f"   🔄 Workflow available: {agent.langgraph_workflow is not None}")
        
        # Test workflow execution
        result = agent.execute_langgraph_workflow("test workflow")
        print(f"   ✅ Workflow execution: {result.get('success', False)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Agent creation error: {e}")
        return False

def test_ui_integration():
    """Test UI components work."""
    print("\n🎨 Testing UI Integration...")
    
    try:
        from agent.adapters.langgraph_ui import WorkflowVisualizer
        
        visualizer = WorkflowVisualizer()
        
        # Add a mock execution
        mock_result = {
            "plan": '{"tool": "test"}',
            "reflection": '{"success": true}',
            "success": True
        }
        
        visualizer.add_execution(mock_result)
        print(f"   ✅ Visualizer created and execution added")
        
        return True
        
    except Exception as e:
        print(f"   ❌ UI integration error: {e}")
        return False

def main():
    """Run all integration tests."""
    print("🚀 Jarvis AI Streamlit Integration Test\n")
    
    tests = [
        test_streamlit_imports,
        test_agent_creation,
        test_ui_integration
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
    print(f"\n📋 Integration Test Summary:")
    print(f"   ✅ Passed: {sum(results)}")
    print(f"   ❌ Failed: {len(results) - sum(results)}")
    print(f"   📊 Success rate: {sum(results)/len(results)*100:.1f}%")
    
    if all(results):
        print(f"\n🎉 All integration tests passed!")
        print(f"💡 The Lang family integration is ready for use in Streamlit.")
    else:
        print(f"\n⚠️ Some integration tests failed.")
    
    return all(results)

if __name__ == "__main__":
    main()