"""
LangChain-compatible tools for Jarvis AI V2

This module converts existing Jarvis AI tools to LangChain format using the @tool decorator.
All tools include detailed docstrings for the agent to understand when to use them.
"""

import os
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
import json

try:
    from langchain_core.tools import tool
    LANGCHAIN_AVAILABLE = True
except ImportError:
    # Fallback decorator when LangChain is not available
    def tool(func):
        func._is_tool = True
        return func
    LANGCHAIN_AVAILABLE = False


# File System Tools
@tool
def list_files(directory: str) -> str:
    """
    List files and directories in the specified directory.
    
    Args:
        directory: Path to the directory to list
        
    Returns:
        String containing the list of files and directories
    """
    try:
        path = Path(directory)
        if not path.exists():
            return f"Error: Directory '{directory}' does not exist"
        
        if not path.is_dir():
            return f"Error: '{directory}' is not a directory"
        
        items = []
        for item in sorted(path.iterdir()):
            if item.is_dir():
                items.append(f"📁 {item.name}/")
            else:
                size = item.stat().st_size
                items.append(f"📄 {item.name} ({size} bytes)")
        
        return f"Contents of '{directory}':\n" + "\n".join(items)
    
    except Exception as e:
        return f"Error listing directory '{directory}': {str(e)}"


@tool
def read_file(path: str) -> str:
    """
    Read the contents of a file.
    
    Args:
        path: Path to the file to read
        
    Returns:
        String containing the file contents or error message
    """
    try:
        file_path = Path(path)
        if not file_path.exists():
            return f"Error: File '{path}' does not exist"
        
        if not file_path.is_file():
            return f"Error: '{path}' is not a file"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return f"Contents of '{path}':\n{content}"
    
    except Exception as e:
        return f"Error reading file '{path}': {str(e)}"


@tool
def write_file(path: str, content: str) -> str:
    """
    Write content to a file. Creates directories if they don't exist.
    
    Args:
        path: Path to the file to write
        content: Content to write to the file
        
    Returns:
        Success or error message
    """
    try:
        file_path = Path(path)
        
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"Successfully wrote {len(content)} characters to '{path}'"
    
    except Exception as e:
        return f"Error writing file '{path}': {str(e)}"


