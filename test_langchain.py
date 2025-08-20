#!/usr/bin/env python3
"""
Test LangChain imports to isolate hanging issue
"""

print("🚀 Testing LangChain imports...")

try:
    print("Importing langchain_core.messages...")
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    print("✅ Messages imported")
    
    print("Importing langchain_core.callbacks...")
    from langchain_core.callbacks import CallbackManager
    print("✅ CallbackManager imported")
    
    print("Importing langchain_core.tracers...")
    from langchain_core.tracers import LangChainTracer
    print("✅ LangChainTracer imported")
    
    print("Creating tracer...")
    tracer = LangChainTracer(project_name="test-project")
    print("✅ Tracer created")
    
except Exception as e:
    print(f"❌ LangChain import failed: {e}")
    import traceback
    traceback.print_exc()

print("✅ LangChain test completed!")
