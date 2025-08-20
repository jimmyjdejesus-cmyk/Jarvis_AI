#!/usr/bin/env python3
"""
Enhanced Agentic Workflow Setup for Jarvis AI
Sets up all necessary components for building real agentic workflows.
"""

import os
import subprocess
import sys
from pathlib import Path

def setup_llm_providers():
    """Setup and configure LLM providers."""
    print("🤖 Setting up LLM Providers...")
    
    # Check for API keys
    providers = {
        "OpenAI": "OPENAI_API_KEY",
        "Anthropic": "ANTHROPIC_API_KEY", 
        "LangSmith": "LANGSMITH_API_KEY"
    }
    
    configured = []
    for provider, env_var in providers.items():
        if os.getenv(env_var):
            configured.append(provider)
            print(f"✅ {provider} configured")
        else:
            print(f"⚠️  {provider} not configured (set {env_var})")
    
    if not configured:
        print("\n🔧 Setting up Ollama for local LLM...")
        setup_ollama()
    
    return configured

def setup_ollama():
    """Setup Ollama for local LLM usage."""
    try:
        # Check if Ollama is installed
        subprocess.run(["ollama", "--version"], check=True, capture_output=True)
        print("✅ Ollama is installed")
        
        # Pull a lightweight model for testing
        print("📥 Pulling llama3.2 model...")
        subprocess.run(["ollama", "pull", "llama3.2"], check=True)
        print("✅ Ollama model ready")
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Ollama not found. Please install from https://ollama.ai/download")
        print("Then run: ollama pull llama3.2")

def install_enhanced_dependencies():
    """Install additional dependencies for agentic workflows."""
    print("📦 Installing enhanced dependencies...")
    
    enhanced_packages = [
        "langchain-openai",          # OpenAI integration
        "langchain-anthropic",       # Claude integration
        "langchain-experimental",    # Latest experimental features
        "langchain-community",       # Community tools
        "langgraph-checkpoint",      # Persistent memory
        "faiss-cpu",                # Vector storage
        "chromadb",                 # Alternative vector DB
        "beautifulsoup4",           # Web scraping
        "selenium",                 # Browser automation
        "requests-html",            # Enhanced web requests
        "python-dotenv",            # Environment management
        "asyncio",                  # Async support
        "aiohttp",                  # Async HTTP
        "sqlalchemy",               # Database ORM
        "redis",                    # Caching and queues
        "celery",                   # Task queues
        "schedule",                 # Job scheduling
    ]
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", *enhanced_packages
        ])
        print("✅ Enhanced dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install enhanced dependencies: {e}")

def create_agentic_config():
    """Create configuration for agentic workflows."""
    print("⚙️ Creating agentic workflow configuration...")
    
    config_content = """# Jarvis AI Agentic Workflow Configuration

# LLM Configuration
llm:
  primary_provider: "openai"  # or "anthropic" or "ollama"
  fallback_provider: "ollama"
  temperature: 0.1
  max_tokens: 4000
  
# Workflow Configuration  
workflows:
  max_iterations: 10
  enable_human_feedback: true
  auto_save_checkpoints: true
  parallel_execution: true
  
# Tool Configuration
tools:
  web_search: true
  code_execution: true
  file_operations: true
  git_operations: true
  database_operations: false
  api_integrations: true
  
# Memory Configuration
memory:
  provider: "sqlite"  # or "redis" for production
  persist_conversations: true
  max_history_length: 100
  
# Monitoring
monitoring:
  langsmith_enabled: true
  log_level: "INFO"
  metrics_enabled: true
  
# Security
security:
  sandbox_code_execution: true
  restrict_file_access: true
  allowed_domains: []
  max_execution_time: 300
"""
    
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    with open(config_dir / "agentic_config.yaml", "w") as f:
        f.write(config_content)
    
    print("✅ Agentic configuration created")

