# NBACore Desktop — PowerShell Launcher
# More reliable than .bat for path resolution
# Usage: Right-click -> Run with PowerShell, or: powershell -ExecutionPolicy Bypass -File start.ps1

$ErrorActionPreference = 'Continue'
$AppDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $AppDir

# Clear proxy
$env:HTTP_PROXY = $null
$env:HTTPS_PROXY = $null
$env:ALL_PROXY = $null
$env:http_proxy = $null
$env:https_proxy = $null
$env:all_proxy = $null

# Set Python path
$PythonExe = 'C:\Users\Administrator\AppData\Local\Programs\Python\Python310\python.exe'
$env:NBA_PYTHON = $PythonExe

Write-Host '========================================' -ForegroundColor Cyan
Write-Host '  NBACore Desktop Starting...' -ForegroundColor Cyan
Write-Host '========================================' -ForegroundColor Cyan
Write-Host ''

# Check Python
if (-not (Test-Path $PythonExe)) {
    Write-Host "[ERROR] Python not found at: $PythonExe" -ForegroundColor Red
    Read-Host 'Press Enter to exit'
    exit 1
}
Write-Host "[OK] Python: $PythonExe" -ForegroundColor Green

# Check Electron
$ElectronCmd = Join-Path $AppDir 'node_modules\.bin\electron.cmd'
if (-not (Test-Path $ElectronCmd)) {
    Write-Host 'Installing dependencies (first run)...' -ForegroundColor Yellow
    npm install
    if (-not (Test-Path $ElectronCmd)) {
        Write-Host '[ERROR] Electron still not found after npm install!' -ForegroundColor Red
        Read-Host 'Press Enter to exit'
        exit 1
    }
}
Write-Host "[OK] Electron: $ElectronCmd" -ForegroundColor Green
Write-Host ''

# Start Electron
& $ElectronCmd .
