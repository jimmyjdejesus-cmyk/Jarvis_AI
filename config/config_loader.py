"""Configuration loader with profile and environment variable support."""

import os
from pathlib import Path
import yaml

CONFIG_DIR = Path(__file__).parent
PROFILES_DIR = CONFIG_DIR / "profiles"


def load_profile(name: str) -> dict:
    """Load a configuration profile by name."""
    profile_file = PROFILES_DIR / f"{name}.yaml"
    if profile_file.exists():
        with open(profile_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def _convert(value: str):
    """Best-effort conversion of strings to native Python types."""
    lower = value.lower()
    if lower in {"true", "false"}:
        return lower == "true"
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def apply_env_overrides(config: dict) -> dict:
    """Apply environment variable overrides with JARVIS__ prefix using double underscores for nesting."""
    prefix = "JARVIS__"
    for key, value in os.environ.items():
        if key.startswith(prefix):
            # convert JARVIS__FOO__BAR to config["foo"]["bar"]
            path = key[len(prefix):].lower().split("__")
            current = config
            for part in path[:-1]:
                current = current.setdefault(part, {})
            current[path[-1]] = _convert(value)
    return config


def load_config() -> dict:
    """Load configuration using profile and environment variables."""
    profile = os.getenv("CONFIG_PROFILE", "development")
    config = {}
    # load default toggles
    default_file = CONFIG_DIR / "default.yaml"
    if default_file.exists():
        with open(default_file, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
            if cfg:
                config.update(cfg)
    # merge profile
    config.update(load_profile(profile))
    # apply overrides
    return apply_env_overrides(config)


if __name__ == "__main__":
    import pprint
    pprint.pp(load_config())
