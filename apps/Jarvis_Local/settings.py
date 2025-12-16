# settings.py
import os
from pathlib import Path

# --- Live, Mutable Settings ---
NUM_RESPONSES = 2
DEEPCONF_ENABLED = False # Disabled until streeaming redone for ollama
CONFIDENCE_THRESHOLD = 0.21 # Start with a reasonable default
RELIABILITY_THRESHOLD = 0.25 # The minimum group_low_conf for a response to be accepted without remediation
# --- Model Configuration ---
# Define your models here as they appear in `ollama list`
VERIFIER_MODEL = "qwen2:4b"
DRAFT_MODEL = "tinyllama:1b"

# Active Model for the entire application
ACTIVE_MODEL_NAME = VERIFIER_MODEL


def get_active_model_path() -> str:
	"""Return a model path that tests can resolve.

	Prefer the explicit `apps/Jarvis_Local/active_model.cfg` (located next to
	this file) if present, otherwise return the declared `ACTIVE_MODEL_NAME`.
	"""
	cfg_path = Path(__file__).resolve().parent / "active_model.cfg"
	if cfg_path.exists():
		return str(cfg_path)
	return ACTIVE_MODEL_NAME


# Mapping of available model names to their identifiers for UI
AVAILABLE_MODELS = {
	"Verifier": VERIFIER_MODEL,
	"Draft": DRAFT_MODEL,
}