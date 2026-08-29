@echo off
cd /d "%~dp0"
echo ============================================
echo   JioHarvest - Web Dashboard
echo   Buka http://127.0.0.1:9121 di browser
echo ============================================
.\venv\Scripts\python.exe -m jiofarm web
pause