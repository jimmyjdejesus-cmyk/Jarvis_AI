@echo off
echo 🚀 Jarvis AI Launcher
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python launcher.py
pause