def create_workflow_templates():
    """Create example workflow templates."""
    print("📝 Creating workflow templates...")
    
    templates_dir = Path("workflow_templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Research Workflow Template
    research_workflow = '''"""
Research Agent Workflow Template
Comprehensive research and analysis workflow.
"""

from typing import Dict, List, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

class ResearchState:
    query: str
    sources: List[str] = []
    research_data: Dict[str, Any] = {}
    analysis: str = ""
    final_report: str = ""
    iteration_count: int = 0

def create_research_workflow():
    """Create a research workflow with planning, data gathering, analysis."""
    
    workflow = StateGraph(ResearchState)
    
    # Add nodes
    workflow.add_node("planner", plan_research)
    workflow.add_node("searcher", gather_data)
    workflow.add_node("analyzer", analyze_data)
    workflow.add_node("reporter", generate_report)
    workflow.add_node("reviewer", review_quality)
    
    # Add edges
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "searcher")
    workflow.add_edge("searcher", "analyzer")
    workflow.add_edge("analyzer", "reporter")
    workflow.add_conditional_edges(
        "reviewer",
        should_continue_research,
        {
            "continue": "searcher",
            "complete": END
        }
    )
    
    return workflow.compile()

def plan_research(state: ResearchState) -> ResearchState:
    """Plan the research approach."""
    # Implementation here
    return state

def gather_data(state: ResearchState) -> ResearchState:
    """Gather data from various sources."""
    # Implementation here
    return state
    
# Add more functions...
'''
    
    with open(templates_dir / "research_workflow.py", "w") as f:
        f.write(research_workflow)
    
    # Code Generation Workflow
    code_workflow = '''"""
Code Generation Agent Workflow
Handles code analysis, generation, testing, and deployment.
"""

from langgraph.graph import StateGraph, END

class CodeState:
    requirements: str
    design: str = ""
    code: str = ""
    tests: str = ""
    review_feedback: str = ""
    deployment_ready: bool = False

def create_code_workflow():
    """Create a code generation workflow."""
    
    workflow = StateGraph(CodeState)
    
    workflow.add_node("architect", design_solution)
    workflow.add_node("coder", generate_code)
    workflow.add_node("tester", create_tests)
    workflow.add_node("reviewer", review_code)
    workflow.add_node("deployer", prepare_deployment)
    
    # Add workflow logic...
    
    return workflow.compile()

# Implement node functions...
'''
    
    with open(templates_dir / "code_workflow.py", "w") as f:
        f.write(code_workflow)
    
    print("✅ Workflow templates created")

def create_agent_examples():
    """Create example agent implementations."""
    print("🤖 Creating agent examples...")
    
    examples_dir = Path("agent_examples")
    examples_dir.mkdir(exist_ok=True)
    
    # Multi-Agent System Example
    multi_agent = '''"""
Multi-Agent System Example
Shows how to coordinate multiple specialized agents.
"""

from langgraph.graph import StateGraph
from typing import Dict, List

class MultiAgentState:
    task: str
    specialist_results: Dict[str, str] = {}
    coordinator_decision: str = ""
    final_output: str = ""

class SpecialistAgent:
    """Base class for specialist agents."""
    
    def __init__(self, specialty: str):
        self.specialty = specialty
    
    def process(self, task: str) -> str:
        """Process task according to specialty."""
        pass

class ResearchAgent(SpecialistAgent):
    """Agent specialized in research and data gathering."""
    
    def process(self, task: str) -> str:
        # Research implementation
        return f"Research results for: {task}"

class AnalysisAgent(SpecialistAgent):
    """Agent specialized in data analysis."""
    
    def process(self, task: str) -> str:
        # Analysis implementation
        return f"Analysis results for: {task}"

class CoordinatorAgent:
    """Coordinates multiple specialist agents."""
    
    def __init__(self):
        self.specialists = {
            "research": ResearchAgent("research"),
            "analysis": AnalysisAgent("analysis"),
        }
    
    def coordinate(self, state: MultiAgentState) -> MultiAgentState:
        """Coordinate specialists based on task requirements."""
        # Coordination logic
        return state

def create_multi_agent_system():
    """Create a multi-agent coordination system."""
    
    workflow = StateGraph(MultiAgentState)
    
    coordinator = CoordinatorAgent()
    
    workflow.add_node("coordinator", coordinator.coordinate)
    workflow.add_node("research_specialist", run_research_specialist)
    workflow.add_node("analysis_specialist", run_analysis_specialist)
    workflow.add_node("synthesizer", synthesize_results)
    
    # Add coordination logic...
    
    return workflow.compile()
'''
    
    with open(examples_dir / "multi_agent_system.py", "w") as f:
        f.write(multi_agent)
    
    print("✅ Agent examples created")

def setup_environment_file():
    """Create .env template for configuration."""
    print("🔧 Creating environment template...")
    
    env_content = """# Jarvis AI Environment Configuration
# Copy this to .env and fill in your values

# LLM API Keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# LangSmith (Recommended for monitoring)
LANGSMITH_API_KEY=your_langsmith_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=jarvis-workflows

# Ollama Configuration (for local LLMs)
OLLAMA_HOST=http://localhost:11434

# Database Configuration
DATABASE_URL=sqlite:///jarvis.db
REDIS_URL=redis://localhost:6379

# Workflow Configuration
MAX_WORKFLOW_ITERATIONS=10
ENABLE_HUMAN_FEEDBACK=true
AUTO_SAVE_CHECKPOINTS=true

# Security
SANDBOX_MODE=true
MAX_EXECUTION_TIME=300
ALLOWED_DOMAINS=github.com,stackoverflow.com,docs.python.org

# Debug
DEBUG_MODE=false
LOG_LEVEL=INFO
"""
    
    with open(".env.template", "w") as f:
        f.write(env_content)
    
    print("✅ Environment template created")
    print("📝 Copy .env.template to .env and configure your API keys")

def main():
    """Main setup function."""
    print("🚀 Setting up Jarvis AI for Agentic Workflows")
    print("=" * 50)
    
    # Setup steps
    setup_llm_providers()
    install_enhanced_dependencies()
    create_agentic_config()
    create_workflow_templates()
    create_agent_examples()
    setup_environment_file()
    
    print("\n" + "=" * 50)
    print("✅ Agentic workflow setup complete!")
    print("\n🎯 Next Steps:")
    print("1. Configure your API keys in .env file")
    print("2. Review config/agentic_config.yaml")
    print("3. Explore workflow_templates/ for examples")
    print("4. Check agent_examples/ for multi-agent patterns")
    print("5. Run: python -c 'from jarvis_ai import test_workflow; test_workflow()'")
    
if __name__ == "__main__":
    main()
