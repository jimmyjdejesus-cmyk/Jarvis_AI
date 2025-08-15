# ollama_client.py
import requests
import json

OLLAMA_ENDPOINT = "http://localhost:11434"


def get_available_models():
    # ... (this function remains the same) ...
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
    Includes detailed print statements for debugging.
    """
    print(f"--- OLLAMA_CLIENT: Preparing to stream for model '{model}' ---")
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True
    }

    try:
        print("--- OLLAMA_CLIENT: Sending POST request to Ollama server... ---")
        # ADDED a 60-second timeout to prevent hanging forever
        response = requests.post(
            f"{OLLAMA_ENDPOINT}/api/generate",
            json=payload,
            stream=True,
            timeout=60
        )
        print(f"--- OLLAMA_CLIENT: Received response with status code: {response.status_code} ---")
        response.raise_for_status()

        print("--- OLLAMA_CLIENT: Starting to iterate through response lines... ---")
        for line in response.iter_lines():
            if line:
                yield json.loads(line.decode('utf-8'))
        print("--- OLLAMA_CLIENT: Finished iterating successfully. ---")

    except requests.exceptions.RequestException as e:
        print(f"--- OLLAMA_CLIENT: CAUGHT AN EXCEPTION: {e} ---")
        yield {"error": f"Connection to Ollama failed or timed out: {e}"}