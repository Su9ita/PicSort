@echo off
chcp 65001 > nul
echo ========================================
echo PicSort - Build EXE
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Building with PyInstaller...
echo.
python -m PyInstaller PicSort.spec --clean

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Build failed
    echo.
    echo Please check:
    echo 1. PyInstaller is installed
    echo    Install: python -m pip install pyinstaller
    echo 2. icon.ico exists
    echo    Generate: python generate_icon.py
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo [2/3] Copying sounds folder...
echo ========================================
if exist sounds (
    xcopy /E /I /Y sounds dist\sounds > nul
    echo OK: sounds folder copied
) else (
    echo SKIP: sounds folder not found
)

echo.
echo ========================================
echo [3/3] Complete!
echo ========================================
echo.
echo PicSort.exe created successfully!
echo Location: dist\PicSort.exe
echo.
echo You can copy this file anywhere and use it.
echo Note: Copy the sounds folder together if needed.
echo.
pause
