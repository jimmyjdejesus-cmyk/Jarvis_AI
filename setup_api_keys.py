#!/usr/bin/env python3
"""
API Key Setup Guide for Jarvis AI Agentic Workflows
"""

import os
import json
from pathlib import Path

def create_env_template():
    """Create a .env template file with all required API keys."""
    
    env_template = """# Jarvis AI - API Keys Configuration
# Copy this file to .env and fill in your actual API keys

# =============================================================================
# LLM PROVIDERS (Choose at least one)
# =============================================================================

# OpenAI (Recommended for production workflows)
# Get key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_key_here

# Anthropic Claude (Great for reasoning tasks)
# Get key from: https://console.anthropic.com/
ANTHROPIC_API_KEY=your_anthropic_key_here

# Google Gemini (Alternative option)
# Get key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_google_key_here

# =============================================================================
# LANGCHAIN ECOSYSTEM
# =============================================================================

# LangSmith (Highly recommended for monitoring & debugging)
# Get key from: https://smith.langchain.com/
LANGSMITH_API_KEY=your_langsmith_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=jarvis-workflows

# LangChain Hub (Optional - for shared prompts)
LANGCHAIN_HUB_API_KEY=your_langsmith_key_here

# =============================================================================
# EXTERNAL SERVICES (Optional but useful for real workflows)
# =============================================================================

# Tavily Search (For web search capabilities)
# Get key from: https://tavily.com/
TAVILY_API_KEY=your_tavily_key_here

# Serper (Alternative search provider)
# Get key from: https://serper.dev/
SERPER_API_KEY=your_serper_key_here

# Weather API (for weather-related workflows)
# Get key from: https://openweathermap.org/api
OPENWEATHER_API_KEY=your_weather_key_here

# =============================================================================
# VECTOR DATABASES (Optional for RAG workflows)
# =============================================================================

# Pinecone (Managed vector database)
# Get key from: https://www.pinecone.io/
PINECONE_API_KEY=your_pinecone_key_here
PINECONE_ENVIRONMENT=your_pinecone_env_here

# Weaviate (Alternative vector database)
# Get key from: https://console.weaviate.cloud/
WEAVIATE_API_KEY=your_weaviate_key_here
WEAVIATE_URL=your_weaviate_url_here

# =============================================================================
# LOCAL OPTIONS (No API keys needed)
# =============================================================================

# Ollama (For local LLMs - no API key required)
# Download from: https://ollama.ai/
OLLAMA_BASE_URL=http://localhost:11434

# Local vector database (ChromaDB - no API key required)
# Will be used automatically if no other vector DB is configured
"""
    
    # Write the template
    with open('.env.template', 'w') as f:
        f.write(env_template)
    
    print("✅ Created .env.template file")
    print("📝 Copy this to .env and fill in your API keys")

def check_current_keys():
    """Check which API keys are currently available."""
    
    print("\n🔍 Checking current API key status...")
    
    # LLM Providers
    llm_keys = {
        'OpenAI': os.getenv('OPENAI_API_KEY'),
        'Anthropic': os.getenv('ANTHROPIC_API_KEY'),
        'Google': os.getenv('GOOGLE_API_KEY'),
    }
    
    # LangChain
    langchain_keys = {
        'LangSmith': os.getenv('LANGSMITH_API_KEY'),
        'LangChain Tracing': os.getenv('LANGCHAIN_TRACING_V2'),
        'LangChain Project': os.getenv('LANGCHAIN_PROJECT'),
    }
    
    # External Services
    external_keys = {
        'Tavily Search': os.getenv('TAVILY_API_KEY'),
        'Serper': os.getenv('SERPER_API_KEY'),
        'OpenWeather': os.getenv('OPENWEATHER_API_KEY'),
    }
    
    # Vector Databases
    vector_keys = {
        'Pinecone': os.getenv('PINECONE_API_KEY'),
        'Weaviate': os.getenv('WEAVIATE_API_KEY'),
    }
    
    print("\n📊 API Key Status Report:")
    print("=" * 50)
    
    print("\n🤖 LLM Providers:")
    for name, key in llm_keys.items():
        status = "✅ Set" if key else "❌ Missing"
        print(f"  {name}: {status}")
    
    print("\n🔗 LangChain Ecosystem:")
    for name, key in langchain_keys.items():
        status = "✅ Set" if key else "❌ Missing"
        print(f"  {name}: {status}")
    
    print("\n🌐 External Services:")
    for name, key in external_keys.items():
        status = "✅ Set" if key else "❌ Missing"
        print(f"  {name}: {status}")
    
    print("\n📚 Vector Databases:")
    for name, key in vector_keys.items():
        status = "✅ Set" if key else "❌ Missing"
        print(f"  {name}: {status}")
    
    # Check Ollama
    print("\n🏠 Local Options:")
    ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    print(f"  Ollama URL: {ollama_url}")
    
    return any(llm_keys.values())

