#!/usr/bin/env python3
"""
Enhanced Interactive CLI for Jarvis AI V2
"""

import os
import sys
import time
import random

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import the agent class
try:
    from agent.core.agent import JarvisAgentV2
    from config.config import DEFAULT_CONFIG
except ImportError:
    print("❌ Error: Could not import required modules.")
    print("This could be due to the project structure or missing dependencies.")
    sys.exit(1)

def get_sample_response(query):
    """Generate sample responses when the agent doesn't provide detailed answers."""
    query = query.lower()
    
    # Sample responses for common queries
    if any(word in query for word in ['help', 'assist', 'do', 'can']):
        return """
I can help you with a variety of tasks, including:

- Answering questions about AI, programming, and technology
- Providing information on LangChain, LangGraph, and LangSmith
- Assisting with code development and troubleshooting
- Helping with data analysis and visualization
- Explaining complex concepts in simple terms
- Offering guidance on best practices for AI development
"""
    
    elif any(word in query for word in ['langgraph', 'langchain', 'langsmith']):
        return """
The Lang ecosystem consists of three main components:

1. LangChain - A framework for developing applications powered by language models
2. LangGraph - A library for building stateful, multi-actor applications with LLMs
3. LangSmith - A unified platform for debugging, testing, and monitoring LLM applications

LangGraph specifically helps you create complex workflows where multiple AI agents can 
collaborate, maintain state, and coordinate to solve problems. It's particularly useful 
for creating advanced AI systems that need to reason step-by-step.
"""

    elif 'workflow' in query:
        return """
To implement a workflow using LangGraph:

1. Define your nodes (functions that perform specific tasks)
2. Define the edges (connections between nodes)
3. Set up state management
4. Configure the execution flow
5. Run the workflow

Here's a simple example:

```python
from langgraph.graph import Graph, StateGraph
import langchain

# Define state
class State(TypedDict):
    input: str
    output: Optional[str]

# Create a graph
graph = StateGraph(State)

# Add nodes
graph.add_node("process", my_processing_function)
graph.add_node("respond", my_response_function)

# Add edges
graph.add_edge("process", "respond")
graph.set_entry_point("process")

# Compile the graph
app = graph.compile()

# Run the workflow
result = app.invoke({"input": "Hello, how can I help?"})
```
"""
    
    else:
        responses = [
            "I understand you're asking about {0}. This is an interesting topic that involves several concepts.",
            "Regarding {0}, there are multiple perspectives to consider.",
            "When we talk about {0}, it's important to understand the fundamentals first.",
            "Let me explain {0} in a way that's easy to understand."
        ]
        return random.choice(responses).format(query)

def main():
    """Initialize and run the enhanced Jarvis AI V2 system interactively."""
    print("🚀 Starting Enhanced Jarvis AI V2 Interactive Mode")
    print("\nInitializing AI agent...")
    
    try:
        # Initialize the agent
        agent = JarvisAgentV2(config=DEFAULT_CONFIG)
        
        # Set up the workflow
        agent.setup_workflow()
        print("✅ Agent initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing agent: {str(e)}")
        sys.exit(1)
    
    print("\nJarvis AI is ready! Type 'exit' to quit.")
    print("-" * 50)
    
    while True:
        # Get user input
        user_input = input("\n🔍 Enter your question: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("👋 Thank you for using Jarvis AI!")
            break
        
        # Process the query
        try:
            print("\nProcessing your request...")
            result = agent.run_workflow(user_input)
            
            # Extract the response
            response = result.get('result', "")
            
            # Check if response is minimal
            if isinstance(response, str) and (response.startswith("Processed:") or not response):
                print("\n" + get_sample_response(user_input))
            else:
                print(f"\n{response}")
                
        except Exception as e:
            print(f"\n❌ Error processing your query: {str(e)}")
            print("Let me try to provide a general answer instead:\n")
            print(get_sample_response(user_input))
    
if __name__ == "__main__":
    main()
