"""
Model Client - Interface for AI model operations
"""

import requests
import subprocess
import json
import logging
from typing import List, Optional, Generator
from pathlib import Path
from urllib.parse import urlparse

# Import legacy model client
import sys
legacy_path = Path(__file__).parent.parent.parent / "legacy"
sys.path.insert(0, str(legacy_path))

try:
    from scripts.ollama_client import *
    LEGACY_OLLAMA_AVAILABLE = True
except ImportError:
    LEGACY_OLLAMA_AVAILABLE = False

logger = logging.getLogger(__name__)

class ModelClient:
    """Modern model client with clean interface"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        parsed = urlparse(base_url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("base_url must include http or https scheme")
        self.base_url = base_url
        self.timeout = 30
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        if LEGACY_OLLAMA_AVAILABLE:
            try:
                return get_available_models()
            except:
                pass
        
        # Fallback implementation
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.ok:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            logger.warning(f"Failed to get models from Ollama: {e}")
        
        # Default fallback models
        return ["llama3.2", "qwen2.5", "gemma2", "codellama"]
    
    def test_connection(self) -> bool:
        """Test connection to Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.ok
        except:
            return False
    
    def pull_model(self, model_name: str) -> Generator[str, None, None]:
        """Pull a model using subprocess"""
        if LEGACY_OLLAMA_AVAILABLE:
            try:
                yield from pull_model_subprocess(model_name)
                return
            except:
                pass
        
        # Fallback implementation
        try:
            process = subprocess.Popen(
                ["ollama", "pull", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            for line in process.stdout:
                yield line.strip()
            
            process.wait()
        except Exception as e:
            yield f"Error pulling model: {e}"
    
    def generate_response(self, model: str, prompt: str, stream: bool = False) -> str:
        """Generate response from model"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": stream
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.ok:
                if stream:
                    return response.text
                else:
                    data = response.json()
                    return data.get("response", "No response generated")
            else:
                return f"Error: HTTP {response.status_code}"
                
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return f"Error generating response: {e}"
    
    def get_model_info(self, model_name: str) -> Optional[dict]:
        """Get information about a specific model"""
        try:
            payload = {"name": model_name}
            response = requests.post(
                f"{self.base_url}/api/show",
                json=payload,
                timeout=10
            )
            
            if response.ok:
                return response.json()
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
        
        return None
    
    def health_check_model(self, model_name: str) -> dict:
        """Check health of a specific model"""
        try:
            import time
            start_time = time.time()
            
            payload = {
                "model": model_name,
                "prompt": "Hello",
                "stream": False
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            end_time = time.time()
            response_time = round(end_time - start_time, 2)
            
            if response.ok:
                return {
                    "model": model_name,
                    "status": "✅ Healthy",
                    "response_time": f"{response_time}s"
                }
            else:
                return {
                    "model": model_name,
                    "status": "❌ Error",
                    "response_time": "N/A"
                }
        except Exception as e:
            return {
                "model": model_name,
                "status": f"❌ {str(e)[:50]}",
                "response_time": "N/A"
            }

# Create global instance
model_client = ModelClient()
