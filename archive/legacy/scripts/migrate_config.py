"""Configuration migration utility to unify legacy and new config systems."""

import os
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

def migrate_legacy_env_to_config() -> Dict[str, Any]:
    """Migrate legacy environment variables to new config format."""
    
    # Map legacy env vars to new config structure
    config_data = {
        "ollama": {
            "host": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            "model": os.getenv("OLLAMA_MODEL", "llama3.1:8b-instruct-q4_K_M"),
            "timeout": int(os.getenv("OLLAMA_TIMEOUT", "120")),
            "max_tokens": int(os.getenv("OLLAMA_MAX_TOKENS", "4096")),
            "temperature": float(os.getenv("OLLAMA_TEMPERATURE", "0.7")),
            "top_p": float(os.getenv("OLLAMA_TOP_P", "0.9"))
        },
        "agents": {
            "max_concurrent": int(os.getenv("MAX_CONCURRENT_AGENTS", "5")),
            "timeout": int(os.getenv("AGENT_TIMEOUT", "300")),
            "memory_limit_mb": int(os.getenv("MEMORY_LIMIT_MB", "8192")),
            "enable_logging": os.getenv("ENABLE_AGENT_LOGGING", "true").lower() == "true",
            "auto_save_state": os.getenv("AUTO_SAVE_STATE", "true").lower() == "true",
            "collaboration_enabled": os.getenv("COLLABORATION_ENABLED", "true").lower() == "true"
        },
        "research": {
            "arxiv_max_results": int(os.getenv("ARXIV_MAX_RESULTS", "50")),
            "enable_web_search": os.getenv("ENABLE_WEB_SEARCH", "true").lower() == "true",
            "cache_ttl": int(os.getenv("RESEARCH_CACHE_TTL", "3600")),
            "max_paper_downloads": int(os.getenv("MAX_PAPER_DOWNLOADS", "100")),
            "enable_semantic_search": os.getenv("ENABLE_SEMANTIC_SEARCH", "true").lower() == "true",
            "knowledge_graph_enabled": os.getenv("KNOWLEDGE_GRAPH_ENABLED", "true").lower() == "true"
        },
        "gui": {
            "theme": os.getenv("THEME", "dark"),
            "window_width": int(os.getenv("WINDOW_WIDTH", "1400")),
            "window_height": int(os.getenv("WINDOW_HEIGHT", "900")),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "auto_save_conversations": os.getenv("AUTO_SAVE_CONVERSATIONS", "true").lower() == "true",
            "enable_notifications": os.getenv("ENABLE_NOTIFICATIONS", "true").lower() == "true"
        },
        "api": {
            "host": os.getenv("API_HOST", "127.0.0.1"),
            "port": int(os.getenv("API_PORT", "8000")),
            "workers": int(os.getenv("API_WORKERS", "4")),
            "enable_cors": os.getenv("ENABLE_CORS", "true").lower() == "true",
            "enable_auth": os.getenv("ENABLE_AUTH", "false").lower() == "true",
            "max_request_size_mb": int(os.getenv("MAX_REQUEST_SIZE_MB", "100"))
        },
        "database": {
            "url": os.getenv("DATABASE_URL", "sqlite:///jarvis.db"),
            "enable_redis_cache": os.getenv("ENABLE_REDIS_CACHE", "false").lower() == "true",
            "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379")
        }
    }
    
    return config_data

def save_unified_config(config_data: Dict[str, Any], config_path: Optional[Path] = None) -> Path:
    """Save unified config to ~/.jarvis/config.json."""
    if config_path is None:
        config_path = Path.home() / ".jarvis" / "config.json"
    
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2)
    
    return config_path

def migrate_legacy_config_files() -> Optional[Path]:
    """Migrate any existing legacy config files."""
    legacy_configs = [
        Path("config.json"),
        Path("jarvis_config.json"),
        Path(".jarvis_config"),
        Path.home() / ".jarvis" / "legacy_config.json"
    ]
    
    for config_file in legacy_configs:
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    legacy_data = json.load(f)
                print(f"Found legacy config at {config_file}")
                # Could add specific migration logic here
                return config_file
            except Exception as e:
                print(f"Failed to read {config_file}: {e}")
    
    return None

def main():
    """Main migration function."""
    print("🔄 Migrating configuration to unified format...")
    
    # Check for existing config
    config_path = Path.home() / ".jarvis" / "config.json"
    if config_path.exists():
        print(f"⚠️  Existing config found at {config_path}")
        response = input("Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("Migration cancelled.")
            return
    
    # Migrate from environment variables
    config_data = migrate_legacy_env_to_config()
    
    # Check for legacy config files
    legacy_config = migrate_legacy_config_files()
    if legacy_config:
        print(f"ℹ️  Found legacy config at {legacy_config}")
        print("   You may want to manually merge any custom settings.")
    
    # Save unified config
    saved_path = save_unified_config(config_data)
    print(f"✅ Unified config saved to {saved_path}")
    
    # Create .env template
    env_template = Path(".env.template")
    env_content = """# Jarvis AI Configuration
# Copy this to .env and customize as needed

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b-instruct-q4_K_M
OLLAMA_TIMEOUT=120
OLLAMA_MAX_TOKENS=4096
OLLAMA_TEMPERATURE=0.7
OLLAMA_TOP_P=0.9

# Agent Configuration
MAX_CONCURRENT_AGENTS=5
AGENT_TIMEOUT=300
MEMORY_LIMIT_MB=8192
ENABLE_AGENT_LOGGING=true
AUTO_SAVE_STATE=true
COLLABORATION_ENABLED=true

# Research Configuration
ARXIV_MAX_RESULTS=50
ENABLE_WEB_SEARCH=true
RESEARCH_CACHE_TTL=3600
MAX_PAPER_DOWNLOADS=100
ENABLE_SEMANTIC_SEARCH=true
KNOWLEDGE_GRAPH_ENABLED=true

# GUI Configuration
THEME=dark
WINDOW_WIDTH=1400
WINDOW_HEIGHT=900
LOG_LEVEL=INFO
AUTO_SAVE_CONVERSATIONS=true
ENABLE_NOTIFICATIONS=true

# API Configuration
API_HOST=127.0.0.1
API_PORT=8000
API_WORKERS=4
ENABLE_CORS=true
ENABLE_AUTH=false
MAX_REQUEST_SIZE_MB=100

# Database Configuration
DATABASE_URL=sqlite:///jarvis.db
ENABLE_REDIS_CACHE=false
REDIS_URL=redis://localhost:6379
"""
    
    with open(env_template, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"📝 Environment template created at {env_template}")
    print("\n🎉 Configuration migration complete!")
    print("\nNext steps:")
    print("1. Copy .env.template to .env and customize")
    print("2. Both GUI and backend will now use ~/.jarvis/config.json")
    print("3. Environment variables will override config file values")

if __name__ == "__main__":
    main()
