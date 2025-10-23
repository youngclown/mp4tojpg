@echo off
echo Building Video Frame Extractor EXE...

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Build with PyInstaller
pyinstaller --onefile --windowed --name="VideoToolkit" --icon=NONE video_frame_extractor.py

echo.
echo Build complete! EXE file is in the 'dist' folder.
pause
