@echo off
setlocal
title Star Wars - Installation

echo ==========================================
echo       STAR WARS - INSTALLATION
echo ==========================================
echo.

set "PROJECT_DIR=%~dp0"
set "VENV_DIR=%PROJECT_DIR%.venv"

cd /d "%PROJECT_DIR%"

echo [1/5] Suche nach Python...
echo.

:: ------------------------------------------------
:: Python Launcher pruefen
:: ------------------------------------------------

where py >nul 2>&1

if %errorlevel%==0 (
    set "PYTHON_CMD=py"
    goto PYTHON_FOUND
)

:: ------------------------------------------------
:: python.exe pruefen
:: ------------------------------------------------

where python >nul 2>&1

if %errorlevel%==0 (
    set "PYTHON_CMD=python"
    goto PYTHON_FOUND
)

echo FEHLER: Python wurde nicht gefunden.
echo.
echo Bitte installiere Python 3.13 von:
echo https://www.python.org/downloads/
echo.
echo Wichtig: Bei der Installation "Add Python to PATH"
echo aktivieren.
echo.
pause
exit /b 1

:PYTHON_FOUND

echo Python wurde gefunden:
%PYTHON_CMD% --version
echo.

:: ------------------------------------------------
:: Virtuelle Umgebung erstellen
:: ------------------------------------------------

if exist "%VENV_DIR%\Scripts\python.exe" (
    echo [2/5] Virtuelle Umgebung wurde bereits gefunden.
    echo.
) else (
    echo [2/5] Erstelle virtuelle Python-Umgebung...
    echo.

    %PYTHON_CMD% -m venv "%VENV_DIR%"

    if %errorlevel% neq 0 (
        echo.
        echo FEHLER: Die virtuelle Umgebung konnte nicht erstellt werden.
        echo.
        pause
        exit /b 1
    )

    echo Virtuelle Umgebung wurde erstellt.
    echo.
)

:: ------------------------------------------------
:: Virtuelle Umgebung pruefen
:: ------------------------------------------------

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo FEHLER: Python in der virtuellen Umgebung wurde nicht gefunden.
    echo.
    pause
    exit /b 1
)

set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"

echo [3/5] Aktualisiere pip innerhalb der virtuellen Umgebung...
echo.

"%VENV_PYTHON%" -m pip install --upgrade pip

if %errorlevel% neq 0 (
    echo.
    echo WARNUNG: pip konnte nicht aktualisiert werden.
    echo Die Installation wird trotzdem fortgesetzt.
    echo.
)

:: ------------------------------------------------
:: Pygame installieren
:: ------------------------------------------------

echo [4/5] Installiere Pygame...
echo.

"%VENV_PYTHON%" -m pip install pygame==2.6.1

if %errorlevel% neq 0 (
    echo.
    echo FEHLER: Pygame konnte nicht installiert werden.
    echo.
    pause
    exit /b 1
)

:: ------------------------------------------------
:: Weitere Abhaengigkeiten
:: ------------------------------------------------

if exist "%PROJECT_DIR%requirements.txt" (
    echo.
    echo [5/5] Installiere weitere Abhaengigkeiten...
    echo.

    "%VENV_PYTHON%" -m pip install -r "%PROJECT_DIR%requirements.txt"

    if %errorlevel% neq 0 (
        echo.
        echo WARNUNG: Einige Abhaengigkeiten aus requirements.txt
        echo konnten nicht installiert werden.
        echo.
    )
) else (
    echo.
    echo [5/5] Keine requirements.txt gefunden.
    echo Keine weiteren Pakete notwendig.
)

echo.
echo ==========================================
echo       INSTALLATION ABGESCHLOSSEN
echo ==========================================
echo.

echo Verwendete Python-Version:
"%VENV_PYTHON%" --version

echo.
echo Installierte Pygame-Version:
"%VENV_PYTHON%" -c "import pygame; print(pygame.version.ver)"

echo.
echo Die virtuelle Umgebung befindet sich hier:
echo %VENV_DIR%

echo.
echo Das System-Python wurde NICHT veraendert.
echo.

pause
endlocal