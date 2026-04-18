@echo off
setlocal EnableDelayedExpansion

echo === DIY PC Build Assistant - Windows ===
echo.

set "SCRIPT_DIR=%~dp0"

:: --- Check Python 3.12+ ------------------------------------------------------
set "PYTHON_BIN="
for %%C in (python3.12 python3 python py) do (
    if "!PYTHON_BIN!"=="" (
        where %%C >nul 2>&1
        if !errorlevel! == 0 (
            for /f "delims=" %%V in ('%%C -c "import sys; print(sys.version_info >= (3,12))" 2^>nul') do (
                if "%%V"=="True" set "PYTHON_BIN=%%C"
            )
        )
    )
)

if "%PYTHON_BIN%"=="" (
    echo Python 3.12+ not found.
    echo.
    where winget >nul 2>&1
    if !errorlevel! == 0 (
        echo Installing Python 3.12 via winget...
        winget install --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
        if !errorlevel! neq 0 (
            echo ERROR: winget install failed.
            echo Please install Python 3.12+ from https://www.python.org/downloads/
            echo Make sure to check "Add Python to PATH" during installation.
            pause
            exit /b 1
        )
        set "PYTHON_BIN=python"
    ) else (
        echo winget is not available.
        echo Please install Python 3.12+ from https://www.python.org/downloads/
        echo Make sure to check "Add Python to PATH" during installation.
        pause
        exit /b 1
    )
)

for /f "delims=" %%V in ('%PYTHON_BIN% --version 2^>^&1') do echo Using Python: %%V

:: --- Check uv ----------------------------------------------------------------
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo uv not found. Installing via pip...
    %PYTHON_BIN% -m pip install --user uv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install uv.
        echo Install it manually: https://github.com/astral-sh/uv
        pause
        exit /b 1
    )
    set "PATH=%APPDATA%\Python\Scripts;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%PATH%"
)

where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: uv is still not on PATH after install.
    echo Add %APPDATA%\Python\Scripts to your PATH and re-run this script.
    pause
    exit /b 1
)

for /f "delims=" %%V in ('uv --version 2^>^&1') do echo Using uv: %%V

:: --- Check CLAUDE_API_KEY ----------------------------------------------------
if "%CLAUDE_API_KEY%"=="" (
    echo.
    echo WARNING: CLAUDE_API_KEY is not set.
    set /p CLAUDE_API_KEY="Enter your Anthropic API key: "
    if "!CLAUDE_API_KEY!"=="" (
        echo ERROR: API key cannot be empty.
        pause
        exit /b 1
    )
)

:: --- Sync dependencies and launch --------------------------------------------
cd /d "%SCRIPT_DIR%"
echo.
echo Syncing dependencies...
uv sync
if %errorlevel% neq 0 (
    echo ERROR: uv sync failed.
    pause
    exit /b 1
)

echo.
echo Launching...
uv run buildcomputer

endlocal
