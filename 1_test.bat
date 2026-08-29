@echo off
cd /d "%~dp0"
echo ============================================
echo   JioHarvest - Mode Uji (tanpa modal)
echo ============================================
.\venv\Scripts\python.exe -m jiofarm run --dry-run --count 5 --concurrency 2
pause