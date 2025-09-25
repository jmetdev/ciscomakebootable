# ISO Bootable Maker

A web interface for creating bootable ISO files from existing ISO images. This application processes ISO files and makes them bootable using modern web technologies and Docker containerization.

## Features

- 🚀 **One-Command Deployment** - Easy setup with Docker
- 📁 **Web-based Upload Interface** - Simple drag-and-drop ISO upload
- ⚡ **Real-time Progress Tracking** - Step-by-step processing status
- 🎯 **Cisco UC Support** - Optimized for Cisco Unified Communications ISOs
- 📦 **Automatic Product Detection** - Extracts version and product information
- 💾 **Direct Download** - Get your processed ISO immediately
- 🎨 **Modern UI** - Clean interface built with Tabler.io components
- 📊 **File Size Display** - Real-time upload progress and file information

## Prerequisites

- **Docker** installed on your system
- **No additional packages required** - Everything is containerized!

## Quick Start

### 🐳 Docker Deployment (Recommended)

#### For Linux/macOS:
```bash
# Clone the repository
git clone <your-repo-url>
cd makeBootable

# Make the deployment script executable
chmod +x deploy.sh

# Deploy the application
./deploy.sh
```

#### For Windows:
```batch
# Clone the repository
git clone <your-repo-url>
cd makeBootable

# Run the deployment script
deploy.bat
```

The deployment script will:
- ✅ Check Docker installation
- 🔨 Build the Docker image
- 🚀 Start the container with proper volume mounts
- 🌐 Automatically open your browser to the application
- 📋 Display container logs for monitoring

### 📍 Access the Application

Once deployed, the application will be available at:
- **URL**: `http://localhost:5013`
- **Auto-opens** in your default browser

## How to Use

### 1. 📤 Upload an ISO File

1. **Navigate** to the web interface at `http://localhost:5013`
2. **Click** "Choose File" or drag-and-drop your ISO file
3. **Supported formats**: `.iso` files (tested with Cisco UC ISOs)
4. **File size**: Up to 16GB supported
5. **Watch** the upload progress bar and file size display

### 2. ⚙️ Process the ISO

1. **Click** "Process ISO" button
2. **Monitor** the real-time progress steps:
   - 📁 **Setup Directories** - Preparing workspace
   - 📦 **Extract ISO** - Extracting contents using 7zip
   - 📋 **Copy Contents** - Moving files to working directory
   - 🔍 **Analyze Product** - Detecting Cisco product information
   - ⚙️ **Check Bootloader** - Verifying boot configuration
   - 🔨 **Generate ISO** - Creating new bootable ISO
   - 🧹 **Cleanup** - Removing temporary files
   - ✅ **Complete** - Processing finished successfully

### 3. 📥 Download Your Bootable ISO

1. **Wait** for all steps to complete (usually 2-5 minutes)
2. **Click** the download link that appears
3. **Save** your new bootable ISO file
4. **Use** the ISO for your deployment needs

## Product Information Display

The application automatically detects and displays:
- **Product Name** (e.g., "Cisco Unified Communications Manager")
- **Version String** (e.g., "15.0.1 (SU3)")
- **Major Version** (e.g., "15")
- **Minor Version** (e.g., "0")
- **Maintenance Version** (e.g., "1")
- **Service Update** (e.g., "SU3" or "GA")
- **Build Number** (e.g., "13900")
- **Full Version** (e.g., "15.0.1.13900")

## Troubleshooting

### Container Won't Start
```bash
# Check if port 5013 is already in use
sudo lsof -i :5013

# Stop any existing containers
docker stop iso-maker-app 2>/dev/null || true
docker rm iso-maker-app 2>/dev/null || true

# Try deploying again
./deploy.sh
```

### Upload Fails
- **Check file size**: Ensure it's under 16GB
- **Verify file format**: Must be a valid `.iso` file
- **Check disk space**: Ensure you have enough space for processing

### Processing Fails
- **Check logs**: View container logs with `docker logs iso-maker-app`
- **Verify ISO**: Ensure the uploaded ISO is not corrupted
- **Retry**: Some network issues may cause temporary failures

### Browser Won't Open
- **Manual access**: Navigate to `http://localhost:5013`
- **Check firewall**: Ensure port 5013 is not blocked
- **Try different browser**: Some browsers may have security restrictions

## How It Works

The application processes ISO files through these steps:

1. **📁 Setup Directories** - Creates temporary workspace
2. **📦 Extract ISO** - Uses 7zip to extract ISO contents (preserves file structure)
3. **📋 Copy Contents** - Moves extracted files to working directory
4. **🔍 Analyze Product** - Parses filename to extract Cisco product information
5. **⚙️ Check Bootloader** - Verifies isolinux bootloader configuration
6. **🔨 Generate ISO** - Creates new bootable ISO using genisoimage
7. **🧹 Cleanup** - Removes temporary files and directories
8. **✅ Complete** - Provides download link for the processed ISO

