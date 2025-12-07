@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo MiniBiblio Update Script
echo ==========================================
echo.

REM Check if .env exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please run install.bat first.
    pause
    exit /b 1
)

REM Show current version
echo Current configuration:
type .env | findstr MINIBIBLIO_VERSION
echo.

REM Pull latest images
echo Pulling latest Docker images...
docker-compose -f docker-compose.prod.yml pull
if errorlevel 1 (
    echo ERROR: Failed to pull images
    pause
    exit /b 1
)

echo.
echo Stopping current containers...
docker-compose -f docker-compose.prod.yml down

echo.
echo Starting updated containers...
docker-compose -f docker-compose.prod.yml up -d
if errorlevel 1 (
    echo ERROR: Failed to start containers
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Update Complete!
echo ==========================================
echo.
echo Services are starting up...
echo Database migrations will run automatically.
echo.
echo Check status: docker-compose -f docker-compose.prod.yml ps
echo View logs: docker-compose -f docker-compose.prod.yml logs -f
echo.
pause

endlocal
