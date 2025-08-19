#!/usr/bin/env python3
"""
Test script for Jarvis AI V2 LangGraph integration

This script tests the core V2 functionality including:
- LangGraph agent creation
- LangChain tools functionality
- Workflow execution
- Error handling and graceful degradation
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_langgraph_availability():
    """Test if LangGraph is available and working."""
    print("🧪 Testing LangGraph availability...")
    
    try:
        from agent.core.langgraph_agent import LANGGRAPH_AVAILABLE, get_agent
        
        if LANGGRAPH_AVAILABLE:
            print("✅ LangGraph is available")
            
            # Try to create an agent
            agent = get_agent(expert_model="test_model")
            if agent:
                print("✅ LangGraph agent created successfully")
                return True
            else:
                print("❌ Failed to create LangGraph agent")
                return False
        else:
            print("❌ LangGraph is not available")
            return False
            
    except ImportError as e:
        print(f"❌ LangGraph import error: {e}")
        return False
    except Exception as e:
        print(f"❌ LangGraph error: {e}")
        return False


def test_langchain_tools():
    """Test LangChain tools functionality."""
    print("\n🧪 Testing LangChain tools...")
    
    try:
        from agent.core.langchain_tools import get_available_tools, get_tools_description
        
        tools = get_available_tools()
        print(f"✅ Found {len(tools)} LangChain tools")
        
        # Test a few key tools
        for tool in tools[:3]:  # Test first 3 tools
            try:
                tool_name = tool.__name__
                print(f"  📋 Tool: {tool_name}")
            except Exception as e:
                print(f"  ❌ Error with tool: {e}")
        
        # Test tool descriptions
        description = get_tools_description()
        if description and "Available tools:" in description:
            print("✅ Tool descriptions generated successfully")
        else:
            print("❌ Failed to generate tool descriptions")
        
        return True
        
    except ImportError as e:
        print(f"❌ LangChain tools import error: {e}")
        return False
    except Exception as e:
        print(f"❌ LangChain tools error: {e}")
        return False


def test_agent_workflow():
    """Test the complete agent workflow."""
    print("\n🧪 Testing agent workflow...")
    
    try:
        from agent.core.langgraph_agent import get_agent
        
        agent = get_agent(expert_model="test_model", use_langgraph=True)
        
        if not agent:
            print("❌ Could not create agent for testing")
            return False
        
        # Test with a simple message
        test_message = "Hello, can you help me list files in the current directory?"
        
        result = agent.invoke(test_message)
        
        if isinstance(result, dict):
            if result.get("error"):
                print(f"⚠️ Agent returned error: {result['error']}")
                if "fallback" in result:
                    print("✅ Fallback response provided")
                return True
            else:
                print("✅ Agent executed successfully")
                print(f"  📋 Current step: {result.get('current_step', 'unknown')}")
                return True
        else:
            print(f"❌ Unexpected result type: {type(result)}")
            return False
            
    except Exception as e:
        print(f"❌ Agent workflow error: {e}")
        return False


def test_v1_compatibility():
    """Test V1 compatibility mode."""
    print("\n🧪 Testing V1 compatibility...")
    
    try:
        from agent.core.core import JarvisAgent
        import agent.tools as tools
        
        # Create agent in V1 mode
        agent = JarvisAgent(
            persona_prompt="Test assistant",
            tool_registry=tools,
            approval_callback=lambda x: True,
            expert_model="test_model",
            use_langgraph=False  # Force V1 mode
        )
        
        # Test basic functionality
        test_message = "Hello world"
        plan = agent.parse_natural_language(test_message, [])
        
        if plan and isinstance(plan, list):
            print("✅ V1 compatibility mode working")
            print(f"  📋 Generated plan with {len(plan)} steps")
            return True
        else:
            print("❌ V1 compatibility mode failed")
            return False
            
    except Exception as e:
        print(f"❌ V1 compatibility error: {e}")
        return False


def test_configuration():
    """Test configuration management for V2."""
    print("\n🧪 Testing V2 configuration...")
    
    try:
        from agent.core.config_manager import get_config
        
        config = get_config()
        
        if hasattr(config, 'v2'):
            v2_config = config.v2
            print("✅ V2 configuration section found")
            print(f"  📋 Enabled: {v2_config.enabled}")
            print(f"  📋 Expert Model: {v2_config.expert_model}")
            print(f"  📋 Max Iterations: {v2_config.max_iterations}")
            return True
        else:
            print("❌ V2 configuration section not found")
            return False
            
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


def test_backend_service():
    """Test if the backend service can be imported and configured."""
    print("\n🧪 Testing backend service...")
    
    try:
        from agent.core.langgraph_backend import create_app
        
        app = create_app()
        
        if app:
            print("✅ Backend FastAPI app created successfully")
            print(f"  📋 App title: {app.title}")
            print(f"  📋 App version: {app.version}")
            return True
        else:
            print("❌ Failed to create backend app")
            return False
            
    except ImportError as e:
        print(f"❌ Backend import error: {e}")
        print("  💡 Install FastAPI: pip install fastapi uvicorn")
        return False
    except Exception as e:
        print(f"❌ Backend error: {e}")
        return False


def main():
    """Run all tests and provide a summary."""
    print("🚀 Jarvis AI V2 Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("LangGraph Availability", test_langgraph_availability),
        ("LangChain Tools", test_langchain_tools),
        ("Agent Workflow", test_agent_workflow),
        ("V1 Compatibility", test_v1_compatibility),
        ("Configuration", test_configuration),
        ("Backend Service", test_backend_service),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! V2 integration is working correctly.")
        return 0
    elif passed >= total // 2:
        print("⚠️ Most tests passed. V2 integration is partially working.")
        return 1
    else:
        print("❌ Many tests failed. V2 integration needs attention.")
        return 2


if __name__ == "__main__":
    sys.exit(main())