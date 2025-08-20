"""
Enhanced RAG Fallback System for Offline and Degraded Operations
Extends existing RAG functionality with improved caching and fallback mechanisms.
"""

import json
import os
import hashlib
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import sys

# Add legacy path for imports
legacy_path = Path(__file__).parent.parent.parent.parent / "legacy"
sys.path.insert(0, str(legacy_path))

try:
    from agent.features.rag_handler import RAGCache, get_rag_cache
    from agent.core.error_handling import get_logger, robust_operation
    LEGACY_AVAILABLE = True
except ImportError as e:
    print(f"Legacy RAG modules not available: {e}")
    LEGACY_AVAILABLE = False

try:
    from langchain_core.runnables import RunnableLambda
    from langchain_core.callbacks import BaseCallbackHandler
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class EnhancedRAGCache:
    """Enhanced RAG cache with persistent storage and offline capabilities."""
    
    def __init__(self, cache_dir: str = "cache", max_size: int = 1000, ttl_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_size = max_size
        self.ttl = timedelta(hours=ttl_hours)
        
        # In-memory cache for fast access
        self.memory_cache = {}
        
        # Persistent cache metadata
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        self.cache_metadata = self._load_metadata()
        
        # Fallback content for emergency situations
        self.emergency_content = {
            "system_info": "System is operating in emergency mode with limited functionality.",
            "help_text": "Available commands: status, help, basic operations only.",
            "error_guidance": "System error detected. Please check system logs for troubleshooting."
        }
        
        if LEGACY_AVAILABLE:
            self.logger = get_logger()
        else:
            import logging
            self.logger = logging.getLogger("enhanced_rag")
            # Create a wrapper to match JarvisLogger interface
            self.logger.logger = self.logger
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load cache metadata from disk."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Failed to load cache metadata: {e}")
        
        return {"entries": {}, "last_cleanup": None, "total_size": 0}
    
    def _save_metadata(self):
        """Save cache metadata to disk."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.cache_metadata, f, indent=2)
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.logger.error(f"Failed to save cache metadata: {e}")
    
    def _get_cache_key(self, prompt: str, files: List[str], mode: str, context: str = "") -> str:
        """Generate cache key for the request."""
        content = f"{prompt}:{','.join(sorted(files))}:{mode}:{context}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _get_cache_file_path(self, cache_key: str) -> Path:
        """Get the file path for a cache entry."""
        return self.cache_dir / f"{cache_key}.pkl"
    
    def get(self, prompt: str, files: List[str], mode: str, context: str = "") -> Optional[str]:
        """Get cached result with fallback mechanisms."""
        cache_key = self._get_cache_key(prompt, files, mode, context)
        
        # Try memory cache first
        if cache_key in self.memory_cache:
            result, timestamp = self.memory_cache[cache_key]
            if datetime.now() - timestamp < self.ttl:
                if hasattr(self, 'logger'):
                    self.logger.logger.debug(f"Memory cache hit: {cache_key[:8]}...")
                return result
            else:
                del self.memory_cache[cache_key]
        
        # Try persistent cache
        cache_file = self._get_cache_file_path(cache_key)
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    cached_data = pickle.load(f)
                
                result, timestamp = cached_data['result'], cached_data['timestamp']
                
                if datetime.now() - timestamp < self.ttl:
                    # Update memory cache
                    self.memory_cache[cache_key] = (result, timestamp)
                    if hasattr(self, 'logger'):
                        self.logger.logger.debug(f"Persistent cache hit: {cache_key[:8]}...")
                    return result
                else:
                    # Remove expired cache file
                    cache_file.unlink()
                    if cache_key in self.cache_metadata["entries"]:
                        del self.cache_metadata["entries"][cache_key]
                        self._save_metadata()
            except Exception as e:
                if hasattr(self, 'logger'):
                    self.logger.logger.error(f"Failed to load cache entry {cache_key}: {e}")
        
        return None
    
    def set(self, prompt: str, files: List[str], mode: str, result: str, context: str = ""):
        """Cache the result with persistent storage."""
        cache_key = self._get_cache_key(prompt, files, mode, context)
        timestamp = datetime.now()
        
        # Store in memory cache
        self.memory_cache[cache_key] = (result, timestamp)
        
        # Store in persistent cache
        try:
            cache_file = self._get_cache_file_path(cache_key)
            cached_data = {
                'result': result,
                'timestamp': timestamp,
                'prompt': prompt[:200],  # Store truncated prompt for debugging
                'mode': mode,
                'context': context[:100]
            }
            
            with open(cache_file, 'wb') as f:
                pickle.dump(cached_data, f)
            
            # Update metadata
            self.cache_metadata["entries"][cache_key] = {
                "timestamp": timestamp.isoformat(),
                "size": len(result),
                "prompt_preview": prompt[:50],
                "mode": mode
            }
            self.cache_metadata["total_size"] = len(self.cache_metadata["entries"])
            self._save_metadata()
            
            if hasattr(self, 'logger'):
                self.logger.logger.debug(f"Cached result: {cache_key[:8]}...")
            
            # Cleanup if cache is too large
            if len(self.cache_metadata["entries"]) > self.max_size:
                self._cleanup_cache()
                
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.logger.error(f"Failed to cache result: {e}")
    
    def _cleanup_cache(self):
        """Remove oldest cache entries to maintain size limit."""
        try:
            # Sort entries by timestamp and remove oldest
            entries = list(self.cache_metadata["entries"].items())
            entries.sort(key=lambda x: x[1]["timestamp"])
            
            to_remove = len(entries) - self.max_size + 100  # Remove extra to avoid frequent cleanups
            
            for cache_key, _ in entries[:to_remove]:
                cache_file = self._get_cache_file_path(cache_key)
                if cache_file.exists():
                    cache_file.unlink()
                
                if cache_key in self.cache_metadata["entries"]:
                    del self.cache_metadata["entries"][cache_key]
                
                if cache_key in self.memory_cache:
                    del self.memory_cache[cache_key]
            
            self.cache_metadata["last_cleanup"] = datetime.now().isoformat()
            self.cache_metadata["total_size"] = len(self.cache_metadata["entries"])
            self._save_metadata()
            
            if hasattr(self, 'logger'):
                self.logger.logger.info(f"Cache cleanup: removed {to_remove} entries")
                
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.logger.error(f"Cache cleanup failed: {e}")
    
    def get_emergency_response(self, prompt: str) -> str:
        """Generate emergency response when all other systems fail."""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["status", "health", "check"]):
            return self.emergency_content["system_info"]
        elif any(word in prompt_lower for word in ["help", "support", "what"]):
            return self.emergency_content["help_text"]
        elif any(word in prompt_lower for word in ["error", "problem", "issue"]):
            return self.emergency_content["error_guidance"]
        else:
            return (f"I'm operating in emergency mode due to system issues. "
                   f"I can only provide basic responses. Your query '{prompt[:50]}...' "
                   f"cannot be processed normally. Please check system status.")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "total_entries": len(self.cache_metadata["entries"]),
            "memory_entries": len(self.memory_cache),
            "cache_dir": str(self.cache_dir),
            "last_cleanup": self.cache_metadata.get("last_cleanup"),
            "cache_size_mb": sum(entry.get("size", 0) for entry in self.cache_metadata["entries"].values()) / (1024 * 1024)
        }


class OfflineRAGHandler:
    """Handles RAG operations in offline/degraded modes."""
    
    def __init__(self, enhanced_cache: Optional[EnhancedRAGCache] = None):
        self.enhanced_cache = enhanced_cache or EnhancedRAGCache()
        
        if LEGACY_AVAILABLE:
            self.legacy_cache = get_rag_cache()
            self.logger = get_logger()
        else:
            self.legacy_cache = None
            import logging
            self.logger = logging.getLogger("offline_rag")
            # Create a wrapper to match JarvisLogger interface
            self.logger.logger = self.logger
        
        # Local knowledge base for offline operation
        self.local_knowledge = self._load_local_knowledge()
    
    def _load_local_knowledge(self) -> Dict[str, str]:
        """Load local knowledge base for offline operation."""
        knowledge_file = Path("cache") / "local_knowledge.json"
        
        if knowledge_file.exists():
            try:
                with open(knowledge_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                if hasattr(self, 'logger'):
                    self.logger.logger.error(f"Failed to load local knowledge: {e}")
        
        # Default local knowledge
        return {
            "system_capabilities": "Jarvis AI with code analysis, file management, and basic completion features.",
            "available_commands": "File operations, code analysis, basic queries, system status checks.",
            "offline_limitations": "Web search, external APIs, and real-time data are not available in offline mode.",
            "troubleshooting": "Check network connectivity, Ollama service status, and system logs for issues."
        }
    
    def handle_rag_request(self, prompt: str, files: List[str], mode: str = "offline", 
                          context: str = "") -> str:
        """Handle RAG request with fallback mechanisms."""
        
        # Try enhanced cache first
        cached_result = self.enhanced_cache.get(prompt, files, mode, context)
        if cached_result:
            return cached_result
        
        # Try legacy cache if available
        if self.legacy_cache:
            try:
                legacy_result = self.legacy_cache.get(prompt, files, mode)
                if legacy_result:
                    # Store in enhanced cache for future use
                    self.enhanced_cache.set(prompt, files, mode, legacy_result, context)
                    return legacy_result
            except Exception as e:
                if hasattr(self, 'logger'):
                    self.logger.logger.error(f"Legacy cache access failed: {e}")
        
        # Try local knowledge base
        local_result = self._search_local_knowledge(prompt)
        if local_result:
            # Cache the local result
            self.enhanced_cache.set(prompt, files, mode, local_result, context)
            return local_result
        
        # Try file-based context if files are provided
        if files:
            file_result = self._extract_file_context(prompt, files)
            if file_result:
                self.enhanced_cache.set(prompt, files, mode, file_result, context)
                return file_result
        
        # Emergency fallback
        emergency_result = self.enhanced_cache.get_emergency_response(prompt)
        return emergency_result
    
    def _search_local_knowledge(self, prompt: str) -> Optional[str]:
        """Search local knowledge base."""
        prompt_lower = prompt.lower()
        
        for key, content in self.local_knowledge.items():
            if any(keyword in prompt_lower for keyword in key.replace("_", " ").split()):
                return f"Based on local knowledge about {key.replace('_', ' ')}: {content}"
        
        return None
    
    def _extract_file_context(self, prompt: str, files: List[str]) -> Optional[str]:
        """Extract context from local files when possible."""
        context_parts = []
        
        for file_path in files[:5]:  # Limit to first 5 files
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()[:1000]  # First 1000 characters
                        context_parts.append(f"File {file_path}:\n{content}")
            except Exception as e:
                context_parts.append(f"File {file_path}: Unable to read - {str(e)}")
        
        if context_parts:
            file_context = "\n\n".join(context_parts)
            return (f"Based on available local files:\n\n{file_context}\n\n"
                   f"Regarding your question: {prompt}\n\n"
                   f"I can only provide basic analysis based on the file content shown above "
                   f"since I'm operating in offline mode.")
        
        return None


# Create LangChain fallback components if available
if LANGCHAIN_AVAILABLE:
    class RAGFallbackChain:
        """LangChain-based RAG fallback chain."""
        
        def __init__(self, offline_handler: OfflineRAGHandler):
            self.offline_handler = offline_handler
        
        def create_chain(self):
            """Create a LangChain runnable for RAG fallback."""
            
            def rag_with_fallback(inputs):
                prompt = inputs.get("prompt", "")
                files = inputs.get("files", [])
                mode = inputs.get("mode", "offline")
                
                return self.offline_handler.handle_rag_request(prompt, files, mode)
            
            return RunnableLambda(rag_with_fallback)
    
    def create_langchain_rag_fallback(offline_handler: OfflineRAGHandler):
        """Create LangChain RAG fallback chain."""
        return RAGFallbackChain(offline_handler).create_chain()

else:
    def create_langchain_rag_fallback(offline_handler: OfflineRAGHandler):
        """Fallback when LangChain is not available."""
        return offline_handler.handle_rag_request


# Global instances
_enhanced_cache = None
_offline_handler = None


def get_enhanced_rag_cache() -> EnhancedRAGCache:
    """Get global enhanced RAG cache instance."""
    global _enhanced_cache
    if _enhanced_cache is None:
        _enhanced_cache = EnhancedRAGCache()
    return _enhanced_cache


def get_offline_rag_handler() -> OfflineRAGHandler:
    """Get global offline RAG handler instance."""
    global _offline_handler
    if _offline_handler is None:
        _offline_handler = OfflineRAGHandler()
    return _offline_handler


# Integration function to replace standard RAG in offline mode
@robust_operation(operation_name="offline_rag_answer") if LEGACY_AVAILABLE else lambda f: f
def offline_rag_answer(prompt: str, files: List[str], expert_model: str = None,
                      chat_history: List[Dict] = None, user: str = None,
                      endpoint: str = None, mode: str = "offline") -> str:
    """
    Enhanced RAG function for offline/degraded operation.
    Falls back gracefully when normal RAG systems are unavailable.
    """
    
    # Get offline handler
    handler = get_offline_rag_handler()
    
    # Build context from chat history if available
    context = ""
    if chat_history:
        recent_history = chat_history[-3:]  # Last 3 messages for context
        context = " ".join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" 
                           for msg in recent_history])
    
    # Handle request with full fallback chain
    result = handler.handle_rag_request(prompt, files, mode, context)
    
    return result