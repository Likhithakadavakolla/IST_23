@echo off
echo Starting EduReach Flask Server...
echo.
echo Server will be available at:
echo   - http://localhost:5000
echo   - http://127.0.0.1:5000
echo.
echo Press Ctrl+C to stop the server
echo.

cd /d "%~dp0"
call venv\Scripts\activate.bat
python app.py

pause
