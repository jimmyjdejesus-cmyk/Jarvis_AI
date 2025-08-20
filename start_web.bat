@echo off
echo 🌐 Starting Jarvis AI Web UI...
cd /d "%~dp0"
call .venv\Scripts\activate.bat
streamlit run legacy/app.py
pause
