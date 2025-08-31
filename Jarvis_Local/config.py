# config.py

# CRITICAL: Make sure this filename is EXACTLY correct.
MODEL_PATH = "Jarvis_Local\models\gemma-3-1b-it-Q4_K_M.gguf"

# This MUST be 0 for CPU only setup, -1 to offload to GPU(if available)
N_GPU_LAYERS = 0

N_THREADS = 6 # Set this to this number of physical CPU cores
# The context window of the model.
N_CTX = 512

# Confidence threshold for filtering responses
CONFIDENCE_THRESHOLD = 10.0