# ISO Bootable Maker - Easy Deployment

This guide will help you quickly deploy the ISO Bootable Maker application using Docker.

## Prerequisites

- Docker installed and running
- Git (to clone the repository)

## Quick Deployment

### Option 1: Automated Script (Recommended)

#### For Linux/macOS:
```bash
# Make the script executable and run it
chmod +x deploy.sh
./deploy.sh
```

#### For Windows:
```cmd
# Double-click deploy.bat or run from command prompt
deploy.bat
```

The script will:
1. ✅ Check if Docker is installed and running
2. 🔨 Build the Docker image
3. 📁 Create necessary directories
4. 🚀 Start the container
5. 🌐 Automatically open your browser to http://localhost:5013

### Option 2: Manual Docker Commands

If you prefer to run the commands manually:

```bash
# Build the image
docker build -t iso-maker .

# Create directories
mkdir -p uploads output

# Run the container
docker run -d \
    --name iso-maker-container \
    --privileged \
    -p 5013:5000 \
    -v "$(pwd)/uploads:/app/uploads" \
    -v "$(pwd)/output:/app/output" \
    iso-maker

# Open browser (Linux/macOS)
open http://localhost:5013

# Open browser (Windows)
start http://localhost:5013
```

## Usage

1. **Upload**: Select an ISO file and click "Process ISO"
2. **Monitor**: Watch the processing steps with real-time progress
3. **Download**: Get your bootable ISO from the results section

## Stopping the Application

```bash
# Stop the container
docker stop iso-maker-container

# Remove the container
docker rm iso-maker-container

# Remove the image (optional)
docker rmi iso-maker
```

## Troubleshooting

### Container won't start
- Check if Docker is running: `docker info`
- Check container logs: `docker logs iso-maker-container`
- Ensure port 5013 is not in use by another application

### Permission issues
- On Linux/macOS, ensure Docker has permission to access the current directory
- Try running with `sudo` if needed

### Browser doesn't open automatically
- Manually navigate to: http://localhost:5013
- Check if your firewall is blocking the port

## Directory Structure

```
iso-maker/
├── uploads/          # Temporary upload storage
├── output/           # Generated bootable ISOs
├── deploy.sh         # Linux/macOS deployment script
├── deploy.bat        # Windows deployment script
└── ...
```

## Support

If you encounter any issues:
1. Check the container logs: `docker logs iso-maker-container`
2. Ensure all prerequisites are met
3. Try rebuilding the image: `docker build -t iso-maker . --no-cache`
