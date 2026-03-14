@echo off
echo ========================================
echo   Systeme d'Ordonnancement Academique
echo ========================================
echo.

REM Vérifier si l'environnement virtuel existe
if exist "venv\Scripts\python.exe" (
    echo [OK] Environnement virtuel trouve
    echo Activation de l'environnement virtuel...
    call venv\Scripts\activate.bat
    echo.
    echo Lancement de l'application...
    python main.py
) else if exist ".venv\Scripts\python.exe" (
    echo [OK] Environnement virtuel trouve (.venv)
    echo Activation de l'environnement virtuel...
    call .venv\Scripts\activate.bat
    echo.
    echo Lancement de l'application...
    python main.py
) else (
    echo [ERREUR] Aucun environnement virtuel trouve!
    echo.
    echo Veuillez:
    echo 1. Installer Python depuis https://www.python.org/downloads/
    echo 2. Creer un environnement virtuel: python -m venv venv
    echo 3. Activer l'environnement: venv\Scripts\activate.bat
    echo 4. Installer les dependances: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

pause
