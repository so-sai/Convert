@echo off
REM Convert Protocol - User Mode Launcher
REM Bypasses UIPI so drag-drop works from Explorer
REM Run by double-clicking this file from File Explorer

echo ========================================
echo  CONVERT PROTOCOL - USER MODE LAUNCHER
echo ========================================
echo.

REM Change to project directory
cd /d "E:\DEV\Convert"

REM Activate virtual environment
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo [OK] Python venv activated
) else (
    echo [WARN] No venv found, continuing...
)

echo.
echo Starting Convert Protocol in USER mode...
echo This enables drag-drop from Explorer.
echo.
echo ======================================
echo   INSTRUCTIONS:
echo   1. Wait for app window to appear
echo   2. Drag .cvbak files onto the window
echo   3. OR click "Open Backup File" button
echo ======================================
echo.
echo DO NOT CLOSE THIS WINDOW!
echo.

REM Run Tauri dev without admin elevation
cargo tauri dev

echo.
echo App closed. Press any key to exit.
pause > nul
