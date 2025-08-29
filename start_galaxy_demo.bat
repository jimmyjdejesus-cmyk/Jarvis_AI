@echo off
setlocal

REM Start backend server
start "GalaxyBackend" cmd /k "python -m app.main"

REM Wait for backend to initialize
ping -n 6 127.0.0.1 >nul

REM Serve demo directory on port 5173
start "GalaxyDemo" cmd /k "python -m http.server 5173 --directory demo"

REM Open browser to the demo
start http://localhost:5173/index.html

endlocal
