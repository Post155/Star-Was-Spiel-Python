@echo off
setlocal EnableExtensions

title Star Wars - Galactic Assault - Start

echo.
echo ============================================================
echo       STAR WARS - GALACTIC ASSAULT
echo       Spiel wird gestartet
echo ============================================================
echo.

REM ------------------------------------------------------------
REM Projekt-Hauptordner ermitteln
REM start.bat liegt in: tools\
REM Projekt liegt daher eine Ebene hoeher.
REM ------------------------------------------------------------

set "PROJECT_DIR=%~dp0.."

for %%I in ("%PROJECT_DIR%") do set "PROJECT_DIR=%%~fI"

set "VENV_DIR=%PROJECT_DIR%\.venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
set "GAME_FILE=%PROJECT_DIR%\StarWarsGame.py"

REM ------------------------------------------------------------
REM Virtuelle Umgebung pruefen
REM ------------------------------------------------------------

if not exist "%PYTHON_EXE%" (
    echo [FEHLER] Die virtuelle Umgebung wurde nicht gefunden.
    echo.
    echo Bitte zuerst folgende Datei ausfuehren:
    echo tools\install.bat
    echo.
    pause
    exit /b 1
)

echo [OK] Virtuelle Python-Umgebung gefunden.
echo.

REM ------------------------------------------------------------
REM Spieldatei pruefen
REM ------------------------------------------------------------

if not exist "%GAME_FILE%" (
    echo [FEHLER] StarWarsGame.py wurde nicht gefunden.
    echo.
    echo Erwarteter Speicherort:
    echo %GAME_FILE%
    echo.
    pause
    exit /b 1
)

echo [OK] StarWarsGame.py gefunden.
echo.

REM ------------------------------------------------------------
REM Pygame pruefen
REM ------------------------------------------------------------

echo [INFO] Pruefe Pygame...

"%PYTHON_EXE%" -c "import pygame; print('Pygame-Version:', pygame.version.ver)"

if errorlevel 1 (
    echo.
    echo [FEHLER] Pygame ist nicht installiert oder funktioniert nicht.
    echo.
    echo Bitte zuerst tools\install.bat ausfuehren.
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Pygame funktioniert.
echo.

REM ------------------------------------------------------------
REM Spiel starten
REM ------------------------------------------------------------

echo ============================================================
echo       SPIEL WIRD GESTARTET
echo ============================================================
echo.

cd /d "%PROJECT_DIR%"

"%PYTHON_EXE%" "%GAME_FILE%"

set "GAME_ERROR=%errorlevel%"

echo.
echo ============================================================

if "%GAME_ERROR%"=="0" (
    echo Das Spiel wurde beendet.
) else (
    echo [FEHLER] Das Spiel wurde mit Fehlercode %GAME_ERROR% beendet.
)

echo ============================================================
echo.

pause
exit /b %GAME_ERROR%