@echo off
chcp 65001 >nul 2>&1
REM ========================================
REM   NBACore Desktop — Windows Launcher
REM ========================================

cd /d "%~dp0"

REM Set Python path
set NBA_PYTHON=C:\Users\Administrator\AppData\Local\Programs\Python\Python310\python.exe
set HTTP_PROXY=
set HTTPS_PROXY=
set ALL_PROXY=
set http_proxy=
set https_proxy=
set all_proxy=

echo ========================================
echo   NBACore Desktop Starting...
echo ========================================
echo.

REM Check node_modules
if not exist "node_modules\.bin\electron.cmd" (
    echo [ERROR] Electron not found! Installing dependencies...
    call npm install
    if errorlevel 1 (
        echo [ERROR] npm install failed!
        echo Please run manually: npm install
        pause
        exit /b 1
    )
)

REM Check Python
if not exist "%NBA_PYTHON%" (
    echo [ERROR] Python not found at: %NBA_PYTHON%
    echo Please edit start.bat and set the correct Python path.
    pause
    exit /b 1
)

echo [OK] Python: %NBA_PYTHON%
echo [OK] Electron: %~dp0node_modules\.bin\electron.cmd
echo.

REM Start Electron using direct path (avoids PATH issues)
"node_modules\.bin\electron.cmd" .

REM If we get here, Electron has exited
echo.
echo ========================================
echo   NBACore Desktop has exited.
echo ========================================
pause
