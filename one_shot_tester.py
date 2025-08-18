import subprocess
import time
import requests
import sys

# --- Configuration ---
APP_CMD = ["streamlit", "run", "app.py", "--server.headless=true", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
OLLAMA_ENDPOINT = "http://localhost:11434"
TEST_MODEL = "qwen3:0.6b"
TEST_PROMPT = "Hello, this is a one-shot test. Are you running?"
APP_URL = "http://localhost:8501"  # Default Streamlit URL

def main():
    """
    One-shot tester for the Jarvis AI application.
    1. Launches the Streamlit app.
    2. Waits for the app to be responsive.
    3. Sends a test prompt to the Ollama model.
    4. Prints the result and terminates the app.
    """
    app_process = None
    try:
        # 1. Launch the app
        print("🚀 Launching the application...")
        app_process = subprocess.Popen(APP_CMD)
        
        # 2. Wait for the app to be responsive
        max_wait = 60
        start_time = time.time()
        is_ready = False
        
        print(f"⏳ Waiting for app to be ready at {APP_URL}...")
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(APP_URL, timeout=2)
                if response.ok:
                    print("✅ Application is ready!")
                    is_ready = True
                    break
            except requests.ConnectionError:
                time.sleep(2)
        
        if not is_ready:
            print("❌ Timed out waiting for the application to start.")
            sys.exit(1)
            
        # 3. Send a test prompt to the model
        print(f"🤖 Sending test prompt to model: '{TEST_MODEL}'...")
        payload = {
            "model": TEST_MODEL,
            "prompt": TEST_PROMPT,
            "stream": False
        }
        
        try:
            response = requests.post(f"{OLLAMA_ENDPOINT}/api/generate", json=payload, timeout=45)
            
            # 4. Print the result
            if response.ok:
                result = response.json()
                print("\\n--- Test Result ---")
                print(f"Model: {result.get('model')}")
                print(f"Response: {result.get('response')}")
                print("✅ Test successful!")
            else:
                print(f"❌ Test failed with status code: {response.status_code}")
                print(f"Error: {response.text}")
                sys.exit(1)
                
        except requests.RequestException as e:
            print(f"❌ Failed to connect to Ollama endpoint: {e}")
            sys.exit(1)

    finally:
        # 5. Terminate the app
        if app_process:
            print("\\n🛑 Terminating the application...")
            app_process.terminate()
            app_process.wait()
            print("✅ Application terminated.")

if __name__ == "__main__":
    main()
