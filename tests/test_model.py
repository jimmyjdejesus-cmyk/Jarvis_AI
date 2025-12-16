# test_model.py
import sys
import os
import time
from apps.Jarvis_Local.settings import ACTIVE_MODEL_NAME, get_active_model_path
from apps.Jarvis_Local.logger_config import log

print(f"Testing model loading for: {ACTIVE_MODEL_NAME}")
print(f"Model path: {get_active_model_path()}")
print(f"Current working directory: {os.getcwd()}")

# Resolve absolute path to model
model_path = get_active_model_path()
# Resolve absolute path safely: the `get_active_model_path` may return an absolute path,
# a path relative to the package, or a model name. Try a few fallbacks.
if os.path.isabs(model_path) or os.path.exists(model_path):
    abs_path = os.path.abspath(model_path)
else:
    candidate = os.path.abspath(os.path.join("apps", "Jarvis_Local", model_path))
    if os.path.exists(candidate):
        abs_path = candidate
    else:
        # Fallback to interpreting the value as-is (may be a model id, not a file path)
        abs_path = os.path.abspath(model_path)
print(f"Absolute model path: {abs_path}")
print(f"File exists: {os.path.exists(abs_path)}")

# Try loading model
try:
    from llama_cpp import Llama
    print("Attempting to load model...")
    start_time = time.time()
    model = Llama(model_path=abs_path, n_ctx=2048, n_gpu_layers=-1)
    load_time = time.time() - start_time
    print(f"Model loaded successfully in {load_time:.2f} seconds")
    
    # Try generating a simple response
    print("Generating sample response...")
    output = model.create_completion(
        "Who won the Battle of Waterloo?",
        max_tokens=128,
        temperature=0.1
    )
    response = output["choices"][0]["text"]
    print(f"Response: {response}")
    print("Test completed successfully!")
except Exception as e:
    print(f"Error: {e}")
