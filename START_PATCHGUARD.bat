@echo off
chcp 65001 > nul
title PatchGuard Manager - Auto Setup and Run

cd /d "%~dp0"
set "PORT=8000"
set "HOST=0.0.0.0"

echo.
echo ====================================================
echo       PatchGuard Manager - Automatic Launcher
echo ====================================================
echo.
echo This launcher will automatically:
echo  1. Create virtual environment if it does not exist
echo  2. Install required dependencies if needed
echo  3. Create database migrations
echo  4. Apply database migrations
echo  5. Start Django local server
echo.

where py >nul 2>nul
if %errorlevel%==0 (
    set "PYTHON_CMD=py -3"
    goto python_found
)

where python >nul 2>nul
if %errorlevel%==0 (
    set "PYTHON_CMD=python"
    goto python_found
)

echo ERROR: Python was not found.
echo.
echo Install Python from https://www.python.org/downloads/
echo During installation, enable: Add Python to PATH
echo.
pause
exit /b 1

:python_found

if not exist "manage.py" (
    echo ERROR: manage.py was not found.
    echo Make sure this BAT file is inside the patchguard_manager project folder.
    echo.
    pause
    exit /b 1
)

if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment.
        echo.
        pause
        exit /b 1
    )
) else (
    echo Virtual environment already exists.
)

set "VENV_PY=venv\Scripts\python.exe"
set "VENV_PIP=venv\Scripts\pip.exe"

echo Checking dependencies...
"%VENV_PY%" -c "import django, reportlab" >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing dependencies from requirements.txt...
    "%VENV_PY%" -m pip install --upgrade pip
    "%VENV_PIP%" install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies.
        echo Check your internet connection or install dependencies manually:
        echo pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
) else (
    echo Dependencies are already installed.
)

echo.
echo Preparing database...
"%VENV_PY%" manage.py makemigrations core --noinput
if %errorlevel% neq 0 (
    echo ERROR: Failed to create migrations.
    echo.
    pause
    exit /b 1
)

"%VENV_PY%" manage.py migrate --noinput
if %errorlevel% neq 0 (
    echo ERROR: Failed to apply migrations.
    echo.
    pause
    exit /b 1
)

for /f "delims=" %%I in ('powershell -NoProfile -Command "$ips = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notmatch '^(127|169\.254)\.' -and $_.InterfaceOperationalStatus -eq 'Up' } | Select-Object -ExpandProperty IPAddress; if ($ips) { $ips[0] } else { '127.0.0.1' }"') do set "LOCAL_IP=%%I"

echo.
echo ====================================================
echo Server is starting...
echo.
echo Open on this computer:
echo   http://127.0.0.1:%PORT%
echo.
echo Open from another device on the same Wi-Fi:
echo   http://%LOCAL_IP%:%PORT%
echo.
echo Demo login:
echo   Username: admin
echo   Password: admin12345
echo.
echo IMPORTANT:
echo   Keep this window open while using the application.
echo   If Windows Firewall asks permission, click Allow Access.
echo ====================================================
echo.

start "" cmd /c "timeout /t 3 >nul && start http://127.0.0.1:%PORT%"
"%VENV_PY%" manage.py runserver %HOST%:%PORT%

echo.
echo Server stopped.
pause
