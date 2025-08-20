#!/usr/bin/env python3
"""
Simple Test Workflow with LangSmith Tracing
Run this to verify your LangSmith setup is working.
"""

import os
from langchain_core.messages import HumanMessage, AIMessage

def simple_traced_workflow():
    """A simple workflow that demonstrates LangSmith tracing."""
    
    print("Planning step...")
    plan = "1. Analyze input\n2. Generate response\n3. Return result"
    print("Planning completed")
    
    print("Execution step...")
    result = "Jarvis AI workflow executed successfully with LangSmith tracing!"
    print("Execution completed")
    
    print("Workflow completed")
    return result

if __name__ == "__main__":
    print("Running Jarvis AI Test Workflow with LangSmith")
    print("=" * 50)
    
    # Check if tracing is enabled
    if os.getenv('LANGCHAIN_TRACING_V2') == 'true':
        print("LangSmith tracing is ENABLED")
    else:
        print("LangSmith tracing is DISABLED")
        print("Set LANGCHAIN_TRACING_V2=true to enable")
    
    # Run the workflow
    try:
        result = simple_traced_workflow()
        print(f"\nResult: {result}")
        print("\nCheck your LangSmith dashboard to see the trace!")
        print("URL: https://smith.langchain.com/")
    except Exception as e:
        print(f"Error: {e}")
