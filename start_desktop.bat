@echo off
echo 🤖 Starting Jarvis AI Desktop App...
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python desktop_app.py
pause
