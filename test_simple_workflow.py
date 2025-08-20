#!/usr/bin/env python3
"""
Simple test of Jarvis AI Agentic Workflow
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

def simple_workflow_demo():
    """Demonstrate a simple multi-step workflow without complex tracing."""
    print("\n🚀 Simple Agentic Workflow Demo")
    print("=" * 40)
    
    query = "What are the key components for production AI apps?"
    print(f"🎯 Query: {query}")
    
    # Step 1: Planning
    print("\n📋 Step 1: Planning")
    plan = [
        "Identify core infrastructure needs",
        "Research monitoring and observability", 
        "Consider scalability requirements",
        "Synthesize best practices"
    ]
    print("   Plan created:")
    for i, step in enumerate(plan, 1):
        print(f"      {i}. {step}")
    
    # Step 2: Research/Analysis
    print("\n🔍 Step 2: Research & Analysis")
    research = {
        "infrastructure": ["Vector databases", "Model serving", "API gateways"],
        "monitoring": ["LangSmith tracing", "Performance metrics", "Error tracking"],
        "scalability": ["Load balancing", "Caching", "Auto-scaling"],
        "best_practices": ["Security", "Testing", "Documentation"]
    }
    print("   Research findings:")
    for category, items in research.items():
        print(f"      {category.title()}: {', '.join(items)}")
    
    # Step 3: Synthesis
    print("\n📝 Step 3: Synthesis")
    result = """
Production-ready AI applications require:

1. **Infrastructure**: Vector databases for embeddings, model serving platforms, API gateways
2. **Monitoring**: LangSmith for tracing, performance metrics, comprehensive error tracking  
3. **Scalability**: Load balancing, intelligent caching, auto-scaling capabilities
4. **Best Practices**: Security protocols, thorough testing, complete documentation

This creates a robust foundation for enterprise AI applications.
"""
    print(f"   Final Result: {result}")
    
    return result

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
            return True
        else:
            print("   ❌ Ollama not responding")
            return False
    except Exception as e:
        print(f"   ❌ Ollama connection failed: {e}")
        print("   💡 Make sure Ollama is running: ollama serve")
        return False

if __name__ == "__main__":
    print("🚀 Starting Jarvis AI Simple Workflow Test")
    print("=" * 50)
    
    # Test LangSmith connection
    langsmith_working = test_langsmith_connection()
    
    if langsmith_working:
        print("🔗 LangSmith monitoring active")
        os.environ['LANGCHAIN_TRACING_V2'] = 'true'
        os.environ['LANGCHAIN_PROJECT'] = 'jarvis-ai-simple-workflow'
    else:
        print("⚠️ LangSmith not available - running in local mode")
    
    # Run the simple workflow
    try:
        result = simple_workflow_demo()
        print("\n🎉 Workflow completed successfully!")
        
        if langsmith_working:
            print("\n📊 Check your LangSmith dashboard for traces!")
            print("   Dashboard: https://smith.langchain.com/")
        
    except Exception as e:
        print(f"\n❌ Workflow failed: {e}")
    
    # Test Ollama integration
    ollama_working = test_ollama_integration()
    
    print("\n" + "=" * 50)
    print("✅ Simple workflow test complete!")
    
    print("\n📋 Status Summary:")
    print(f"   🔗 LangSmith: {'✅ Connected' if langsmith_working else '❌ Not available'}")
    print(f"   🦙 Ollama: {'✅ Connected' if ollama_working else '❌ Not available'}")
    
    print("\n🚀 Next steps:")
    print("1. Check LangSmith dashboard for traces")
    print("2. Run more complex agentic workflows")
    print("3. Build custom agent chains!")
