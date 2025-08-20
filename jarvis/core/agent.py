"""
Core Agent - Main AI agent functionality
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

# Import legacy agent
import sys
legacy_path = Path(__file__).parent.parent.parent / "legacy"
sys.path.insert(0, str(legacy_path))

try:
    from agent.core.core import JarvisAgent as LegacyAgent
    LEGACY_AGENT_AVAILABLE = True
except ImportError:
    LEGACY_AGENT_AVAILABLE = False

logger = logging.getLogger(__name__)

class JarvisAgent:
    """Modern Jarvis AI agent with clean interface"""
    
    def __init__(self, model_name: str = "llama3.2", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.conversation_history = []
        
        # Try to use legacy agent if available
        if LEGACY_AGENT_AVAILABLE:
            try:
                self.legacy_agent = LegacyAgent(model_name)
                self.has_legacy = True
            except:
                self.has_legacy = False
        else:
            self.has_legacy = False
    
    def chat(self, message: str, stream: bool = False) -> str:
        """Chat with the AI agent"""
        if self.has_legacy:
            try:
                return self.legacy_agent.chat(message)
            except:
                pass
        
        # Fallback implementation
        from jarvis.models.client import model_client
        
        try:
            response = model_client.generate_response(
                model=self.model_name,
                prompt=message,
                stream=stream
            )
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": message
            })
            self.conversation_history.append({
                "role": "assistant", 
                "content": response
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            return f"I apologize, but I encountered an error: {e}. Please try again."
    
    def set_model(self, model_name: str):
        """Change the active model"""
        self.model_name = model_name
        if self.has_legacy and hasattr(self.legacy_agent, 'set_model'):
            try:
                self.legacy_agent.set_model(model_name)
            except:
                pass
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        if self.has_legacy and hasattr(self.legacy_agent, 'clear_history'):
            try:
                self.legacy_agent.clear_history()
            except:
                pass
    
    def get_history(self) -> list:
        """Get conversation history"""
        if self.has_legacy and hasattr(self.legacy_agent, 'get_history'):
            try:
                return self.legacy_agent.get_history()
            except:
                pass
        
        return self.conversation_history
    
    def get_available_tools(self) -> list:
        """Get available tools"""
        if self.has_legacy and hasattr(self.legacy_agent, 'get_available_tools'):
            try:
                return self.legacy_agent.get_available_tools()
            except:
                pass
        
        # Fallback tools
        return [
            "chat",
            "model_selection", 
            "conversation_history",
            "basic_responses"
        ]
    
    def process_with_tools(self, message: str, tools: list = None) -> str:
        """Process message with specific tools"""
        if self.has_legacy and hasattr(self.legacy_agent, 'process_with_tools'):
            try:
                return self.legacy_agent.process_with_tools(message, tools)
            except:
                pass
        
        # Fallback - use basic chat
        return self.chat(message)

# Create global instance
jarvis_agent = JarvisAgent()
