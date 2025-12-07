@echo off
setlocal

echo ========================================
echo MiniBiblio Database Restore
echo ========================================
echo.

:: Check if MiniBiblio is running
docker ps | findstr minibiblio-db >nul 2>&1
if errorlevel 1 (
    echo ERROR: MiniBiblio database is not running
    echo Please start MiniBiblio first with: start.bat
    echo.
    pause
    exit /b 1
)

:: Check if backups directory exists
if not exist "..\backups" (
    echo ERROR: No backups directory found
    echo Create a backup first with: backup.bat
    echo.
    pause
    exit /b 1
)

:: List available backups
echo Available backups:
echo.
dir /b ..\backups\*.sql
echo.

:: Prompt for backup file
set /p backup_file="Enter backup filename (e.g., minibiblio-backup-20241203.sql): "

:: Check if file exists
if not exist "..\backups\%backup_file%" (
    echo.
    echo ERROR: Backup file not found: %backup_file%
    pause
    exit /b 1
)

:: Confirm
echo.
echo ⚠️  WARNING: This will replace ALL current data with the backup!
echo.
set /p confirm="Type YES to continue, anything else to cancel: "
if /i not "%confirm%"=="YES" (
    echo.
    echo Restore cancelled
    pause
    exit /b 0
)

:: Restore backup
echo.
echo Restoring backup: %backup_file%
echo.

:: Drop and recreate database
docker exec minibiblio-db psql -U postgres -c "DROP DATABASE IF EXISTS minibiblio;"
docker exec minibiblio-db psql -U postgres -c "CREATE DATABASE minibiblio;"

:: Restore from backup
docker exec -i minibiblio-db psql -U postgres minibiblio < "..\backups\%backup_file%"

if errorlevel 1 (
    echo.
    echo ERROR: Restore failed
    echo You may need to recreate the database manually
    pause
    exit /b 1
)

echo.
echo ========================================
echo Restore completed successfully!
echo ========================================
echo.
echo Database has been restored from: %backup_file%
echo.
echo Restarting services...
docker-compose -f ..\docker-compose.prod.yml restart

echo.
echo [OK] Services restarted
echo Wait 30 seconds and refresh your browser
echo.
pause
