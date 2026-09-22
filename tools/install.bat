@echo off
setlocal EnableExtensions

title Star Wars - Galactic Assault - Installation

echo.
echo ============================================================
echo       STAR WARS - GALACTIC ASSAULT
echo       Virtuelle Python-Umgebung wird eingerichtet
echo ============================================================
echo.

REM ------------------------------------------------------------
REM Projekt-Hauptordner ermitteln
REM install.bat liegt in: tools\
REM Projekt liegt daher eine Ebene hoeher.
REM ------------------------------------------------------------

set "PROJECT_DIR=%~dp0.."

for %%I in ("%PROJECT_DIR%") do set "PROJECT_DIR=%%~fI"

set "VENV_DIR=%PROJECT_DIR%\.venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
set "REQUIREMENTS=%PROJECT_DIR%\requirements.txt"

echo Projektordner:
echo %PROJECT_DIR%
echo.

REM ------------------------------------------------------------
REM Python suchen
REM ------------------------------------------------------------

where py >nul 2>&1

if %errorlevel%==0 (
    set "PYTHON_CMD=py"
    goto :python_found
)

where python >nul 2>&1

if %errorlevel%==0 (
    set "PYTHON_CMD=python"
    goto :python_found
)

echo [FEHLER] Python wurde nicht gefunden.
echo.
echo Bitte installiere Python und stelle sicher,
echo dass Python ueber die Eingabeaufforderung erreichbar ist.
echo.
pause
exit /b 1

:python_found

echo [OK] Python wurde gefunden.
echo.

REM ------------------------------------------------------------
REM Virtuelle Umgebung erstellen
REM ------------------------------------------------------------

if exist "%PYTHON_EXE%" (
    echo [OK] Virtuelle Umgebung existiert bereits.
) else (
    echo [INFO] Erstelle virtuelle Python-Umgebung...
    echo.

    %PYTHON_CMD% -m venv "%VENV_DIR%"

    if errorlevel 1 (
        echo.
        echo [FEHLER] Die virtuelle Umgebung konnte nicht erstellt werden.
        echo.
        pause
        exit /b 1
    )

    echo.
    echo [OK] Virtuelle Umgebung wurde erstellt.
)

echo.

REM ------------------------------------------------------------
REM PIP aktualisieren
REM ------------------------------------------------------------

echo [INFO] Aktualisiere pip innerhalb der virtuellen Umgebung...
echo.

"%PYTHON_EXE%" -m pip install --upgrade pip

if errorlevel 1 (
    echo.
    echo [WARNUNG] pip konnte nicht aktualisiert werden.
    echo Die Installation wird trotzdem fortgesetzt.
)

echo.

REM ------------------------------------------------------------
REM requirements.txt pruefen
REM ------------------------------------------------------------

if not exist "%REQUIREMENTS%" (
    echo [FEHLER] requirements.txt wurde nicht gefunden.
    echo.
    echo Erwarteter Speicherort:
    echo %REQUIREMENTS%
    echo.
    pause
    exit /b 1
)

echo [OK] requirements.txt gefunden.
echo.

REM ------------------------------------------------------------
REM Abhaengigkeiten installieren
REM ------------------------------------------------------------

echo [INFO] Installiere benoetigte Python-Pakete...
echo.
echo Die Pakete werden NUR in .venv installiert.
echo Die globale Python-Installation wird nicht veraendert.
echo.

"%PYTHON_EXE%" -m pip install -r "%REQUIREMENTS%"

if errorlevel 1 (
    echo.
    echo ============================================================
    echo [FEHLER] Installation fehlgeschlagen.
    echo ============================================================
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo [ERFOLG] Installation abgeschlossen!
echo ============================================================
echo.
echo Die virtuelle Umgebung befindet sich hier:
echo %VENV_DIR%
echo.
echo Zum Starten des Spiels:
echo tools\start.bat
echo.

pause
exit /b 0