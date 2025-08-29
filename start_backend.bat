```batch
@echo off
echo 🚀 Starting Jarvis AI Backend Server
echo ========================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python from [https://python.org/](https://python.org/)
    pause
    exit /b 1
)

echo ✅ Python found

REM Check if app directory exists
if not exist "app" (
    echo ❌ Backend directory 'app' not found!
    echo 💡 Make sure you're in the correct directory
    pause
    exit /b 1
)

REM Check if main.py exists
if not exist "app\main.py" (
    echo ❌ main.py not found in app directory!
    pause
    exit /b 1
)

echo 📦 Installing Python dependencies...
python -m pip install -r requirements.txt

echo 🚀 Starting FastAPI server on http://localhost:8000...
echo 📚 API docs will be available at: http://localhost:8000/docs
echo.
echo ⚠️ Keep this window open - closing it will stop the backend server
echo 🛑 Press Ctrl+C to stop the server
echo.

cd app
python main.py

pause

