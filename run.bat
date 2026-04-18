@echo off
title NexCare AI — Hospital Management System
color 0A

echo.
echo  =============================================
echo       NexCare AI - Hospital Management System
echo  =============================================
echo.

:: Step 1: Install dependencies
echo  [1/2] Installing dependencies...
echo.
pip install streamlit pandas plotly --quiet
if %ERRORLEVEL% neq 0 (
    echo.
    echo  ERROR: Failed to install dependencies.
    echo  Make sure Python and pip are installed.
    echo  Try running: python -m pip install streamlit pandas plotly
    pause
    exit /b 1
)
echo        Done!
echo.

:: Step 2: Launch Streamlit
echo  [2/2] Starting NexCare AI...
echo.
echo  =============================================
echo    App will open at: http://localhost:8501
echo    Press Ctrl+C here to stop the server.
echo  =============================================
echo.

streamlit run "%~dp0Home.py" --server.headless false

pause
