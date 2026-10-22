@echo off
setlocal
cd /d "%~dp0"
if errorlevel 1 exit /b 1

set "PYTHON=python"
if not defined VIRTUAL_ENV if exist ".venv\Scripts\python.exe" set "PYTHON=%~dp0.venv\Scripts\python.exe"
if defined VIRTUAL_ENV set "PYTHON=%VIRTUAL_ENV%\Scripts\python.exe"

"%PYTHON%" build.py %*
exit /b %errorlevel%
