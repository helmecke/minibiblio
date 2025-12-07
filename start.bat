@echo off
echo ========================================
echo Starting MiniBiblio...
echo ========================================
echo.

docker-compose -f docker-compose.prod.yml up -d

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start MiniBiblio
    echo Run 'logs.bat' to see detailed error messages
    pause
    exit /b 1
)

echo.
echo ========================================
echo MiniBiblio is starting...
echo ========================================
echo.
echo Please wait 30-60 seconds for all services to initialize
echo.
echo Once ready, open in your browser:
echo   http://localhost:3000
echo.
echo Default admin credentials:
echo   Username: admin
echo   Password: admin123
echo.
echo ⚠️  IMPORTANT: Change the admin password immediately after first login!
echo.
echo Useful commands:
echo   - stop.bat        Stop MiniBiblio
echo   - logs.bat        View application logs
echo   - backup.bat      Create database backup
echo   - update.bat      Update to latest version
echo.
pause
