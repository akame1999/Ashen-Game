@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher ^(py^) not found. Install Python 3.10+ first.
  pause
  exit /b 1
)
py -3 -m pip install -r requirements.txt pyinstaller
if errorlevel 1 goto :error
py -3 -m PyInstaller --noconfirm --clean --onefile --windowed --name AshenVeil main.py
if errorlevel 1 goto :error
echo.
echo Build complete: dist\AshenVeil.exe
pause
exit /b 0
:error
echo Build failed. Review the error messages above.
pause
exit /b 1
