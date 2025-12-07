@echo off
echo ========================================
echo Stopping MiniBiblio...
echo ========================================
echo.

docker-compose -f docker-compose.prod.yml down

if errorlevel 1 (
    echo.
    echo ERROR: Failed to stop MiniBiblio
    pause
    exit /b 1
)

echo.
echo [OK] MiniBiblio stopped successfully
echo.
echo Your data is safely stored in Docker volumes
echo To restart, run: start.bat
echo.
pause
