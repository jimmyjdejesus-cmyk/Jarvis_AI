# config.py
from pathlib import Path

# CRITICAL: Make sure this filename is EXACTLY correct.
# Use a path relative to this file so the model path remains correct after moving.
MODEL_PATH = str(Path(__file__).resolve().parent / "models" / "gemma-3-1b-it-Q4_K_M.gguf")

# This MUST be 0 for CPU only setup, -1 to offload to GPU(if available)
N_GPU_LAYERS = -1

N_THREADS = 8 # Set this to this number of physical CPU cores
# The context window of the model.
N_CTX = 512

# Confidence threshold for filtering responses
CONFIDENCE_THRESHOLD = 2.0