@echo off
echo =========================================
echo    Holiday Hacker — Python Edition
echo =========================================
echo.
python main.py
if errorlevel 1 (
    echo.
    echo An error occurred while running Holiday Hacker.
)
pause
