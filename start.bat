@echo off
setlocal
title Star Wars - Spiel

set "PROJECT_DIR=%~dp0"
set "VENV_DIR=%PROJECT_DIR%.venv"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"

cd /d "%PROJECT_DIR%"

echo ==========================================
echo       STAR WARS - SPIELSTART
echo ==========================================
echo.

:: ------------------------------------------------
:: Virtuelle Umgebung pruefen
:: ------------------------------------------------

if not exist "%VENV_PYTHON%" (
    echo FEHLER:
    echo Die virtuelle Python-Umgebung wurde nicht gefunden.
    echo.
    echo Bitte zuerst "install.bat" ausfuehren.
    echo.
    pause
    exit /b 1
)

:: ------------------------------------------------
:: Spiel pruefen
:: ------------------------------------------------

if not exist "%PROJECT_DIR%StarWarsGame.py" (
    echo FEHLER:
    echo StarWarsGame.py wurde nicht gefunden.
    echo.
    echo Stelle sicher, dass start.bat im Hauptordner
    echo des Spiels liegt.
    echo.
    pause
    exit /b 1
)

:: ------------------------------------------------
:: Pygame pruefen
:: ------------------------------------------------

"%VENV_PYTHON%" -c "import pygame" >nul 2>&1

if %errorlevel% neq 0 (
    echo FEHLER:
    echo Pygame ist in der virtuellen Umgebung nicht installiert.
    echo.
    echo Bitte zuerst "install.bat" ausfuehren.
    echo.
    pause
    exit /b 1
)

echo Starte Star Wars...
echo.

:: ------------------------------------------------
:: Spiel starten
:: ------------------------------------------------

"%VENV_PYTHON%" "%PROJECT_DIR%StarWarsGame.py"

set "EXIT_CODE=%errorlevel%"

echo.
echo ==========================================
echo       SPIEL BEENDET
echo ==========================================
echo.

if not "%EXIT_CODE%"=="0" (
    echo Das Spiel wurde mit einem Fehler beendet.
    echo Fehlercode: %EXIT_CODE%
    echo.
    pause
)

endlocal
exit /b %EXIT_CODE%