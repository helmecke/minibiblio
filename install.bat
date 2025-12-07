@echo off
echo:
echo ==========================================
echo MiniBiblio Installation
echo ==========================================
echo:
echo This installer will use pre-built Docker images from GitHub Packages.
echo Default version: latest (always uses newest release)
echo:
echo To use a specific version, edit MINIBIBLIO_VERSION in .env after installation.
echo Available versions: https://github.com/helmecke/minibiblio/releases
echo:

:: Check Docker is running
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not running
    echo Please install Docker Desktop for Windows from:
    echo https://www.docker.com/products/docker-desktop/
    echo:
    pause
    exit /b 1
)

echo [OK] Docker is installed
echo:

:: Check if .env file exists
if not exist .env (
    echo Creating .env file from template...
    if exist .env.production (
        copy .env.production .env
    ) else (
        echo ERROR: .env.production template not found
        pause
        exit /b 1
    )
    echo:
    echo .env file created. Using default version (latest).
    echo To pin to a specific version, edit MINIBIBLIO_VERSION in .env
    echo Example: MINIBIBLIO_VERSION=1.0.0
    echo:
    echo ========================================
    echo IMPORTANT: Configure your .env file
    echo ========================================
    echo:
    echo Please edit the .env file and set secure values for:
    echo   1. POSTGRES_PASSWORD - Strong database password
    echo   2. JWT_SECRET - Generate at https://generate-secret.vercel.app/32
    echo   3. AUTH_SECRET - Generate at https://generate-secret.vercel.app/32
    echo   4. ADMIN_PASSWORD - Change from default 'admin123'
    echo:
    echo Press any key to open .env file in Notepad...
    pause >nul
    notepad .env
    echo:
    echo Have you updated all required values in .env? (Y/N)
    set /p confirmed=
    if /i not "%confirmed%"=="Y" (
        echo Installation cancelled. Please configure .env and run install.bat again.
        pause
        exit /b 1
    )
) else (
    echo [OK] .env file already exists
)

echo:
echo Pulling Docker images from GitHub Packages...
docker-compose -f docker-compose.prod.yml pull

if errorlevel 1 (
    echo:
    echo ERROR: Failed to pull Docker images
    pause
    exit /b 1
)

echo:
echo ========================================
echo Installation Complete!
echo ========================================
echo:
echo Next steps:
echo   1. Run 'start.bat' to start MiniBiblio
echo   2. Wait 30-60 seconds for services to start
echo   3. Open http://localhost:3000 in your browser
echo   4. Login with username: admin, password: admin123
echo   5. Change the admin password immediately!
echo:
pause
