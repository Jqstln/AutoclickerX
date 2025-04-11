@echo off
echo Starting build process for AutoclickerX...

:: Make sure previous builds are cleared
IF EXIST build rmdir /s /q build
IF EXIST dist rmdir /s /q dist
IF EXIST main.spec del /q main.spec

:: Run PyInstaller with UPX compression using python -m
python -m PyInstaller ^
  --name AutoclickerX ^
  --icon=assets\logo_mouse.ico ^
  --version-file=version.txt ^
  --noconsole ^
  --clean ^
  --onefile ^
  --upx-dir=tools\upx ^
  main.py

echo Build complete! Check the dist folder for AutoclickerX.exe
pause
