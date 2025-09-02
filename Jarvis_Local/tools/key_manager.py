# tools/key_manager.py
import keyring
from logger_config import log

# Use a unique service name for your application
SERVICE_NAME = "jarvis_local_ai"
USERNAME = "openai_api_key"

def save_api_key(api_key: str):
    """Saves the API key to the system's keyring."""
    try:
        keyring.set_password(SERVICE_NAME, USERNAME, api_key)
        log.info("OpenAI API key has been securely saved to the system keyring.")
        return True
    except Exception as e:
        log.error(f"Failed to save API key to keyring: {e}", exc_info=True)
        return False

def load_api_key() -> str | None:
    """Loads the API key from the system's keyring."""
    try:
        api_key = keyring.get_password(SERVICE_NAME, USERNAME)
        if api_key:
            log.info("OpenAI API key loaded from system keyring.")
            return api_key
        else:
            log.warning("OpenAI API key not found in system keyring.")
            return None
    except Exception as e:
        log.error(f"Failed to load API key from keyring: {e}", exc_info=True)
        return None