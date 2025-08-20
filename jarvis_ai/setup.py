"""
Setup entry point for Jarvis AI
Reuses the existing enhanced setup system
"""

import sys
from pathlib import Path

# Add legacy directory to path for imports
current_dir = Path(__file__).parent.parent
legacy_dir = current_dir / "legacy"
sys.path.insert(0, str(legacy_dir))

def main():
    """Main setup entry point - delegates to enhanced setup."""
    try:
        # Import and run the existing enhanced setup
        from setup_enhanced import main as enhanced_main
        enhanced_main()
    except ImportError as e:
        print(f"❌ Could not import enhanced setup: {e}")
        print("Running basic setup...")
        basic_setup()
    except Exception as e:
    setup_enhanced_path = legacy_dir / "setup_enhanced.py"
    if setup_enhanced_path.exists():
        try:
            # Import and run the existing enhanced setup
            from setup_enhanced import main as enhanced_main
            enhanced_main()
        except ImportError as e:
            print(f"❌ Could not import enhanced setup: {e}")
            print("Running basic setup...")
            basic_setup()
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            sys.exit(1)
    else:
        print(f"❌ setup_enhanced.py not found in {legacy_dir}")
        print("Running basic setup...")
        basic_setup()

def basic_setup():
    """Basic setup fallback if enhanced setup isn't available."""
    import subprocess
    import os
    
    print("🔧 Running basic Jarvis AI setup...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print("✅ Python version check passed")
    
    # Install dependencies
    try:
        print("📦 Installing dependencies...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ])
        
        # Install from requirements if available
        requirements_files = [
            current_dir / "legacy" / "requirements_enhanced.txt",
            current_dir / "development" / "requirements.txt"
        ]
        
        for req_file in requirements_files:
            if req_file.exists():
                print(f"📦 Installing from {req_file}")
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "-r", str(req_file)
                ])
                break
        else:
            print("📦 Installing basic dependencies...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "streamlit>=1.30.0",
                "langchain>=0.1.0",
                "langgraph>=0.0.40",
                "fastapi>=0.100.0",
                "uvicorn>=0.22.0"
            ])
        
        print("✅ Dependencies installed successfully")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)
    
    # Create basic directory structure
    try:
        print("📁 Creating directory structure...")
        for directory in ["data", "logs", "config", "plugins"]:
            os.makedirs(directory, exist_ok=True)
        print("✅ Directory structure created")
        
    except Exception as e:
        print(f"❌ Failed to create directories: {e}")
        sys.exit(1)
    
    print("🎉 Basic setup completed successfully!")
    print("   Next steps:")
    print("   1. Run 'jarvis config --init' to initialize configuration")
    print("   2. Run 'jarvis run' to start the application")

if __name__ == "__main__":
    main()