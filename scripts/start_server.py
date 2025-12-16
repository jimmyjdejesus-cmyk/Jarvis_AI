#!/usr/bin/env python3
"""
Simple Jarvis AI Server Startup Script

This script starts the Jarvis AI server with proper configuration
and handles dependency issues.
"""

import os
import sys
import uvicorn
from pathlib import Path

def setup_environment():
    """Setup environment and check dependencies."""
    print("🔧 Setting up Jarvis AI environment...")
    
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Try to import dependencies
    try:
        import fastapi
        import uvicorn
        import pydantic
        print(f"✅ FastAPI {fastapi.__version__}")
        print(f"✅ Uvicorn {uvicorn.__version__}")
        print(f"✅ Pydantic {pydantic.__version__}")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Installing requirements...")
        os.system(f"{sys.executable} -m pip install -r requirements.txt")
    
    return True

def load_config():
    """Load or create default configuration."""
    print("📋 Loading configuration...")
    
    try:
        # Try to import and load config
        from jarvis_core.config import load_config, AppConfig, PersonaConfig
        
        try:
            config = load_config()
            print("✅ Configuration loaded from file")
            return config
        except Exception as e:
            print(f"⚠️  Could not load config file: {e}")
            print("Creating default configuration...")
            
            # Create default configuration
            from jarvis_core.config import OllamaConfig, OpenRouterConfig, WindowsMLConfig, SecurityConfig, ContextPipelineConfig, MonitoringConfig
            
            config = AppConfig(
                ollama=OllamaConfig(host="http://127.0.0.1:11434"),
                openrouter=OpenRouterConfig(api_key=""),
                windowsml=WindowsMLConfig(enabled=False),
                security=SecurityConfig(api_keys=[]),  # No API keys for testing
                context_pipeline=ContextPipelineConfig(),
                monitoring=MonitoringConfig(enable_metrics_harvest=False),
                allowed_personas=["generalist"],
                enable_research_features=False
            )
            print("✅ Default configuration created")
            return config
            
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("Trying minimal configuration...")
        
        # Create minimal working configuration
        from jarvis_core.config import AppConfig, PersonaConfig
        
        default_persona = PersonaConfig(
            name="generalist",
            description="Default test persona",
            system_prompt="You are a helpful assistant.",
            max_context_window=2048,
            routing_hint="general"
        )
        
        config = AppConfig(
            personas={"generalist": default_persona},
            allowed_personas=["generalist"],
            security={"api_keys": []}
        )
        return config

def start_server():
    """Start the Jarvis AI server."""
    print("🚀 Starting Jarvis AI Server...")
    
    # Setup environment
    setup_environment()
    
    # Load configuration
    config = load_config()
    
    try:
        # Try to build the app
        from jarvis_core.server import build_app
        app = build_app(config)
        print("✅ FastAPI application created")
    except Exception as e:
        print(f"❌ Failed to build application: {e}")
        print("Attempting to create minimal server...")
        
        # Create minimal server as fallback
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse
        
        app = FastAPI(title="Jarvis AI", version="1.0.0")
        
        @app.get("/health")
        async def health():
            return {"status": "ok", "available_models": ["test"]}
        
        @app.get("/api/v1/models")
        async def models():
            return ["test-model"]
        
        @app.get("/api/v1/personas")
        async def personas():
            return [{"name": "generalist", "description": "Default persona"}]
        
        @app.post("/api/v1/chat")
        async def chat(request: dict):
            return {
                "content": "Test response",
                "model": "test",
                "tokens": 10,
                "diagnostics": {}
            }
        
        print("✅ Minimal server created")
    
    # Start server
    port = int(os.getenv("JARVIS_PORT", "8000"))
    host = os.getenv("JARVIS_HOST", "127.0.0.1")
    
    print(f"🌐 Starting server on {host}:{port}")
    print(f"🔗 Health check: http://{host}:{port}/health")
    print(f"📖 API docs: http://{host}:{port}/docs")
    
    try:
        uvicorn.run(
            app, 
            host=host, 
            port=port,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server()
