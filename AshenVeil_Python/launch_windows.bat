@echo off
setlocal
cd /d "%~dp0"
echo ========================================
echo   ASHEN VEIL - Python Combat Sandbox
echo ========================================
echo.
where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher ^(py^) was not found. Install Python 3.10+ from https://www.python.org/downloads/ and enable the Python Launcher.
  pause
  exit /b 1
)
echo Installing game dependency if needed...
py -3 -m pip install -r requirements.txt
if errorlevel 1 (
  echo Dependency installation failed. Check your internet connection and Python installation.
  pause
  exit /b 1
)
echo Starting Ashen Veil...
py -3 main.py
if errorlevel 1 (
  echo The game exited with an error. Review the output above.
  pause
  exit /b 1
)
endlocal
