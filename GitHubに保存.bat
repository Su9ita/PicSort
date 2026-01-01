@echo off
echo ========================================
echo PicSort - Save to GitHub
echo ========================================
echo.

cd /d "%~dp0"

echo Checking changes...
git status
echo.

set /p message="Enter commit message: "

if "%message%"=="" (
    echo ERROR: Commit message is required
    pause
    exit /b 1
)

echo.
echo ========================================
echo Saving to GitHub...
echo ========================================

git add .
git commit -m "%message%"
git push

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS! Saved to GitHub
    echo ========================================
) else (
    echo.
    echo ========================================
    echo ERROR: Failed to save
    echo ========================================
)

echo.
pause
