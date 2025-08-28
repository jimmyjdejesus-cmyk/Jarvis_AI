#!/usr/bin/env python3
"""
Simple Backend Starter for Jarvis AI
Starts only the FastAPI backend server
"""

import subprocess
import sys
import os
from pathlib import Path

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting Jarvis AI Backend Server...")
    
    backend_path = Path("app")
    if not backend_path.exists():
        print("❌ Backend directory 'app' not found!")
        print("💡 Make sure you're in the correct directory")
        return False
    
    # Check if main.py exists
    main_file = backend_path / "main.py"
    if not main_file.exists():
        print("❌ main.py not found in app directory!")
        return False
    
    try:
        # Install Python dependencies first
        print("📦 Installing Python dependencies...")
        subprocess.run([
            sys.executable, "-m", "pip", "install",
            "fastapi==0.111.0", "uvicorn", "websockets", "redis", "pydantic>=2.7,<3"
        ], check=True)
        print("✅ Python dependencies installed")
        
        # Start the backend server
        print("🚀 Starting FastAPI server on http://localhost:8000...")
        subprocess.run([sys.executable, "main.py"], cwd=backend_path)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start backend: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🤖 Jarvis AI Backend Starter")
    print("=" * 40)
    print("This will start only the backend server.")
    print("Use start_jarvis.bat for the full system.")
    print("=" * 40)
    
    success = start_backend()
    if success:
        print("👋 Backend stopped successfully!")
    else:
        print("❌ Backend failed to start!")
        input("Press Enter to exit...")
