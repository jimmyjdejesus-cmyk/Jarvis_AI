#!/usr/bin/env python3
"""
Interactive CLI for Jarvis AI V2
"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.core.agent import JarvisAgentV2
from config.config import DEFAULT_CONFIG

def main():
    """Initialize and run the Jarvis AI V2 system interactively."""
    print("🚀 Starting Jarvis AI V2 Interactive Mode")
    
    # Initialize the agent
    agent = JarvisAgentV2(config=DEFAULT_CONFIG)
    
    # Set up the workflow
    agent.setup_workflow()
    
    print("\nJarvis AI is ready! Type 'exit' to quit.")
    print("-----------------------------------------")
    
    while True:
        # Get user input
        user_input = input("\n🔍 Enter your question: ")
        
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("👋 Thank you for using Jarvis AI!")
            break
        
        # Process the query
        try:
            result = agent.run_workflow(user_input)
            print("\n✅ Result:")
            
            # Extract the detailed response if available
            response = result.get('result', "")
            if isinstance(response, str) and response.startswith("Processed:"):
                print("I'm here to help you with various tasks including:")
                print("- Answering questions about AI, programming, and technology")
                print("- Providing information on LangChain, LangGraph, and LangSmith")
                print("- Helping with code development and troubleshooting")
                print("- Assisting with data analysis and visualization")
                print("- Explaining complex concepts in simple terms")
                print("- Offering guidance on best practices for AI development")
            else:
                print(response)
        except Exception as e:
            print(f"\n❌ Error processing your query: {str(e)}")
    
if __name__ == "__main__":
    main()
