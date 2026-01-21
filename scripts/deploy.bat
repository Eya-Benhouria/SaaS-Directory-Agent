@echo off
REM ===========================================
REM Script de déploiement pour Windows
REM SaaS Directory Submission Agent
REM ===========================================

echo.
echo ========================================
echo   SaaS Directory Agent - Deploiement
echo ========================================
echo.

:MENU
echo Que voulez-vous faire?
echo.
echo   1. Initialiser Git et pousser vers GitHub
echo   2. Deployer le Frontend sur Vercel
echo   3. Deployer le Backend sur Railway
echo   4. Tout deployer (GitHub + Vercel + Railway)
echo   5. Verifier les outils installes
echo   6. Quitter
echo.
set /p choice="Votre choix [1-6]: "

if "%choice%"=="1" goto GITHUB
if "%choice%"=="2" goto VERCEL
if "%choice%"=="3" goto RAILWAY
if "%choice%"=="4" goto ALL
if "%choice%"=="5" goto CHECK
if "%choice%"=="6" goto END

echo Choix invalide!
goto MENU

:CHECK
echo.
echo Verification des outils...
echo.

where node >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Node.js installe
    node -v
) else (
    echo [X] Node.js non installe
)

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Python installe
    python --version
) else (
    echo [X] Python non installe
)

where git >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Git installe
    git --version
) else (
    echo [X] Git non installe
)

where vercel >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Vercel CLI installe
) else (
    echo [!] Vercel CLI non installe
    echo     Pour installer: npm i -g vercel
)

where railway >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Railway CLI installe
) else (
    echo [!] Railway CLI non installe
    echo     Pour installer: npm i -g @railway/cli
)

echo.
pause
goto MENU

:GITHUB
echo.
echo === Configuration GitHub ===
echo.

git status >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Initialisation de Git...
    git init
)

git remote get-url origin >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo.
    set /p GITHUB_URL="URL de votre repo GitHub: "
    git remote add origin %GITHUB_URL%
)

echo.
echo Ajout des fichiers...
git add .

echo.
set /p COMMIT_MSG="Message de commit: "
git commit -m "%COMMIT_MSG%"

echo.
echo Push vers GitHub...
git push -u origin main

echo.
echo [OK] Code pousse sur GitHub!
echo.
pause
goto MENU

:VERCEL
echo.
echo === Deploiement Vercel ===
echo.

cd frontend

where vercel >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installation de Vercel CLI...
    call npm i -g vercel
)

echo.
echo Deploiement en production...
call vercel --prod

cd ..

echo.
echo [OK] Frontend deploye sur Vercel!
echo.
pause
goto MENU

:RAILWAY
echo.
echo === Deploiement Railway ===
echo.

cd backend

where railway >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installation de Railway CLI...
    call npm i -g @railway/cli
)

echo.
echo Connexion a Railway...
call railway login

echo.
echo Deploiement...
call railway up

cd ..

echo.
echo [OK] Backend deploye sur Railway!
echo.
pause
goto MENU

:ALL
echo.
echo === Deploiement complet ===
echo.

REM GitHub
call :GITHUB_SILENT

REM Vercel
echo.
echo Deploiement Frontend sur Vercel...
cd frontend
call vercel --prod
cd ..

REM Railway
echo.
echo Deploiement Backend sur Railway...
cd backend
call railway up
cd ..

echo.
echo ========================================
echo   Deploiement termine!
echo ========================================
echo.
echo Vos URLs:
echo   Frontend: https://votre-projet.vercel.app
echo   Backend:  https://votre-projet.up.railway.app
echo   API Docs: https://votre-projet.up.railway.app/docs
echo.
echo Prochaines etapes:
echo   1. Configurez VITE_API_URL sur Vercel
echo   2. Ajoutez CORS_ORIGINS sur Railway
echo.
pause
goto MENU

:GITHUB_SILENT
git add .
git commit -m "Deploy: %date% %time%"
git push -u origin main
goto :eof

:END
echo.
echo Au revoir!
echo.
