#!/usr/bin/env python3
"""
LangChain Tools integration for Jarvis AI.

This module creates LangChain Tool wrappers around existing Jarvis AI functionality,
enabling seamless integration with the Lang family ecosystem while preserving
existing functionality.
"""

from typing import Any, Dict, List, Optional
import json

try:
    from langchain.tools import Tool
    from langchain.agents import AgentType
    from langchain_core.tools import BaseTool
    from pydantic import BaseModel, Field
    LANGCHAIN_AVAILABLE = True
except ImportError:
    # Fallback classes when LangChain is not available
    class Tool:
        def __init__(self, **kwargs):
            pass
    
    class BaseTool:
        def __init__(self, **kwargs):
            pass
    
    class BaseModel:
        def __init__(self, **kwargs):
            pass
        
    class Field:
        def __init__(self, default=None, **kwargs):
            self.default = default
    
    def Field(default=None, **kwargs):
        return default
    
    LANGCHAIN_AVAILABLE = False

# Import existing Jarvis AI tools
import agent.tools as jarvis_tools
import agent.features.rag_handler as rag_handler
import agent.features.code_review as code_review
import agent.features.code_search as code_search
import agent.features.repo_context as repo_context


class JarvisToolWrapper(BaseTool):
    """Base wrapper class for converting Jarvis AI tools to LangChain Tools."""
    
    def __init__(self, name: str, description: str, jarvis_tool: str, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.description = description
        self.jarvis_tool = jarvis_tool
    
    def _run(self, **kwargs) -> str:
        """Execute the wrapped Jarvis tool."""
        if not LANGCHAIN_AVAILABLE:
            return "LangChain not available - falling back to direct execution"
        
        try:
            # Convert kwargs to Jarvis tool format
            step = {
                "tool": self.jarvis_tool,
                "args": kwargs
            }
            
            # Execute using existing Jarvis tools system
            result = jarvis_tools.run_tool(step)
            
            # Convert result to string for LangChain compatibility
            if isinstance(result, dict):
                return json.dumps(result, indent=2)
            elif isinstance(result, list):
                return "\n".join(str(item) for item in result)
            else:
                return str(result)
                
        except Exception as e:
            return f"Error executing {self.jarvis_tool}: {str(e)}"


class FileIngestTool(JarvisToolWrapper):
    """LangChain tool for file ingestion."""
    
    def __init__(self):
        super().__init__(
            name="file_ingest",
            description="Ingest and process files for analysis. Takes a list of file paths.",
            jarvis_tool="file_ingest"
        )
    
    def _run(self, files: List[str]) -> str:
        """Ingest files for processing."""
        return super()._run(files=files)


class CodeReviewTool(JarvisToolWrapper):
    """LangChain tool for code review."""
    
    def __init__(self):
        super().__init__(
            name="code_review",
            description="Review code for quality, style, and potential issues. Takes file_path and optional check_types.",
            jarvis_tool="code_review"
        )
    
    def _run(self, file_path: str, check_types: Optional[List[str]] = None) -> str:
        """Review code file."""
        return super()._run(file_path=file_path, check_types=check_types)


class CodeSearchTool(JarvisToolWrapper):
    """LangChain tool for code search."""
    
    def __init__(self):
        super().__init__(
            name="code_search",
            description="Search for code patterns, functions, or text in repositories.",
            jarvis_tool="code_search"
        )
    
    def _run(self, query: str, repository_path: Optional[str] = None, 
             search_type: str = "all", case_sensitive: bool = False, regex: bool = False) -> str:
        """Search code."""
        return super()._run(
            query=query, 
            repository_path=repository_path,
            search_type=search_type,
            case_sensitive=case_sensitive,
            regex=regex
        )


class RAGTool(JarvisToolWrapper):
    """LangChain tool for RAG (Retrieval Augmented Generation)."""
    
    def __init__(self):
        super().__init__(
            name="rag_query",
            description="Query knowledge base using RAG. Takes prompt, files, and optional parameters.",
            jarvis_tool="llm_rag"
        )
    
    def _run(self, prompt: str, files: Optional[List[str]] = None, 
             mode: str = "file", chat_history: Optional[List] = None) -> str:
        """Execute RAG query."""
        return super()._run(
            prompt=prompt,
            files=files or [],
            mode=mode,
            chat_history=chat_history or []
        )


class RepoContextTool(JarvisToolWrapper):
    """LangChain tool for repository context analysis."""
    
    def __init__(self):
        super().__init__(
            name="repo_context",
            description="Analyze repository structure and context. Takes repository_path.",
            jarvis_tool="repo_context"
        )
    
    def _run(self, repository_path: str) -> str:
        """Get repository context."""
        return super()._run(repository_path=repository_path)


class CheckOllamaStatusTool(BaseTool):
    """LangChain tool for checking Ollama status - system monitoring."""
    
    def __init__(self):
        super().__init__()
        self.name = "check_ollama_status"
        self.description = "Check if Ollama service is running and accessible for LLM operations."
    
    def _run(self) -> str:
        """Check Ollama status."""
        try:
            import requests
            import os
            
            # Try to connect to Ollama
            ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
            response = requests.get(f"{ollama_host}/api/tags", timeout=5)
            
            if response.status_code == 200:
                models = response.json().get("models", [])
                return f"Ollama is running. Available models: {len(models)}"
            else:
                return f"Ollama responded with status {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return "Ollama is not accessible - service may be down"
        except requests.exceptions.Timeout:
            return "Ollama connection timed out"
        except Exception as e:
            return f"Error checking Ollama status: {str(e)}"


def create_langchain_tools() -> List[BaseTool]:
    """Create all LangChain tools from Jarvis AI functionality."""
    
    if not LANGCHAIN_AVAILABLE:
        print("Warning: LangChain not available, returning empty tools list")
        return []
    
    tools = [
        FileIngestTool(),
        CodeReviewTool(),
        CodeSearchTool(), 
        RAGTool(),
        RepoContextTool(),
        CheckOllamaStatusTool()
    ]
    
    return tools


def get_tool_by_name(name: str) -> Optional[BaseTool]:
    """Get a specific tool by name."""
    tools = create_langchain_tools()
    for tool in tools:
        if tool.name == name:
            return tool
    return None


# Legacy function to maintain backwards compatibility
def preview_tool_action(step):
    """Preview a tool action - maintains compatibility with existing code."""
    return jarvis_tools.preview_tool_action(step)


def run_tool(step, expert_model=None, draft_model=None, user=None):
    """Run a tool - maintains compatibility with existing code.""" 
    return jarvis_tools.run_tool(step, expert_model, draft_model, user)