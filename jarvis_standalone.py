#!/usr/bin/env python3
"""
Jarvis AI Standalone Assistant
A standalone assistant that provides helpful responses without relying on the full agent implementation.
"""

import os
import sys
import time
import random
from datetime import datetime

def display_header():
    """Display an attractive ASCII art header"""
    header = """
    ██╗  █████╗  ██████╗  ██╗   ██╗ ██╗ ███████╗     █████╗  ██╗
    ██║ ██╔══██╗ ██╔══██╗ ██║   ██║ ██║ ██╔════╝    ██╔══██╗ ██║
    ██║ ███████║ ██████╔╝ ██║   ██║ ██║ ███████╗    ███████║ ██║
    ██║ ██╔══██║ ██╔══██╗  ██║ ██╔╝ ██║ ╚════██║    ██╔══██║ ██║
    ██║ ██║  ██║ ██║  ██║   ███╔╝  ██║ ███████║    ██║  ██║ ██║
    ╚═╝ ╚═╝  ╚═╝ ╚═╝  ╚═╝    ╚══╝   ╚═╝ ╚══════╝    ╚═╝  ╚═╝ ╚═╝
    """
    print(header)
    print("\nStandalone AI Assistant - Ready to help!")
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 70)

def get_ai_response(query):
    """
    Generate informative responses based on the query.
    """
    query = query.lower().strip()
    
    # Help topics
    if any(word in query for word in ['help', 'assist', 'do', 'can', 'what']):
        return """
I can assist you with various tasks, including:

1. AI & Machine Learning:
   - Explaining ML algorithms and concepts
   - Suggesting best practices for AI development
   - Providing information about LLMs, neural networks, etc.

2. Programming & Development:
   - Helping with code issues and debugging
   - Suggesting code improvements
   - Explaining programming concepts

3. LangChain Ecosystem:
   - Using LangChain for AI application development
   - Building workflows with LangGraph
   - Monitoring and testing with LangSmith

4. Data Analysis:
   - Data processing techniques
   - Visualization approaches
   - Statistical methods

5. Project Management:
   - Software development methodologies
   - Best practices for team collaboration
   - Version control strategies

What specific area would you like to explore further?
"""
    
    # AI agents
    elif any(phrase in query for phrase in ['ai agent', 'agent', 'assistant']):
        return """
# AI Agents: An Overview

AI agents are software entities that can perceive their environment, make decisions, and take actions to achieve specific goals. They represent a key advancement in artificial intelligence that moves beyond simple input-output systems toward more autonomous and interactive capabilities.

## Key Components of AI Agents:

1. **Perception**: Ability to gather information from their environment through various inputs (text, images, API data)

2. **Reasoning**: Processing inputs and making decisions based on:
   - Knowledge base
   - Learned patterns
   - Logical inference
   - Large language models (LLMs)

3. **Action**: Taking steps that affect their environment, such as:
   - Generating responses
   - Making API calls
   - Accessing tools
   - Storing/retrieving information

4. **Memory**: Maintaining context across interactions:
   - Short-term working memory
   - Long-term knowledge storage
   - Conversational history

5. **Planning**: Creating sequences of actions to achieve goals:
   - Breaking complex tasks into subtasks
   - Evaluating alternative approaches
   - Adapting plans based on new information

## Types of AI Agents:

1. **Simple Reflex Agents**: Act based on current input only
2. **Model-Based Agents**: Maintain internal state to track unobserved aspects
3. **Goal-Based Agents**: Work toward specific objectives
4. **Utility-Based Agents**: Optimize for preferred outcomes
5. **Learning Agents**: Improve performance through experience

## Advanced Agent Architectures:

- **Multi-Agent Systems**: Teams of specialized agents that collaborate
- **Agent-Based Workflows**: Using tools like LangGraph to create complex processes
- **Agentic RAG Systems**: Combining retrieval and generation for enhanced knowledge

Would you like me to elaborate on any particular aspect of AI agents?
"""
    
    # LangGraph
    elif 'langgraph' in query:
        return """
# LangGraph: Building Stateful Multi-Actor Systems

LangGraph is a powerful library for creating complex, stateful applications with multiple AI agents. It's built on top of LangChain and provides a framework for orchestrating interactions between different components.

## Core Concepts:

### 1. Graph Structure
LangGraph uses a directed graph model where:
- **Nodes** are functions or agents that perform specific tasks
- **Edges** define the flow between nodes
- **State** is maintained and passed between nodes

### 2. StateGraph
The central component that:
- Manages the application's state
- Controls execution flow
- Determines when to transition between nodes

### 3. Key Features

- **First-Class State Management**: Maintain context across multiple steps
- **Conditional Edges**: Create dynamic workflows based on outputs
- **Cyclic Execution**: Allow for iterative refinement
- **Parallelism**: Run multiple nodes simultaneously
- **Checkpointing**: Save and resume execution state
- **Human-in-the-Loop**: Integrate human feedback

## Example Implementation:

```python
from langgraph.graph import StateGraph
from typing import TypedDict, Optional

# Define your state
class AgentState(TypedDict):
    input: str
    intermediate_steps: list
    output: Optional[str]

# Create a graph
graph = StateGraph(AgentState)

# Add nodes
graph.add_node("planner", planner_function)
graph.add_node("researcher", researcher_function)
graph.add_node("writer", writer_function)

# Define edges - basic linear flow
graph.add_edge("planner", "researcher")
graph.add_edge("researcher", "writer")

# Add conditional edges for complex flows
graph.add_conditional_edges(
    "writer",
    check_output_quality,
    {
        "needs_revision": "planner",  # Loop back if quality is poor
        "complete": END  # Finish if quality is good
    }
)

# Set the entry point
graph.set_entry_point("planner")

# Compile the graph
workflow = graph.compile()
```

Would you like to see more examples or learn about specific aspects of LangGraph?
"""
    
    # LangChain
    elif 'langchain' in query:
        return """
# LangChain: A Framework for LLM-Powered Applications

LangChain is an open-source framework designed to simplify the development of applications powered by large language models (LLMs). It provides a standardized interface for chains, tools, and agents.

## Core Components:

### 1. Models
- Interface with various LLMs (OpenAI, Anthropic, local models)
- Standardized inputs and outputs
- Chat models, text generation, and embeddings

### 2. Prompts
- Template management
- Dynamic prompt construction
- Example selectors for few-shot learning

### 3. Memory
- Conversation buffer memory
- Summary memory
- Entity memory
- Vector store memory

### 4. Chains
- Combine multiple components into pipelines
- Sequential chains, router chains
- Transform inputs/outputs between steps

### 5. Retrievers
- Vector stores and embeddings
- Contextual compression
- Self-querying retrievers
- Multi-vector retrievers

### 6. Tools & Agents
- Tool usage with LLMs
- Agent frameworks (ReAct, Plan-and-Execute)
- Built-in tools for web search, math, coding

## Example:

```python
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

# Create a simple chain
model = ChatOpenAI()
prompt = ChatPromptTemplate.from_template(
    "Answer the following question: {question}"
)

chain = (
    {"question": RunnablePassthrough()} 
    | prompt 
    | model 
    | StrOutputParser()
)

# Run the chain
response = chain.invoke("What is the capital of France?")
```

Would you like to explore any specific aspect of LangChain in more detail?
"""
    
    # LangSmith
    elif 'langsmith' in query:
        return """
# LangSmith: A Platform for LLM Application Development

LangSmith is a unified platform for debugging, testing, evaluating, and monitoring LLM applications. It's designed to help developers build robust AI systems more efficiently.

## Key Capabilities:

### 1. Tracing & Debugging
- Visualize execution traces of your LangChain applications
- Inspect inputs, outputs, and intermediate steps
- Track token usage and latency
- Debug complex agent workflows

### 2. Testing
- Create test datasets from production traces
- Run regression tests to prevent regressions
- Conduct A/B tests between different prompts or models
- Validate outputs against expected behaviors

### 3. Evaluation
- Automated evaluation using LLMs
- Human feedback collection
- Custom evaluation metrics
- Benchmark different approaches

### 4. Monitoring
- Track production metrics
- Set up alerts for quality issues
- Monitor costs and performance
- Analyze user interactions

## Integration:

```python
import os
from langchain.callbacks.tracers import LangSmithTracer
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Set up environment
os.environ["LANGSMITH_API_KEY"] = "your-api-key"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "My Project"

# Create components with tracing
tracer = LangSmithTracer(project_name="My Project")
model = ChatOpenAI(callbacks=[tracer])
prompt = ChatPromptTemplate.from_template("Tell me about {topic}")

# Run with tracing
response = model.invoke(prompt.format(topic="artificial intelligence"))
```

Would you like to learn more about specific LangSmith features or how to use it for particular use cases?
"""
    
    # Workflow implementation
    elif 'workflow' in query:
        return """
# Implementing AI Workflows with LangGraph

Creating effective AI workflows requires thoughtful design and architecture. Here's a comprehensive guide:

## 1. Design Your Workflow

Start by mapping out the logical flow:
- What are the key steps in your process?
- What decisions need to be made?
- Where might cycles or iterations be needed?
- What are your entry and exit conditions?

## 2. Define Your State

The state object is crucial - it carries information between nodes:

```python
from typing import TypedDict, List, Optional

class WorkflowState(TypedDict):
    # Input state
    query: str
    context: Optional[List[str]]
    
    # Intermediate state
    research_results: Optional[List[dict]]
    plan: Optional[List[str]]
    draft: Optional[str]
    
    # Output state
    final_answer: Optional[str]
    confidence_score: Optional[float]
```

## 3. Create Your Nodes

Nodes are functions that:
- Take the current state as input
- Perform some operation
- Return updates to the state

```python
def research_node(state: WorkflowState) -> dict:
    """Research information related to the query."""
    query = state["query"]
    
    # Perform research operations
    results = perform_research(query)
    
    # Return updates to state
    return {"research_results": results}

def planning_node(state: WorkflowState) -> dict:
    """Create a plan based on research."""
    research = state["research_results"]
    query = state["query"]
    
    # Generate plan based on research
    plan = create_plan(query, research)
    
    # Return updates to state
    return {"plan": plan}
```

## 4. Build Your Graph

```python
from langgraph.graph import StateGraph

# Initialize the graph
workflow = StateGraph(WorkflowState)

# Add nodes
workflow.add_node("research", research_node)
workflow.add_node("plan", planning_node)
workflow.add_node("draft", draft_node)
workflow.add_node("revise", revise_node)
workflow.add_node("finalize", finalize_node)

# Add basic edges
workflow.add_edge("research", "plan")
workflow.add_edge("plan", "draft")

# Add conditional edges
workflow.add_conditional_edges(
    "draft",
    evaluate_draft_quality,
    {
        "needs_revision": "revise",
        "acceptable": "finalize"
    }
)

workflow.add_edge("revise", "draft")  # Create a cycle for revision

# Set entry point
workflow.set_entry_point("research")

# Compile
app = workflow.compile()
```

## 5. Execute Your Workflow

```python
# Run the workflow
result = app.invoke({
    "query": "Explain the impact of quantum computing on cryptography",
    "context": ["Recent developments in quantum algorithms", "Post-quantum cryptography"]
})

print(result["final_answer"])
```

## 6. Advanced Techniques

- **Parallelism**: Run multiple nodes simultaneously
- **Checkpointing**: Save workflow state for resuming later
- **Human-in-the-loop**: Add human approval/feedback steps
- **Tool integration**: Connect to external APIs and services
- **Nested workflows**: Create workflows that call other workflows

Would you like me to elaborate on any specific aspect of workflow implementation?
"""

    # Catch-all for other queries
    else:
        responses = [
            f"I'd be happy to discuss {query} in detail. Could you specify what aspect you're most interested in?",
            f"Regarding {query}, there are several important considerations. What specific information are you looking for?",
            f"{query} is an interesting topic. To provide the most helpful response, could you share what you already know or what you're trying to accomplish?",
            f"I can provide information about {query}. Would you like a general overview or something more specific?"
        ]
        return random.choice(responses)

def display_thinking_animation(duration=1.5):
    """Display a thinking animation for a specified duration"""
    thinking_frames = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
    end_time = time.time() + duration
    
    print("Thinking ", end="", flush=True)
    while time.time() < end_time:
        for frame in thinking_frames:
            print(f"\rThinking {frame}", end="", flush=True)
            time.sleep(0.1)
            if time.time() >= end_time:
                break
    
    print("\r" + " " * 20 + "\r", end="", flush=True)

def main():
    """Main function to run the standalone assistant"""
    display_header()
    
    print("\nWelcome to the Jarvis AI Standalone Assistant!")
    print("Ask me anything about AI, programming, or the Lang ecosystem.")
    print("Type 'exit', 'quit', or 'bye' to end the session.\n")
    
    while True:
        # Get user input
        user_input = input("\n🔍 Ask Jarvis: ").strip()
        
        if not user_input:
            continue
            
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("\n👋 Thank you for using Jarvis AI! Have a great day!")
            break
            
        # Display thinking animation
        display_thinking_animation()
        
        # Get and display response
        response = get_ai_response(user_input)
        print(f"\n{response}")

if __name__ == "__main__":
    main()
