@echo off
REM Script de lancement pour Windows

echo Demarrage de IA-MultiTools...
echo.

REM Verifier si l'environnement virtuel existe
if exist .venv\Scripts\activate.bat (
    echo Activation de l'environnement virtuel...
    call .venv\Scripts\activate.bat
)

REM Lancer l'application
python run.py %*

REM Pause seulement en cas d'erreur
if errorlevel 1 (
    echo.
    echo Une erreur s'est produite.
    pause
)

