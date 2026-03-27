@echo off
echo ================================================
echo     FIDO Cloud Authentication - Starting...
echo ================================================

:: Check if venv exists, if not create it
IF NOT EXIST "venv\Scripts\python.exe" (
    echo [1/3] Creating virtual environment...
    python -m venv venv
    echo [2/3] Installing dependencies...
    venv\Scripts\pip.exe install -r requirements.txt
) ELSE (
    echo [INFO] Virtual environment found.
)

echo [3/3] Starting Flask server...
echo.
echo  Open your browser at: http://localhost:5000
echo  Press CTRL+C to stop the server.
echo.
venv\Scripts\python.exe App.py
pause
