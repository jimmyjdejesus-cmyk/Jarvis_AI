"""Core Agent - Main AI agent functionality."""

import logging
import requests
import json
from typing import Dict, Any, List

from agent.features.rag_handler import RAGHandler

logger = logging.getLogger(__name__)


class JarvisAgent:
    """Modern Jarvis AI agent with clean interface."""

    def __init__(
        self,
        model_name: str = "llama3.2",
        base_url: str = "http://localhost:11434",
        rag_handler: RAGHandler | None = None,
    ) -> None:
        self.model_name = model_name
        self.base_url = base_url
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history = 10
        self.rag = rag_handler or RAGHandler()

    def chat(self, message: str, context: Dict[str, Any] | None = None) -> str:
        """Send chat message and get response."""
        try:
            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": message})

            # Keep history manageable
            if len(self.conversation_history) > self.max_history * 2:
                self.conversation_history = self.conversation_history[-self.max_history :]

            # Build retrieval-augmented context
            if self.rag:
                context_chunk = self.rag.build_context(message)
                if context_chunk:
                    self.conversation_history.append(
                        {"role": "system", "content": context_chunk}
                    )

            # Prepare the request
            url = f"{self.base_url}/api/chat"
            payload = {
                "model": self.model_name,
                "messages": self.conversation_history,
                "stream": False,
            }

            response = requests.post(url, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                assistant_message = result.get("message", {}).get("content", "No response")

                # Add assistant response to history
                self.conversation_history.append(
                    {"role": "assistant", "content": assistant_message}
                )

                return assistant_message
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return "Sorry, I'm having trouble connecting to the AI service."

        except requests.exceptions.RequestException as e:  # pragma: no cover - network
            logger.error(f"Request error: {e}")
            return "Sorry, I'm having trouble connecting to the AI service."
        except Exception as e:  # pragma: no cover - safeguard
            logger.error(f"Chat error: {e}")
            return "Sorry, I encountered an error processing your request."

    def generate_response(self, prompt: str, context: Dict[str, Any] | None = None) -> str:
        """Generate a response to a prompt."""
        try:
            url = f"{self.base_url}/api/generate"
            payload: Dict[str, Any] = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
            }

            if context:
                payload["context"] = context

            response = requests.post(url, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response")
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return "Sorry, I'm having trouble generating a response."

        except requests.exceptions.RequestException as e:  # pragma: no cover - network
            logger.error(f"Request error: {e}")
            return "Sorry, I'm having trouble connecting to the AI service."
        except Exception as e:  # pragma: no cover - safeguard
            logger.error(f"Generation error: {e}")
            return "Sorry, I encountered an error generating a response."

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []

    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self.conversation_history.copy()

    def is_available(self) -> bool:
        """Check if the AI service is available."""
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except Exception:  # pragma: no cover - network
            return False

    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                return [model.get("name", "") for model in models]
            else:
                return []

        except Exception as e:  # pragma: no cover - network
            logger.error(f"Error getting models: {e}")
            return []

    def set_model(self, model_name: str) -> None:
        """Change the current model."""
        self.model_name = model_name
        logger.info(f"Model changed to: {model_name}")

    # RAG APIs
    def index_document(self, principal: str, scope: str, key: str, text: str) -> None:
        """Index a document for later retrieval."""
        self.rag.index_document(principal, scope, key, text)

    def semantic_search(self, query: str, n_results: int = 5) -> List[str]:
        """Perform semantic search over indexed documents."""
        return self.rag.semantic_search(query, n_results)


# Global instance
_jarvis_agent: JarvisAgent | None = None


def get_jarvis_agent(
    model_name: str = "llama3.2", base_url: str = "http://localhost:11434"
) -> JarvisAgent:
    """Get global Jarvis agent instance."""
    global _jarvis_agent
    if _jarvis_agent is None:
        _jarvis_agent = JarvisAgent(model_name, base_url)
    return _jarvis_agent
