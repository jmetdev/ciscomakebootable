#!/bin/bash

# ISO Bootable Maker - Easy Deployment Script
# This script builds and runs the Docker container, then opens the browser

set -e  # Exit on any error

echo "🚀 ISO Bootable Maker - Starting deployment..."
echo "=============================================="

# Check if Docker is installed and running
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is installed and running"

# Build the Docker image
echo ""
echo "🔨 Building Docker image..."
docker build -t iso-maker .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully"
else
    echo "❌ Failed to build Docker image"
    exit 1
fi

# Create directories if they don't exist
echo ""
echo "📁 Creating directories..."
mkdir -p uploads output

# Stop any existing container with the same name
echo ""
echo "🧹 Cleaning up existing containers..."
docker stop iso-maker-container 2>/dev/null || true
docker rm iso-maker-container 2>/dev/null || true

# Run the container
echo ""
echo "🚀 Starting container..."
docker run -d \
    --name iso-maker-container \
    --privileged \
    -p 5013:5000 \
    -v "$(pwd)/uploads:/app/uploads" \
    -v "$(pwd)/output:/app/output" \
    iso-maker

if [ $? -eq 0 ]; then
    echo "✅ Container started successfully"
else
    echo "❌ Failed to start container"
    exit 1
fi

# Wait a moment for the app to start
echo ""
echo "⏳ Waiting for application to start..."
sleep 3

# Check if the container is running
if docker ps | grep -q iso-maker-container; then
    echo "✅ Container is running"
else
    echo "❌ Container failed to start"
    echo "📋 Container logs:"
    docker logs iso-maker-container
    exit 1
fi

# Determine the URL to open
URL="http://localhost:5013"

echo ""
echo "🎉 Deployment successful!"
echo "=============================================="
echo "📱 Application URL: $URL"
echo "📁 Uploads directory: $(pwd)/uploads"
echo "📁 Output directory: $(pwd)/output"
echo ""
echo "🛑 To stop the container, run: docker stop iso-maker-container"
echo "🗑️  To remove the container, run: docker rm iso-maker-container"
echo ""

# Try to open the browser automatically
echo "🌐 Opening browser..."
if command -v xdg-open &> /dev/null; then
    # Linux
    xdg-open "$URL" &
elif command -v open &> /dev/null; then
    # macOS
    open "$URL" &
elif command -v start &> /dev/null; then
    # Windows (Git Bash)
    start "$URL" &
else
    echo "⚠️  Could not auto-open browser. Please manually open: $URL"
fi

echo ""
echo "✨ Ready to use! The browser should open automatically."
echo "   If not, manually navigate to: $URL"
