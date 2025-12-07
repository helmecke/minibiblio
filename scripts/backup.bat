@echo off
setlocal

echo ========================================
echo MiniBiblio Database Backup
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

:: Get current timestamp
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set timestamp=%datetime:~0,8%-%datetime:~8,6%

:: Create backup directory if it doesn't exist
if not exist "..\backups" mkdir "..\backups"

:: Create backup
set backup_file=..\backups\minibiblio-backup-%timestamp%.sql
echo Creating backup: %backup_file%
echo.

docker exec minibiblio-db pg_dump -U postgres minibiblio > "%backup_file%"

if errorlevel 1 (
    echo.
    echo ERROR: Backup failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Backup completed successfully!
echo ========================================
echo.
echo Backup saved to: %backup_file%
echo.
echo To restore this backup, use: restore.bat
echo.
pause

endlocal
