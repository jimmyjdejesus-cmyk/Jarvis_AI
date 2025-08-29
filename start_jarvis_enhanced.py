#!/usr/bin/env python3
"""
Enhanced Jarvis AI Startup Script
Starts both backend and frontend servers for the enhanced UI system
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def check_npm_available():
    """Check if npm is available"""
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check Python dependencies
    try:
        import fastapi
        import uvicorn
        import websockets
        import redis
        import requests
        print("✅ Python dependencies found")
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("📦 Installing Python dependencies...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "fastapi==0.111.0", "uvicorn", "websockets", "redis", "requests", "pydantic>=2.7,<3"], check=True)
            print("✅ Python dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install Python dependencies")
            return False
    
    # Check if Node.js is available
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js found: {result.stdout.strip()}")
        else:
            print("❌ Node.js not found. Please install Node.js to run the frontend.")
            print("📥 Download from: https://nodejs.org/")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found. Please install Node.js to run the frontend.")
        print("📥 Download from: https://nodejs.org/")
        print("💡 Make sure to add Node.js to your system PATH during installation")
        return False
    
    # Check if npm is available
    if not check_npm_available():
        print("❌ npm not found. npm should be installed with Node.js.")
        print("💡 Try reinstalling Node.js from https://nodejs.org/")
        return False
    else:
        print("✅ npm found")
    
    # Check if npm dependencies are installed
    frontend_path = Path("src-tauri")
    if frontend_path.exists():
        node_modules = frontend_path / "node_modules"
        if not node_modules.exists():
            print("📦 Installing Node.js dependencies...")
            try:
                # First try normal install
                result = subprocess.run(["npm", "install"], cwd=frontend_path, capture_output=True, text=True, check=True)
                print("✅ Node.js dependencies installed successfully")
            except subprocess.CalledProcessError as e:
                # If normal install fails, try with --legacy-peer-deps
                try:
                    print("⚠️ Retrying with --legacy-peer-deps...")
                    result = subprocess.run(["npm", "install", "--legacy-peer-deps"], cwd=frontend_path, capture_output=True, text=True, check=True)
                    print("✅ Node.js dependencies installed successfully (with legacy peer deps)")
                except subprocess.CalledProcessError as e2:
                    print(f"❌ Failed to install Node.js dependencies:")
                    print(f"Error: {e2.stderr}")
                    print("💡 Try manually running: npm install --legacy-peer-deps")
                    return False
            except FileNotFoundError:
                print("❌ npm command not found. Please ensure Node.js and npm are properly installed.")
                return False
        else:
            print("✅ Node.js dependencies found")
    else:
        print("⚠️ Frontend directory 'src-tauri' not found. Frontend features will not be available.")
    
    return True

def start_backend():
    """Start the FastAPI backend server"""
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
        # Install Python dependencies first
        print("📦 Installing Python dependencies...")
        subprocess.run([
            sys.executable, "-m", "pip", "install",
            "fastapi==0.111.0", "uvicorn", "websockets", "redis", "requests", "pydantic>=2.7,<3"
        ], check=True, capture_output=True)
        print("✅ Python dependencies ready")
        
        # Start the backend server with proper output handling
        print("🚀 Starting FastAPI server on http://localhost:8000...")
        
        if os.name == 'nt':  # Windows
            # On Windows, create a new console window for the backend
            process = subprocess.Popen(
                [sys.executable, "main.py"],
                cwd=backend_path,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:  # Unix/Linux/macOS
            process = subprocess.Popen(
                [sys.executable, "main.py"],
                cwd=backend_path
            )
        
        # Give it a moment to start
        time.sleep(3)
        
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
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return None
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def start_frontend():
    """Start the React frontend development server"""
    print("🎨 Starting React frontend development server...")
    frontend_path = Path("src-tauri")
    
    if not frontend_path.exists():
        print("❌ Frontend directory 'src-tauri' not found!")
        return None
    
    # Check if npm is available before trying to start
    if not check_npm_available():
        print("❌ npm not found. Cannot start frontend server.")
        print("💡 Please install Node.js from https://nodejs.org/")
        return None
    
    try:
        # Start the frontend server
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False
        )
        
        # Give it a moment to start
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ Frontend server started successfully")
            print("🌐 Frontend available at: http://localhost:5173")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Frontend failed to start:")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return None
            
    except FileNotFoundError:
        print("❌ npm command not found. Please ensure Node.js and npm are properly installed.")
        print("📥 Download from: https://nodejs.org/")
        return None
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return None

def build_tauri_executable():
    """Build Tauri desktop executable"""
    print("🔨 Building Tauri Desktop Executable...")
    frontend_path = Path("src-tauri")
    
    if not frontend_path.exists():
        print("❌ Frontend directory 'src-tauri' not found!")
        return False
    
    # Check if npm is available before trying to build
    if not check_npm_available():
        print("❌ npm not found. Cannot build Tauri executable.")
        print("💡 Please install Node.js from https://nodejs.org/")
        return False
    
    try:
        # Install Tauri CLI if not present
        print("📦 Installing Tauri CLI...")
        result = subprocess.run(
            ["npm", "install", "@tauri-apps/cli"],
            cwd=frontend_path,
            capture_output=True,
            text=True,
            shell=False,
            check=True
        )
        print("✅ Tauri CLI installed successfully")
        
        # Build the executable
        print("🔨 Building executable (this may take several minutes)...")
        result = subprocess.run(
            ["npm", "run", "tauri:build"],
            cwd=frontend_path,
            capture_output=True,
            text=True,
            shell=False
        )
        
        if result.returncode == 0:
            print("✅ Tauri executable built successfully!")
            print("📁 Executable location:")
            
            # Find the built executable
            target_dir = frontend_path / "src-tauri" / "target" / "release"
            if target_dir.exists():
                for file in target_dir.iterdir():
                    if file.suffix in ['.exe', '.app', ''] and 'jarvis' in file.name.lower():
                        print(f"   • {file}")
            
            return True
        else:
            print(f"❌ Build failed:")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Tauri CLI:")
        print(f"Error: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ npm command not found. Please ensure Node.js and npm are properly installed.")
        print("📥 Download from: https://nodejs.org/")
        return False
    except Exception as e:
        print(f"❌ Error building executable: {e}")
        return False

def main():
    """Main startup function"""
    print("🤖 Enhanced Jarvis AI Startup Script")
    print("=" * 50)
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--build" or sys.argv[1] == "-b":
            print("🔨 Building Tauri Desktop Executable...")
            if not check_dependencies():
                print("❌ Dependency check failed. Please install missing dependencies.")
                return
            
            if build_tauri_executable():
                print("\n🎉 Build completed successfully!")
                print("📋 You can now distribute the executable file.")
            else:
                print("\n❌ Build failed. Check the error messages above.")
            return
        
        elif sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("🤖 Enhanced Jarvis AI Startup Script")
            print("\nUsage:")
            print("  python start_jarvis_enhanced.py          # Start development servers")
            print("  python start_jarvis_enhanced.py --build  # Build desktop executable")
            print("  python start_jarvis_enhanced.py --help   # Show this help")
            print("\nDevelopment Mode:")
            print("  • Starts FastAPI backend server")
            print("  • Starts React frontend development server")
            print("  • Opens browser automatically")
            print("\nBuild Mode:")
            print("  • Creates standalone desktop executable")
            print("  • Includes all dependencies")
            print("  • Ready for distribution")
            return
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed. Please install missing dependencies.")
        return
    
    print("\n🚀 Starting Enhanced Jarvis AI System...")
    print("=" * 50)
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ Failed to start backend server. Exiting.")
        return
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ Failed to start frontend server. Stopping backend.")
        backend_process.terminate()
        return
    
    print("\n🎉 Enhanced Jarvis AI System Started Successfully!")
    print("=" * 50)
    print("🔗 Access the application:")
    print("   • Frontend UI: http://localhost:5173")
    print("   • Backend API: http://localhost:8000")
    print("   • API Documentation: http://localhost:8000/docs")
    print("\n📋 Features Available:")
    print("   • 🌌 Galaxy View - Workflow visualization")
    print("   • 💬 Enhanced Chat - Customizable chat interface")
    print("   • 💀 Dead-End Shelf - Failed task management")
    print("   • 🤖 Multi-Agent Orchestration - Real-time coordination")
    print("   • ⚡ Real-time Updates - WebSocket communication")
    print("   • 📊 Performance Metrics - Live system monitoring")
    
    print("\n💡 Build Options:")
    print("   • Run 'python start_jarvis_enhanced.py --build' to create desktop executable")
    print("   • Run 'python start_jarvis_enhanced.py --help' for more options")
    
    print("\n⌨️  Press Ctrl+C to stop all servers")
    
    # Open browser
    try:
        time.sleep(2)
        webbrowser.open("http://localhost:5173")
        print("🌐 Opening browser...")
    except:
        pass
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("❌ Backend process stopped unexpectedly")
                break
            if frontend_process.poll() is not None:
                print("❌ Frontend process stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Enhanced Jarvis AI System...")
        
        # Terminate processes
        if backend_process:
            backend_process.terminate()
            print("✅ Backend server stopped")
        
        if frontend_process:
            frontend_process.terminate()
            print("✅ Frontend server stopped")
        
        print("👋 Enhanced Jarvis AI System stopped successfully!")

if __name__ == "__main__":
    main()