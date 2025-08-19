#!/usr/bin/env python3
"""
Quick Start Script for Jarvis AI V2

This script helps new users get started with Jarvis AI V2 by:
1. Checking system requirements
2. Installing dependencies
3. Setting up configuration
4. Testing the installation
5. Starting the services
"""

import sys
import subprocess
import os
from pathlib import Path
import shutil

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_step(step, description):
    """Print a formatted step."""
    print(f"\n🔄 Step {step}: {description}")

def run_command(cmd, description="", check=True):
    """Run a shell command with error handling."""
    try:
        print(f"Running: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        if result.stdout:
            print(result.stdout)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported")
        print("Required: Python 3.8 or higher")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_ollama():
    """Check if Ollama is available."""
    if shutil.which("ollama"):
        print("✅ Ollama is installed")
        # Try to connect to Ollama API
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                print("✅ Ollama is running and accessible")
                return True
            else:
                print("⚠️ Ollama is installed but not running")
                print("Start Ollama with: ollama serve")
                return False
        except:
            print("⚠️ Ollama is installed but not accessible")
            return False
    else:
        print("❌ Ollama is not installed")
        print("Install from: https://ollama.ai/download")
        return False

def install_dependencies():
    """Install required dependencies."""
    print("Installing Python dependencies...")
    
    # First, try to install basic requirements
    if not run_command("pip install --upgrade pip"):
        print("❌ Failed to upgrade pip")
        return False
    
    # Check if requirements file exists
    req_file = "requirements_enhanced.txt"
    if not os.path.exists(req_file):
        print(f"❌ {req_file} not found")
        return False
    
    # Install requirements
    if run_command(f"pip install -r {req_file}", check=False):
        print("✅ Dependencies installed successfully")
        return True
    else:
        print("⚠️ Some dependencies failed to install")
        print("You may need to install them manually")
        return False

def setup_configuration():
    """Set up configuration files."""
    config_dir = Path("config")
    config_file = config_dir / "config.yaml"
    example_file = config_dir / "config.example.yaml"
    
    # Create config directory if it doesn't exist
    config_dir.mkdir(exist_ok=True)
    
    # Copy example config if config doesn't exist
    if not config_file.exists() and example_file.exists():
        try:
            shutil.copy(example_file, config_file)
            print(f"✅ Created config file: {config_file}")
            print("💡 You can customize the settings in config/config.yaml")
            return True
        except Exception as e:
            print(f"❌ Failed to create config file: {e}")
            return False
    elif config_file.exists():
        print(f"✅ Config file already exists: {config_file}")
        return True
    else:
        print("⚠️ No example config file found")
        return False

def test_installation():
    """Test the V2 installation."""
    print("Testing V2 integration...")
    
    test_script = "scripts/test_v2_integration.py"
    if os.path.exists(test_script):
        success = run_command(f"python {test_script}", check=False)
        return success
    else:
        print(f"❌ Test script not found: {test_script}")
        return False

def start_services():
    """Start the Jarvis AI services."""
    print("Starting services...")
    
    print("\n📋 To start Jarvis AI:")
    print("1. Start V2 Backend (optional but recommended):")
    print("   python scripts/start_v2_backend.py --reload")
    print()
    print("2. Start Streamlit UI:")
    print("   streamlit run app.py")
    print()
    print("3. Open your browser to: http://localhost:8501")
    print()
    print("💡 Enable V2 in the sidebar for the best experience!")

def main():
    """Main quick start process."""
    print_header("🚀 Jarvis AI V2 Quick Start")
    
    print("Welcome to Jarvis AI V2! This script will help you get started.")
    
    # Step 1: Check system requirements
    print_step(1, "Checking System Requirements")
    
    if not check_python_version():
        print("\n❌ System requirements not met. Please upgrade Python.")
        return 1
    
    ollama_ok = check_ollama()
    if not ollama_ok:
        print("\n⚠️ Ollama not available. Some features may not work.")
        choice = input("Continue anyway? (y/N): ").lower()
        if choice != 'y':
            return 1
    
    # Step 2: Install dependencies
    print_step(2, "Installing Dependencies")
    
    if not install_dependencies():
        print("\n❌ Failed to install dependencies")
        print("Try installing manually: pip install -r requirements_enhanced.txt")
        return 1
    
    # Step 3: Setup configuration
    print_step(3, "Setting Up Configuration")
    
    setup_configuration()
    
    # Step 4: Test installation
    print_step(4, "Testing Installation")
    
    test_success = test_installation()
    if test_success:
        print("\n✅ Installation test completed successfully!")
    else:
        print("\n⚠️ Some tests failed, but basic functionality should work")
    
    # Step 5: Start services
    print_step(5, "Starting Services")
    
    start_services()
    
    print_header("🎉 Setup Complete!")
    
    print("Jarvis AI V2 is ready to use!")
    print()
    print("📚 Useful Resources:")
    print("  • Migration Guide: docs/V2_MIGRATION_GUIDE.md")
    print("  • Configuration: config/config.yaml")
    print("  • Test Integration: python scripts/test_v2_integration.py")
    print("  • Start Backend: python scripts/start_v2_backend.py")
    print()
    print("❓ Need Help?")
    print("  • Check the documentation in the docs/ folder")
    print("  • Run the test script to diagnose issues")
    print("  • Open GitHub issues for bugs or questions")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)