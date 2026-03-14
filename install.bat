@echo off
echo ========================================
echo   Installation des dependances
echo ========================================
echo.

REM Vérifier si l'environnement virtuel existe
if exist "venv\Scripts\python.exe" (
    echo [OK] Environnement virtuel trouve (venv)
    call venv\Scripts\activate.bat
    echo.
    echo Installation des dependances...
    pip install -r requirements.txt
    echo.
    echo [OK] Installation terminee!
) else if exist ".venv\Scripts\python.exe" (
    echo [OK] Environnement virtuel trouve (.venv)
    call .venv\Scripts\activate.bat
    echo.
    echo Installation des dependances...
    pip install -r requirements.txt
    echo.
    echo [OK] Installation terminee!
) else (
    echo [ERREUR] Aucun environnement virtuel trouve!
    echo.
    echo Creation d'un nouvel environnement virtuel...
    python -m venv venv
    if errorlevel 1 (
        echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH
        echo.
        echo Veuillez installer Python depuis https://www.python.org/downloads/
        echo Assurez-vous de cocher "Add Python to PATH" lors de l'installation
        pause
        exit /b 1
    )
    call venv\Scripts\activate.bat
    echo.
    echo Installation des dependances...
    pip install -r requirements.txt
    echo.
    echo [OK] Installation terminee!
)

pause
