import requests
import json
import subprocess
import sys


OLLAMA_ENDPOINT = "http://localhost:11434"

# Simple in-memory cache for available models

_model_cache = None
_model_cache_time = 0
_MODEL_CACHE_TTL = 60  # seconds

def clear_model_cache():
    """
    Clears the internal model cache and resets cache time.
    """
    global _model_cache, _model_cache_time
    _model_cache = None
    _model_cache_time = 0


def get_available_models():
    """
    Fetches the list of locally available models from the Ollama API, with caching.
    """
    import time
    global _model_cache, _model_cache_time
    now = time.time()
    if _model_cache and (now - _model_cache_time < _MODEL_CACHE_TTL):
        return _model_cache
    try:
        response = requests.get(f"{OLLAMA_ENDPOINT}/api/tags")
        response.raise_for_status()
        models = response.json().get("models", [])
        _model_cache = [model['name'] for model in models]
        _model_cache_time = now
        return _model_cache
    except requests.exceptions.RequestException as e:
        print(f"Error fetching models: {e}")
        return _model_cache if _model_cache else []


def stream_generation(model, prompt, draft_model=None):
    """
    Sends a prompt and an optional draft model to the Ollama API for a streaming response.
    """
    payload = {"model": model, "prompt": prompt, "stream": True}
    if draft_model:
        # Pass the draft model as an option for speculative decoding
        payload["options"] = {"draft_model": draft_model}

    try:
        response = requests.post(
            f"{OLLAMA_ENDPOINT}/api/generate",
            json=payload,
            stream=True,
            timeout=120
        )
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                yield json.loads(line.decode('utf-8'))
    except requests.exceptions.RequestException as e:
        yield {"error": f"Connection to Ollama failed or timed out: {e}"}


def generate_non_streamed_response(model, prompt, draft_model=None):
    """
    Generates a complete response from a model without streaming, with an optional draft model.
    """
    payload = {"model": model, "prompt": prompt, "stream": False}
    if draft_model:
        payload["options"] = {"draft_model": draft_model}

    try:
        response = requests.post(
            f"{OLLAMA_ENDPOINT}/api/generate",
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        return response.json().get("response", "")
    except requests.exceptions.RequestException as e:
        print(f"Error in non-streamed generation: {e}")
        return f"Error: Could not get a response from Ollama. {e}"


def pull_model_subprocess(model_name):
    """
    Runs 'ollama pull' as a subprocess and yields the output line by line,
    using a more robust method to handle output buffering.
    """
    command = ["ollama", "pull", model_name]
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0,
            encoding='utf-8',
            errors='replace'
        )
        for line in process.stdout:
            yield line.strip()
        process.wait()
    except FileNotFoundError:
        yield "Ollama command not found. Make sure Ollama is installed and in your system's PATH."
    except Exception as e:
        yield f"An unexpected error occurred: {e}"


def get_model_details():
    """
    Get detailed information about installed models from Ollama API
    """
    try:
        response = requests.get(f"{OLLAMA_ENDPOINT}/api/tags")
        response.raise_for_status()
        return response.json().get("models", [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching model details: {e}")
        return []


def delete_model(model_name):
    """
    Delete a model using Ollama API
    """
    try:
        response = requests.delete(f"{OLLAMA_ENDPOINT}/api/delete", json={"name": model_name})
        response.raise_for_status()
        # Clear the cache since model list changed
        global _model_cache
        _model_cache = None
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error deleting model {model_name}: {e}")
        return False


def update_endpoint(new_endpoint):
    """
    Update the Ollama endpoint and clear cache
    """
    global OLLAMA_ENDPOINT, _model_cache
    OLLAMA_ENDPOINT = new_endpoint
    _model_cache = None  # Clear cache when endpoint changes