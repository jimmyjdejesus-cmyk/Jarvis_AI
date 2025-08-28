@echo off
REM Jarvis AI One-Click Installer for Windows
REM This script provides automated installation for non-technical users

setlocal enabledelayedexpansion

REM Configuration
set JARVIS_VERSION=2.0.0
set INSTALL_DIR=%USERPROFILE%\jarvis-ai
set PYTHON_MIN_VERSION=3.8

REM Colors (Windows doesn't support colors in batch easily, so we'll use plain text)
echo.
echo ================================================================
echo                    Jarvis AI Installer
echo          Privacy-first AI Development Assistant
echo                     Version %JARVIS_VERSION%
echo ================================================================
echo.

echo Checking system requirements...

REM Check if Python is installed
python --version >nul 2>&1
if !errorlevel! neq 0 (
    echo Python not found. Checking for python3...
    python3 --version >nul 2>&1
    if !errorlevel! neq 0 (
        echo ERROR: Python %PYTHON_MIN_VERSION%+ is required but not found.
        echo Please install Python from https://python.org
        echo Make sure to check "Add Python to PATH" during installation.
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=python3
    )
) else (
    set PYTHON_CMD=python
)

echo ✓ Python check passed

REM Check Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git is required but not found.
    echo Please install Git from https://git-scm.com
    pause
    exit /b 1
)

echo ✓ Git check passed

REM Check pip
%PYTHON_CMD% -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip not found. Please ensure Python is properly installed.
    pause
    exit /b 1
)

echo ✓ pip check passed

REM Create installation directory
echo Creating installation directory at %INSTALL_DIR%...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
cd /d "%INSTALL_DIR%"

REM Clone repository
echo Downloading Jarvis AI...
if exist ".git" (
    git pull origin main
) else (
    git clone %REPO_URL% .
)

if %errorlevel% neq 0 (
    echo ERROR: Failed to download Jarvis AI
    pause
    exit /b 1
)

echo ✓ Download completed

REM Create virtual environment
echo Creating Python virtual environment...
%PYTHON_CMD% -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

echo ✓ Virtual environment created

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

REM Install Jarvis AI
echo Installing Jarvis AI and dependencies...
echo This may take several minutes...
pip install -e .

if %errorlevel% neq 0 (
    echo ERROR: Failed to install Jarvis AI
    pause
    exit /b 1
)

echo ✓ Installation completed

REM Initialize configuration
echo Initializing configuration...
jarvis config --init

echo ✓ Configuration initialized

REM Create launcher script
echo Creating launcher script...
(
echo @echo off
echo cd /d "%INSTALL_DIR%"
echo call venv\Scripts\activate.bat
echo jarvis run %%*
echo pause
) > start-jarvis.bat

REM Create desktop shortcut
echo Creating desktop shortcut...
set DESKTOP=%USERPROFILE%\Desktop
(
echo @echo off
echo cd /d "%INSTALL_DIR%"
echo call venv\Scripts\activate.bat
echo jarvis run %%*
) > "%DESKTOP%\Jarvis AI.bat"

REM Installation complete
echo.
echo ================================================================
echo 🎉 Jarvis AI installation completed successfully!
echo ================================================================
echo.
echo Getting Started:
echo 1. Double-click "Jarvis AI.bat" on your Desktop
echo    or
echo    Run %INSTALL_DIR%\start-jarvis.bat
echo.
echo 2. Open your browser to: http://localhost:8501
echo.
echo 3. To update Jarvis AI in the future:
echo    - Open Command Prompt in %INSTALL_DIR%
echo    - Run: git pull ^&^& pip install -e .
echo.
echo Configuration file: %INSTALL_DIR%\config\config.yaml
echo Documentation: https://github.com/jimmyjdejesus-cmyk/Jarvis_AI/docs
echo.
echo Press any key to exit...
pause >nul