## Supported Cisco Products

The application automatically detects and processes:
- **Cisco Unified Communications Manager** (CUCM)
- **Cisco Unity Connection** (CUC)
- **Cisco Emergency Responder** (CER)
- **Cisco IM & Presence** (IMP)
- **Cisco Contact Center Express** (UCCX)
- **Cisco Prime Collaboration Deployment** (PCD)

## File Structure

```
makeBootable/
├── .gitignore              # Git ignore rules
├── .dockerignore           # Docker ignore rules
├── app.py                  # Main Flask application
├── deploy.sh               # Linux/macOS deployment script
├── deploy.bat              # Windows deployment script
├── DEPLOYMENT.md           # Detailed deployment instructions
├── Dockerfile              # Docker container definition
├── README.md               # This file
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html          # Web interface template
├── uploads/
│   └── .gitkeep            # Preserve empty directory
└── output/
    └── .gitkeep            # Preserve empty directory
```

## Docker Configuration

### Container Details
- **Base Image**: Python 3.13 on Debian Trixie
- **Port**: 5013 (mapped from container port 5000)
- **Container Name**: `iso-maker-app`
- **Restart Policy**: Unless stopped

### Volume Mounts
- **`./output:/app/output`** - Generated bootable ISO files
- **`./uploads:/app/uploads`** - Temporary storage for uploaded files
- **`./tmp:/app/tmp`** - Temporary processing directories

## Dockerfile Details

### Base Image
```dockerfile
FROM python:3.13-slim-trixie
```
- **Python 3.13** - Latest Python runtime
- **Debian Trixie** - Latest stable Debian distribution
- **Slim variant** - Minimal base image for reduced size

### System Packages Installed
The Dockerfile installs the following apt packages to support ISO processing:

```dockerfile
RUN apt-get update && apt-get install -y \
    python3 \          # Python 3 runtime
    python3-pip \      # Python package manager
    python3-venv \     # Python virtual environment support
    genisoimage \      # ISO creation and manipulation tool
    rsync \            # File synchronization utility
    isolinux \         # Linux bootloader for ISO files
    sudo \             # System administration tool
    curl \             # HTTP client for health checks
    p7zip-full \       # 7zip archive extraction tool
    && rm -rf /var/lib/apt/lists/*
```

### Package Purposes

| Package | Purpose | Used For |
|---------|---------|----------|
| **python3** | Python runtime | Core application execution |
| **python3-pip** | Package manager | Installing Python dependencies |
| **python3-venv** | Virtual environments | Python environment management |
| **genisoimage** | ISO creation | Generating bootable ISO files |
| **rsync** | File sync | Copying ISO contents efficiently |
| **isolinux** | Bootloader | Linux boot configuration for ISOs |
| **sudo** | System admin | Mount/unmount operations (with NOPASSWD) |
| **curl** | HTTP client | Container health checks |
| **p7zip-full** | Archive tool | Extracting ISO contents |

### Security Configuration
```dockerfile
# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Configure sudo access for mount operations
RUN echo "appuser ALL=(ALL) NOPASSWD: /bin/mount, /bin/umount" > /etc/sudoers.d/appuser

# Switch to non-root user
USER appuser
```

### Directory Structure
```dockerfile
RUN mkdir -p /app/uploads /app/output /app/templates /app/tmp
```
- **`/app/uploads`** - Temporary file upload storage
- **`/app/output`** - Generated ISO file storage  
- **`/app/templates`** - Web interface templates
- **`/app/tmp`** - Processing workspace

### Health Check
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1
```
- **30-second intervals** - Regular health monitoring
- **10-second timeout** - Fast failure detection
- **5-second start period** - Grace period for startup
- **3 retries** - Tolerance for temporary issues

## Management Commands

### View Container Logs
```bash
docker logs iso-maker-app
```

### Stop the Container
```bash
docker stop iso-maker-app
```

### Remove the Container
```bash
docker rm iso-maker-app
```

### Restart the Container
```bash
docker restart iso-maker-app
```

## API Endpoints

- `GET /` - Main upload interface
- `POST /upload` - File upload and processing
- `GET /step-status` - Real-time processing status
- `GET /product-info` - Extracted product information
- `GET /download/<filename>` - Download processed ISO file

## Security & Privacy

- ✅ **No data retention** - Files are automatically deleted after processing
- ✅ **Container isolation** - Runs in isolated Docker environment
- ✅ **File type validation** - Only `.iso` files accepted
- ✅ **Temporary processing** - All operations use temporary directories
- ✅ **Automatic cleanup** - No persistent storage of uploaded files

## Performance

- **Processing Time**: 2-5 minutes for typical Cisco UC ISOs
- **File Size Limit**: Up to 16GB supported
- **Memory Usage**: ~2GB RAM during processing
- **Disk Space**: Requires 2x the ISO size for temporary processing

## License

This project is provided as-is for educational and development purposes.
