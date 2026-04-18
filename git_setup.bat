@echo off
title NexCare AI — GitHub Setup
color 0B

echo.
echo  =============================================
echo       NexCare AI - GitHub Repository Setup
echo  =============================================
echo.

:: Step 1: Initialize Git
echo  [1/3] Initializing local repository...
git init
if %ERRORLEVEL% neq 0 (
    echo.
    echo  ERROR: Git not found. Please install Git from https://git-scm.com/
    pause
    exit /b 1
)

:: Step 2: Rename gitignore
if exist gitignore.txt (
    rename gitignore.txt .gitignore
)

:: Step 3: Add and Commit
echo  [2/3] Staging files and committing...
git add .
git commit -m "Initial commit: NexCare AI Hospital Management System"

echo.
echo  =============================================
echo   SUCCESS: Local repository is ready!
echo  =============================================
echo.
echo  NEXT STEPS:
echo  1. Go to https://github.com/new
echo  2. Create a repository named "NexCareAI"
echo  3. Copy the "Remote URL" (e.g., https://github.com/yourname/NexCareAI.git)
echo  4. Paste the following commands in your terminal:
echo.
echo     git remote add origin YOUR_REMOTE_URL
echo     git branch -M main
echo     git push -u origin main
echo.
echo  =============================================
pause
