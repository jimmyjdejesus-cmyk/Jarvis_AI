# ollama_client.py
import requests
import json
import subprocess

OLLAMA_ENDPOINT = "http://localhost:11434"

def get_available_models():
    """
    Fetches the list of locally available models from the Ollama API.
    """
    try:
        response = requests.get(f"{OLLAMA_ENDPOINT}/api/tags")
        response.raise_for_status()
        models = response.json().get("models", [])
        return [model['name'] for model in models]
    except requests.exceptions.RequestException:
        return []

def stream_generation(model, prompt):
    """
    Sends a prompt to the selected model and streams the response.
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True
    }
    try:
        response = requests.post(
            f"{OLLAMA_ENDPOINT}/api/generate",
            json=payload,
            stream=True,
            timeout=120  # Increased timeout for large model loading
        )
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                yield json.loads(line.decode('utf-8'))
    except requests.exceptions.RequestException as e:
        yield {"error": f"Connection to Ollama failed or timed out: {e}"}

def pull_model_subprocess(model_name):
    """
    Runs 'ollama pull' as a subprocess and yields the output line by line.
    """
    command = ["ollama", "pull", model_name]
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8'
        )
        for line in iter(process.stdout.readline, ''):
            yield line.strip()
        process.wait()
    except FileNotFoundError:
        yield "Ollama command not found. Make sure Ollama is installed and in your system's PATH."