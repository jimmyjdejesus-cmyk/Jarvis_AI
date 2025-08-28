@echo off
echo 🚀 Starting Cerebro Galaxy Backend (Windows)
echo ================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python from https://python.org/
    pause
    exit /b 1
)

echo ✅ Python found

REM Install dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

REM Navigate to app directory
if not exist "app" (
    echo ❌ App directory not found! Make sure you're in the correct directory.
    pause
    exit /b 1
)

cd app

REM Check if main.py exists
if not exist "main.py" (
    echo ❌ main.py not found in app directory!
    pause
    exit /b 1
)

echo 🧠 Starting Cerebro Galaxy Backend...
echo 📡 Backend will be available at: http://localhost:8000
echo 🔌 WebSocket endpoint: ws://localhost:8000/ws/{client_id}
echo.
echo ⚠️ Keep this window open - closing it will stop the backend
echo 🛑 Press Ctrl+C to stop the server
echo.

REM Start the backend
python main.py

pause

