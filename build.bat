@echo off
echo Starting build process for AutoclickerX...

:: make sure the paths exists and are correct, if yes then delete them
IF EXIST build rmdir /s /q build
IF EXIST dist rmdir /s /q dist
IF EXIST main.spec del /q main.spec

:: run pyinstaller with the specified options
python -m PyInstaller ^
  --name AutoclickerX ^
  --icon=assets\logo_mouse.ico ^
  --version-file=version.txt ^
  --noconsole ^
  --clean ^
  --onefile ^
  main.py

echo Build complete! Check the dist folder for AutoclickerX.exe
pause
