import requests
import json
import subprocess
import sys

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