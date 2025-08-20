#!/usr/bin/env python3
"""
Jarvis AI Launcher
Choose how you want to run Jarvis AI: Web UI, Desktop App, or CLI
"""

import sys
import subprocess
import os
from pathlib import Path

def check_dependency(package):
    """Check if a package is installed."""
    try:
        __import__(package)
        return True
    except ImportError:
        return False

def install_package(package):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def show_menu():
    """Show the main menu."""
    print("🤖 JARVIS AI LAUNCHER")
    print("=" * 30)
    print()
    print("Choose how to run Jarvis AI:")
    print()
    print("1. 🖥️  Desktop App (Basic) - Uses built-in tkinter")
    print("2. 🎨 Desktop App (Modern) - Uses customtkinter (sleek UI)")
    print("3. 🌐 Web UI - Streamlit interface")
    print("4. 💻 CLI - Command line interface")
    print("5. 🧪 Test Workflow - Run agentic workflow test")
    print("6. 📊 Open LangSmith Dashboard")
    print("7. ❌ Exit")
    print()

def run_desktop_basic():
    """Run the basic desktop app."""
    print("🖥️ Starting Basic Desktop App...")
    subprocess.run([sys.executable, "desktop_app.py"])

def run_desktop_modern():
    """Run the modern desktop app."""
    if not check_dependency("customtkinter"):
        print("📦 CustomTkinter not found. Installing...")
        if install_package("customtkinter"):
            print("✅ CustomTkinter installed successfully!")
        else:
            print("❌ Failed to install CustomTkinter. Using basic desktop app instead.")
            run_desktop_basic()
            return
    
    print("🎨 Starting Modern Desktop App...")
    subprocess.run([sys.executable, "modern_desktop_app.py"])

def run_web_ui():
    """Run the Streamlit web UI."""
    if not check_dependency("streamlit"):
        print("📦 Streamlit not found. Installing...")
        if install_package("streamlit"):
            print("✅ Streamlit installed successfully!")
        else:
            print("❌ Failed to install Streamlit.")
            return
    
    print("🌐 Starting Web UI...")
    print("📍 Will open in your browser at http://localhost:8501")
    
    # Try new clean app.py first, fallback to legacy
    app_files = ["app.py", "legacy/app.py"]
    
    for app_file in app_files:
        if Path(app_file).exists():
            print(f"📁 Using: {app_file}")
            subprocess.run([sys.executable, "-m", "streamlit", "run", app_file])
            break
    else:
        print("❌ No app.py file found")

def run_cli():
    """Run the CLI interface."""
    if Path("v2/enhanced_interactive.py").exists():
        print("💻 Starting Enhanced CLI...")
        subprocess.run([sys.executable, "v2/enhanced_interactive.py"])
    elif Path("jarvis_standalone.py").exists():
        print("💻 Starting Standalone CLI...")
        subprocess.run([sys.executable, "jarvis_standalone.py"])
    else:
        print("❌ CLI interface not found.")

def test_workflow():
    """Run the workflow test."""
    print("🧪 Running Agentic Workflow Test...")
    subprocess.run([sys.executable, "test_full_workflow.py"])

def open_langsmith():
    """Open LangSmith dashboard."""
    import webbrowser
    print("📊 Opening LangSmith Dashboard...")
    webbrowser.open('https://smith.langchain.com/')

def main():
    """Main launcher function."""
    while True:
        show_menu()
        
        try:
            choice = input("Enter your choice (1-7): ").strip()
            print()
            
            if choice == "1":
                run_desktop_basic()
            elif choice == "2":
                run_desktop_modern()
            elif choice == "3":
                run_web_ui()
            elif choice == "4":
                run_cli()
            elif choice == "5":
                test_workflow()
            elif choice == "6":
                open_langsmith()
            elif choice == "7":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
            
            print("\n" + "=" * 50 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Change to the script directory
    os.chdir(Path(__file__).parent)
    main()