@tool
def read_legacy_file(path: str) -> str:
    """
    Read a file from the legacy 'old/' directory for reference.
    Used during V1 to V2 migration to access archived functionality.
    
    Args:
        path: Path to the file relative to the old/ directory
        
    Returns:
        String containing the file contents or error message
    """
    try:
        # Prepend 'old/' to the path
        legacy_path = Path("old") / path
        
        if not legacy_path.exists():
            return f"Error: Legacy file 'old/{path}' does not exist"
        
        with open(legacy_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return f"Legacy file contents of 'old/{path}':\n{content}"
    
    except Exception as e:
        return f"Error reading legacy file 'old/{path}': {str(e)}"


# Code Execution Tools
@tool
def run_pytest() -> str:
    """
    Run pytest to execute all tests in the current project.
    
    Returns:
        String containing pytest output and results
    """
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        output = f"Exit code: {result.returncode}\n"
        output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
        
        return output
    
    except subprocess.TimeoutExpired:
        return "Error: pytest timed out after 5 minutes"
    except FileNotFoundError:
        return "Error: pytest not found. Make sure pytest is installed."
    except Exception as e:
        return f"Error running pytest: {str(e)}"


@tool
def lint_file(path: str) -> str:
    """
    Run linting checks on a Python file using flake8.
    
    Args:
        path: Path to the Python file to lint
        
    Returns:
        String containing linting results
    """
    try:
        file_path = Path(path)
        if not file_path.exists():
            return f"Error: File '{path}' does not exist"
        
        if not file_path.suffix == '.py':
            return f"Warning: '{path}' is not a Python file"
        
        # Try flake8 first, then fallback to basic syntax check
        try:
            result = subprocess.run(
                ["flake8", str(file_path)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return f"✅ No linting issues found in '{path}'"
            else:
                return f"Linting issues in '{path}':\n{result.stdout}"
                
        except FileNotFoundError:
            # Fallback to syntax check if flake8 not available
            try:
                with open(file_path, 'r') as f:
                    compile(f.read(), file_path, 'exec')
                return f"✅ No syntax errors found in '{path}' (basic check)"
            except SyntaxError as e:
                return f"Syntax error in '{path}': {str(e)}"
    
    except Exception as e:
        return f"Error linting file '{path}': {str(e)}"


# Version Control Tools
@tool
def git_status() -> str:
    """
    Get the current git status of the repository.
    
    Returns:
        String containing git status output
    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            if result.stdout.strip():
                return f"Git status:\n{result.stdout}"
            else:
                return "Git status: Working directory clean"
        else:
            return f"Git error: {result.stderr}"
    
    except subprocess.TimeoutExpired:
        return "Error: git status timed out"
    except FileNotFoundError:
        return "Error: git not found. Make sure git is installed."
    except Exception as e:
        return f"Error getting git status: {str(e)}"


@tool
def git_commit(message: str) -> str:
    """
    Commit changes to git with the specified message.
    
    Args:
        message: Commit message
        
    Returns:
        String containing commit result
    """
    try:
        # First, add all changes
        add_result = subprocess.run(
            ["git", "add", "."],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if add_result.returncode != 0:
            return f"Error adding files: {add_result.stderr}"
        
        # Then commit
        commit_result = subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if commit_result.returncode == 0:
            return f"Successfully committed with message: '{message}'\n{commit_result.stdout}"
        else:
            return f"Commit failed: {commit_result.stderr}"
    
    except subprocess.TimeoutExpired:
        return "Error: git commit timed out"
    except FileNotFoundError:
        return "Error: git not found. Make sure git is installed."
    except Exception as e:
        return f"Error committing changes: {str(e)}"


@tool
def github_create_pr(title: str, body: str) -> str:
    """
    Create a GitHub pull request. Requires gh CLI to be installed and authenticated.
    
    Args:
        title: Title of the pull request
        body: Body/description of the pull request
        
    Returns:
        String containing PR creation result
    """
    try:
        result = subprocess.run(
            ["gh", "pr", "create", "--title", title, "--body", body],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            return f"Successfully created PR: '{title}'\n{result.stdout}"
        else:
            return f"Failed to create PR: {result.stderr}"
    
    except subprocess.TimeoutExpired:
        return "Error: gh pr create timed out"
    except FileNotFoundError:
        return "Error: gh CLI not found. Install GitHub CLI and authenticate."
    except Exception as e:
        return f"Error creating PR: {str(e)}"


# System Monitoring Tools
@tool
def check_ollama_status() -> str:
    """
    Check if Ollama is running and accessible.
    
    Returns:
        String containing Ollama status information
    """
    try:
        import requests
        
        # Try to connect to Ollama API
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [m.get('name', 'unknown') for m in models]
            return f"✅ Ollama is running with {len(models)} models: {', '.join(model_names)}"
        else:
            return f"❌ Ollama responded with status {response.status_code}"
    
    except requests.exceptions.ConnectionError:
        return "❌ Ollama is not running or not accessible at localhost:11434"
    except requests.exceptions.Timeout:
        return "❌ Ollama connection timed out"
    except Exception as e:
        return f"❌ Error checking Ollama status: {str(e)}"


# Web Search Tool (using existing implementation)
@tool
def web_search(query: str) -> str:
    """
    Search the web using DuckDuckGo and return relevant results.
    
    Args:
        query: Search query string
        
    Returns:
        String containing search results
    """
    try:
        from duckduckgo_search import DDGS
        
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        
        if not results:
            return f"No search results found for query: '{query}'"
        
        output = f"Search results for '{query}':\n\n"
        for i, result in enumerate(results, 1):
            output += f"{i}. {result.get('title', 'No title')}\n"
            output += f"   URL: {result.get('href', 'No URL')}\n"
            output += f"   {result.get('body', 'No description')}\n\n"
        
        return output
    
    except ImportError:
        return "Error: duckduckgo-search not installed. Install with: pip install duckduckgo-search"
    except Exception as e:
        return f"Error performing web search: {str(e)}"


# IDE Integration Tools (placeholder implementations)
@tool
def ide_get_open_file_path() -> str:
    """
    Get the path of the currently open file in the IDE.
    Note: This is a placeholder implementation. Real implementation would
    require IDE-specific plugins or APIs.
    
    Returns:
        String containing the file path or error message
    """
    return "IDE integration not implemented. Requires custom IDE plugins."


@tool
def ide_insert_text(text: str) -> str:
    """
    Insert text at the current cursor position in the IDE.
    
    Args:
        text: Text to insert
        
    Returns:
        String containing result of the operation
    """
    return f"IDE integration not implemented. Would insert: '{text[:50]}...'"


# Note-taking Integration Tools (placeholder implementations)
@tool
def onenote_create_page(section: str, title: str, content: str) -> str:
    """
    Create a new page in OneNote.
    
    Args:
        section: OneNote section name
        title: Page title
        content: Page content
        
    Returns:
        String containing result of the operation
    """
    return f"OneNote integration not implemented. Would create page '{title}' in section '{section}'"


@tool
def goodnotes_create_note(notebook: str, content: str) -> str:
    """
    Create a new note in GoodNotes.
    
    Args:
        notebook: GoodNotes notebook name
        content: Note content
        
    Returns:
        String containing result of the operation
    """
    return f"GoodNotes integration not implemented. Would create note in notebook '{notebook}'"


# Collect all tools
ALL_TOOLS = [
    list_files,
    read_file,
    write_file,
    read_legacy_file,
    run_pytest,
    lint_file,
    git_status,
    git_commit,
    github_create_pr,
    check_ollama_status,
    web_search,
    ide_get_open_file_path,
    ide_insert_text,
    onenote_create_page,
    goodnotes_create_note,
]


def get_available_tools() -> List:
    """
    Get list of all available LangChain tools.
    
    Returns:
        List of tool functions decorated with @tool
    """
    return ALL_TOOLS


def get_tool_by_name(name: str):
    """
    Get a specific tool by name.
    
    Args:
        name: Name of the tool function
        
    Returns:
        Tool function or None if not found
    """
    for tool_func in ALL_TOOLS:
        if tool_func.__name__ == name:
            return tool_func
    return None


def get_tools_description() -> str:
    """
    Get a description of all available tools.
    
    Returns:
        String containing descriptions of all tools
    """
    descriptions = []
    for tool_func in ALL_TOOLS:
        doc = tool_func.__doc__ or "No description available"
        descriptions.append(f"- {tool_func.__name__}: {doc.split('.')[0]}.")
    
    return "Available tools:\n" + "\n".join(descriptions)