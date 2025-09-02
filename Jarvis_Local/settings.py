# settings.py

# --- Live, Mutable Settings ---

# Voting Configuration
NUM_RESPONSES = 1

# Deep Thinking w/ Confidence
DEEPCONF_ENABLED = True
CONFIDENCE_THRESHOLD = 1.0

N_GPU_LAYERS = -1
N_THREADS = 8

AVAILABLE_MODELS = [
    "gemma-3-1b-it-Q4_K_M.gguf",

]

N_CTX = 2048  # Adjust as needed for your model
ACTIVE_MODEL_PATH = f"Jarvis_Local/models/{AVAILABLE_MODELS[0]}"