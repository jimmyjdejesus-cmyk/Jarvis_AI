#!/usr/bin/env python3
"""
LangSmith Setup and Test for Jarvis AI
Configures LangSmith monitoring and tests the connection.
"""

import os
import sys
from pathlib import Path

def load_env_file():
    """Load environment variables from .env file."""
    env_file = Path('.env')
    if env_file.exists():
        print("📄 Loading .env file...")
        try:
            # Simple .env parser
            with open('.env', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
            print("✅ Environment variables loaded")
        except Exception as e:
            print(f"❌ Error loading .env file: {e}")
    else:
        print("⚠️ No .env file found. Please create one with your API keys.")

def check_langsmith_setup():
    """Check if LangSmith is properly configured."""
    print("\n🔍 Checking LangSmith Configuration...")
    
    api_key = os.getenv('LANGSMITH_API_KEY')
    tracing = os.getenv('LANGCHAIN_TRACING_V2')
    project = os.getenv('LANGCHAIN_PROJECT')
    
    if not api_key:
        print("❌ LANGSMITH_API_KEY not set")
        print("   Get your key from: https://smith.langchain.com/")
        return False
    
    if api_key.startswith(('ls_', 'lsv2_sk_', 'lsv2_pt_')):
        print("✅ LangSmith API key format looks correct")
    else:
        print("⚠️ API key format not recognized - please verify")
    
    if tracing == 'true':
        print("✅ LangChain tracing enabled")
    else:
        print("⚠️ LangChain tracing not enabled")
    
    if project:
        print(f"✅ Project name set to: {project}")
    else:
        print("⚠️ No project name set")
    
    return bool(api_key)

def test_langsmith_connection():
    """Test connection to LangSmith."""
    print("\n🧪 Testing LangSmith Connection...")
    
    try:
        # Import and test LangSmith
        from langsmith import Client
        
        client = Client()
        
        # Try to get current user info (fix the callable issue)
        user_info = client.info
        print(f"✅ Connected to LangSmith successfully!")
        print(f"   Session info retrieved")
        
        # Test with a simple operation
        try:
            # Try to list projects (this will verify the connection works)
            projects = list(client.list_projects(limit=1))
            print(f"   Found {len(projects)} project(s) in your account")
        except Exception as e:
            print(f"   Connection established but limited access: {e}")
        
        return True
        
    except ImportError:
        print("❌ LangSmith not installed. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "langsmith"])
        print("✅ LangSmith installed. Please run this script again.")
        return False
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("   Please check your API key and internet connection")
        return False

def test_simple_workflow():
    """Test a simple workflow with LangSmith tracing."""
    print("\n🚀 Testing Workflow with LangSmith Tracing...")
    
    try:
        from langchain_core.messages import HumanMessage
        from langchain_core.tracers import LangChainTracer
        
        # Create a simple test
        tracer = LangChainTracer()
        
        # Simulate a workflow step
        with tracer.trace("test_workflow"):
            print("   📝 Simulating workflow step...")
            result = "Test workflow completed successfully"
        
        print("✅ Workflow tracing test completed")
        print("   Check your LangSmith dashboard for trace data")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        return False

def show_dashboard_info():
    """Show information about accessing the LangSmith dashboard."""
    print("\n📊 LangSmith Dashboard Access:")
    print("=" * 50)
    print("🌐 URL: https://smith.langchain.com/")
    
    project = os.getenv('LANGCHAIN_PROJECT', 'default')
    print(f"📁 Project: {project}")
    print("\n🎯 What you can see in the dashboard:")
    print("  • Real-time workflow execution traces")
    print("  • Performance metrics and timing")
    print("  • Input/output data for each step")
    print("  • Error tracking and debugging info")
    print("  • Cost analysis across different models")

def create_test_workflow():
    """Create a simple test workflow that uses LangSmith tracing."""
    
    test_code = '''#!/usr/bin/env python3
"""
Simple Test Workflow with LangSmith Tracing
Run this to verify your LangSmith setup is working.
"""

import os
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tracers import LangChainTracer

def simple_traced_workflow():
    """A simple workflow that demonstrates LangSmith tracing."""
    
    # Initialize tracer
    tracer = LangChainTracer()
    
    # Start a traced workflow
    with tracer.trace("jarvis_test_workflow", inputs={"query": "test"}) as trace:
        
        # Step 1: Planning
        with tracer.trace("planning_step") as planning_trace:
            plan = "1. Analyze input\\n2. Generate response\\n3. Return result"
            planning_trace.outputs = {"plan": plan}
            print("🧠 Planning completed")
        
        # Step 2: Execution
        with tracer.trace("execution_step") as exec_trace:
            result = "Jarvis AI workflow executed successfully with LangSmith tracing!"
            exec_trace.outputs = {"result": result}
            print("⚡ Execution completed")
        
        # Step 3: Final result
        trace.outputs = {"final_result": result}
        print("✅ Workflow completed")
    
    return result

if __name__ == "__main__":
    print("🚀 Running Jarvis AI Test Workflow with LangSmith")
    print("=" * 50)
    
    # Check if tracing is enabled
    if os.getenv('LANGCHAIN_TRACING_V2') == 'true':
        print("📡 LangSmith tracing is ENABLED")
    else:
        print("⚠️ LangSmith tracing is DISABLED")
        print("Set LANGCHAIN_TRACING_V2=true to enable")
    
    # Run the workflow
    try:
        result = simple_traced_workflow()
        print(f"\\n🎉 Result: {result}")
        print("\\n📊 Check your LangSmith dashboard to see the trace!")
        print("   URL: https://smith.langchain.com/")
    except Exception as e:
        print(f"❌ Error: {e}")
'''
    
    with open('test_langsmith_workflow.py', 'w') as f:
        f.write(test_code)
    
    print("✅ Created test_langsmith_workflow.py")

def main():
    """Main setup and test function."""
    print("🔧 Jarvis AI - LangSmith Setup and Test")
    print("=" * 50)
    
    # Load environment
    load_env_file()
    
    # Check configuration
    langsmith_configured = check_langsmith_setup()
    
    if not langsmith_configured:
        print("\n❌ LangSmith not properly configured")
        print("\n📝 To fix this:")
        print("1. Get API key from: https://smith.langchain.com/")
        print("2. Add to .env file: LANGSMITH_API_KEY=your_key_here")
        print("3. Run this script again")
        return
    
    # Test connection
    if test_langsmith_connection():
        print("\n🎉 LangSmith is working!")
        
        # Create test workflow
        create_test_workflow()
        
        # Show dashboard info
        show_dashboard_info()
        
        print("\n🚀 Next Steps:")
        print("1. Run: python test_langsmith_workflow.py")
        print("2. Check your LangSmith dashboard for traces")
        print("3. Start building real agentic workflows!")
    
    else:
        print("\n❌ LangSmith connection failed")
        print("Please check your API key and try again")

if __name__ == "__main__":
    main()
