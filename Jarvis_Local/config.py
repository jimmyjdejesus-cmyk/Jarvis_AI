# config.py

# CRITICAL: Make sure this filename is EXACTLY correct.
MODEL_PATH = "Jarvis_Local\models\Phi-4-mini-instruct.Q4_K_M.gguf"

# This MUST be 0 for CPU only setup, -1 to offload to GPU(if available)
N_GPU_LAYERS = -1

# The context window of the model.
N_CTX = 512