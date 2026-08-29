@echo off
cd /d "%~dp0"
echo ============================================
echo   JioHarvest - Cek Saldo Provider
echo ============================================
.\venv\Scripts\python.exe -m jiofarm balance
pause