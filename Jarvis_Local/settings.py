# settings.py
import platform

# --- Live, Mutable Settings ---
NUM_RESPONSES = 2
DEEPCONF_ENABLED = True
CONFIDENCE_THRESHOLD = 0.21 # Start with a reasonable default
RELIABILITY_THRESHOLD = 0.25 # The minimum group_low_conf for a response to be accepted without remediation
MAX_TOKENS = 750  # Maximum number of tokens to generate per response
BASELINE_MODE = False  # When True, forces the orchestrator to use the BaselineAgent

# --- Model Configuration ---
# Define your models here
AVAILABLE_MODELS = {
    "gemma3-1b": "Jarvis_Local/models/gemma-3-1b-it-Q4_K_M.gguf",
    "Jan-v1-4b": "Jarvis_Local/models/Jan-v1-4B-Q6_K.gguf"
}

ACTIVE_MODEL_NAME = "Jan-v1-4b"  # Switch to Janus v1 4B model

# --- Hardware Configuration ---
def get_active_model_path():
    return AVAILABLE_MODELS[ACTIVE_MODEL_NAME]

N_GPU_LAYERS = -1  # For Janus v1 4B (36 layers as per model metadata)
N_THREADS = 8

N_CTX = 2048
VERBOSE = False