@echo off
cd /d "%~dp0"
if not exist "assets\icons\ClipNova.ico" (
  echo Error: assets\icons\ClipNova.ico file nahi mili.
  pause
  exit /b 1
)
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --windowed --name "ClipNova" --icon "assets\icons\ClipNova.ico" --add-data "assets\icons;assets\icons" --add-data "assets\payments;assets\payments" --collect-all yt_dlp app.py
) else (
  py -3 -m PyInstaller --noconfirm --clean --windowed --name "ClipNova" --icon "assets\icons\ClipNova.ico" --add-data "assets\icons;assets\icons" --add-data "assets\payments;assets\payments" --collect-all yt_dlp app.py
)
if errorlevel 1 (
  echo Build mein masla aya. Upar error check karein.
) else (
  echo EXE dist\ClipNova\ClipNova.exe mein tayyar hai.
)
pause