def create_minimal_setup_guide():
    """Create a guide for minimal setup to get started."""
    
    guide = """# 🚀 Quick Start Guide for Jarvis AI Agentic Workflows

## Option 1: Free/Local Setup (No API keys required)

1. **Install Ollama** (Local LLM)
   ```bash
   # Download from: https://ollama.ai/
   # Then run:
   ollama pull llama2
   # or
   ollama pull codellama
   ```

2. **Set environment variables:**
   ```bash
   export OLLAMA_BASE_URL=http://localhost:11434
   ```

3. **Ready to build workflows!** 
   - No API costs
   - Works offline
   - Good for development and testing

## Option 2: Production Setup (Recommended)

1. **Get LangSmith API Key** (Free tier available)
   - Go to: https://smith.langchain.com/
   - Sign up and get your API key
   - Set these environment variables:
   ```bash
   export LANGSMITH_API_KEY=your_key_here
   export LANGCHAIN_TRACING_V2=true
   export LANGCHAIN_PROJECT=jarvis-workflows
   ```

2. **Get an LLM Provider Key** (Choose one):
   
   **OpenAI** (Most reliable, paid):
   ```bash
   export OPENAI_API_KEY=your_key_here
   ```
   
   **Anthropic Claude** (Great for reasoning, paid):
   ```bash
   export ANTHROPIC_API_KEY=your_key_here
   ```

3. **Optional: Add search capabilities**
   ```bash
   # Tavily (free tier available)
   export TAVILY_API_KEY=your_key_here
   ```

## Option 3: Full Featured Setup

Follow Option 2, then add:
- Vector database (Pinecone/Weaviate)
- Additional external services
- Weather, news, and other APIs

## 🎯 What Each Service Provides:

- **LangSmith**: Workflow monitoring, debugging, A/B testing
- **OpenAI/Anthropic**: High-quality LLM responses
- **Tavily/Serper**: Web search capabilities for agents
- **Pinecone/Weaviate**: Vector storage for RAG workflows
- **Ollama**: Local LLMs (free, private, offline)

## 💡 Recommendation for Beginners:

Start with **Option 1** (Ollama + local setup) to learn workflow basics, then upgrade to **Option 2** when you need production features.
"""
    
    with open('AGENTIC_WORKFLOWS_SETUP.md', 'w') as f:
        f.write(guide)
    
    print("✅ Created AGENTIC_WORKFLOWS_SETUP.md")

def main():
    """Main setup function."""
    print("🔧 Jarvis AI - Agentic Workflows Setup")
    print("=" * 50)
    
    # Create template and guide
    create_env_template()
    create_minimal_setup_guide()
    
    # Check current status
    has_llm_key = check_current_keys()
    
    print("\n📋 Next Steps:")
    if not has_llm_key:
        print("1. Choose your setup option from AGENTIC_WORKFLOWS_SETUP.md")
        print("2. For local setup: Install Ollama from https://ollama.ai/")
        print("3. For cloud setup: Get API keys and update .env file")
        print("4. Run 'python setup_agentic_workflows.py' to install workflow tools")
    else:
        print("1. You have LLM access configured!")
        print("2. Consider adding LangSmith for monitoring")
        print("3. Run 'python setup_agentic_workflows.py' to install workflow tools")
    
    print("\n🎯 Ready to build agentic workflows!")

if __name__ == "__main__":
    main()
