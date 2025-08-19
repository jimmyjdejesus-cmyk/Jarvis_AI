#!/usr/bin/env python3
"""
Custom DocumentLoader classes for Jarvis AI proprietary knowledge sources.

This module provides LangChain-compatible document loaders for various
knowledge sources used by Jarvis AI.
"""

from typing import Any, Dict, List, Optional, Iterator
import os
import json
from pathlib import Path

try:
    from langchain.docstore.document import Document
    from langchain.document_loaders.base import BaseLoader
    from langchain_core.documents import Document as CoreDocument
    LANGCHAIN_AVAILABLE = True
except ImportError:
    # Fallback when LangChain is not available
    LANGCHAIN_AVAILABLE = False
    
    class Document:
        def __init__(self, page_content: str, metadata: Dict[str, Any] = None):
            self.page_content = page_content
            self.metadata = metadata or {}
    
    class BaseLoader:
        def load(self) -> List[Document]:
            return []


class JarvisKnowledgeLoader(BaseLoader):
    """Loader for Jarvis AI's internal knowledge base."""
    
    def __init__(self, knowledge_path: str = "data/knowledge"):
        """Initialize the knowledge loader."""
        self.knowledge_path = Path(knowledge_path)
    
    def load(self) -> List[Document]:
        """Load documents from the knowledge base."""
        documents = []
        
        if not self.knowledge_path.exists():
            return documents
        
        # Load text files
        for file_path in self.knowledge_path.rglob("*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": str(file_path),
                        "type": "knowledge_base",
                        "filename": file_path.name,
                        "category": file_path.parent.name
                    }
                )
                documents.append(doc)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        # Load markdown files
        for file_path in self.knowledge_path.rglob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": str(file_path),
                        "type": "documentation",
                        "filename": file_path.name,
                        "format": "markdown"
                    }
                )
                documents.append(doc)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        return documents


class JarvisConfigLoader(BaseLoader):
    """Loader for Jarvis AI configuration documentation."""
    
    def __init__(self, config_path: str = "config"):
        """Initialize the config loader."""
        self.config_path = Path(config_path)
    
    def load(self) -> List[Document]:
        """Load configuration documentation."""
        documents = []
        
        # Load YAML config files as documentation
        for file_path in self.config_path.rglob("*.yaml"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                doc = Document(
                    page_content=f"Configuration file: {file_path.name}\n\n{content}",
                    metadata={
                        "source": str(file_path),
                        "type": "configuration",
                        "filename": file_path.name,
                        "format": "yaml"
                    }
                )
                documents.append(doc)
            except Exception as e:
                print(f"Error loading config {file_path}: {e}")
        
        return documents


class JarvisProjectLoader(BaseLoader):
    """Loader for project-specific documentation and code context."""
    
    def __init__(self, project_path: str = ".", include_code: bool = False):
        """Initialize the project loader."""
        self.project_path = Path(project_path)
        self.include_code = include_code
    
    def load(self) -> List[Document]:
        """Load project documentation."""
        documents = []
        
        # Load README files
        readme_patterns = ["README.md", "readme.md", "README.txt", "readme.txt"]
        for pattern in readme_patterns:
            readme_files = list(self.project_path.rglob(pattern))
            for file_path in readme_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    doc = Document(
                        page_content=content,
                        metadata={
                            "source": str(file_path),
                            "type": "readme",
                            "filename": file_path.name,
                            "directory": str(file_path.parent)
                        }
                    )
                    documents.append(doc)
                except Exception as e:
                    print(f"Error loading README {file_path}: {e}")
        
        # Load docs directory
        docs_path = self.project_path / "docs"
        if docs_path.exists():
            for file_path in docs_path.rglob("*.md"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    doc = Document(
                        page_content=content,
                        metadata={
                            "source": str(file_path),
                            "type": "documentation",
                            "filename": file_path.name,
                            "section": file_path.stem
                        }
                    )
                    documents.append(doc)
                except Exception as e:
                    print(f"Error loading doc {file_path}: {e}")
        
        # Optionally include Python files for code context
        if self.include_code:
            for file_path in self.project_path.rglob("*.py"):
                # Skip virtual environment and cache directories
                if any(part in str(file_path) for part in ["venv", "__pycache__", ".git"]):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Only include files smaller than 10KB to avoid overwhelming context
                    if len(content) < 10000:
                        doc = Document(
                            page_content=content,
                            metadata={
                                "source": str(file_path),
                                "type": "code",
                                "filename": file_path.name,
                                "language": "python",
                                "module": str(file_path.relative_to(self.project_path))
                            }
                        )
                        documents.append(doc)
                except Exception as e:
                    print(f"Error loading code {file_path}: {e}")
        
        return documents


class JarvisChatHistoryLoader(BaseLoader):
    """Loader for chat history and user interactions."""
    
    def __init__(self, chat_history_path: str = "data/chat_history"):
        """Initialize the chat history loader."""
        self.chat_history_path = Path(chat_history_path)
    
    def load(self) -> List[Document]:
        """Load chat history as documents."""
        documents = []
        
        if not self.chat_history_path.exists():
            return documents
        
        # Load JSON chat history files
        for file_path in self.chat_history_path.rglob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    chat_data = json.load(f)
                
                # Convert chat history to text format
                if isinstance(chat_data, list):
                    content_lines = []
                    for msg in chat_data:
                        if isinstance(msg, dict):
                            role = msg.get("role", "unknown")
                            content = msg.get("content", "")
                            content_lines.append(f"{role}: {content}")
                    
                    content = "\n".join(content_lines)
                else:
                    content = json.dumps(chat_data, indent=2)
                
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": str(file_path),
                        "type": "chat_history",
                        "filename": file_path.name,
                        "session": file_path.stem
                    }
                )
                documents.append(doc)
            except Exception as e:
                print(f"Error loading chat history {file_path}: {e}")
        
        return documents


def create_composite_loader(
    knowledge_path: str = "data/knowledge",
    config_path: str = "config", 
    project_path: str = ".",
    chat_history_path: str = "data/chat_history",
    include_code: bool = False
) -> List[Document]:
    """Create a composite loader that loads from all sources."""
    
    all_documents = []
    
    # Load from all sources
    loaders = [
        JarvisKnowledgeLoader(knowledge_path),
        JarvisConfigLoader(config_path),
        JarvisProjectLoader(project_path, include_code),
        JarvisChatHistoryLoader(chat_history_path)
    ]
    
    for loader in loaders:
        try:
            documents = loader.load()
            all_documents.extend(documents)
        except Exception as e:
            print(f"Error loading from {loader.__class__.__name__}: {e}")
    
    return all_documents


def load_jarvis_knowledge() -> List[Document]:
    """Convenience function to load all Jarvis AI knowledge sources."""
    return create_composite_loader()


# For backwards compatibility with existing code
def read_legacy_file(path: str) -> str:
    """Read a file from the old/ directory for reference."""
    legacy_path = Path("old") / path
    if legacy_path.exists():
        try:
            with open(legacy_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading legacy file {path}: {e}"
    else:
        return f"Legacy file {path} not found"