"""
Scripts module for Jarvis AI
"""

import requests
import subprocess

def get_available_models():
    """Get available Ollama models"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.ok:
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
    except:
        pass
    return ["llama3.2", "qwen2.5", "gemma2"] # Default fallback models

try:
    from legacy.scripts.ollama_client import get_available_models, pull_model_subprocess
except ImportError:
    # Fallback implementations
    import requests
    import subprocess

    def get_available_models():
        """Get available Ollama models"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.ok:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except:
            pass
        return ["llama3.2", "qwen2.5", "gemma2"] # Default fallback models

    def pull_model_subprocess(model_name):
        """Pull a model using subprocess"""
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