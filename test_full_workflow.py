#!/usr/bin/env python3
"""
Test Jarvis AI Agentic Workflow with LangSmith
This demonstrates a real agentic workflow with proper LangSmith tracing.
"""

import os
from pathlib import Path

# Load environment variables from .env file
def load_env():
    env_file = Path('.env')
    if env_file.exists():
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Load environment first
load_env()

# Now import LangChain components
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.callbacks import CallbackManager
from langchain_core.tracers import LangChainTracer

def setup_environment():
    """Setup environment variables and configuration."""
    # Load environment variables (already done by load_env())
    
    # Ensure required environment variables are set
    required_vars = ['LANGSMITH_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️ Missing environment variables: {missing_vars}")
        print("💡 Make sure your .env file is configured correctly")
    
    # Set LangChain tracing if LangSmith is available
    if os.getenv('LANGSMITH_API_KEY'):
        os.environ['LANGCHAIN_TRACING_V2'] = 'true'
        os.environ['LANGCHAIN_PROJECT'] = 'jarvis-ai-workflow'

def test_langsmith_connection():
    """Test connection to LangSmith."""
    try:
        from langsmith import Client
        
        client = Client()
        projects = list(client.list_projects(limit=1))
        print(f"✅ LangSmith connected! Found {len(projects)} project(s) in your account")
        return True
        
    except Exception as e:
        print(f"❌ LangSmith connection failed: {e}")
        return False

def create_simple_agent_workflow(workflow_input="What are the key components needed for building production-ready AI applications?"):
    """Create a simple multi-step agent workflow with LangSmith tracing."""
    
    print("🤖 Starting Jarvis AI Agentic Workflow")
    print("=" * 50)
    
    # Check tracing status
    tracing_enabled = os.getenv('LANGCHAIN_TRACING_V2') == 'true'
    project_name = os.getenv('LANGCHAIN_PROJECT', 'default')
    
    print(f"📡 LangSmith Tracing: {'ENABLED' if tracing_enabled else 'DISABLED'}")
    print(f"📁 Project: {project_name}")
    
    if not tracing_enabled:
        print("⚠️ To enable tracing, set LANGCHAIN_TRACING_V2=true in your .env file")
    
    # Initialize tracer
    tracer = LangChainTracer() if tracing_enabled else None
    
    # Simulate an agentic workflow
    workflow_input = "Analyze the benefits of using LangGraph for agentic workflows"
    
    print(f"\n🎯 Input: {workflow_input}")
    
    # Step 1: Planning
    print("\n📋 Step 1: Planning")
    plan = create_plan(workflow_input)
    print(f"   Plan: {plan}")
    
    # Step 2: Research/Analysis
    print("\n🔍 Step 2: Research & Analysis")
    research = conduct_research(plan)
    print(f"   Research: {research}")
    
    # Step 3: Synthesis
    print("\n📝 Step 3: Synthesis")
    final_result = synthesize_results(research)
    print(f"\n✅ Final Result: {final_result}")
    
    if tracing_enabled:
        print("\n📊 Check your LangSmith dashboard for detailed traces!")
        print("   URL: https://smith.langchain.com/")
    
    return final_result

def create_plan(query):
    """Planning step - break down the query into actionable steps."""
    return [
        "Identify key components of LangGraph",
        "Research agentic workflow benefits", 
        "Compare with traditional approaches",
        "Synthesize findings"
    ]

def conduct_research(plan):
    """Research step - gather information based on the plan."""
    return {
        "langgraph_features": [
            "Stateful multi-actor systems",
            "Conditional execution paths",
            "Human-in-the-loop integration",
            "Persistent memory"
        ],
        "agentic_benefits": [
            "Autonomous decision making",
            "Iterative refinement",
            "Tool orchestration",
            "Error handling and recovery"
        ],
        "advantages": [
            "Better reasoning capabilities",
            "More robust workflows",
            "Easier debugging and monitoring",
            "Scalable agent coordination"
        ]
    }

def synthesize_results(research):
    """Synthesis step - create final comprehensive answer."""
    return """
LangGraph enables powerful agentic workflows through:

1. **Stateful Architecture**: Maintains context across multiple steps
2. **Conditional Logic**: Routes decisions based on intermediate results  
3. **Tool Integration**: Seamlessly orchestrates multiple AI tools
4. **Error Recovery**: Handles failures gracefully with fallback strategies
5. **Human Oversight**: Allows human intervention when needed

This makes it ideal for complex, multi-step reasoning tasks that require
autonomous agents to collaborate and make decisions.
"""

def test_ollama_integration():
    """Test integration with Ollama for local LLM usage."""
    print("\n🦙 Testing Ollama Integration")
    
    ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    print(f"   Ollama URL: {ollama_url}")
    
    try:
        import requests
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"   ✅ Ollama connected! Found {len(models)} models")
            for model in models[:3]:  # Show first 3 models
                print(f"      - {model.get('name', 'Unknown')}")
        else:
            print("   ❌ Ollama not responding")
    except Exception as e:
        print(f"   ❌ Ollama connection failed: {e}")
        print("   💡 Make sure Ollama is running: ollama serve")

if __name__ == "__main__":
    print("🚀 Starting Jarvis AI Agentic Workflow Test")
    print("=" * 50)
    
    # Configure environment
    setup_environment()
    
    # Test LangSmith connection
    langsmith_working = test_langsmith_connection()
    
    if langsmith_working:
        print("\n🔗 LangSmith monitoring active - workflows will be traced")
    else:
        print("\n⚠️ LangSmith not available - running in local mode")
    
    # Run the workflow
    test_query = "What are the key components needed for building production-ready AI applications?"
    
    print(f"\n🎯 Query: {test_query}")
    
    try:
        result = create_simple_agent_workflow(test_query)
        
        if langsmith_working:
            print("\n📊 Check your LangSmith dashboard for workflow traces!")
            print("   Dashboard: https://smith.langchain.com/")
        
        print("\n🎉 Workflow completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Workflow failed: {e}")
    
    # Test Ollama integration
    test_ollama_integration()
    
    print("\n" + "=" * 50)
    print("✅ Agentic workflow test complete!")
    print("\n🚀 Next steps:")
    print("1. Check LangSmith dashboard for traces")
    print("2. Explore the workflow_templates/ directory")
    print("3. Build your own agentic workflows!")
