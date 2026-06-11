@echo off
chcp 65001 >nul
cd /d %~dp0

echo.
echo === 晓观潮 · 中南大信息聚合 ===

:: Find Python - 自动搜索常见路径
set PYTHON_CMD=
where python >nul 2>nul && set PYTHON_CMD=python
if "%PYTHON_CMD%"=="" where python3 >nul 2>nul && set PYTHON_CMD=python3
if "%PYTHON_CMD%"=="" (
    for /d %%d in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
        if exist "%%d\python.exe" set PYTHON_CMD=%%d\python.exe
    )
)
if "%PYTHON_CMD%"=="" (
    echo [ERROR] Python 3.10+ not found. Please install Python first.
    pause
    exit /b 1
)
echo Python: %PYTHON_CMD%

:: Check if venv exists, if not create and install deps
if not exist "venv\" (
    echo [First time setup - creating virtual environment...]
    "%PYTHON_CMD%" -m venv venv --system-site-packages
    if exist venv\Scripts\pip.exe (
        echo [Installing dependencies...]
        venv\Scripts\pip.exe install -r requirements.txt -q
    )
    echo [Setup complete!]
)

echo [Starting server...]
echo Open http://localhost:5000 in your browser
echo.

call venv\Scripts\python.exe app.py
pause
