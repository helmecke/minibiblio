@echo off
echo ========================================
echo Setup Automatic Daily Backup
echo ========================================
echo:

echo This will create a Windows Task Scheduler job to run
echo database backups daily at 2:00 AM
echo:
set /p confirm="Continue? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo Cancelled
    pause
    exit /b 0
)

:: Get the full path to backup.bat
set script_path=%~dp0backup.bat

:: Create scheduled task
schtasks /create /tn "MiniBiblio Daily Backup" /tr "%script_path%" /sc daily /st 02:00 /f

if errorlevel 1 (
    echo:
    echo ERROR: Failed to create scheduled task
    echo You may need to run this script as Administrator
    pause
    exit /b 1
)

echo:
echo ========================================
echo Automatic backup configured!
echo ========================================
echo:
echo Daily backups will run at 2:00 AM
echo:
echo To manage the scheduled task:
echo   1. Open Task Scheduler (taskschd.msc)
echo   2. Look for "MiniBiblio Daily Backup"
echo:
echo To remove automatic backup:
echo   schtasks /delete /tn "MiniBiblio Daily Backup" /f
echo:
pause
