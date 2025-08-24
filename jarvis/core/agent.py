"""
Core Agent - Main AI agent functionality
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class JarvisAgent:
    """Modern Jarvis AI agent with clean interface"""
    
    def __init__(self, model_name: str = "llama3.2", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.conversation_history = []
    
    def chat(self, message: str, stream: bool = False) -> str:
        """Chat with the AI agent"""
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
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_history(self) -> list:
        """Get conversation history"""
        return self.conversation_history
    
    def get_available_tools(self) -> list:
        """Get available tools"""
        return [
            "chat",
            "model_selection", 
            "conversation_history",
            "basic_responses"
        ]
    
    def process_with_tools(self, message: str, tools: list = None) -> str:
        """Process message with specific tools"""
        # This is a placeholder for a more advanced tool processing system
        return self.chat(message)

# Create global instance
jarvis_agent = JarvisAgent()
