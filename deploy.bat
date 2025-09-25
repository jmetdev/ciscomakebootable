@echo off
REM ISO Bootable Maker - Easy Deployment Script for Windows
REM This script builds and runs the Docker container, then opens the browser

echo 🚀 ISO Bootable Maker - Starting deployment...
echo ==============================================

REM Check if Docker is installed and running
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker first.
    echo    Visit: https://docs.docker.com/get-docker/
    pause
    exit /b 1
)

docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

echo ✅ Docker is installed and running

REM Build the Docker image
echo.
echo 🔨 Building Docker image...
docker build -t iso-maker .

if %errorlevel% neq 0 (
    echo ❌ Failed to build Docker image
    pause
    exit /b 1
)

echo ✅ Docker image built successfully

REM Create directories if they don't exist
echo.
echo 📁 Creating directories...
if not exist "uploads" mkdir uploads
if not exist "output" mkdir output

REM Stop any existing container with the same name
echo.
echo 🧹 Cleaning up existing containers...
docker stop iso-maker-container >nul 2>&1
docker rm iso-maker-container >nul 2>&1

REM Run the container
echo.
echo 🚀 Starting container...
docker run -d --name iso-maker-container --privileged -p 5013:5000 -v "%cd%/uploads:/app/uploads" -v "%cd%/output:/app/output" iso-maker

if %errorlevel% neq 0 (
    echo ❌ Failed to start container
    pause
    exit /b 1
)

echo ✅ Container started successfully

REM Wait a moment for the app to start
echo.
echo ⏳ Waiting for application to start...
timeout /t 3 /nobreak >nul

REM Check if the container is running
docker ps | findstr iso-maker-container >nul
if %errorlevel% neq 0 (
    echo ❌ Container failed to start
    echo 📋 Container logs:
    docker logs iso-maker-container
    pause
    exit /b 1
)

echo ✅ Container is running

REM Set the URL
set URL=http://localhost:5013

echo.
echo 🎉 Deployment successful!
echo ==============================================
echo 📱 Application URL: %URL%
echo 📁 Uploads directory: %cd%\uploads
echo 📁 Output directory: %cd%\output
echo.
echo 🛑 To stop the container, run: docker stop iso-maker-container
echo 🗑️  To remove the container, run: docker rm iso-maker-container
echo.

REM Try to open the browser automatically
echo 🌐 Opening browser...
start "" "%URL%"

echo.
echo ✨ Ready to use! The browser should open automatically.
echo    If not, manually navigate to: %URL%

pause
