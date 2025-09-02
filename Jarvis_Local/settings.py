# settings.py
import platform

# --- Live, Mutable Settings ---
NUM_RESPONSES = 2
DEEPCONF_ENABLED = True
CONFIDENCE_THRESHOLD = 0.21 # Start with a reasonable default

# --- Model Configuration ---
# Define your models here
AVAILABLE_MODELS = {
    "gemma3-1b": "Jarvis_Local/models/gemma-3-1b-it-Q4_K_M.gguf",
    "Jan-v1-4b": "Jarvis_Local/models/Jan-v1-4B-Q6_K.gguf"
}

ACTIVE_MODEL_NAME = list(AVAILABLE_MODELS.keys())[0]  # Default to the first model

# --- Hardware Configuration ---
def get_active_model_path():
    return AVAILABLE_MODELS[ACTIVE_MODEL_NAME]

N_GPU_LAYERS = -1 # Full GPU offload for desktop
N_THREADS = 8

N_CTX = 2048
VERBOSE = False