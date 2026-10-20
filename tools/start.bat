@echo off
setlocal EnableExtensions

title Star Wars - Galactic Assault - Start

set "PROJECT_DIR=%~dp0.."
for %%I in ("%PROJECT_DIR%") do set "PROJECT_DIR=%%~fI"

set "VENV_DIR=%PROJECT_DIR%\.venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
set "GAME_FILE=%PROJECT_DIR%\main.py"

if not exist "%PYTHON_EXE%" (
    echo [FEHLER] Die virtuelle Umgebung wurde nicht gefunden.
    echo Bitte zuerst "tools\install.bat" ausfuehren.
    pause
    exit /b 1
)

if not exist "%GAME_FILE%" (
    echo [FEHLER] main.py wurde nicht gefunden.
    pause
    exit /b 1
)

cd /d "%PROJECT_DIR%"
"%PYTHON_EXE%" "%GAME_FILE%"
exit /b %ERRORLEVEL%