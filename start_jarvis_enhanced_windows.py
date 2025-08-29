#!/usr/bin/env python3
"""
Enhanced Jarvis AI Startup Script - Windows Optimized
Handles Windows-specific npm and Node.js issues
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def print_windows_setup_guide():
    """Print setup guide for Windows users"""
    print("🪟 Windows Setup Guide")
    print("=" * 50)
    print("If you're having issues with npm/Node.js, follow these steps:")
    print()
    print("1. 📥 Download and install Node.js:")
    print("   • Visit: https://nodejs.org/")
    print("   • Download the LTS version (recommended)")
    print("   • During installation, check 'Add to PATH'")
    print()
    print("2. 🔄 Restart your command prompt/PowerShell")
    print("   • Close current terminal")
    print("   • Open new PowerShell as Administrator")
    print()
    print("3. ✅ Verify installation:")
    print("   • Run: node --version")
    print("   • Run: npm --version")
    print()
    print("4. 🚀 Try running the script again:")
    print("   • python start_jarvis_enhanced.py")
    print()

def check_windows_node_installation():
    """Check Node.js installation on Windows"""
    print("🔍 Checking Windows Node.js installation...")
    
    # Check multiple possible npm locations on Windows
    npm_commands = ["npm", "npm.cmd", "npm.exe"]
    node_commands = ["node", "node.exe"]
    
    # Check Node.js
    node_found = False
    for cmd in node_commands:
        try:
            result = subprocess.run([cmd, "--version"], capture_output=True, text=True, shell=False)
            if result.returncode == 0:
                print(f"✅ Node.js found: {result.stdout.strip()}")
                node_found = True
                break
        except:
            continue
    
    if not node_found:
        print("❌ Node.js not found")
        return False
    
    # Check npm
    npm_found = False
    for cmd in npm_commands:
        try:
            result = subprocess.run([cmd, "--version"], capture_output=True, text=True, shell=False)
            if result.returncode == 0:
                print(f"✅ npm found: {result.stdout.strip()}")
                npm_found = True
                break
        except:
            continue
    
    if not npm_found:
        print("❌ npm not found")
        return False
    
    return True

def install_dependencies_windows():
    """Install dependencies with Windows-specific handling"""
    print("📦 Installing dependencies (Windows mode)...")
    
    # Install Python dependencies
    try:
        print("Installing Python dependencies...")
        subprocess.run([
            sys.executable, "-m", "pip", "install",
            "fastapi==0.111.0", "uvicorn", "websockets", "redis", "requests", "pydantic>=2.7,<3"
        ], check=True, shell=False)
        print("✅ Python dependencies installed")
    except subprocess.CalledProcessError:
        print("❌ Failed to install Python dependencies")
        return False
    
    # Install Node.js dependencies
    frontend_path = Path("src-tauri")
    if frontend_path.exists():
        node_modules = frontend_path / "node_modules"
        if not node_modules.exists():
            print("Installing Node.js dependencies...")
            try:
                # Try different npm commands for Windows
                for npm_cmd in ["npm", "npm.cmd"]:
                    try:
                        # First try normal install
                        subprocess.run([npm_cmd, "install"], cwd=frontend_path, check=True, shell=False)
                        print("✅ Node.js dependencies installed")
                        return True
                    except subprocess.CalledProcessError:
                        # If normal install fails, try with --legacy-peer-deps
                        try:
                            print("⚠️ Retrying with --legacy-peer-deps...")
                            subprocess.run([npm_cmd, "install", "--legacy-peer-deps"], cwd=frontend_path, check=True, shell=False)
                            print("✅ Node.js dependencies installed (with legacy peer deps)")
                            return True
                        except subprocess.CalledProcessError:
                            continue
                    except FileNotFoundError:
                        continue
                
                print("❌ Failed to install Node.js dependencies")
                print("💡 Try manually running: npm install --legacy-peer-deps")
                return False
            except Exception as e:
                print(f"❌ Error installing dependencies: {e}")
                return False
        else:
            print("✅ Node.js dependencies already installed")
    
    return True

def start_backend_windows():
    """Start backend with Windows-specific handling"""
    print("🚀 Starting FastAPI backend server...")
    backend_path = Path("app")
    
    if not backend_path.exists():
        print("❌ Backend directory 'app' not found!")
        return None
    
    # Check if main.py exists
    main_file = backend_path / "main.py"
    if not main_file.exists():
        print("❌ main.py not found in app directory!")
        return None
    
    try:
        # Start the backend server in a new console window
        print("🚀 Starting FastAPI server on http://localhost:8000...")
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=backend_path,
            shell=False,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        # Give it a moment to start
        time.sleep(4)
        
        if process.poll() is None:
            print("✅ Backend server started successfully")
            print("📡 API available at: http://localhost:8000")
            print("📚 API docs available at: http://localhost:8000/docs")
            
            # Test the connection
            try:
                import requests
                requests.get("http://localhost:8000/health", timeout=5)
                print("✅ Backend health check passed")
            except ImportError:
                print("⚠️ 'requests' not installed; skipping backend health check")
            except Exception:
                print("⚠️ Backend starting up, health check will retry...")
            
            return process
        else:
            print("❌ Backend failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def start_frontend_windows():
    """Start frontend with Windows-specific handling"""
    print("🎨 Starting React frontend development server...")
    frontend_path = Path("src-tauri")
    
    if not frontend_path.exists():
        print("❌ Frontend directory 'src-tauri' not found!")
        return None
    
    try:
        # Try different npm commands for Windows
        for npm_cmd in ["npm", "npm.cmd"]:
            try:
                process = subprocess.Popen(
                    [npm_cmd, "run", "dev"],
                    cwd=frontend_path,
                    shell=False,
                    creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                )
                
                # Give it a moment to start
                time.sleep(5)
                
                if process.poll() is None:
                    print("✅ Frontend server started successfully")
                    print("🌐 Frontend available at: http://localhost:5173")
                    return process
                else:
                    continue
                    
            except FileNotFoundError:
                continue
        
        print("❌ Failed to start frontend server")
        return None
            
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return None

def main():
    """Main function optimized for Windows"""
    print("🤖 Enhanced Jarvis AI - Windows Startup")
    print("=" * 50)
    
    # Check for help
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print_windows_setup_guide()
        return
    
    # Check if we're on Windows
    if os.name != 'nt':
        print("⚠️ This script is optimized for Windows.")
        print("💡 Use 'python start_jarvis_enhanced.py' for cross-platform support.")
        return
    
    # Check Node.js installation
    if not check_windows_node_installation():
        print("\n❌ Node.js/npm not properly installed")
        print_windows_setup_guide()
        return
    
    # Install dependencies
    if not install_dependencies_windows():
        print("\n❌ Failed to install dependencies")
        print("💡 Try running as Administrator")
        return
    
    print("\n🚀 Starting Enhanced Jarvis AI System...")
    print("=" * 50)
    
    # Start backend
    backend_process = start_backend_windows()
    if not backend_process:
        print("❌ Failed to start backend server")
        return
    
    # Start frontend
    frontend_process = start_frontend_windows()
    if not frontend_process:
        print("❌ Failed to start frontend server")
        if backend_process:
            backend_process.terminate()
        return
    
    print("\n🎉 Enhanced Jarvis AI System Started Successfully!")
    print("=" * 50)
    print("🔗 Access the application:")
    print("   • Frontend UI: http://localhost:5173")
    print("   • Backend API: http://localhost:8000")
    print("   • API Documentation: http://localhost:8000/docs")
    
    print("\n💡 Windows Tips:")
    print("   • Both servers are running in separate console windows")
    print("   • Close the console windows to stop the servers")
    print("   • Or press Ctrl+C in this window to stop both")
    
    # Open browser
    try:
        time.sleep(3)
        webbrowser.open("http://localhost:5173")
        print("🌐 Opening browser...")
    except:
        pass
    
    try:
        # Keep the script running
        print("\n⌨️  Press Ctrl+C to stop all servers")
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("❌ Backend process stopped")
                break
            if frontend_process.poll() is not None:
                print("❌ Frontend process stopped")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Enhanced Jarvis AI System...")
        
        # Terminate processes
        try:
            if backend_process:
                backend_process.terminate()
                print("✅ Backend server stopped")
        except:
            pass
        
        try:
            if frontend_process:
                frontend_process.terminate()
                print("✅ Frontend server stopped")
        except:
            pass
        
        print("👋 Enhanced Jarvis AI System stopped successfully!")

if __name__ == "__main__":
    main()