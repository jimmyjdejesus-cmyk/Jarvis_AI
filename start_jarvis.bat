@echo off
echo 🤖 Enhanced Jarvis AI - Windows Launcher
echo ================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python from https://python.org/
    echo 💡 Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✅ Python found

REM Try the Windows-optimized script first
if exist start_jarvis_enhanced_windows.py (
    echo 🚀 Starting with Windows-optimized script...
    python start_jarvis_enhanced_windows.py
) else if exist start_jarvis_enhanced.py (
    echo 🚀 Starting with cross-platform script...
    python start_jarvis_enhanced.py
) else (
    echo ❌ Startup scripts not found!
    echo 💡 Make sure you're in the correct directory
    pause
    exit /b 1
)

pause
